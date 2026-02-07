"""쿼리 재작성 클라이언트

검색 쿼리 확장 기능 제공
"""

import json
import logging
from typing import List, Optional

from app.config.settings import Settings

from .base import OpenAIClientBase

logger = logging.getLogger(__name__)


class QueryRewriter(OpenAIClientBase):
    """쿼리 재작성 클라이언트"""

    def __init__(self, settings: Settings):
        super().__init__(settings)

    async def rewrite_query(
        self,
        place: str,
        partner: str,
        activity: str,
        count: int = 3,
        context_hints: Optional[List[str]] = None,
    ) -> List[str]:
        """검색 쿼리 확장 (JSON 응답)

        원본 컨텍스트를 여러 검색 쿼리로 확장하여
        더 다양한 카드 후보를 확보합니다.

        Args:
            place: 장소
            partner: 대화 상대
            activity: 현재 활동
            count: 생성할 쿼리 수
            context_hints: 과거 피드백에서 추출된 컨텍스트 힌트

        Returns:
            확장된 쿼리 목록
        """
        logger.info(
            "쿼리 재작성 시작: place=%s, partner=%s, activity=%s",
            place,
            partner,
            activity,
        )

        prompt = self._build_prompt(place, partner, activity, count, context_hints)

        try:
            response = self._client.responses.create(
                model=self._settings.openai_filter_model,
                instructions="AAC 카드 검색 쿼리 확장 전문가입니다. JSON 형식으로 응답해주세요.",
                input=prompt,
                max_output_tokens=self._settings.query_rewrite_max_tokens,
                temperature=0.7,
                text={"format": {"type": "json_object"}},
            )

            content = response.output_text or "{}"
            result = json.loads(content)
            queries = result.get("queries", [])

            if queries:
                logger.info(f"쿼리 재작성 완료: {len(queries)}개 생성")
                return queries[:count]

        except json.JSONDecodeError as e:
            logger.warning(f"쿼리 재작성 JSON 파싱 오류: {e}")

        except Exception as e:
            logger.warning(f"쿼리 재작성 API 오류: {e}")

        return []

    def _build_prompt(
        self,
        place: str,
        partner: str,
        activity: str,
        count: int,
        context_hints: Optional[List[str]],
    ) -> str:
        """쿼리 재작성 프롬프트 생성"""
        hints_section = ""
        if context_hints:
            hints_section = f"""
## 과거 유사 상황 (피드백 기반)
다음은 과거에 비슷한 상황에서 사용된 표현입니다. 이를 참고하여 쿼리를 확장하세요:
{', '.join(context_hints)}
"""

        return f"""AAC 카드 검색을 위해 쿼리를 확장해주세요.

## 원본 컨텍스트
- 장소: {place or '없음'}
- 대화 상대: {partner or '없음'}
- 현재 활동: {activity or '없음'}
{hints_section}
## 요청
위 상황에서 필요한 AAC 카드를 찾기 위한 검색 쿼리 {count}개를 생성하세요.
각 쿼리는 서로 다른 관점에서 작성:
1. 동의어/유사어를 사용한 표현
2. 관련 활동이나 행동을 확장한 표현
3. 감정이나 요구 표현을 추가한 표현

## 응답 형식 (JSON)
{{"queries": ["쿼리1 상황에서 사용하는 의사소통 카드", "쿼리2 상황에서 사용하는 의사소통 카드", "쿼리3 상황에서 사용하는 의사소통 카드"]}}"""
