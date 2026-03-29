use crypto_wasm::{decrypt_json, decrypt_text, encrypt_json, encrypt_text};
use js_sys::{Object, Reflect};
use wasm_bindgen_test::*;

#[wasm_bindgen_test]
fn encrypt_then_decrypt_text_roundtrip() {
    let token = encrypt_text("passphrase".into(), "hello".into()).unwrap();
    let plaintext = decrypt_text("passphrase".into(), token).unwrap();
    assert_eq!(plaintext, "hello");
}

#[wasm_bindgen_test]
fn encrypt_then_decrypt_json_roundtrip() {
    let value = Object::new();
    Reflect::set(&value, &"message".into(), &"hello".into()).unwrap();

    let token = encrypt_json("passphrase".into(), value.into()).unwrap();
    let parsed = decrypt_json("passphrase".into(), token).unwrap();
    let message = Reflect::get(&parsed, &"message".into()).unwrap();

    assert_eq!(message.as_string().as_deref(), Some("hello"));
}
