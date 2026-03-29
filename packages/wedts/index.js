import {
  decryptJson as decryptJsonRaw,
  decryptText as decryptTextRaw,
  encryptJson as encryptJsonRaw,
  encryptText as encryptTextRaw
} from "./dist/wasm/crypto_wasm.js";

export const encryptText = (passphrase, plaintext) =>
  encryptTextRaw(passphrase, plaintext);

export const decryptText = (passphrase, token) =>
  decryptTextRaw(passphrase, token);

export const encryptJson = (passphrase, value) =>
  encryptJsonRaw(passphrase, value);

export const decryptJson = (passphrase, token) =>
  decryptJsonRaw(passphrase, token);
