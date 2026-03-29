# crypto-core

`crypto-core` is the canonical Rust implementation for the WED token protocol.

Every other package in this repository depends on this crate for the actual encryption and decryption behavior:

- [`crypto-wasm`](../crypto-wasm) exposes it to JavaScript through `wasm-bindgen`
- [`wedpy`](../crypto-python) exposes it to Python through `PyO3`

## What It Implements

- `AES-256-GCM` for authenticated encryption
- `Argon2id` for deriving a 32-byte key from a passphrase
- a stable token format shared across languages

Token format:

```text
wed1.<salt_b64url>.<nonce_b64url>.<ciphertext_b64url>
```

Field sizes:

- salt: 16 bytes
- nonce: 12 bytes
- key: 32 bytes

## Rust API

Text helpers:

```rust
use crypto_core::{decrypt_text, encrypt_text};

let token = encrypt_text("shared-passphrase", "hello")?;
let plaintext = decrypt_text("shared-passphrase", &token)?;
```

Byte helpers:

```rust
use crypto_core::{decrypt_bytes, encrypt_bytes};

let token = encrypt_bytes("shared-passphrase", b"hello")?;
let plaintext = decrypt_bytes("shared-passphrase", &token)?;
```

## Error Model

The crate exposes `CryptoError` with these variants:

- `InvalidFormat`
- `DecryptFailed`
- `InvalidUtf8`

`DecryptFailed` intentionally covers both wrong-passphrase and tampered-token cases.

## Tests

Run:

```bash
cargo test -p crypto-core
```

The test suite covers:

- roundtrip encryption and decryption
- randomization of salt and nonce
- wrong-passphrase failures
- malformed or truncated token failures
