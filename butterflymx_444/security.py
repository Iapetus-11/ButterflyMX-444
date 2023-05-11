import hashlib
import hmac
import secrets
from base64 import b64decode, b64encode
from datetime import datetime, timedelta

from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError, JWTError

import butterflymx_444.settings as settings
from butterflymx_444.models.user import User


def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    """
    Assumes plaintext password and base64 encoded salt, returns base64 hashed password and salt

    If no salt is provided, a 256 bit long one is generated
    """

    password_bytes = password.encode()
    salt_bytes = b64decode(salt) if salt is not None else secrets.token_bytes(32)

    hashed_password = hashlib.scrypt(
        password_bytes,
        salt=salt_bytes,
        n=32768,
        r=16,
        p=1,
        maxmem=(2 ** 27),
    )

    return b64encode(hashed_password).decode(), b64encode(salt_bytes).decode()


def compare_passwords(password: str, stored_password: str) -> bool:
    """
    Assumes both passwords are base64 encoded
    """

    return hmac.compare_digest(password, stored_password)


def create_jwt_token(username: str) -> tuple[str, datetime]:
    """Returns the generated JWT token and its expiration datetime"""

    now = datetime.utcnow()
    expires_at = now + timedelta(days=settings.JWT_EXPIRATION_DAYS)

    token = jwt.encode(
        {
            'sub': username,
            'iat': now,
            'exp': expires_at,
        },
        settings.JWT_SECRET,
        algorithm='HS256',
    )

    return token, expires_at


def validate_jwt_token(token: str | None) -> bool:
    """Returns True if the token is valid"""

    if token is None:
        return False

    try:
        decoded = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])

        return decoded.get('sub') and get_user(decoded['sub'])
    except (JWTError, ExpiredSignatureError, JWTClaimsError):
        pass

    return False


def get_user(username: str) -> User | None:
    for user in settings.USERS:
        if username.lower() == user.username.lower():
            return user

    return None
