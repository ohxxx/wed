use aes_gcm::aead::{Aead, KeyInit};
use aes_gcm::{Aes256Gcm, Key, Nonce};
use argon2::{Algorithm, Argon2, Params, Version};
use base64::engine::general_purpose::URL_SAFE_NO_PAD;
use base64::Engine;
use core::fmt;

const VERSION_PREFIX: &str = "wed1";
const SALT_LEN: usize = 16;
const NONCE_LEN: usize = 12;
const KEY_LEN: usize = 32;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum CryptoError {
    InvalidFormat,
    DecryptFailed,
    InvalidUtf8,
}

impl fmt::Display for CryptoError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::InvalidFormat => f.write_str("invalid encrypted token format"),
            Self::DecryptFailed => f.write_str("decryption failed"),
            Self::InvalidUtf8 => f.write_str("decrypted plaintext is not valid utf-8"),
        }
    }
}

impl std::error::Error for CryptoError {}

pub fn encrypt_bytes(passphrase: &str, plaintext: &[u8]) -> Result<String, CryptoError> {
    let salt = random_bytes::<SALT_LEN>()?;
    let nonce = random_bytes::<NONCE_LEN>()?;
    let key = derive_key(passphrase, &salt)?;
    let cipher = Aes256Gcm::new(Key::<Aes256Gcm>::from_slice(&key));
    let ciphertext = cipher
        .encrypt(Nonce::from_slice(&nonce), plaintext)
        .map_err(|_| CryptoError::DecryptFailed)?;

    Ok(format!(
        "{VERSION_PREFIX}.{}.{}.{}",
        URL_SAFE_NO_PAD.encode(salt),
        URL_SAFE_NO_PAD.encode(nonce),
        URL_SAFE_NO_PAD.encode(ciphertext),
    ))
}

pub fn decrypt_bytes(passphrase: &str, token: &str) -> Result<Vec<u8>, CryptoError> {
    let (salt, nonce, ciphertext) = parse_token(token)?;
    let key = derive_key(passphrase, &salt)?;
    let cipher = Aes256Gcm::new(Key::<Aes256Gcm>::from_slice(&key));

    cipher
        .decrypt(Nonce::from_slice(&nonce), ciphertext.as_ref())
        .map_err(|_| CryptoError::DecryptFailed)
}

pub fn encrypt_text(passphrase: &str, plaintext: &str) -> Result<String, CryptoError> {
    encrypt_bytes(passphrase, plaintext.as_bytes())
}

pub fn decrypt_text(passphrase: &str, token: &str) -> Result<String, CryptoError> {
    let plaintext = decrypt_bytes(passphrase, token)?;
    String::from_utf8(plaintext).map_err(|_| CryptoError::InvalidUtf8)
}

fn derive_key(passphrase: &str, salt: &[u8]) -> Result<[u8; KEY_LEN], CryptoError> {
    let params =
        Params::new(19_456, 2, 1, Some(KEY_LEN)).map_err(|_| CryptoError::InvalidFormat)?;
    let argon2 = Argon2::new(Algorithm::Argon2id, Version::V0x13, params);
    let mut key = [0u8; KEY_LEN];

    argon2
        .hash_password_into(passphrase.as_bytes(), salt, &mut key)
        .map_err(|_| CryptoError::InvalidFormat)?;

    Ok(key)
}

fn parse_token(token: &str) -> Result<(Vec<u8>, Vec<u8>, Vec<u8>), CryptoError> {
    let parts: Vec<&str> = token.split('.').collect();
    if parts.len() != 4 {
        return Err(CryptoError::InvalidFormat);
    }
    if parts[0] != VERSION_PREFIX {
        return Err(CryptoError::DecryptFailed);
    }

    let salt = URL_SAFE_NO_PAD
        .decode(parts[1])
        .map_err(|_| CryptoError::InvalidFormat)?;
    let nonce = URL_SAFE_NO_PAD
        .decode(parts[2])
        .map_err(|_| CryptoError::InvalidFormat)?;
    let ciphertext = URL_SAFE_NO_PAD
        .decode(parts[3])
        .map_err(|_| CryptoError::InvalidFormat)?;

    if salt.len() != SALT_LEN || nonce.len() != NONCE_LEN || ciphertext.is_empty() {
        return Err(CryptoError::InvalidFormat);
    }

    Ok((salt, nonce, ciphertext))
}

fn random_bytes<const N: usize>() -> Result<[u8; N], CryptoError> {
    let mut bytes = [0u8; N];
    getrandom::getrandom(&mut bytes).map_err(|_| CryptoError::DecryptFailed)?;
    Ok(bytes)
}
