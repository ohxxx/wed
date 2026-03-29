import assert from "node:assert/strict";
import { decryptJson, decryptText, encryptJson, encryptText } from "../index.js";

const textToken = encryptText("shared-passphrase", "hello from wedts");
assert.equal(decryptText("shared-passphrase", textToken), "hello from wedts");

const payload = { source: "wedts", ok: true };
const jsonToken = encryptJson("shared-passphrase", payload);
assert.deepEqual(decryptJson("shared-passphrase", jsonToken), payload);

console.log("wedts runtime ok");
