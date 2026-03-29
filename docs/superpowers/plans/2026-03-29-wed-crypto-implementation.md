# WED Crypto Package Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Rust-based symmetric encryption package with a WASM package for React and a Python package for backend use, with verified interoperability between both bindings.

**Architecture:** Create a Rust workspace with a `crypto-core` crate that owns the token protocol and cryptographic behavior, then expose thin wrappers through `wasm-bindgen` and `pyo3`. Keep the canonical encrypted token format in the Rust core so all language bindings share exactly the same behavior.

**Tech Stack:** Rust, Cargo workspace, `aes-gcm`, `argon2`, `base64`, `rand`, `wasm-bindgen`, `wasm-bindgen-test`, `pyo3`, `maturin`, Node.js, Python 3, pytest

---

### Task 1: Scaffold workspace and core crate

**Files:**
- Create: `Cargo.toml`
- Create: `crates/crypto-core/Cargo.toml`
- Create: `crates/crypto-core/src/lib.rs`
- Create: `crates/crypto-core/tests/core_roundtrip.rs`
- Modify: `README.md`

- [ ] **Step 1: Write the failing core tests**

```rust
#[test]
fn encrypt_then_decrypt_roundtrip_text() {
    let token = encrypt_text("passphrase", "hello").unwrap();
    let plaintext = decrypt_text("passphrase", &token).unwrap();
    assert_eq!(plaintext, "hello");
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cargo test -p crypto-core`
Expected: FAIL because the workspace and crate do not exist yet

- [ ] **Step 3: Write minimal workspace and core implementation**

Create the workspace, add the `crypto-core` crate, implement:
- `encrypt_bytes`
- `decrypt_bytes`
- `encrypt_text`
- `decrypt_text`
- token parsing and formatting
- stable error enum

- [ ] **Step 4: Run test to verify it passes**

Run: `cargo test -p crypto-core`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add Cargo.toml crates/crypto-core README.md
git commit -m "feat: add core crypto crate"
```

### Task 2: Harden protocol behavior with red-green tests

**Files:**
- Modify: `crates/crypto-core/src/lib.rs`
- Modify: `crates/crypto-core/tests/core_roundtrip.rs`

- [ ] **Step 1: Write failing tests for protocol safety**

Add tests for:
- wrong passphrase fails
- malformed token fails
- same plaintext and passphrase produce different tokens

- [ ] **Step 2: Run tests to verify they fail**

Run: `cargo test -p crypto-core`
Expected: FAIL on the newly added scenarios

- [ ] **Step 3: Write minimal implementation updates**

Add:
- strict token validation
- controlled error mapping
- random salt and nonce generation

- [ ] **Step 4: Run tests to verify they pass**

Run: `cargo test -p crypto-core`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add crates/crypto-core
git commit -m "feat: harden crypto token protocol"
```

### Task 3: Add WASM bindings for React

**Files:**
- Create: `crates/crypto-wasm/Cargo.toml`
- Create: `crates/crypto-wasm/src/lib.rs`
- Create: `crates/crypto-wasm/tests/web.rs`
- Create: `examples/react/README.md`

- [ ] **Step 1: Write the failing WASM tests**

Add tests that call:
- `encryptText`
- `decryptText`

- [ ] **Step 2: Run test to verify it fails**

Run: `cargo test -p crypto-wasm`
Expected: FAIL because the crate and exports do not exist yet

- [ ] **Step 3: Write minimal WASM binding implementation**

Export JS-friendly functions:
- `encryptText`
- `decryptText`
- `encryptJson`
- `decryptJson`

- [ ] **Step 4: Run tests to verify they pass**

Run: `cargo test -p crypto-wasm`
Expected: PASS for host tests

- [ ] **Step 5: Commit**

```bash
git add crates/crypto-wasm examples/react
git commit -m "feat: add wasm crypto bindings"
```

### Task 4: Add Python bindings

**Files:**
- Create: `crates/crypto-python/Cargo.toml`
- Create: `crates/crypto-python/src/lib.rs`
- Create: `crates/crypto-python/python/wed_crypto/__init__.py`
- Create: `crates/crypto-python/pyproject.toml`
- Create: `crates/crypto-python/tests/test_crypto.py`
- Create: `examples/python/README.md`

- [ ] **Step 1: Write the failing Python tests**

Add tests for:
- `encrypt_text`
- `decrypt_text`
- `encrypt_json`
- `decrypt_json`

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest crates/crypto-python/tests/test_crypto.py -q`
Expected: FAIL because the module is not built yet

- [ ] **Step 3: Write minimal Python binding implementation**

Expose functions through `pyo3` and a small Python package wrapper.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest crates/crypto-python/tests/test_crypto.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add crates/crypto-python examples/python
git commit -m "feat: add python crypto bindings"
```

### Task 5: Verify interoperability and usage

**Files:**
- Modify: `README.md`
- Create: `tests/vectors/README.md`

- [ ] **Step 1: Write failing interoperability checks**

Add tests or scripts that confirm:
- core-generated tokens decrypt via Python
- Python-generated tokens decrypt via core
- WASM binding exports are consistent with core behavior

- [ ] **Step 2: Run verification to confirm the checks fail without glue**

Run: `cargo test --workspace`
Expected: FAIL until missing integration pieces are added

- [ ] **Step 3: Write minimal verification glue and documentation**

Add:
- interoperability tests
- usage notes in `README.md`
- example install and call patterns for React and Python

- [ ] **Step 4: Run full verification**

Run:
- `cargo test --workspace`
- `python -m pytest crates/crypto-python/tests/test_crypto.py -q`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add README.md tests/vectors
git commit -m "docs: add interoperability usage guidance"
```
