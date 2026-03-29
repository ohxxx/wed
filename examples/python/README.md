# Python Example

1. Create and activate a virtualenv:

```bash
python3 -m venv /tmp/wed-venv
source /tmp/wed-venv/bin/activate
python -m pip install pytest maturin
```

2. Install the Rust extension:

```bash
maturin develop --manifest-path crates/crypto-python/Cargo.toml
```

3. Use it:

```python
from wed_crypto import decrypt_text, encrypt_text

token = encrypt_text("shared-passphrase", "hello")
plaintext = decrypt_text("shared-passphrase", token)
```
