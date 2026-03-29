# React Example

1. Install dependencies:

```bash
npm install
```

2. Run the complete example test:

```bash
npm test
```

This uses the local `@ohxxx/wedts` package directly.

3. Load it in a React app:

```ts
import { decryptJson, encryptJson } from "@ohxxx/wedts";

const token = encryptJson("shared-passphrase", { hello: "world" });
const payload = decryptJson("shared-passphrase", token);
```
