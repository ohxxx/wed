#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


PACKAGE_JSON_PATH = Path("packages/wedts/package.json")
PACKAGE_LOCK_PATH = Path("packages/wedts/package-lock.json")
CORE_CARGO_PATH = Path("crates/crypto-core/Cargo.toml")
WASM_CARGO_PATH = Path("crates/crypto-wasm/Cargo.toml")
PYTHON_CARGO_PATH = Path("crates/crypto-python/Cargo.toml")
PYPROJECT_PATH = Path("crates/crypto-python/pyproject.toml")
DIST_DIR = Path("dist/releases")

VERSION_LINE_RE = re.compile(r'^(version\s*=\s*")([^"]+)(".*)$', re.MULTILINE)


class ReleaseError(RuntimeError):
    pass


@dataclass(frozen=True)
class CommandStep:
    label: str
    argv: list[str]
    cwd: Path
    shell: bool = False


def repo_root() -> Path:
    return Path(__file__).resolve().parent


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def replace_toml_version(path: Path, version: str) -> None:
    content = path.read_text(encoding="utf-8")
    updated, count = VERSION_LINE_RE.subn(rf'\g<1>{version}\g<3>', content, count=1)
    if count != 1:
        raise ReleaseError(f"could not update version in {path}")
    path.write_text(updated, encoding="utf-8")


def read_toml_version(path: Path) -> str:
    content = path.read_text(encoding="utf-8")
    match = VERSION_LINE_RE.search(content)
    if match is None:
        raise ReleaseError(f"could not find version in {path}")
    return match.group(2)


def collect_versions(root: Path) -> dict[str, str]:
    package_json = read_json(root / PACKAGE_JSON_PATH)
    package_lock = read_json(root / PACKAGE_LOCK_PATH)

    versions = {
        str(PACKAGE_JSON_PATH): package_json["version"],
        str(PACKAGE_LOCK_PATH): package_lock["version"],
        f"{PACKAGE_LOCK_PATH}#packages['']": package_lock["packages"][""]["version"],
        str(CORE_CARGO_PATH): read_toml_version(root / CORE_CARGO_PATH),
        str(WASM_CARGO_PATH): read_toml_version(root / WASM_CARGO_PATH),
        str(PYTHON_CARGO_PATH): read_toml_version(root / PYTHON_CARGO_PATH),
        str(PYPROJECT_PATH): read_toml_version(root / PYPROJECT_PATH),
    }
    return versions


def ensure_synced(root: Path) -> str:
    versions = collect_versions(root)
    unique_versions = sorted(set(versions.values()))
    if len(unique_versions) != 1:
        details = "\n".join(f"  {path}: {version}" for path, version in versions.items())
        raise ReleaseError(f"version mismatch detected:\n{details}")
    return unique_versions[0]


def sync_versions(root: Path, version: str) -> None:
    package_json_path = root / PACKAGE_JSON_PATH
    package_lock_path = root / PACKAGE_LOCK_PATH

    package_json = read_json(package_json_path)
    package_json["version"] = version
    write_json(package_json_path, package_json)

    package_lock = read_json(package_lock_path)
    package_lock["version"] = version
    if "packages" in package_lock and "" in package_lock["packages"]:
        package_lock["packages"][""]["version"] = version
    write_json(package_lock_path, package_lock)

    replace_toml_version(root / CORE_CARGO_PATH, version)
    replace_toml_version(root / WASM_CARGO_PATH, version)
    replace_toml_version(root / PYTHON_CARGO_PATH, version)
    replace_toml_version(root / PYPROJECT_PATH, version)


def build_release_plan(root: Path, dry_run: bool) -> list[CommandStep]:
    package_dir = root / "packages/wedts"
    steps = [
        CommandStep("cargo tests", ["cargo", "test", "--workspace"], root),
        CommandStep("wasm tests", ["wasm-pack", "test", "--node", "crates/crypto-wasm"], root),
        CommandStep("npm install", ["npm", "install"], package_dir),
        CommandStep("npm runtime tests", ["npm", "test"], package_dir),
        CommandStep("npm typecheck", ["npm", "run", "typecheck"], package_dir),
    ]

    if dry_run:
        steps.extend(
            [
                CommandStep(
                    "npm pack dry-run",
                    ["npm", "pack", "--dry-run"],
                    package_dir,
                ),
                CommandStep(
                    "python build",
                    [
                        "maturin",
                        "build",
                        "--manifest-path",
                        "crates/crypto-python/Cargo.toml",
                        "--out",
                        str(DIST_DIR),
                    ],
                    root,
                ),
                CommandStep(
                    "twine check",
                    [sys.executable, "-m", "twine", "check", f"{DIST_DIR}/*"],
                    root,
                    shell=True,
                ),
            ]
        )
    else:
        steps.extend(
            [
                CommandStep(
                    "npm publish",
                    ["npm", "publish", "--access", "public"],
                    package_dir,
                ),
                CommandStep(
                    "python publish",
                    [
                        "maturin",
                        "publish",
                        "--manifest-path",
                        "crates/crypto-python/Cargo.toml",
                        "--skip-existing",
                    ],
                    root,
                ),
            ]
        )

    return steps


