from cryptography.fernet import Fernet
from jose import jwt
from passlib.context import CryptContext

from coin_tracker.config import settings

pwd_context = CryptContext(schemes=["bcrypt"])
fernet = Fernet(settings.fernet_key)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def create_access_token(data: dict) -> str:
    return jwt.encode(data, settings.secret_key)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key)


def encrypt_data(data: str) -> bytes:
    return fernet.encrypt(data.encode())


def decrypt_data(data: str) -> str:
    return fernet.decrypt(data.encode()).decode()
