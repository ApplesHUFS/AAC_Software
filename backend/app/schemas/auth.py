"""인증 관련 스키마"""

import re
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class RegisterRequest(BaseModel):
    """회원가입 요청"""

    user_id: str = Field(..., alias="userId", min_length=1)
    name: str = Field(..., min_length=1)
    age: int = Field(..., ge=1, le=100)
    gender: str
    disability_type: str = Field(..., alias="disabilityType")
    communication_characteristics: str = Field(..., alias="communicationCharacteristics")
    interesting_topics: List[str] = Field(..., alias="interestingTopics", min_length=1)
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        """비밀번호 복잡도 검증: 최소 8자, 대문자, 소문자, 숫자, 특수문자 포함"""
        if len(v) < 8:
            raise ValueError("비밀번호는 최소 8자 이상이어야 합니다")
        if not re.search(r"[A-Z]", v):
            raise ValueError("비밀번호에 대문자가 포함되어야 합니다")
        if not re.search(r"[a-z]", v):
            raise ValueError("비밀번호에 소문자가 포함되어야 합니다")
        if not re.search(r"\d", v):
            raise ValueError("비밀번호에 숫자가 포함되어야 합니다")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("비밀번호에 특수문자가 포함되어야 합니다")
        return v

    class Config:
        populate_by_name = True


class LoginRequest(BaseModel):
    """로그인 요청"""

    user_id: str = Field(..., alias="userId")
    password: str

    class Config:
        populate_by_name = True


class UserResponse(BaseModel):
    """사용자 정보 응답 (비밀번호 제외)"""

    name: str
    age: int
    gender: str
    disability_type: str = Field(..., alias="disabilityType")
    communication_characteristics: str = Field(..., alias="communicationCharacteristics")
    interesting_topics: List[str] = Field(..., alias="interestingTopics")
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

    class Config:
        populate_by_name = True


class LoginResponse(BaseModel):
    """로그인 응답"""

    user_id: str = Field(..., alias="userId")
    authenticated: bool
    user: UserResponse

    class Config:
        populate_by_name = True


class ProfileUpdateRequest(BaseModel):
    """프로필 업데이트 요청"""

    name: Optional[str] = None
    age: Optional[int] = Field(None, ge=1, le=100)
    gender: Optional[str] = None
    disability_type: Optional[str] = Field(None, alias="disabilityType")
    communication_characteristics: Optional[str] = Field(
        None, alias="communicationCharacteristics"
    )
    interesting_topics: Optional[List[str]] = Field(None, alias="interestingTopics")

    class Config:
        populate_by_name = True


class TokenResponse(BaseModel):
    """토큰 응답"""

    access_token: str = Field(..., alias="accessToken")
    refresh_token: str = Field(..., alias="refreshToken")
    token_type: str = Field(default="bearer", alias="tokenType")

    class Config:
        populate_by_name = True


class RefreshTokenRequest(BaseModel):
    """리프레시 토큰 요청"""

    refresh_token: str = Field(..., alias="refreshToken")

    class Config:
        populate_by_name = True
