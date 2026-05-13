import hashlib
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from config import ENCRYPTION_SALT

def derive_key(user_id: int) -> bytes:
    """AES-256 ключ = SHA256(user_id + соль из env)"""
    material = f"{user_id}{ENCRYPTION_SALT.decode()}".encode()
    return hashlib.sha256(material).digest()

def encrypt(user_id: int, plaintext: str) -> bytes:
    key = derive_key(user_id)
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    # PKCS7 padding
    block_size = 16
    data = plaintext.encode()
    pad_len = block_size - len(data) % block_size
    data += bytes([pad_len] * pad_len)
    ciphertext = encryptor.update(data) + encryptor.finalize()
    return iv + ciphertext

def decrypt(user_id: int, encrypted_data: bytes) -> str:
    key = derive_key(user_id)
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded = decryptor.update(ciphertext) + decryptor.finalize()
    pad_len = padded[-1]
    return padded[:-pad_len].decode()
