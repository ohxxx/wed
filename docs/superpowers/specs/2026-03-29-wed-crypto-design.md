# WED Rust/WASM Cross-Platform Crypto Package Design

## Goal

Build a symmetric encryption package centered on Rust so that:

- React can use it through a WASM package
- Python can use it through a native extension backed by the same Rust core
- Frontend and backend can encrypt and decrypt each other's payloads without protocol drift

The primary use case is HTTP request and response payload protection, where callers pass a passphrase and receive a single transport-safe encrypted token string.

## Non-Goals

- Asymmetric encryption
- Browser-only secrecy against an attacker who controls the frontend runtime
- File streaming for very large payloads in the first version
- Automatic network transport integration for React or Python frameworks

## Recommended Architecture

Use a Rust workspace with three crates:

1. `crates/crypto-core`
   - Owns the encryption protocol, key derivation, token parsing, error types, and test vectors
   - Exposes a stable Rust API consumed by all bindings
2. `crates/crypto-wasm`
   - Wraps `crypto-core` with `wasm-bindgen`
   - Produces the npm package used by React
3. `crates/crypto-python`
   - Wraps `crypto-core` with `pyo3`
   - Produces the Python package used by the backend

This keeps all cryptographic behavior in one implementation while exposing platform-appropriate APIs.

## Cryptography Choices

- Encryption algorithm: `AES-256-GCM`
- Key derivation: `Argon2id`
- Salt length: `16` bytes, generated randomly per encryption
- Nonce length: `12` bytes, generated randomly per encryption
- Token encoding: URL-safe Base64 without padding
- Protocol version prefix: `wed1`

Rationale:

- `AES-256-GCM` is widely supported, authenticated, and appropriate for request payload sizes
- `Argon2id` provides a stronger passphrase-to-key derivation path than plain hashing or weaker KDF defaults
- Random salt and nonce prevent deterministic output for identical inputs
- Base64url avoids transport issues in JSON, URLs, headers, and form fields

## Transport Format

Encrypted output is a single string token:

```text
wed1.<salt_b64url>.<nonce_b64url>.<ciphertext_b64url>
```

Rules:

- `wed1` is a fixed protocol version marker
- `salt_b64url` encodes 16 raw salt bytes
- `nonce_b64url` encodes 12 raw nonce bytes
- `ciphertext_b64url` encodes the AES-GCM output including the authentication tag
- Token parsing is strict and rejects malformed or extra segments

This token is the only cross-language wire format. All bindings must treat it as canonical.

## Core API Design

`crypto-core` exposes the protocol through bytes-first functions and thin text helpers.

### Rust API

```rust
pub fn encrypt_bytes(passphrase: &str, plaintext: &[u8]) -> Result<String, CryptoError>;
pub fn decrypt_bytes(passphrase: &str, token: &str) -> Result<Vec<u8>, CryptoError>;

pub fn encrypt_text(passphrase: &str, plaintext: &str) -> Result<String, CryptoError>;
pub fn decrypt_text(passphrase: &str, token: &str) -> Result<String, CryptoError>;
```

Design constraints:

- Callers provide a passphrase, not a raw symmetric key
- The library internally derives the AES-256 key from the passphrase and random salt
- Text helpers are implemented on top of the byte helpers
- JSON support remains a binding-level convenience, not a crypto-core responsibility

## Binding APIs

Bindings should stay intentionally small and map to the canonical token format.

### WASM / React API

Export functions with JS-friendly names:

```ts
encryptText(passphrase: string, plaintext: string): string
decryptText(passphrase: string, token: string): string
encryptJson(passphrase: string, value: unknown): string
decryptJson<T = unknown>(passphrase: string, token: string): T
```

Notes:

- `encryptJson` uses `JSON.stringify`
- `decryptJson` uses `JSON.parse`
- Binary byte-array APIs can be added later if needed, but are not required for the first delivery

### Python API

Expose matching functions:

```python
encrypt_text(passphrase: str, plaintext: str) -> str
decrypt_text(passphrase: str, token: str) -> str
encrypt_json(passphrase: str, value: Any) -> str
decrypt_json(passphrase: str, token: str) -> Any
```

Notes:

- `encrypt_json` uses `json.dumps`
- `decrypt_json` uses `json.loads`
- The first version can focus on text and JSON APIs since the main target is HTTP payload encryption

