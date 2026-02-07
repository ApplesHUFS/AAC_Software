"""외부 의존성 Mock 테스트

OpenAI API와 CLIP 모델의 Mock 테스트입니다.
네트워크 오류, 타임아웃, 잘못된 응답 등 다양한 시나리오를 테스트합니다.
AAA (Arrange-Act-Assert) 패턴을 준수합니다.
"""

import json
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

from app.config.settings import Settings
from app.infrastructure.external.openai_client import OpenAIClient
from app.infrastructure.external.clip_client import CLIPEmbeddingClient
from app.core.exceptions import LLMServiceError, LLMTimeoutError, LLMRateLimitError


@pytest.fixture
def test_settings() -> Settings:
    """테스트용 설정"""
    return Settings(
        openai_api_key="test-api-key",
        debug=True,
        device="cpu",
    )


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI 응답 생성 헬퍼"""

    def _create_response(output_text: str):
        response = MagicMock()
        response.output_text = output_text
        return response

    return _create_response


class TestOpenAIClientMock:
    """OpenAI 클라이언트 Mock 테스트"""

    def test_encode_image_to_base64(self, test_settings: Settings, tmp_path: Path):
        """이미지 Base64 인코딩"""
        # Arrange
        client = OpenAIClient(test_settings)
        test_image = tmp_path / "test.png"
        test_image.write_bytes(b"fake image content")

        # Act
        result = client.encode_image_to_base64(test_image)

        # Assert
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_image_media_type_png(self, test_settings: Settings):
        """PNG 미디어 타입 반환"""
        # Arrange
        client = OpenAIClient(test_settings)

        # Act
        result = client.get_image_media_type("image.png")

        # Assert
        assert result == "image/png"

    def test_get_image_media_type_jpeg(self, test_settings: Settings):
        """JPEG 미디어 타입 반환"""
        # Arrange
        client = OpenAIClient(test_settings)

        # Act
        result_jpg = client.get_image_media_type("image.jpg")
        result_jpeg = client.get_image_media_type("image.jpeg")

        # Assert
        assert result_jpg == "image/jpeg"
        assert result_jpeg == "image/jpeg"

    def test_get_image_media_type_default(self, test_settings: Settings):
        """알 수 없는 확장자는 PNG 반환"""
        # Arrange
        client = OpenAIClient(test_settings)

        # Act
        result = client.get_image_media_type("image.unknown")

        # Assert
        assert result == "image/png"

    @pytest.mark.asyncio
    async def test_interpret_cards_success(
        self, test_settings: Settings, mock_openai_response
    ):
        """카드 해석 성공"""
        # Arrange
        with patch.object(
            OpenAIClient, "__init__", lambda self, settings: setattr(self, "_settings", settings) or setattr(self, "_client", MagicMock())
        ):
            client = OpenAIClient(test_settings)
            mock_response = mock_openai_response(
                json.dumps({
                    "interpretations": [
                        "사과 주세요",
                        "과일 먹고 싶어요",
                        "배가 고파요",
                    ]
                })
            )
            client._client.responses.create = MagicMock(return_value=mock_response)

            card_images = [{"base64": "abc", "media_type": "image/png", "name": "사과"}]
            user_persona = {"name": "테스트", "age": 10}
            context = {"place": "학교", "time": "10시"}

            # Act
            result = await client.interpret_cards(card_images, user_persona, context)

            # Assert
            assert len(result) == 3
            assert "사과" in result[0]

    @pytest.mark.asyncio
    async def test_interpret_cards_incomplete_response(
        self, test_settings: Settings, mock_openai_response
    ):
        """불완전한 해석 응답 처리"""
        # Arrange
        with patch.object(
            OpenAIClient, "__init__", lambda self, settings: setattr(self, "_settings", settings) or setattr(self, "_client", MagicMock())
        ):
            client = OpenAIClient(test_settings)
            # 2개만 반환하는 응답
            mock_response = mock_openai_response(
                json.dumps({"interpretations": ["해석1", "해석2"]})
            )
            client._client.responses.create = MagicMock(return_value=mock_response)

            # Act
            result = await client.interpret_cards(
                [{"base64": "abc", "media_type": "image/png", "name": "test"}],
                {"name": "test"},
                {"place": "test"},
            )

            # Assert
            assert len(result) == 3
            assert "해석을 생성할 수 없습니다" in result[2]

    @pytest.mark.asyncio
    async def test_filter_cards_success(
        self, test_settings: Settings, mock_openai_response
    ):
        """카드 필터링 성공"""
        # Arrange
        with patch.object(
            OpenAIClient, "__init__", lambda self, settings: setattr(self, "_settings", settings) or setattr(self, "_client", MagicMock())
        ):
            client = OpenAIClient(test_settings)
            mock_response = mock_openai_response(
                json.dumps({
                    "appropriate": ["card1", "card2"],
                    "inappropriate": ["card3"],
                    "highly_relevant": ["card1"],
                })
            )
            client._client.responses.create = MagicMock(return_value=mock_response)

            # Act
            result = await client.filter_cards("test prompt")

            # Assert
            assert "appropriate" in result
            assert len(result["appropriate"]) == 2
            assert "card3" in result["inappropriate"]

    @pytest.mark.asyncio
    async def test_filter_cards_graceful_degradation(self, test_settings: Settings):
        """필터링 실패 시 Graceful Degradation"""
        # Arrange
        with patch.object(
            OpenAIClient, "__init__", lambda self, settings: setattr(self, "_settings", settings) or setattr(self, "_client", MagicMock())
        ):
            client = OpenAIClient(test_settings)
            client._client.responses.create = MagicMock(
                side_effect=Exception("API Error")
            )

            # Act
            result = await client.filter_cards("test prompt", max_retries=1)

            # Assert (Graceful Degradation - 빈 결과 반환)
            assert result["appropriate"] == []
            assert result["inappropriate"] == []

    @pytest.mark.asyncio
    async def test_rewrite_query_success(
        self, test_settings: Settings, mock_openai_response
    ):
        """쿼리 재작성 성공"""
        # Arrange
        with patch.object(
            OpenAIClient, "__init__", lambda self, settings: setattr(self, "_settings", settings) or setattr(self, "_client", MagicMock())
        ):
            client = OpenAIClient(test_settings)
            mock_response = mock_openai_response(
                json.dumps({
                    "queries": [
                        "학교에서 점심 먹기",
                        "식사 시간 카드",
                        "밥 먹고 싶어요 표현",
                    ]
                })
            )
            client._client.responses.create = MagicMock(return_value=mock_response)

            # Act
            result = await client.rewrite_query(
                place="학교",
                partner="선생님",
                activity="점심 시간",
                count=3,
            )

            # Assert
            assert len(result) == 3
            assert any("학교" in q or "점심" in q for q in result)

    @pytest.mark.asyncio
    async def test_rewrite_query_with_context_hints(
        self, test_settings: Settings, mock_openai_response
    ):
        """컨텍스트 힌트가 있는 쿼리 재작성"""
        # Arrange
        with patch.object(
            OpenAIClient, "__init__", lambda self, settings: setattr(self, "_settings", settings) or setattr(self, "_client", MagicMock())
        ):
            client = OpenAIClient(test_settings)
            mock_response = mock_openai_response(
                json.dumps({"queries": ["힌트 기반 쿼리1", "힌트 기반 쿼리2"]})
            )
            client._client.responses.create = MagicMock(return_value=mock_response)

            # Act
            result = await client.rewrite_query(
                place="학교",
                partner="선생님",
                activity="수업",
                count=2,
                context_hints=["과거 표현1", "과거 표현2"],
            )

            # Assert
            assert len(result) == 2

    @pytest.mark.asyncio
    async def test_rewrite_query_fallback_on_error(self, test_settings: Settings):
        """쿼리 재작성 실패 시 빈 리스트 반환"""
        # Arrange
        with patch.object(
            OpenAIClient, "__init__", lambda self, settings: setattr(self, "_settings", settings) or setattr(self, "_client", MagicMock())
        ):
            client = OpenAIClient(test_settings)
            client._client.responses.create = MagicMock(
                side_effect=Exception("API Error")
            )

            # Act
            result = await client.rewrite_query(
                place="학교",
                partner="선생님",
                activity="점심",
            )

            # Assert
            assert result == []

    @pytest.mark.asyncio
    async def test_summarize_conversation_success(
        self, test_settings: Settings, mock_openai_response
    ):
        """대화 요약 성공"""
        # Arrange
        with patch.object(
            OpenAIClient, "__init__", lambda self, settings: setattr(self, "_settings", settings) or setattr(self, "_client", MagicMock())
        ):
            client = OpenAIClient(test_settings)
            mock_response = mock_openai_response("사용자가 음식을 자주 요청함")
            client._client.responses.create = MagicMock(return_value=mock_response)

            history = [
                {"cards": ["사과", "물"], "interpretation": "사과와 물 주세요"},
                {"cards": ["밥"], "interpretation": "밥 먹고 싶어요"},
            ]

            # Act
            result = await client.summarize_conversation(history)

            # Assert
            assert isinstance(result, str)
            assert len(result) > 0

    @pytest.mark.asyncio
    async def test_summarize_conversation_empty_history(self, test_settings: Settings):
        """빈 대화 히스토리 요약"""
        # Arrange
        with patch.object(
            OpenAIClient, "__init__", lambda self, settings: setattr(self, "_settings", settings) or setattr(self, "_client", MagicMock())
        ):
            client = OpenAIClient(test_settings)

            # Act
            result = await client.summarize_conversation([])

            # Assert
            assert result == ""


class TestCLIPEmbeddingClientMock:
    """CLIP 임베딩 클라이언트 Mock 테스트"""

    def test_get_embedding_dimension(self, test_settings: Settings):
        """임베딩 차원 반환"""
        # Arrange
        with patch.object(CLIPEmbeddingClient, "_load_model", return_value=None):
            client = CLIPEmbeddingClient(test_settings)

            # Act
            dimension = client.get_embedding_dimension()

            # Assert
            assert dimension == 768

    def test_encode_text_returns_normalized_vector(self, test_settings: Settings):
        """텍스트 인코딩이 정규화된 벡터 반환"""
        # Arrange
        mock_model = MagicMock()
        mock_processor = MagicMock()

        # Mock 텍스트 특징 반환
        mock_features = MagicMock()
        mock_features.norm.return_value = MagicMock()
        mock_features.__truediv__ = MagicMock(return_value=mock_features)
        mock_features.cpu.return_value.numpy.return_value.flatten.return_value.astype.return_value = np.random.randn(768).astype(np.float32)
        mock_model.get_text_features.return_value = mock_features

        with patch.object(CLIPEmbeddingClient, "_load_model", return_value=None):
            client = CLIPEmbeddingClient(test_settings)
            client._model = mock_model
            client._processor = mock_processor
            client._device = "cpu"

            mock_processor.return_value = {"input_ids": MagicMock()}

            # Act
            result = client.encode_text("테스트 텍스트")

            # Assert
            assert isinstance(result, np.ndarray)
            assert result.shape == (768,)
            assert result.dtype == np.float32

    def test_encode_texts_batch_empty_list(self, test_settings: Settings):
        """빈 텍스트 목록 인코딩"""
        # Arrange
        with patch.object(CLIPEmbeddingClient, "_load_model", return_value=None):
            client = CLIPEmbeddingClient(test_settings)

            # Act
            result = client.encode_texts_batch([])

            # Assert
            assert isinstance(result, np.ndarray)
            assert result.shape == (0, 768)

    def test_encode_with_augmentation_empty_text(self, test_settings: Settings):
        """빈 텍스트 증강 인코딩"""
        # Arrange
        with patch.object(CLIPEmbeddingClient, "_load_model", return_value=None):
            client = CLIPEmbeddingClient(test_settings)

            # Act
            result = client.encode_with_augmentation("")

            # Assert
            assert isinstance(result, np.ndarray)
            assert result.shape == (768,)
            assert np.allclose(result, np.zeros(768))

    def test_encode_with_augmentation_whitespace_text(self, test_settings: Settings):
        """공백만 있는 텍스트 증강 인코딩"""
        # Arrange
        with patch.object(CLIPEmbeddingClient, "_load_model", return_value=None):
            client = CLIPEmbeddingClient(test_settings)

            # Act
            result = client.encode_with_augmentation("   ")

            # Assert
            assert np.allclose(result, np.zeros(768))

    def test_get_device_auto_detection(self, test_settings: Settings):
        """디바이스 자동 감지"""
        # Arrange
        test_settings.device = "auto"
        with patch.object(CLIPEmbeddingClient, "_load_model", return_value=None):
            with patch("torch.cuda.is_available", return_value=False):
                client = CLIPEmbeddingClient(test_settings)

                # Act
                device = client._get_device()

                # Assert
                assert device == "cpu"

    def test_get_device_explicit_cpu(self, test_settings: Settings):
        """명시적 CPU 디바이스"""
        # Arrange
        test_settings.device = "cpu"
        with patch.object(CLIPEmbeddingClient, "_load_model", return_value=None):
            client = CLIPEmbeddingClient(test_settings)

            # Act
            device = client._get_device()

            # Assert
            assert device == "cpu"


class TestOpenAIClientErrorHandling:
    """OpenAI 클라이언트 에러 처리 테스트"""

    @pytest.mark.asyncio
    async def test_interpret_cards_timeout_error(self, test_settings: Settings):
        """카드 해석 타임아웃 에러"""
        # Arrange
        from openai import APITimeoutError

        with patch.object(
            OpenAIClient, "__init__", lambda self, settings: setattr(self, "_settings", settings) or setattr(self, "_client", MagicMock())
        ):
            client = OpenAIClient(test_settings)
            client._client.responses.create = MagicMock(
                side_effect=APITimeoutError(request=MagicMock())
            )

            # Act & Assert
            with pytest.raises(LLMTimeoutError):
                await client.interpret_cards(
                    [{"base64": "abc", "media_type": "image/png", "name": "test"}],
                    {"name": "test"},
                    {"place": "test"},
                    max_retries=1,
                )

    @pytest.mark.asyncio
    async def test_interpret_cards_rate_limit_error(self, test_settings: Settings):
        """카드 해석 Rate Limit 에러"""
        # Arrange
        from openai import RateLimitError

        with patch.object(
            OpenAIClient, "__init__", lambda self, settings: setattr(self, "_settings", settings) or setattr(self, "_client", MagicMock())
        ):
            client = OpenAIClient(test_settings)

            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_response.headers = {}

            client._client.responses.create = MagicMock(
                side_effect=RateLimitError(
                    message="Rate limit exceeded",
                    response=mock_response,
                    body=None,
                )
            )

            # Act & Assert
            with pytest.raises(LLMRateLimitError):
                await client.interpret_cards(
                    [{"base64": "abc", "media_type": "image/png", "name": "test"}],
                    {"name": "test"},
                    {"place": "test"},
                    max_retries=1,
                )

    @pytest.mark.asyncio
    async def test_interpret_cards_json_decode_error(
        self, test_settings: Settings, mock_openai_response
    ):
        """카드 해석 JSON 파싱 에러"""
        # Arrange
        with patch.object(
            OpenAIClient, "__init__", lambda self, settings: setattr(self, "_settings", settings) or setattr(self, "_client", MagicMock())
        ):
            client = OpenAIClient(test_settings)
            mock_response = mock_openai_response("invalid json {{{")
            client._client.responses.create = MagicMock(return_value=mock_response)

            # Act & Assert
            with pytest.raises(LLMServiceError):
                await client.interpret_cards(
                    [{"base64": "abc", "media_type": "image/png", "name": "test"}],
                    {"name": "test"},
                    {"place": "test"},
                    max_retries=1,
                )

    @pytest.mark.asyncio
    async def test_filter_cards_json_decode_error_graceful(
        self, test_settings: Settings, mock_openai_response
    ):
        """필터링 JSON 파싱 에러 시 Graceful Degradation"""
        # Arrange
        with patch.object(
            OpenAIClient, "__init__", lambda self, settings: setattr(self, "_settings", settings) or setattr(self, "_client", MagicMock())
        ):
            client = OpenAIClient(test_settings)
            mock_response = mock_openai_response("not json")
            client._client.responses.create = MagicMock(return_value=mock_response)

            # Act
            result = await client.filter_cards("test prompt", max_retries=1)

            # Assert (Graceful Degradation)
            assert result["appropriate"] == []
            assert result["inappropriate"] == []

    @pytest.mark.asyncio
    async def test_rerank_cards_graceful_degradation(self, test_settings: Settings):
        """재순위화 실패 시 Graceful Degradation"""
        # Arrange
        with patch.object(
            OpenAIClient, "__init__", lambda self, settings: setattr(self, "_settings", settings) or setattr(self, "_client", MagicMock())
        ):
            client = OpenAIClient(test_settings)
            client._client.responses.create = MagicMock(
                side_effect=Exception("API Error")
            )

            # Act
            result = await client.rerank_cards("test prompt", max_retries=1)

            # Assert
            assert result["ranked"] == []


class TestMockIntegration:
    """Mock을 사용한 통합 테스트"""

    @pytest.mark.asyncio
    async def test_full_interpretation_flow_with_mock(
        self, test_settings: Settings, mock_openai_response
    ):
        """전체 해석 흐름 Mock 테스트"""
        # Arrange
        with patch.object(
            OpenAIClient, "__init__", lambda self, settings: setattr(self, "_settings", settings) or setattr(self, "_client", MagicMock())
        ):
            client = OpenAIClient(test_settings)

            # 쿼리 재작성 응답
            rewrite_response = mock_openai_response(
                json.dumps({"queries": ["확장 쿼리1", "확장 쿼리2"]})
            )

            # 필터링 응답
            filter_response = mock_openai_response(
                json.dumps({
                    "appropriate": ["card1", "card2"],
                    "inappropriate": [],
                    "highly_relevant": ["card1"],
                })
            )

            # 해석 응답
            interpret_response = mock_openai_response(
                json.dumps({
                    "interpretations": ["해석1", "해석2", "해석3"]
                })
            )

            call_count = 0

            def mock_create(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if "쿼리" in str(kwargs.get("input", "")):
                    return rewrite_response
                elif "필터" in str(kwargs.get("instructions", "")) or "적합성" in str(kwargs.get("instructions", "")):
                    return filter_response
                else:
                    return interpret_response

            client._client.responses.create = MagicMock(side_effect=mock_create)

            # Act - 쿼리 재작성
            queries = await client.rewrite_query(
                place="학교",
                partner="선생님",
                activity="점심",
            )

            # Act - 필터링
            filter_result = await client.filter_cards("필터 프롬프트")

            # Act - 해석
            interpretations = await client.interpret_cards(
                [{"base64": "abc", "media_type": "image/png", "name": "test"}],
                {"name": "test"},
                {"place": "학교"},
            )

            # Assert
            assert len(queries) == 2
            assert len(filter_result["appropriate"]) == 2
            assert len(interpretations) == 3
