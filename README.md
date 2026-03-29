# WED Crypto

Rust-based symmetric encryption package for shared frontend and backend use:

- React consumes the WASM bindings in [`crates/crypto-wasm`](/Users/xxx/Documents/Repos/github.com/ohxxx/wed/crates/crypto-wasm)
- Python consumes the native extension in [`crates/crypto-python`](/Users/xxx/Documents/Repos/github.com/ohxxx/wed/crates/crypto-python)
- Both bindings share the same core protocol from [`crates/crypto-core`](/Users/xxx/Documents/Repos/github.com/ohxxx/wed/crates/crypto-core)

## Token Format

Encrypted payloads are encoded as:

```text
wed1.<salt_b64url>.<nonce_b64url>.<ciphertext_b64url>
```

Internally the library uses:

- `AES-256-GCM`
- `Argon2id`
- random 16-byte salt
- random 12-byte nonce

## Rust Core

Run the core tests:

```bash
cargo test -p crypto-core
```

## React / WASM Usage

Build the package for a bundler-based React app:

```bash
wasm-pack build crates/crypto-wasm --target bundler --out-dir pkg
```

Then import the generated package in React:

```ts
import init, { decryptText, encryptJson, encryptText } from "./pkg/crypto_wasm";

await init();

const token = encryptJson("shared-passphrase", { message: "hello" });
const plaintext = decryptText("shared-passphrase", token);
```

Run the WASM tests:

```bash
wasm-pack test --node crates/crypto-wasm
```

Run the complete React example test:

```bash
cd examples/react
npm test
```

## Python Usage

Create a virtualenv, install the extension in editable mode, then import it:

```bash
python3 -m venv /tmp/wed-venv
source /tmp/wed-venv/bin/activate
python -m pip install pytest maturin
maturin develop --manifest-path crates/crypto-python/Cargo.toml
```

```python
from wed_crypto import decrypt_json, encrypt_json

token = encrypt_json("shared-passphrase", {"message": "hello"})
payload = decrypt_json("shared-passphrase", token)
```

Run the Python tests:

```bash
source /tmp/wed-venv/bin/activate
pytest crates/crypto-python/tests/test_crypto.py -q
```

Run the complete Python example test:

```bash
bash examples/python/run_example_test.sh
```

## Security Note

This package gives you authenticated symmetric encryption for request payloads, but if the frontend can decrypt then the frontend runtime necessarily has access to the passphrase or a derived equivalent. It is suitable for protocol-level protection, not for hiding secrets from a user who controls the browser runtime.
