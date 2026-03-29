from wedpy import decrypt_json, decrypt_text, encrypt_json, encrypt_text


def main():
    text_token = encrypt_text("shared-passphrase", "hello from python")
    assert decrypt_text("shared-passphrase", text_token) == "hello from python"

    payload = {"source": "python", "ok": True}
    json_token = encrypt_json("shared-passphrase", payload)
    assert decrypt_json("shared-passphrase", json_token) == payload

    print("python example ok")


if __name__ == "__main__":
    main()
