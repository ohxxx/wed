# Verification Notes

The canonical encrypted token format is shared by the Rust core, the WASM bindings, and the Python bindings.

Recommended verification commands:

```bash
cargo test --workspace
wasm-pack test --node crates/crypto-wasm
source /tmp/wed-venv/bin/activate && pytest crates/crypto-python/tests/test_crypto.py -q
```

These cover:

- Rust core roundtrip behavior and protocol validation
- WASM text and JSON roundtrip behavior under Node
- Python text and JSON roundtrip behavior through the compiled extension
