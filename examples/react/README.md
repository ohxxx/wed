# React Example

This directory is a runnable consumer check for [`@ohxxx/wedts`](../../packages/wedts/README.md).

It installs the local package, rebuilds the WASM layer, and verifies that a frontend-style caller can roundtrip both text and JSON values.

## Run

```bash
cd examples/react
npm install
npm test
```

Expected success output:

```text
react example ok
```

## Example Usage

```ts
import { decryptJson, encryptJson } from "@ohxxx/wedts";

const token = encryptJson("shared-passphrase", { hello: "world" });
const payload = decryptJson<{ hello: string }>("shared-passphrase", token);
```
