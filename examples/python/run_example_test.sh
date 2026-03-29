#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv-example-python"

python3 -m venv "${VENV_DIR}"
source "${VENV_DIR}/bin/activate"
python -m pip install -q maturin
maturin develop --manifest-path "${ROOT_DIR}/crates/crypto-python/Cargo.toml" >/dev/null
python "${ROOT_DIR}/examples/python/test_example.py"
