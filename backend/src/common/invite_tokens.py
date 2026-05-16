import hashlib
import secrets


def generate_invite_token() -> str:
    return secrets.token_urlsafe(32)


def hash_invite_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode()).hexdigest()
