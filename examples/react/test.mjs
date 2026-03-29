import assert from "node:assert/strict";
import { decryptJson, decryptText, encryptJson, encryptText } from "./pkg/crypto_wasm.js";

const textToken = encryptText("shared-passphrase", "hello from react");
assert.equal(decryptText("shared-passphrase", textToken), "hello from react");

const payload = { source: "react", ok: true };
const jsonToken = encryptJson("shared-passphrase", payload);
assert.deepEqual(decryptJson("shared-passphrase", jsonToken), payload);

console.log("react example ok");
