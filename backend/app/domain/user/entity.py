"""사용자 엔티티 정의"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

import bcrypt


@dataclass
class User:
    """사용자 도메인 엔티티"""

    user_id: str
    name: str
    age: int
    gender: str
    disability_type: str
    communication_characteristics: str
    interesting_topics: List[str]
    password_hash: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @staticmethod
    def hash_password(password: str) -> str:
        """bcrypt로 비밀번호 해시 생성 (salt 자동 포함)"""
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode("utf-8")

    def verify_password(self, password: str) -> bool:
        """bcrypt로 비밀번호 검증"""
        try:
            password_bytes = password.encode("utf-8")
            hash_bytes = self.password_hash.encode("utf-8")
            return bcrypt.checkpw(password_bytes, hash_bytes)
        except (ValueError, TypeError):
            return False

    def to_dict(self) -> dict:
        """딕셔너리 변환 (저장용)"""
        return {
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "disability_type": self.disability_type,
            "communication_characteristics": self.communication_characteristics,
            "interesting_topics": self.interesting_topics,
            "password": self.password_hash,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def to_response_dict(self) -> dict:
        """응답용 딕셔너리 변환 (비밀번호 제외)"""
        return {
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "disabilityType": self.disability_type,
            "communicationCharacteristics": self.communication_characteristics,
            "interestingTopics": self.interesting_topics,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, user_id: str, data: dict) -> "User":
        """딕셔너리에서 엔티티 생성"""
        created_at = data.get("created_at")
        updated_at = data.get("updated_at")

        return cls(
            user_id=user_id,
            name=data["name"],
            age=data["age"],
            gender=data["gender"],
            disability_type=data["disability_type"],
            communication_characteristics=data["communication_characteristics"],
            interesting_topics=data.get("interesting_topics", []),
            password_hash=data.get("password", ""),
            created_at=datetime.fromisoformat(created_at) if created_at else datetime.now(),
            updated_at=datetime.fromisoformat(updated_at) if updated_at else datetime.now(),
        )
