import pytest
from encryption import encrypt, decrypt

def test_encrypt_decrypt():
    uid = 12345
    text = "Секретные данные"
    enc = encrypt(uid, text)
    assert decrypt(uid, enc) == text

def test_wrong_user_fails():
    enc = encrypt(1, "test")
    with pytest.raises(ValueError):
        decrypt(2, enc)
