from __future__ import annotations

import hashlib
import hmac
import secrets

ALGORITHM = "sha256"
ITERATIONS = 390000


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac(ALGORITHM, password.encode(), salt.encode(), ITERATIONS)
    return f"{salt}${hashed.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, hashed_value = stored_hash.split("$")
    except ValueError:
        return False
    new_hash = hashlib.pbkdf2_hmac(ALGORITHM, password.encode(), salt.encode(), ITERATIONS)
    return hmac.compare_digest(new_hash.hex(), hashed_value)


