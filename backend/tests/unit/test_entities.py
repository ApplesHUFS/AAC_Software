"""엔티티 유닛 테스트

Card, User, Context 엔티티의 데이터 변환 및 검증 로직을 테스트합니다.
"""

from datetime import datetime

import pytest

from app.domain.card.entity import Card, CardHistory, Interpretation
from app.domain.context.entity import Context
from app.domain.user.entity import User


class TestCardEntity:
    """카드 엔티티 테스트"""

    def test_card_to_dict(self, sample_card: Card):
        """딕셔너리 변환 테스트"""
        # Act
        result = sample_card.to_dict()

        # Assert
        assert result["id"] == "001_사과"
        assert result["name"] == "사과"
        assert result["filename"] == "001_사과.png"
        assert result["imagePath"] == "/api/images/001_사과.png"
        assert result["index"] == 0
        assert result["selected"] is False

    def test_card_from_filename(self):
        """파일명에서 카드 생성"""
        # Arrange
        filename = "123_물컵.png"

        # Act
        card = Card.from_filename(filename, index=5)

        # Assert
        assert card.id == "123_물컵"
        assert card.name == "123_물컵"
        assert card.filename == "123_물컵.png"
        assert card.image_path == "/api/images/123_물컵.png"
        assert card.index == 5
        assert card.selected is False

    def test_card_from_filename_without_extension(self):
        """확장자 없는 파일명 처리"""
        # Arrange
        filename = "card_name_only"

        # Act
        card = Card.from_filename(filename)

        # Assert
        assert card.name == "card_name_only"
        assert card.filename == "card_name_only"

    def test_card_from_filename_with_spaces(self):
        """공백이 포함된 파일명 처리"""
        # Arrange
        filename = "001 사과 주세요.png"

        # Act
        card = Card.from_filename(filename)

        # Assert
        assert card.id == "001_사과_주세요"
        assert card.name == "001 사과 주세요"


class TestCardHistoryEntity:
    """카드 히스토리 엔티티 테스트"""

    def test_card_history_to_dict(self, sample_cards):
        """히스토리 딕셔너리 변환"""
        # Arrange
        now = datetime(2024, 1, 15, 10, 30, 0)
        history = CardHistory(
            context_id="ctx-001",
            page_number=1,
            cards=sample_cards[:3],
            timestamp=now,
        )

        # Act
        result = history.to_dict()

        # Assert
        assert result["contextId"] == "ctx-001"
        assert result["pageNumber"] == 1
        assert len(result["cards"]) == 3
        assert result["timestamp"] == "2024-01-15T10:30:00"


class TestInterpretationEntity:
    """해석 엔티티 테스트"""

    def test_interpretation_to_dict(self):
        """해석 딕셔너리 변환"""
        # Arrange
        interpretation = Interpretation(
            index=0,
            text="사과 주세요",
            selected=True,
        )

        # Act
        result = interpretation.to_dict()

        # Assert
        assert result["index"] == 0
        assert result["text"] == "사과 주세요"
        assert result["selected"] is True


class TestContextEntity:
    """컨텍스트 엔티티 테스트"""

    def test_context_to_dict(self, sample_context: Context):
        """딕셔너리 변환"""
        # Act
        result = sample_context.to_dict()

        # Assert
        assert result["contextId"] == "ctx-test-001"
        assert result["userId"] == "test-user-001"
        assert result["time"] == "10시 30분"
        assert result["place"] == "학교"
        assert result["interactionPartner"] == "선생님"
        assert result["currentActivity"] == "수업 중"
        assert "createdAt" in result

    def test_context_to_summary_dict(self, sample_context: Context):
        """요약 딕셔너리 변환 (해석용)"""
        # Act
        result = sample_context.to_summary_dict()

        # Assert
        assert result["time"] == "10시 30분"
        assert result["place"] == "학교"
        assert result["interactionPartner"] == "선생님"
        assert result["currentActivity"] == "수업 중"
        assert "contextId" not in result
        assert "userId" not in result

    def test_context_generate_id(self):
        """UUID 기반 ID 생성"""
        # Act
        id1 = Context.generate_id()
        id2 = Context.generate_id()

        # Assert
        assert id1 != id2
        assert len(id1) == 36  # UUID 형식

    def test_context_get_current_time(self):
        """현재 시간 문자열 생성"""
        # Act
        time_str = Context.get_current_time()

        # Assert
        assert "시" in time_str
        assert "분" in time_str


class TestUserEntity:
    """사용자 엔티티 테스트"""

    def test_user_hash_password(self):
        """비밀번호 해시 생성"""
        # Arrange
        password = "mypassword123"

        # Act
        hash1 = User.hash_password(password)
        hash2 = User.hash_password(password)
        hash_different = User.hash_password("otherpassword")

        # Assert
        assert hash1 == hash2  # 같은 입력이면 같은 해시
        assert hash1 != hash_different  # 다른 입력이면 다른 해시
        assert len(hash1) == 64  # SHA256 해시 길이

    def test_user_verify_password(self, sample_user: User):
        """비밀번호 검증"""
        # Assert
        assert sample_user.verify_password("test1234") is True
        assert sample_user.verify_password("wrongpassword") is False

    def test_user_to_dict(self, sample_user: User):
        """저장용 딕셔너리 변환"""
        # Act
        result = sample_user.to_dict()

        # Assert
        assert result["name"] == "테스트 사용자"
        assert result["age"] == 10
        assert result["gender"] == "남성"
        assert result["disability_type"] == "자폐스펙트럼장애"
        assert result["communication_characteristics"] == "간단한 문장 사용"
        assert result["interesting_topics"] == ["놀이", "음식", "동물"]
        assert "password" in result

    def test_user_to_response_dict(self, sample_user: User):
        """응답용 딕셔너리 변환 (비밀번호 제외)"""
        # Act
        result = sample_user.to_response_dict()

        # Assert
        assert result["name"] == "테스트 사용자"
        assert result["age"] == 10
        assert result["gender"] == "남성"
        assert result["disabilityType"] == "자폐스펙트럼장애"
        assert result["communicationCharacteristics"] == "간단한 문장 사용"
        assert result["interestingTopics"] == ["놀이", "음식", "동물"]
        assert "password" not in result
        assert "password_hash" not in result

    def test_user_from_dict(self):
        """딕셔너리에서 엔티티 생성"""
        # Arrange
        data = {
            "name": "홍길동",
            "age": 15,
            "gender": "남성",
            "disability_type": "지적장애",
            "communication_characteristics": "짧은 단어 사용",
            "interesting_topics": ["게임", "음악"],
            "password": "hashed_password",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-02T00:00:00",
        }

        # Act
        user = User.from_dict("user-123", data)

        # Assert
        assert user.user_id == "user-123"
        assert user.name == "홍길동"
        assert user.age == 15
        assert user.interesting_topics == ["게임", "음악"]
        assert user.password_hash == "hashed_password"

    def test_user_from_dict_with_missing_optional_fields(self):
        """선택 필드 없이 엔티티 생성"""
        # Arrange
        data = {
            "name": "김철수",
            "age": 20,
            "gender": "남성",
            "disability_type": "의사소통장애",
            "communication_characteristics": "문장 사용",
        }

        # Act
        user = User.from_dict("user-456", data)

        # Assert
        assert user.interesting_topics == []
        assert user.password_hash == ""
