# React Example

1. Run the complete example test:

```bash
npm test
```

This will:

- build the WASM package into `examples/react/pkg`
- execute the example script against the generated package

2. If you want to build manually:

```bash
cd ../../crates/crypto-wasm
wasm-pack build . --dev --target nodejs --out-dir ../../examples/react/pkg
```

3. Load it in a React app:

```ts
import { decryptJson, encryptJson } from "./pkg/crypto_wasm.js";

const token = encryptJson("shared-passphrase", { hello: "world" });
const payload = decryptJson("shared-passphrase", token);
```
