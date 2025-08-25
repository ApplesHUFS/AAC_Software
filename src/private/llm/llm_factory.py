import base64
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class LLMFactory:
    """OpenAI API 통합 관리 팩토리.

    이미지 처리, LLM 호출, 응답 파싱 등 OpenAI 관련 기능을 중앙화하여
    card_interpreter와 conversation_memory에서 공통으로 사용합니다.

    Attributes:
        client: OpenAI API 클라이언트
        model: 사용할 모델명
        temperature: 온도 설정
        max_tokens: 최대 토큰 수
        timeout: API 호출 타임아웃
        images_folder: 이미지 폴더 경로
    """

    def __init__(self, config: Dict[str, Any]):
        """LLMFactory 초기화.

        Args:
            config: 설정 딕셔너리
        """
        self.client = OpenAI()
        self.model = config.get('openai_model')
        self.temperature = config.get('openai_temperature')
        self.max_tokens = config.get('interpretation_max_tokens')
        self.timeout = config.get('api_timeout')
        self.images_folder = Path(config.get('images_folder'))

    def encode_image(self, image_path: Path) -> str:
        """이미지를 base64로 인코딩.

        Args:
            image_path: 이미지 파일 경로

        Returns:
            str: base64 인코딩된 이미지 문자열
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def prepare_card_images_content(self, cards: List[str]) -> List[Dict[str, Any]]:
        """카드 이미지들을 OpenAI Vision API 형태로 준비.

        Args:
            cards: 카드 파일명 리스트

        Returns:
            List[Dict]: OpenAI Vision API 콘텐츠 형식
        """
        content = []

        for i, card_filename in enumerate(cards, 1):
            image_path = self.images_folder / card_filename

            if image_path.exists():
                base64_image = self.encode_image(image_path)
                content.extend([
                    {"type": "text", "text": f"\n카드 {i}:"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                            "detail": "high"
                        }
                    }
                ])
            else:
                keyword = card_filename.replace('.png', '').replace('_', ' ')
                content.append({
                    "type": "text",
                    "text": f"\n카드 {i}: {keyword} (이미지 파일 없음)"
                })

        return content

    def call_vision_api(self, system_prompt: str, user_content: List[Dict[str, Any]],
                       temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> str:
        """OpenAI Vision API 호출.

        Args:
            system_prompt: 시스템 프롬프트
            user_content: 사용자 콘텐츠 (텍스트 + 이미지)
            temperature: 온도 설정 (선택사항)
            max_tokens: 최대 토큰 수 (선택사항)

        Returns:
            str: API 응답 내용
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=temperature or self.temperature,
            max_tokens=max_tokens or self.max_tokens,
            timeout=self.timeout
        )

        return response.choices[0].message.content.strip()

    def parse_interpretations(self, content: str) -> List[str]:
        """OpenAI 응답에서 해석들을 추출.

        Args:
            content: OpenAI 응답 내용

        Returns:
            List[str]: 추출된 해석 리스트 (최대 3개)
        """
        lines = [line.strip() for line in content.split('\n') if line.strip()]

        interpretations = []
        for cleaned in lines:
            if cleaned:
                # 번호나 접두사 제거
                import re
                cleaned = re.sub(r'^[\d\.\-\*]+\s*', '', cleaned)
                cleaned = re.sub(r'^(첫\s*번째|두\s*번째|세\s*번째|해석\s*\d+)\s*:?\s*', '', cleaned)

                if cleaned and len(cleaned) > 5:
                    interpretations.append(cleaned)

        return interpretations[:3]

    def generate_card_interpretations(self, persona: Dict[str, Any], context: Dict[str, Any],
                                    cards: List[str], past_interpretation: str = "") -> List[str]:
        """카드 해석 생성 (card_interpreter에서 사용).

        Args:
            persona: 사용자 페르소나 정보
            context: 상황 정보
            cards: 선택된 카드 리스트
            past_interpretation: 과거 해석 이력

        Returns:
            List[str]: 3개의 해석 결과
        """
        system_prompt = """당신은 AAC(보완대체의사소통) 전문가입니다.
사용자의 페르소나와 상황을 고려하여 선택된 AAC 카드 이미지들을 해석해주세요.

해석 원칙:
1. 이미지를 직접 보고 시각적 요소(객체, 행동, 표정, 색깔 등)를 파악하여 해석
2. 사용자의 의도를 정확히 파악하여 자연스러운 한국어로 표현
3. 페르소나의 특성(나이, 성별, 장애유형, 의사소통 특성)을 반영
4. 상황 맥락(시간, 장소, 대화상대, 활동)을 고려
5. 과거 해석 패턴이 있다면 일관성 유지

정확히 3개의 해석을 제공하되, 각각 다른 관점에서 접근해주세요.
해석 앞에 번호나 접두사는 붙이지 마세요."""

        # 이미지 콘텐츠 준비
        image_content = self.prepare_card_images_content(cards)

        user_content = [{
            "type": "text",
            "text": f"""페르소나:
- 나이: {persona.get('age', '알 수 없음')}
- 성별: {persona.get('gender', '알 수 없음')}
- 장애 유형: {persona.get('disability_type', '알 수 없음')}
- 의사소통 특성: {persona.get('communication_characteristics', '알 수 없음')}
- 관심 주제: {', '.join(persona.get('interesting_topics', []))}

현재 상황:
- 시간: {context.get('time', '알 수 없음')}
- 장소: {context.get('place', '알 수 없음')}
- 대화 상대: {context.get('interaction_partner', '알 수 없음')}
- 현재 활동: {context.get('current_activity', '알 수 없음')}

{past_interpretation if past_interpretation else ""}
"""
        }]

        user_content.extend(image_content)
        user_content.append({
            "type": "text",
            "text": """
위 이미지들을 보고 이 사용자가 전달하고자 하는 의도를 3가지 관점에서 해석해주세요.
이미지의 시각적 내용과 순서를 반드시 고려하세요.
각 해석은 접두사 없이 바로 내용으로 시작하세요."""
        })

        content = self.call_vision_api(system_prompt, user_content)
        interpretations = self.parse_interpretations(content)

        # 정확히 3개가 나오지 않으면 에러 발생
        if len(interpretations) != 3:
            raise ValueError(f"해석이 정확히 3개 생성되지 않았습니다. 생성된 해석 수: {len(interpretations)}")

        return interpretations

    def analyze_card_interpretation_connection(self, cards: List[str], context: Dict[str, Any],
                                             final_interpretation: str) -> str:
        """카드 이미지와 해석의 연결성 분석 (conversation_memory에서 사용).

        Args:
            cards: 선택된 카드 파일명 리스트
            context: 상황 정보
            final_interpretation: 최종 선택된 해석

        Returns:
            str: 분석된 연결성 요약
        """
        content = [{
            "type": "text",
            "text": f"""다음 AAC 카드 이미지들을 보고, 주어진 상황에서 어떤 시각적 특징이 최종 해석으로 연결되었는지 분석해주세요.

상황 정보:
- 시간: {context.get('time', '알 수 없음')}
- 장소: {context.get('place', '알 수 없음')}
- 대화 상대: {context.get('interaction_partner', '알 수 없음')}
- 현재 활동: {context.get('current_activity', '알 수 없음')}

최종 해석: {final_interpretation}

이미지들:"""
        }]

        # 각 카드 이미지 추가
        for i, card_filename in enumerate(cards, 1):
            image_path = self.images_folder / card_filename

            if image_path.exists():
                base64_image = self.encode_image(image_path)
                content.extend([
                    {"type": "text", "text": f"\n카드 {i}:"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                            "detail": "low"
                        }
                    }
                ])
            else:
                content.append({
                    "type": "text",
                    "text": f"\n카드 {i}: {card_filename} (이미지 파일 없음)"
                })

        content.append({
            "type": "text",
            "text": "\n위 이미지들의 어떤 시각적 요소(객체, 색깔, 행동, 표정 등)가 최종 해석으로 연결되었는지 50자 이내로 분석해주세요."
        })

        return self.call_vision_api("", content, temperature=0.3, max_tokens=100)
