# WED Crypto

WED Crypto is a shared symmetric encryption stack for frontend and backend use.

- Frontend package: [`@ohxxx/wedts`](packages/wedts)
- Python package: [`wedpy`](crates/crypto-python)
- Shared Rust protocol core: [`crypto-core`](crates/crypto-core)
- Low-level WASM binding crate: [`crypto-wasm`](crates/crypto-wasm)

The goal is simple: React and Python use the same token format, the same key-derivation rules, and the same authenticated encryption behavior.

## Package Map

| Package | What it is for | Where to start |
| --- | --- | --- |
| `@ohxxx/wedts` | TypeScript-friendly npm package for React and other JS apps | [`packages/wedts/README.md`](packages/wedts/README.md) |
| `wedpy` | Python extension module backed by the Rust core | [`crates/crypto-python/README.md`](crates/crypto-python/README.md) |
| `crypto-core` | Canonical protocol and crypto implementation | [`crates/crypto-core/README.md`](crates/crypto-core/README.md) |
| `crypto-wasm` | Low-level Rust-to-WASM exports used by `@ohxxx/wedts` | [`crates/crypto-wasm/README.md`](crates/crypto-wasm/README.md) |

## Protocol

Encrypted payloads are encoded as a single token string:

```text
wed1.<salt_b64url>.<nonce_b64url>.<ciphertext_b64url>
```

Protocol details:

- algorithm: `AES-256-GCM`
- key derivation: `Argon2id`
- salt: random 16 bytes
- nonce: random 12 bytes
- encoding: URL-safe base64 without padding

If decryption fails, callers only get a controlled error. The API does not distinguish between a wrong passphrase and a tampered token.

## Quick Start

React or TypeScript:

```bash
npm install @ohxxx/wedts
```

```ts
import { decryptJson, encryptJson } from "@ohxxx/wedts";

const token = encryptJson("shared-passphrase", { message: "hello" });
const payload = decryptJson<{ message: string }>("shared-passphrase", token);
```

Python:

```bash
pip install wedpy
```

```python
from wedpy import decrypt_json, encrypt_json

token = encrypt_json("shared-passphrase", {"message": "hello"})
payload = decrypt_json("shared-passphrase", token)
```

## Repository Layout

```text
crates/
  crypto-core/    Canonical Rust implementation and protocol tests
  crypto-wasm/    wasm-bindgen exports
  crypto-python/  PyO3 extension module for Python
packages/
  wedts/          Typed npm wrapper around the WASM build
examples/
  react/          Runnable npm example
  python/         Runnable Python example
tests/
  vectors/        Verification notes for cross-package behavior
```

## Verification

Core Rust tests:

```bash
cargo test -p crypto-core
```

Workspace tests:

```bash
cargo test --workspace
```

WASM tests:

```bash
wasm-pack test --node crates/crypto-wasm
```

Typed npm package checks:

```bash
cd packages/wedts
npm install
npm test
npm run typecheck
```

React example:

```bash
cd examples/react
npm install
npm test
```

Python extension tests:

```bash
python3 -m venv /tmp/wed-venv
source /tmp/wed-venv/bin/activate
python -m pip install pytest maturin
maturin develop --manifest-path crates/crypto-python/Cargo.toml
pytest crates/crypto-python/tests/test_crypto.py -q
```

Python example:

```bash
bash examples/python/run_example_test.sh
```

See [`tests/vectors/README.md`](tests/vectors/README.md) for the validation matrix.

## Security Scope

This project gives you authenticated symmetric encryption for request payloads. It does not hide secrets from a user who controls the browser runtime, because a frontend that can decrypt must also have access to the passphrase or an equivalent derived key.
