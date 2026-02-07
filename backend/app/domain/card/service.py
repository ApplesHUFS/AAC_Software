"""카드 서비스"""

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from app.config.settings import Settings

logger = logging.getLogger(__name__)
from app.domain.card.entity import Card, CardHistory, Interpretation
from app.domain.card.recommender import CardRecommender
from app.domain.context.entity import Context
from app.domain.user.entity import User
from app.infrastructure.external.openai_client import OpenAIClient
from app.infrastructure.persistence.memory_repository import InMemoryCardHistoryRepository


@dataclass
class RecommendResult:
    """카드 추천 결과"""

    success: bool
    cards: List[Card]
    context_info: Dict[str, Any]
    pagination: Dict[str, int]
    message: str


@dataclass
class ValidateResult:
    """카드 검증 결과"""

    valid: bool
    selected_count: int
    message: str


@dataclass
class InterpretResult:
    """카드 해석 결과"""

    success: bool
    interpretations: List[Interpretation]
    feedback_id: int
    selected_cards: List[Dict[str, Any]]
    message: str


class CardService:
    """카드 관련 비즈니스 로직"""

    def __init__(
        self,
        settings: Settings,
        recommender: CardRecommender,
        openai_client: OpenAIClient,
        history_repository: InMemoryCardHistoryRepository,
    ):
        self._settings = settings
        self._recommender = recommender
        self._openai = openai_client
        self._history_repo = history_repository
        self._feedback_id_counter = 0

    async def recommend_cards(
        self,
        user: User,
        context: Context,
    ) -> RecommendResult:
        """카드 추천 (LLM 필터 포함)"""
        logger.info(
            "카드 추천 서비스 시작: user=%s, context=%s",
            user.user_id, context.context_id
        )

        # 이미 추천된 카드 조회
        excluded_cards = await self._history_repo.get_all_recommended_cards(
            context.context_id
        )
        logger.debug("제외할 카드: %d개", len(excluded_cards))

        # 비동기 카드 추천 (LLM 필터 + 재순위화)
        cards = await self._recommender.recommend_cards_async(
            preferred_keywords=user.interesting_topics,
            place=context.place,
            interaction_partner=context.interaction_partner,
            current_activity=context.current_activity,
            excluded_cards=excluded_cards,
            user=user,
            context_entity=context,
        )

        # 히스토리 저장
        total_pages = self._history_repo.get_total_pages(context.context_id)
        new_page = total_pages + 1

        history = CardHistory(
            context_id=context.context_id,
            page_number=new_page,
            cards=cards,
            timestamp=datetime.now(),
        )
        await self._history_repo.save_history(history)

        logger.info(
            "카드 추천 서비스 완료: %d개 카드, page=%d",
            len(cards), new_page
        )

        return RecommendResult(
            success=True,
            cards=cards,
            context_info=context.to_summary_dict(),
            pagination={
                "currentPage": new_page,
                "totalPages": new_page,
            },
            message="카드 추천이 완료되었습니다.",
        )

    def validate_selection(
        self,
        selected_cards: List[str],
        all_recommended_cards: List[str],
    ) -> ValidateResult:
        """카드 선택 검증"""
        logger.debug("카드 선택 검증: %d개 선택", len(selected_cards))
        selected_count = len(selected_cards)

        # 선택 개수 검증
        if selected_count < self._settings.min_card_selection:
            logger.warning("카드 선택 실패: 최소 개수 미달 (%d개)", selected_count)
            return ValidateResult(
                valid=False,
                selected_count=selected_count,
                message=f"최소 {self._settings.min_card_selection}개의 카드를 선택해주세요.",
            )

        if selected_count > self._settings.max_card_selection:
            logger.warning("카드 선택 실패: 최대 개수 초과 (%d개)", selected_count)
            return ValidateResult(
                valid=False,
                selected_count=selected_count,
                message=f"최대 {self._settings.max_card_selection}개의 카드만 선택 가능합니다.",
            )

        # 추천된 카드 중에서 선택했는지 검증
        all_recommended_set = set(all_recommended_cards)
        for card in selected_cards:
            if card not in all_recommended_set:
                logger.warning("카드 선택 실패: 비추천 카드 선택 (%s)", card)
                return ValidateResult(
                    valid=False,
                    selected_count=selected_count,
                    message=f"'{card}'는 추천된 카드가 아닙니다.",
                )

        logger.info("카드 선택 검증 성공: %d개", selected_count)
        return ValidateResult(
            valid=True,
            selected_count=selected_count,
            message="카드 선택이 유효합니다.",
        )

    async def interpret_cards(
        self,
        user: User,
        context: Context,
        selected_cards: List[str],
    ) -> InterpretResult:
        """카드 해석"""
        logger.info(
            "카드 해석 시작: user=%s, %d개 카드",
            user.user_id, len(selected_cards)
        )

        # 이미지 로드 및 인코딩
        card_images = []
        selected_card_info = []

        for filename in selected_cards:
            image_path = self._settings.images_folder / filename
            if image_path.exists():
                base64_data = self._openai.encode_image_to_base64(image_path)
                media_type = self._openai.get_image_media_type(filename)

                name = filename.rsplit(".", 1)[0] if "." in filename else filename

                card_images.append(
                    {
                        "base64": base64_data,
                        "media_type": media_type,
                        "name": name,
                    }
                )

                selected_card_info.append(
                    {
                        "filename": filename,
                        "name": name,
                        "imagePath": f"/api/images/{filename}",
                    }
                )

        # 해석 생성
        interpretation_texts = await self._openai.interpret_cards(
            card_images=card_images,
            user_persona=user.to_response_dict(),
            context=context.to_summary_dict(),
            memory_summary=None,
        )

        # 해석 객체 생성
        interpretations = [
            Interpretation(index=i, text=text)
            for i, text in enumerate(interpretation_texts)
        ]

        # 피드백 ID 생성
        self._feedback_id_counter += 1

        logger.info(
            "카드 해석 완료: %d개 해석 생성, feedback_id=%d",
            len(interpretations), self._feedback_id_counter
        )

        return InterpretResult(
            success=True,
            interpretations=interpretations,
            feedback_id=self._feedback_id_counter,
            selected_cards=selected_card_info,
            message="카드 해석이 완료되었습니다.",
        )

    async def get_history_summary(self, context_id: str) -> Dict[str, Any]:
        """히스토리 요약 조회"""
        histories = await self._history_repo.get_history_by_context(context_id)

        if not histories:
            return {
                "contextId": context_id,
                "totalPages": 0,
                "latestPage": 0,
                "historySummary": [],
            }

        summary = []
        for history in histories:
            summary.append(
                {
                    "pageNumber": history.page_number,
                    "cardCount": len(history.cards),
                    "timestamp": history.timestamp.isoformat(),
                }
            )

        return {
            "contextId": context_id,
            "totalPages": len(histories),
            "latestPage": histories[-1].page_number if histories else 0,
            "historySummary": summary,
        }

    async def get_history_page(
        self, context_id: str, page_number: int
    ) -> Optional[Dict[str, Any]]:
        """특정 페이지 히스토리 조회"""
        history = await self._history_repo.get_history_page(context_id, page_number)

        if not history:
            return None

        total_pages = self._history_repo.get_total_pages(context_id)

        return {
            "cards": [card.to_dict() for card in history.cards],
            "pagination": {
                "currentPage": page_number,
                "totalPages": total_pages,
            },
            "timestamp": history.timestamp.isoformat(),
            "contextId": context_id,
        }
