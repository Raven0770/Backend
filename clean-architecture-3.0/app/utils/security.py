"""
Utility — Security Helpers (JWT + Password Hashing)

This module contains the low-level functions for:
  1. Hashing and verifying passwords (using bcrypt).
  2. Creating and decoding JWT tokens (using PyJWT).

These are pure utility functions — they know nothing about HTTP,
databases, or business rules. Any layer can import and use them.

Libraries used:
  - bcrypt:  Industry-standard password hashing algorithm. It
             automatically salts passwords and is intentionally slow
             to resist brute-force attacks.
  - PyJWT:   Lightweight library to encode/decode JSON Web Tokens.
             A JWT is a signed string that carries data (called
             "claims") — here we store the username inside it.
"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

# ---------- Configuration ---------- #

# The secret key used to sign JWT tokens.
# In production: load from environment variable or a secrets manager.
SECRET_KEY = "super-secret-key-change-in-production"

# The signing algorithm. HS256 = HMAC with SHA-256 (symmetric).
ALGORITHM = "HS256"

# How long a token stays valid after creation.
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# ---------- Password helpers ---------- #

def hash_password(plain_password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    bcrypt.gensalt() creates a random salt (extra random bytes mixed
    into the hash so that two identical passwords produce different
    hashes). The result is a bytes string like:
        b'$2b$12$LJ3m4ys...'

    We decode it to a regular str for easy storage.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Check if a plain-text password matches a bcrypt hash.

    bcrypt.checkpw() re-hashes the plain password with the same salt
    that is embedded inside the stored hash, then compares them.
    Returns True if they match, False otherwise.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


# ---------- JWT helpers ---------- #

def create_access_token(data: dict) -> str:
    """
    Create a JWT access token.

    Args:
        data: A dict of "claims" to embed in the token.
              Example: {"sub": "alice"}

    The token payload will look like:
        {
            "sub": "alice",
            "exp": 1700000000   ← expiration timestamp
        }

    jwt.encode() signs this payload with our SECRET_KEY using HS256,
    producing a string like:
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOi..."
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """
    Decode and verify a JWT access token.

    Returns the payload dict if the token is valid and not expired.
    Returns None if the token is invalid, tampered with, or expired.

    jwt.decode() does three things:
      1. Splits the token into header.payload.signature
      2. Re-signs header.payload with SECRET_KEY and checks the
         signature matches — if not, someone tampered with it.
      3. Checks the "exp" claim — if it's in the past, the token
         has expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
