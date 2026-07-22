import base64
import hashlib
import hmac
import json

from typing import Optional

from future.middleware.Middleware import Middleware
from future.response import Response
from future.settings import APP_KEY

SESSION_COOKIE_NAME = "session"
SESSION_COOKIE_PATH = "/"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"


class SessionMiddleware(Middleware):
    name = "session"

    def _secret(self) -> str:
        app = self.request.scope.get("app")
        if app is not None and getattr(app, "config", None):
            return str(app.config.get("APP_KEY") or APP_KEY)
        return str(APP_KEY)

    def _sign(self, payload: bytes) -> str:
        digest = hmac.new(self._secret().encode("utf-8"), payload, hashlib.sha256).hexdigest()
        return base64.urlsafe_b64encode(payload).decode("ascii") + "." + digest

    def _unsign(self, raw: str) -> dict:
        body_b64, digest = raw.rsplit(".", 1)
        payload = base64.urlsafe_b64decode(body_b64.encode("ascii"))
        expected = hmac.new(self._secret().encode("utf-8"), payload, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(digest, expected):
            raise ValueError("invalid session signature")
        data = json.loads(payload.decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("invalid session payload")
        return data

    async def before(self) -> Optional[Response]:
        raw = self.request.cookies.get(SESSION_COOKIE_NAME)
        if not raw:
            return None
        try:
            if "." in raw:
                self.request.session = self._unsign(raw)
            else:
                # Legacy unsigned base64 JSON sessions
                payload = base64.urlsafe_b64decode(raw.encode("ascii"))
                data = json.loads(payload.decode("utf-8"))
                self.request.session = data if isinstance(data, dict) else {}
        except Exception:
            self.request.session = {}
        return None

    async def after(self) -> Optional[Response]:
        if not self.request.session:
            self.response.delete_cookie(SESSION_COOKIE_NAME, path=SESSION_COOKIE_PATH)
            return None
        payload = json.dumps(
            self.request.session,
            default=str,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        value = self._sign(payload)
        self.response.set_cookie(
            SESSION_COOKIE_NAME,
            value,
            path=SESSION_COOKIE_PATH,
            httponly=SESSION_COOKIE_HTTPONLY,
            samesite=SESSION_COOKIE_SAMESITE,
            secure=(self.request.scheme == "https"),
        )
        return None