## Data Flow

### Encrypt

1. Accept passphrase and plaintext bytes
2. Generate random salt
3. Derive a 32-byte key from passphrase + salt using fixed `Argon2id` parameters
4. Generate random nonce
5. Encrypt with `AES-256-GCM`
6. Base64url-encode salt, nonce, and ciphertext
7. Assemble the `wed1` token string

### Decrypt

1. Parse and validate the `wed1` token structure
2. Base64url-decode salt, nonce, and ciphertext
3. Re-derive the key from passphrase + salt using the same fixed `Argon2id` parameters
4. Attempt authenticated decryption with `AES-256-GCM`
5. Return plaintext bytes or a controlled error

## Fixed KDF Parameters

The first version should hardcode the `Argon2id` parameter set so that all bindings remain interoperable without additional configuration.

Guidelines:

- Define the parameters once in `crypto-core`
- Include them in tests and docs
- Keep them internal for v1 instead of exposing tuning knobs

This reduces integration mistakes. If parameter versioning becomes necessary later, it should be introduced through a new protocol prefix rather than optional per-call settings.

## Error Model

Bindings should expose a stable, compact error surface instead of leaking raw dependency errors.

Canonical core errors:

- `InvalidFormat`
  - Token structure is invalid
  - Base64 decoding fails
  - Salt or nonce length is wrong
- `DecryptFailed`
  - Authentication failed
  - Passphrase is incorrect
  - Ciphertext was corrupted or tampered with
  - Version is unsupported after initial parsing
- `InvalidUtf8`
  - Text decoding failed after successful decryption
- `JsonError`
  - JSON serialization or deserialization failed in the binding helper

Security rule:

- The external API must not distinguish "wrong passphrase" from "tampered ciphertext"

## Package Layout

Proposed repository structure:

```text
Cargo.toml
README.md
crates/
  crypto-core/
  crypto-wasm/
  crypto-python/
examples/
  react/
  python/
tests/
  vectors/
```

Responsibilities:

- `crypto-core`: source of truth for protocol and crypto behavior
- `crypto-wasm`: JS/WASM-facing package metadata and exported functions
- `crypto-python`: Python-facing package metadata and exported functions
- `examples/react`: minimal React usage sample
- `examples/python`: minimal Python usage sample
- `tests/vectors`: stable interoperability fixtures if explicit vectors are needed

## Testing Strategy

Testing must prioritize protocol compatibility over crate-local convenience.

### Core Tests

- Encrypt then decrypt returns the original plaintext
- Equal plaintext + equal passphrase produce different tokens across runs
- Wrong passphrase fails decryption
- Modified token fails decryption
- Invalid segment counts and malformed base64 fail parsing
- Text helpers reject invalid UTF-8 correctly

### Cross-Binding Compatibility Tests

- Rust-generated token decrypts in WASM binding
- Rust-generated token decrypts in Python binding
- WASM-generated token decrypts in Python binding
- Python-generated token decrypts in WASM binding

### Fixture / Vector Tests

- Generate a deterministic test vector suite for CI
- Validate token parsing and decryption against known-good values
- Keep at least one JSON payload example and one plain text example

## Documentation Requirements

The initial delivery should include:

- Root README with purpose, security caveats, and package layout
- React usage example
- Python usage example
- Token format explanation
- Clear note that frontend decryption implies the passphrase is present in the frontend context

## Security Caveats

- This package protects payload transport and provides authenticated encryption, but it does not make browser-held secrets inaccessible to a user who controls the browser environment
- Passphrase management remains an application concern
- Reusing a human-readable low-entropy passphrase weakens the system even when `Argon2id` is used

## Implementation Sequence

1. Scaffold Rust workspace and package layout
2. Implement `crypto-core` token format, KDF, encryption, and parsing
3. Add core unit tests and protocol vectors
4. Add WASM bindings and React usage example
5. Add Python bindings and Python usage example
6. Add cross-language interoperability tests
7. Finish documentation for installation and usage

## Open Decisions Resolved

- Symmetric encryption only: yes
- Frontend and backend must be mutually interoperable: yes
- Passphrase-derived key instead of caller-supplied raw key: yes
- Text and JSON helpers on top of a canonical token string: yes
- Shared Rust core with WASM frontend package and Rust-backed Python extension: yes
