import importlib.util
import json
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock


def load_release_module():
    repo_root = Path(__file__).resolve().parents[1]
    module_path = repo_root / "release.py"
    spec = importlib.util.spec_from_file_location("wed_release", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ReleaseScriptTests(unittest.TestCase):
    def setUp(self):
        self.module = load_release_module()
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)

        (self.root / "packages" / "wedts").mkdir(parents=True)
        (self.root / "crates" / "crypto-core").mkdir(parents=True)
        (self.root / "crates" / "crypto-wasm").mkdir(parents=True)
        (self.root / "crates" / "crypto-python").mkdir(parents=True)

        (self.root / "packages" / "wedts" / "package.json").write_text(
            json.dumps({"name": "@ohxxx/wedts", "version": "0.1.0"}, indent=2) + "\n",
            encoding="utf-8",
        )
        (self.root / "packages" / "wedts" / "package-lock.json").write_text(
            json.dumps(
                {
                    "name": "@ohxxx/wedts",
                    "version": "0.1.0",
                    "packages": {
                        "": {"name": "@ohxxx/wedts", "version": "0.1.0"},
                    },
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        for crate_name in ("crypto-core", "crypto-wasm", "crypto-python"):
            (self.root / "crates" / crate_name / "Cargo.toml").write_text(
                textwrap.dedent(
                    f"""\
                    [package]
                    name = "{crate_name}"
                    version = "0.1.0"
                    edition = "2021"
                    """
                ),
                encoding="utf-8",
            )
        (self.root / "crates" / "crypto-python" / "pyproject.toml").write_text(
            textwrap.dedent(
                """\
                [project]
                name = "wedpy"
                version = "0.1.0"
                """
            ),
            encoding="utf-8",
        )

    def tearDown(self):
        self.tempdir.cleanup()

    def test_sync_versions_updates_all_manifests(self):
        self.module.sync_versions(self.root, "1.2.3")

        versions = self.module.collect_versions(self.root)
        self.assertEqual(set(versions.values()), {"1.2.3"})

        package_lock = json.loads(
            (self.root / "packages" / "wedts" / "package-lock.json").read_text(encoding="utf-8")
        )
        self.assertEqual(package_lock["version"], "1.2.3")
        self.assertEqual(package_lock["packages"][""]["version"], "1.2.3")

    def test_build_release_plan_switches_publish_commands_for_dry_run(self):
        dry_run_steps = self.module.build_release_plan(self.root, dry_run=True)
        release_steps = self.module.build_release_plan(self.root, dry_run=False)

        dry_run_commands = [" ".join(step.argv) for step in dry_run_steps]
        release_commands = [" ".join(step.argv) for step in release_steps]

        self.assertIn("npm pack --dry-run", dry_run_commands)
        self.assertIn(
            "maturin build --manifest-path crates/crypto-python/Cargo.toml --out dist/releases",
            dry_run_commands,
        )
        self.assertTrue(
            any(command.endswith("-m twine check dist/releases/*") for command in dry_run_commands)
        )

        self.assertIn("npm publish --access public", release_commands)
        self.assertIn(
            "maturin publish --manifest-path crates/crypto-python/Cargo.toml --skip-existing",
            release_commands,
        )

    def test_require_environment_rejects_missing_twine_for_dry_run(self):
        with mock.patch.object(self.module.shutil, "which", return_value="/usr/bin/fake"):
            with mock.patch.object(self.module.importlib.util, "find_spec", return_value=None):
                with self.assertRaisesRegex(self.module.ReleaseError, "twine"):
                    self.module.require_environment(dry_run=True)

    def test_parse_args_accepts_explicit_version(self):
        args = self.module.parse_args(["1.4.0"])
        self.assertEqual(args.version, "1.4.0")
        self.assertFalse(args.dry_run)

    def test_require_release_version_for_publish(self):
        with self.assertRaisesRegex(self.module.ReleaseError, "version"):
            self.module.require_release_version(version=None, dry_run=False)

    def test_require_publish_credentials_rejects_missing_pypi_token(self):
        with mock.patch.dict(self.module.os.environ, {}, clear=True):
            with self.assertRaisesRegex(self.module.ReleaseError, "MATURIN_PYPI_TOKEN"):
                self.module.require_publish_credentials(dry_run=False)

    def test_require_publish_credentials_maps_pypi_token_for_maturin(self):
        with mock.patch.dict(self.module.os.environ, {"PYPI_TOKEN": "pypi-test"}, clear=True):
            self.module.require_publish_credentials(dry_run=False)
            self.assertEqual(self.module.os.environ["MATURIN_PYPI_TOKEN"], "pypi-test")

    def test_filter_release_plan_skips_existing_npm_publish(self):
        steps = self.module.build_release_plan(self.root, dry_run=False)
        with mock.patch.object(self.module, "npm_version_exists", return_value=True):
            filtered_steps = self.module.filter_release_plan(self.root, steps, "0.1.0", dry_run=False)

        self.assertNotIn("npm publish", [step.label for step in filtered_steps])
        self.assertIn("python publish", [step.label for step in filtered_steps])

    def test_filter_release_plan_keeps_npm_publish_for_new_version(self):
        steps = self.module.build_release_plan(self.root, dry_run=False)
        with mock.patch.object(self.module, "npm_version_exists", return_value=False):
            filtered_steps = self.module.filter_release_plan(self.root, steps, "0.1.0", dry_run=False)

        self.assertIn("npm publish", [step.label for step in filtered_steps])


if __name__ == "__main__":
    unittest.main()
