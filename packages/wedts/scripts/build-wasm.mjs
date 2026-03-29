import { execFileSync } from "node:child_process";
import { mkdirSync, rmSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const packageDir = path.resolve(scriptDir, "..");
const repoRoot = path.resolve(packageDir, "..", "..");
const outDir = path.join(packageDir, "dist", "wasm");

rmSync(outDir, { recursive: true, force: true });
mkdirSync(outDir, { recursive: true });

execFileSync(
  "wasm-pack",
  [
    "build",
    path.join(repoRoot, "crates", "crypto-wasm"),
    "--target",
    "bundler",
    "--release",
    "--out-dir",
    outDir
  ],
  {
    cwd: repoRoot,
    stdio: "inherit"
  }
);

rmSync(path.join(outDir, "package.json"), { force: true });
rmSync(path.join(outDir, ".gitignore"), { force: true });
