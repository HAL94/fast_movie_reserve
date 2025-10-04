from typing import Any

from fastapi import HTTPException
from app.core.config import settings
from itsdangerous import SignatureExpired, URLSafeTimedSerializer


class CookieSigner:
    def __init__(self):
        self._secret_key = settings.SECRET_COOKIE_KEY
        self.signer = URLSafeTimedSerializer(self._secret_key, "cookie-salt")

    def dumps(self, obj: Any, salt: str | bytes | None = None) -> str:
        return self.signer.dumps(obj, salt)

    def loads(self, signed_data: Any, max_age: int | None = None) -> Any:
        try:
            data = self.signer.loads(signed_data, max_age=max_age)
            return data
        except SignatureExpired:
            raise HTTPException(status_code=401, detail="Cookie has expired")
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid cookie signature")


cookie_signer = CookieSigner()


def get_cookie_signer():
    global cookie_signer
    if not cookie_signer:
        cookie_signer = CookieSigner()

    return cookie_signer
