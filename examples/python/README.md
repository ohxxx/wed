# Python Example

This directory is a runnable consumer check for [`wedpy`](../../crates/crypto-python/README.md).

It creates an isolated virtual environment, installs the local Rust-backed extension with `maturin develop`, and runs example assertions.

## Run

```bash
cd examples/python
bash run_example_test.sh
```

Expected success output:

```text
python example ok
```

## Manual Setup

```bash
python3 -m venv /tmp/wed-venv
source /tmp/wed-venv/bin/activate
python -m pip install pytest maturin
maturin develop --manifest-path crates/crypto-python/Cargo.toml
```

## Example Usage

```python
from wedpy import decrypt_text, encrypt_text

token = encrypt_text("shared-passphrase", "hello")
plaintext = decrypt_text("shared-passphrase", token)
```
