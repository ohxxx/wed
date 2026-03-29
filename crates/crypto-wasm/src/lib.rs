use wasm_bindgen::prelude::*;

#[wasm_bindgen(js_name = encryptText)]
pub fn encrypt_text(passphrase: String, plaintext: String) -> Result<String, JsValue> {
    crypto_core::encrypt_text(&passphrase, &plaintext)
        .map_err(|err| JsValue::from_str(&err.to_string()))
}

#[wasm_bindgen(js_name = decryptText)]
pub fn decrypt_text(passphrase: String, token: String) -> Result<String, JsValue> {
    crypto_core::decrypt_text(&passphrase, &token)
        .map_err(|err| JsValue::from_str(&err.to_string()))
}

#[wasm_bindgen(js_name = encryptJson)]
pub fn encrypt_json(passphrase: String, value: JsValue) -> Result<String, JsValue> {
    let plaintext = js_sys::JSON::stringify(&value)?
        .as_string()
        .ok_or_else(|| JsValue::from_str("JSON.stringify returned a non-string value"))?;

    encrypt_text(passphrase, plaintext)
}

#[wasm_bindgen(js_name = decryptJson)]
pub fn decrypt_json(passphrase: String, token: String) -> Result<JsValue, JsValue> {
    let plaintext = decrypt_text(passphrase, token)?;
    js_sys::JSON::parse(&plaintext)
}
