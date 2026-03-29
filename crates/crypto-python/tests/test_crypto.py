import json

from wed_crypto import decrypt_json, decrypt_text, encrypt_json, encrypt_text


def test_encrypt_then_decrypt_text_roundtrip():
    token = encrypt_text("passphrase", "hello")
    plaintext = decrypt_text("passphrase", token)
    assert plaintext == "hello"


def test_encrypt_then_decrypt_json_roundtrip():
    token = encrypt_json("passphrase", {"message": "hello"})
    payload = decrypt_json("passphrase", token)
    assert payload == {"message": "hello"}
