"""加密工具 — AES-256 加密/解密，用于保护 secrets.yaml"""
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


_KEY_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".key")


def _derive_key(password: str, salt: bytes) -> bytes:
    """从密码派生加密密钥"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def encrypt_data(plaintext: str, password: str) -> str:
    """加密字符串，返回 base64 编码的密文"""
    salt = os.urandom(16)
    key = _derive_key(password, salt)
    f = Fernet(key)
    encrypted = f.encrypt(plaintext.encode())
    return base64.urlsafe_b64encode(salt + encrypted).decode()


def decrypt_data(ciphertext_b64: str, password: str) -> str:
    """解密字符串"""
    data = base64.urlsafe_b64decode(ciphertext_b64.encode())
    salt = data[:16]
    encrypted = data[16:]
    key = _derive_key(password, salt)
    f = Fernet(key)
    return f.decrypt(encrypted).decode()


def hash_sha256(text: str) -> str:
    """SHA-256 哈希（用于日志脱敏后的校验）"""
    import hashlib
    return hashlib.sha256(text.encode()).hexdigest()
