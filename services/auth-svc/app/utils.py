import hashlib
import os
import secrets


def generate_code(length: int = 6) -> str:
    return ''.join(secrets.choice('0123456789') for _ in range(length))


def hash_code(code: str, secret: str) -> str:
    return hashlib.sha256(f"{code}:{secret}".encode('utf-8')).hexdigest()


def mask_phone(phone: str) -> str:
    if len(phone) <= 4:
        return '*' * len(phone)
    return phone[:3] + '*' * (len(phone) - 4) + phone[-1:]
