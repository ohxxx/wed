# wedpy

Python bindings for the WED Rust crypto core.

```python
from wedpy import encrypt_json, decrypt_json

token = encrypt_json("shared-passphrase", {"message": "hello"})
payload = decrypt_json("shared-passphrase", token)
```

The package exposes:

- `encrypt_text`
- `decrypt_text`
- `encrypt_json`
- `decrypt_json`
