# wedpy

`wedpy` is the Python package for the WED symmetric encryption protocol.

It is implemented as a native Python extension backed by the shared Rust core in [`crypto-core`](../crypto-core).

## Install

From PyPI:

```bash
pip install wedpy
```

From this repository for local development:

```bash
python3 -m venv /tmp/wed-venv
source /tmp/wed-venv/bin/activate
python -m pip install pytest maturin
maturin develop --manifest-path crates/crypto-python/Cargo.toml
```

## API

The package exports:

- `encrypt_text(passphrase, plaintext) -> str`
- `decrypt_text(passphrase, token) -> str`
- `encrypt_json(passphrase, value) -> str`
- `decrypt_json(passphrase, token) -> Any`

Text example:

```python
from wedpy import decrypt_text, encrypt_text

token = encrypt_text("shared-passphrase", "hello")
plaintext = decrypt_text("shared-passphrase", token)
```

JSON example:

```python
from wedpy import decrypt_json, encrypt_json

token = encrypt_json("shared-passphrase", {"message": "hello"})
payload = decrypt_json("shared-passphrase", token)
```

## Notes

- `encrypt_json` uses Python's `json.dumps` with compact separators.
- `decrypt_json` returns the deserialized Python object.
- Errors are surfaced as `ValueError`.

## Test

Run the package tests:

```bash
source /tmp/wed-venv/bin/activate
pytest crates/crypto-python/tests/test_crypto.py -q
```

Run the runnable example:

```bash
bash examples/python/run_example_test.sh
```
