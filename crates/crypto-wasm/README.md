# crypto-wasm

`crypto-wasm` is the low-level Rust/WASM binding crate for the WED protocol.

Most frontend consumers should use [`@ohxxx/wedts`](../../packages/wedts/README.md) instead of importing this crate output directly. `@ohxxx/wedts` adds a stable npm package layout and TypeScript declarations on top of the generated WASM build.

## Exports

This crate exposes four `wasm-bindgen` functions:

- `encryptText(passphrase, plaintext)`
- `decryptText(passphrase, token)`
- `encryptJson(passphrase, value)`
- `decryptJson(passphrase, token)`

`encryptJson` uses `JSON.stringify` in JavaScript before delegating to the Rust core.
`decryptJson` decrypts to text and then runs `JSON.parse`.

## Build

This crate is usually built through the npm wrapper package:

```bash
cd packages/wedts
npm install
npm run build:wasm
```

If you want the raw WASM output directly:

```bash
wasm-pack build crates/crypto-wasm --target bundler --release
```

## Test

Run:

```bash
wasm-pack test --node crates/crypto-wasm
```

The tests cover both text and JSON roundtrips.
