"""PersonaSearcher 단위 테스트"""

import pytest

from tests.conftest import MockEmbeddingProvider, MockVectorIndex

from app.domain.card.persona_searcher import PersonaSearcher


class TestPersonaSearcher:
    """PersonaSearcher 테스트"""

    @pytest.fixture
    def searcher(self) -> PersonaSearcher:
        """테스트용 PersonaSearcher"""
        filenames = [
            "001_사과.png",
            "002_바나나.png",
            "003_놀이.png",
            "004_음식.png",
            "005_동물.png",
            "006_강아지.png",
            "007_고양이.png",
            "008_축구.png",
        ]
        embedding = MockEmbeddingProvider()
        vector_index = MockVectorIndex(filenames)
        return PersonaSearcher(embedding, vector_index)

    def test_returns_empty_when_no_keywords(self, searcher: PersonaSearcher):
        """키워드가 없으면 빈 결과 반환"""
        result = searcher.search(keywords=[], count=10, excluded_indices=set())

        assert result == []

    def test_search_returns_scored_cards(self, searcher: PersonaSearcher):
        """검색 결과가 ScoredCard 목록으로 반환"""
        result = searcher.search(
            keywords=["놀이", "음식"],
            count=5,
            excluded_indices=set(),
        )

        assert len(result) > 0
        for sc in result:
            assert hasattr(sc, "card")
            assert hasattr(sc, "semantic_score")
            assert hasattr(sc, "persona_score")
            assert sc.persona_score == 1.0  # 페르소나 검색 표시

    def test_respects_count_limit(self, searcher: PersonaSearcher):
        """count 제한을 준수"""
        result = searcher.search(
            keywords=["놀이", "음식", "동물"],
            count=3,
            excluded_indices=set(),
        )

        assert len(result) <= 3

    def test_excludes_specified_indices(self, searcher: PersonaSearcher):
        """제외된 인덱스는 결과에 포함되지 않음"""
        excluded = {0, 1, 2}  # 처음 3개 카드 제외
        result = searcher.search(
            keywords=["놀이"],
            count=10,
            excluded_indices=excluded,
        )

        excluded_filenames = {"001_사과.png", "002_바나나.png", "003_놀이.png"}
        for sc in result:
            assert sc.card.filename not in excluded_filenames

    def test_removes_duplicate_cards(self, searcher: PersonaSearcher):
        """중복 카드 제거"""
        result = searcher.search(
            keywords=["놀이", "놀이", "놀이"],  # 같은 키워드 반복
            count=10,
            excluded_indices=set(),
        )

        filenames = [sc.card.filename for sc in result]
        assert len(filenames) == len(set(filenames))  # 중복 없음


class TestBuildPersonaQueries:
    """_build_persona_queries 메서드 테스트"""

    @pytest.fixture
    def searcher(self) -> PersonaSearcher:
        """테스트용 PersonaSearcher"""
        filenames = ["001_test.png"]
        embedding = MockEmbeddingProvider()
        vector_index = MockVectorIndex(filenames)
        return PersonaSearcher(embedding, vector_index)

    def test_builds_individual_keyword_queries(self, searcher: PersonaSearcher):
        """개별 키워드 쿼리 생성"""
        queries = searcher._build_persona_queries(["놀이", "음식"])

        assert any("놀이" in q for q in queries)
        assert any("음식" in q for q in queries)

    def test_builds_combined_query(self, searcher: PersonaSearcher):
        """복합 쿼리 생성 (2개 이상 키워드)"""
        queries = searcher._build_persona_queries(["놀이", "음식", "동물"])

        # 복합 쿼리가 존재하는지 확인
        combined_queries = [q for q in queries if "놀이" in q and "음식" in q]
        assert len(combined_queries) > 0

    def test_respects_max_keyword_limit(self, searcher: PersonaSearcher):
        """최대 키워드 개수 제한"""
        many_keywords = ["키워드" + str(i) for i in range(10)]
        queries = searcher._build_persona_queries(many_keywords)

        # MAX_KEYWORD_QUERIES(5) + 1(복합 쿼리) 이하
        assert len(queries) <= 6

    def test_handles_empty_keywords(self, searcher: PersonaSearcher):
        """빈 키워드 처리"""
        queries = searcher._build_persona_queries([])
        assert queries == []

    def test_handles_whitespace_keywords(self, searcher: PersonaSearcher):
        """공백 키워드 필터링"""
        queries = searcher._build_persona_queries(["놀이", "  ", "", "음식"])

        # 공백 키워드는 쿼리에 포함되지 않음
        for q in queries:
            assert "  " not in q
