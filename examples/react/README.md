# React Example

1. Build the WASM package:

```bash
wasm-pack build crates/crypto-wasm --target bundler --out-dir pkg
```

2. Load it in a React app:

```ts
import init, { decryptJson, encryptJson } from "./pkg/crypto_wasm";

await init();

const token = encryptJson("shared-passphrase", { hello: "world" });
const payload = decryptJson("shared-passphrase", token);
```
