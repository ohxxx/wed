# Python Example

1. Run the complete example test:

```bash
bash run_example_test.sh
```

This will:

- create a local example virtualenv
- install the Rust-backed Python module with `maturin develop`
- run the example assertions

2. If you want to do it manually, create and activate a virtualenv:

```bash
python3 -m venv /tmp/wed-venv
source /tmp/wed-venv/bin/activate
python -m pip install pytest maturin
```

3. Install the Rust extension:

```bash
maturin develop --manifest-path crates/crypto-python/Cargo.toml
```

4. Use it:

```python
from wed_crypto import decrypt_text, encrypt_text

token = encrypt_text("shared-passphrase", "hello")
plaintext = decrypt_text("shared-passphrase", token)
```
