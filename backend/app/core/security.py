"""JWT 토큰 생성 및 검증 모듈"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from pydantic import BaseModel

from app.config.settings import get_settings


class TokenPayload(BaseModel):
    """JWT 토큰 페이로드"""

    sub: str  # user_id
    exp: datetime
    iat: datetime
    type: str = "access"


class TokenService:
    """JWT 토큰 관리 서비스"""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
    ):
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_expire = access_token_expire_minutes
        self._refresh_expire = refresh_token_expire_days

    def create_access_token(self, user_id: str) -> str:
        """액세스 토큰 생성"""
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=self._access_expire)

        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": now,
            "type": "access",
        }

        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def create_refresh_token(self, user_id: str) -> str:
        """리프레시 토큰 생성"""
        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=self._refresh_expire)

        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": now,
            "type": "refresh",
        }

        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def verify_token(self, token: str, token_type: str = "access") -> Optional[str]:
        """토큰 검증 및 user_id 반환

        Returns:
            user_id if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token, self._secret_key, algorithms=[self._algorithm]
            )

            if payload.get("type") != token_type:
                return None

            return payload.get("sub")

        except JWTError:
            return None

    def decode_token(self, token: str) -> Optional[TokenPayload]:
        """토큰 디코딩 (검증 포함)"""
        try:
            payload = jwt.decode(
                token, self._secret_key, algorithms=[self._algorithm]
            )
            return TokenPayload(**payload)
        except (JWTError, ValueError):
            return None


def get_token_service() -> TokenService:
    """토큰 서비스 싱글톤"""
    settings = get_settings()
    return TokenService(
        secret_key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        access_token_expire_minutes=settings.jwt_access_expire_minutes,
        refresh_token_expire_days=settings.jwt_refresh_expire_days,
    )
