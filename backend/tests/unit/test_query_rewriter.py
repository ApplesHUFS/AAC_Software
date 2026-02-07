"""쿼리 재작성기 유닛 테스트

NoOpQueryRewriter와 쿼리 확장 로직을 테스트합니다.
"""

import pytest

from app.domain.card.query_rewriter import NoOpQueryRewriter


class TestNoOpQueryRewriter:
    """NoOp 쿼리 재작성기 테스트"""

    @pytest.fixture
    def rewriter(self) -> NoOpQueryRewriter:
        """NoOp 재작성기 인스턴스"""
        return NoOpQueryRewriter()

    @pytest.mark.asyncio
    async def test_rewrite_returns_single_query(self, rewriter: NoOpQueryRewriter):
        """원본 쿼리만 반환"""
        # Arrange
        place = "학교"
        partner = "선생님"
        activity = "수업 중"

        # Act
        result = await rewriter.rewrite(place, partner, activity)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], str)

    @pytest.mark.asyncio
    async def test_rewrite_includes_place_in_query(self, rewriter: NoOpQueryRewriter):
        """장소가 쿼리에 포함됨"""
        # Act
        result = await rewriter.rewrite("병원", "", "")

        # Assert
        assert "병원" in result[0]

    @pytest.mark.asyncio
    async def test_rewrite_includes_partner_in_query(self, rewriter: NoOpQueryRewriter):
        """대화 상대가 쿼리에 포함됨"""
        # Act
        result = await rewriter.rewrite("", "엄마", "")

        # Assert
        assert "엄마" in result[0]
        assert "함께" in result[0]

    @pytest.mark.asyncio
    async def test_rewrite_includes_activity_in_query(self, rewriter: NoOpQueryRewriter):
        """현재 활동이 쿼리에 포함됨"""
        # Act
        result = await rewriter.rewrite("", "", "밥 먹기")

        # Assert
        assert "밥 먹기" in result[0]

    @pytest.mark.asyncio
    async def test_rewrite_combines_all_context(self, rewriter: NoOpQueryRewriter):
        """모든 컨텍스트가 결합됨"""
        # Act
        result = await rewriter.rewrite("집", "동생", "놀기")

        # Assert
        query = result[0]
        assert "집" in query
        assert "동생" in query
        assert "놀기" in query
        assert "의사소통 카드" in query

    @pytest.mark.asyncio
    async def test_rewrite_handles_empty_context(self, rewriter: NoOpQueryRewriter):
        """빈 컨텍스트 처리"""
        # Act
        result = await rewriter.rewrite("", "", "")

        # Assert
        assert len(result) == 1
        assert "일상생활 의사소통 카드" in result[0]

    @pytest.mark.asyncio
    async def test_rewrite_strips_whitespace(self, rewriter: NoOpQueryRewriter):
        """공백 문자 정리"""
        # Act
        result = await rewriter.rewrite("  학교  ", "  선생님  ", "  공부  ")

        # Assert
        query = result[0]
        assert "  학교  " not in query
        assert "학교" in query

    @pytest.mark.asyncio
    async def test_rewrite_handles_whitespace_only_values(
        self, rewriter: NoOpQueryRewriter
    ):
        """공백만 있는 값 처리"""
        # Act
        result = await rewriter.rewrite("   ", "엄마", "")

        # Assert
        query = result[0]
        assert "엄마" in query
        # 공백만 있는 값은 포함되지 않음
        assert query.strip() == query or "   " not in query

    @pytest.mark.asyncio
    async def test_rewrite_query_ends_with_card_suffix(self, rewriter: NoOpQueryRewriter):
        """쿼리가 의사소통 카드 접미사로 끝남"""
        # Act
        result = await rewriter.rewrite("마트", "아빠", "쇼핑")

        # Assert
        assert result[0].endswith("의사소통 카드")


class TestQueryBuilding:
    """쿼리 빌딩 로직 테스트"""

    @pytest.fixture
    def rewriter(self) -> NoOpQueryRewriter:
        return NoOpQueryRewriter()

    @pytest.mark.asyncio
    async def test_partner_format_with_suffix(self, rewriter: NoOpQueryRewriter):
        """대화 상대에 '와 함께' 접미사 추가"""
        # Act
        result = await rewriter.rewrite("", "친구", "")

        # Assert
        assert "친구와 함께" in result[0]

    @pytest.mark.asyncio
    async def test_query_part_order(self, rewriter: NoOpQueryRewriter):
        """쿼리 부분의 순서: 장소 -> 상대 -> 활동"""
        # Act
        result = await rewriter.rewrite("학교", "선생님", "공부")
        query = result[0]

        # Assert
        place_idx = query.find("학교")
        partner_idx = query.find("선생님")
        activity_idx = query.find("공부")

        assert place_idx < partner_idx < activity_idx
