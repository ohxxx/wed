import json
import unittest
from pathlib import Path


class NodeScriptTests(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parents[1]

    def test_wedts_runtime_test_uses_wasm_flag(self):
        package_json = json.loads(
            (self.repo_root / "packages" / "wedts" / "package.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            package_json["scripts"]["test"],
            "node --experimental-wasm-modules tests/runtime.mjs",
        )

    def test_react_example_uses_wasm_flag(self):
        package_json = json.loads(
            (self.repo_root / "examples" / "react" / "package.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            package_json["scripts"]["test"],
            "node --experimental-wasm-modules test.mjs",
        )


if __name__ == "__main__":
    unittest.main()
