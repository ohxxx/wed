use crypto_core::{decrypt_text, encrypt_text, CryptoError};

#[test]
fn encrypt_then_decrypt_roundtrip_text() {
    let token = encrypt_text("passphrase", "hello").unwrap();
    let plaintext = decrypt_text("passphrase", &token).unwrap();
    assert_eq!(plaintext, "hello");
}

#[test]
fn wrong_passphrase_fails_with_decrypt_error() {
    let token = encrypt_text("passphrase", "hello").unwrap();
    let err = decrypt_text("different-passphrase", &token).unwrap_err();
    assert_eq!(err, CryptoError::DecryptFailed);
}

#[test]
fn malformed_token_fails_with_invalid_format() {
    let err = decrypt_text("passphrase", "not-a-valid-token").unwrap_err();
    assert_eq!(err, CryptoError::InvalidFormat);
}

#[test]
fn same_plaintext_encrypts_to_different_tokens() {
    let first = encrypt_text("passphrase", "hello").unwrap();
    let second = encrypt_text("passphrase", "hello").unwrap();
    assert_ne!(first, second);
}

#[test]
fn unsupported_version_maps_to_decrypt_failed() {
    let token = encrypt_text("passphrase", "hello").unwrap();
    let unsupported = token.replacen("wed1", "wed2", 1);
    let err = decrypt_text("passphrase", &unsupported).unwrap_err();
    assert_eq!(err, CryptoError::DecryptFailed);
}
