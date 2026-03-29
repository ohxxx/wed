# @ohxxx/wedts

`@ohxxx/wedts` is the TypeScript-friendly npm package for the WED symmetric encryption protocol.

It wraps the generated WASM output from [`crypto-wasm`](../../crates/crypto-wasm) and adds a stable JavaScript entrypoint plus TypeScript declarations.

## Install

```bash
npm install @ohxxx/wedts
```

## API

The package exports:

- `encryptText(passphrase: string, plaintext: string): string`
- `decryptText(passphrase: string, token: string): string`
- `encryptJson(passphrase: string, value: unknown): string`
- `decryptJson<T = unknown>(passphrase: string, token: string): T`

Text example:

```ts
import { decryptText, encryptText } from "@ohxxx/wedts";

const token = encryptText("shared-passphrase", "hello");
const plaintext = decryptText("shared-passphrase", token);
```

JSON example with type inference:

```ts
import { decryptJson, encryptJson } from "@ohxxx/wedts";

const token = encryptJson("shared-passphrase", { message: "hello" });
const payload = decryptJson<{ message: string }>("shared-passphrase", token);
```

## Local Development

Install dependencies and rebuild the WASM output:

```bash
cd packages/wedts
npm install
npm run build:wasm
```

The build script compiles [`crates/crypto-wasm`](../../crates/crypto-wasm) with `wasm-pack` and copies the generated assets into `dist/wasm`.

## Test

Runtime test:

```bash
cd packages/wedts
npm test
```

Type test:

```bash
cd packages/wedts
npm run typecheck
```

For an end-to-end consumer example, see [`examples/react/README.md`](../../examples/react/README.md).
