# Verification Notes

The same token protocol is validated through every packaging layer in this repository.

## Coverage Matrix

- Rust core: protocol parsing, roundtrips, and failure cases
- WASM binding: text and JSON roundtrips through `wasm-bindgen`
- npm wrapper: runtime behavior plus TypeScript declarations
- Python extension: text and JSON roundtrips through the compiled module
- consumer examples: React-style and Python-style usage from outside the package directories

## Commands

Rust workspace:

```bash
cargo test --workspace
```

WASM crate only:

```bash
wasm-pack test --node crates/crypto-wasm
```

npm wrapper runtime and type checks:

```bash
cd packages/wedts
npm install
npm test
npm run typecheck
```

Python extension:

```bash
python3 -m venv /tmp/wed-venv
source /tmp/wed-venv/bin/activate
python -m pip install pytest maturin
maturin develop --manifest-path crates/crypto-python/Cargo.toml
pytest crates/crypto-python/tests/test_crypto.py -q
```

Consumer examples:

```bash
cd examples/react && npm install && npm test
cd examples/python && bash run_example_test.sh
```