def npm_version_exists(root: Path, version: str) -> bool:
    package_json = read_json(root / PACKAGE_JSON_PATH)
    package_name = package_json["name"]
    result = subprocess.run(
        ["npm", "view", f"{package_name}@{version}", "version", "--json"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return True

    combined_output = f"{result.stdout}\n{result.stderr}"
    if "E404" in combined_output or "404" in combined_output:
        return False

    raise ReleaseError(
        f"failed to query npm for {package_name}@{version}: {combined_output.strip()}"
    )


def filter_release_plan(
    root: Path, steps: list[CommandStep], version: str, dry_run: bool
) -> list[CommandStep]:
    if dry_run:
        return steps

    package_name = read_json(root / PACKAGE_JSON_PATH)["name"]
    if not npm_version_exists(root, version):
        return steps

    print(f"npm package {package_name}@{version} already exists, skipping npm publish")
    return [step for step in steps if step.label != "npm publish"]


def require_environment(dry_run: bool) -> None:
    required_commands = ["cargo", "wasm-pack", "npm", "maturin"]
    missing_commands = [
        command for command in required_commands if shutil.which(command) is None
    ]
    if missing_commands:
        raise ReleaseError(f"missing required commands: {', '.join(missing_commands)}")

    if dry_run and importlib.util.find_spec("twine") is None:
        raise ReleaseError("python module 'twine' is required for --dry-run")


def run_step(step: CommandStep) -> None:
    print(f"\n==> {step.label}")
    print(f"cwd: {step.cwd}")
    print(f"cmd: {' '.join(shlex.quote(part) for part in step.argv)}")

    if step.shell:
        command = " ".join(shlex.quote(part) for part in step.argv)
        subprocess.run(command, cwd=step.cwd, shell=True, check=True)
        return

    subprocess.run(step.argv, cwd=step.cwd, check=True)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync versions and release @ohxxx/wedts plus wedpy from the repo root."
    )
    parser.add_argument(
        "version",
        nargs="?",
        help="version to apply before building and publishing; if omitted, the current synced version is used",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="build and validate publish artifacts without uploading them",
    )
    return parser.parse_args(argv)


def require_release_version(version: str | None, dry_run: bool) -> None:
    if version is None and not dry_run:
        raise ReleaseError(
            "an explicit version is required for publish runs, for example: python3 release.py 0.1.1"
        )


def require_publish_credentials(dry_run: bool) -> None:
    if dry_run:
        return

    if not os.environ.get("MATURIN_PYPI_TOKEN") and os.environ.get("PYPI_TOKEN"):
        os.environ["MATURIN_PYPI_TOKEN"] = os.environ["PYPI_TOKEN"]

    if not os.environ.get("MATURIN_PYPI_TOKEN"):
        raise ReleaseError(
            "PyPI publish requires MATURIN_PYPI_TOKEN; you can also export PYPI_TOKEN and the script will reuse it"
        )


def main() -> int:
    args = parse_args()
    root = repo_root()
    require_environment(dry_run=args.dry_run)
    require_release_version(version=args.version, dry_run=args.dry_run)
    require_publish_credentials(dry_run=args.dry_run)

    if args.version:
        sync_versions(root, args.version)

    version = ensure_synced(root)
    print(f"release version: {version}")

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    for artifact in DIST_DIR.iterdir():
        if artifact.is_file():
            artifact.unlink()

    steps = build_release_plan(root, dry_run=args.dry_run)
    steps = filter_release_plan(root, steps, version, dry_run=args.dry_run)

    for step in steps:
        run_step(step)

    mode = "dry-run completed" if args.dry_run else "publish completed"
    print(f"\n{mode} for version {version}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ReleaseError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
