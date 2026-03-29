import { decryptJson, decryptText, encryptJson, encryptText } from "../index.js";

const textToken = encryptText("shared-passphrase", "hello");
const plaintext: string = decryptText("shared-passphrase", textToken);

const jsonToken = encryptJson("shared-passphrase", { message: "hello" });
const payload = decryptJson<{ message: string }>("shared-passphrase", jsonToken);
const message: string = payload.message;

void plaintext;
void message;
