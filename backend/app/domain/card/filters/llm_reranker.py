"""GPT-4o 기반 카드 재순위화

필터링된 카드들을 현재 상황에 맞게 재순위화합니다.
LLM의 컨텍스트 이해 능력을 활용하여 가장 관련성 높은
카드가 상위에 오도록 순위를 조정합니다.
"""

import logging
from typing import Dict, List

from app.domain.card.filters.base import (
    FilterContext,
    ICardReranker,
)
from app.domain.card.interfaces import ScoredCard
from app.infrastructure.external.openai_client import OpenAIClient

logger = logging.getLogger(__name__)


class LLMCardReranker(ICardReranker):
    """GPT-4o 기반 카드 재순위화

    현재 상황(장소, 활동, 대화 상대)을 고려하여
    카드의 순위를 최적화합니다.
    """

    def __init__(
        self,
        openai_client: OpenAIClient,
        batch_size: int = 30,
    ):
        self._openai = openai_client
        self._batch_size = batch_size

    async def rerank_cards(
        self,
        candidates: List[ScoredCard],
        filter_ctx: FilterContext,
    ) -> List[ScoredCard]:
        """카드 재순위화 실행"""
        if not candidates:
            return []

        # 배치 처리를 위해 카드 이름 추출
        card_names = [
            self._extract_card_name(c.card.filename)
            for c in candidates[: self._batch_size]
        ]

        # 프롬프트 생성 및 API 호출
        prompt = self._build_rerank_prompt(card_names, filter_ctx)
        response = await self._openai.rerank_cards(prompt)

        # 응답이 비어있으면 원본 순서 유지
        ranked_names = response.get("ranked", [])
        if not ranked_names:
            logger.warning("LLM 재순위화 응답 없음, 원본 순서 유지")
            return candidates

        # 재순위화 적용
        return self._apply_ranking(candidates, ranked_names)

    def _build_rerank_prompt(
        self,
        card_names: List[str],
        filter_ctx: FilterContext,
    ) -> str:
        """재순위화 프롬프트 생성"""
        user = filter_ctx.user
        context = filter_ctx.context

        # 관심 주제 포맷팅
        topics_str = ", ".join(user.interesting_topics) if user.interesting_topics else "없음"

        return f"""AAC 카드를 현재 상황에 맞게 순위를 매겨주세요.

## 사용자 상황
- {user.age}세 {user.disability_type} 사용자
- {context.place}에서 {context.interaction_partner}와 함께
- 현재 활동: "{context.current_activity}"
- 관심 주제: {topics_str}

## 카드 목록
{card_names}

## 우선순위 기준
1. **현재 활동 관련**: "{context.current_activity}"와 직접 관련된 카드 (예: 먹다, 맛있다)
2. **관심 주제 관련**: 사용자의 관심 주제({topics_str})와 관련된 카드
   - 관심 주제 카드는 의사소통 동기 부여에 중요하므로 상위 배치
3. **기본 의사소통**: 좋다, 싫다, 더, 그만, 도와주세요 등 필수 표현
4. **장소/상대 관련**: {context.place}, {context.interaction_partner}와 관련된 카드
5. **감정 표현**: 행복, 슬픔, 아파요 등 감정 카드
6. **요청 표현**: 화장실, 물, 쉬고 싶어요 등 기본 요청

## 응답 형식 (JSON)
가장 유용한 순서대로 카드명을 배열로 제공해주세요:
{{
  "ranked": ["카드명1", "카드명2", "카드명3", ...]
}}

모든 카드를 빠짐없이 순위에 포함해주세요."""

    def _apply_ranking(
        self,
        candidates: List[ScoredCard],
        ranked_names: List[str],
    ) -> List[ScoredCard]:
        """재순위화 결과 적용"""
        # 카드명으로 인덱싱
        name_to_card: Dict[str, ScoredCard] = {}
        for c in candidates:
            name = self._extract_card_name(c.card.filename)
            name_to_card[name] = c

        # LLM 순위에 따라 정렬
        reranked: List[ScoredCard] = []
        used_names: set = set()

        for name in ranked_names:
            if name in name_to_card and name not in used_names:
                card = name_to_card[name]
                # 순위에 따른 점수 보너스 (상위일수록 높은 보너스)
                rank_bonus = 0.1 * (1 - len(reranked) / len(candidates))
                card.semantic_score += rank_bonus
                reranked.append(card)
                used_names.add(name)

        # LLM 순위에 없는 카드는 뒤에 추가
        for c in candidates:
            name = self._extract_card_name(c.card.filename)
            if name not in used_names:
                reranked.append(c)

        return reranked

    def _extract_card_name(self, filename: str) -> str:
        """파일명에서 카드 이름 추출"""
        name = filename.rsplit(".", 1)[0]
        if "_" in name:
            return name.split("_", 1)[1]
        return name

    def get_reranker_name(self) -> str:
        return "LLMCardReranker"
