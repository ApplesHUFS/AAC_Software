"""CLIP 임베딩 클라이언트

전처리 파이프라인과 동일한 CLIP 모델을 사용하여
텍스트를 이미지 임베딩과 동일한 공간으로 인코딩
"""

from typing import List, Optional

import numpy as np
import torch
from transformers import CLIPModel, CLIPProcessor

from app.config.settings import Settings
from app.domain.card.interfaces import IEmbeddingProvider


class CLIPEmbeddingClient(IEmbeddingProvider):
    """CLIP 기반 텍스트 임베딩 클라이언트

    전처리 단계에서 사용된 동일한 CLIP 모델로 텍스트를 인코딩하여
    이미지 임베딩과 통합된 시맨틱 공간에서 검색 가능하게 함

    Attributes:
        _settings: 애플리케이션 설정
        _model: CLIP 모델 (지연 로딩)
        _processor: CLIP 프로세서 (지연 로딩)
        _device: 추론 디바이스 (cuda/cpu)
    """

    CLIP_MAX_LENGTH = 77  # CLIP 텍스트 인코더 최대 토큰 길이

    def __init__(self, settings: Settings):
        self._settings = settings
        self._model: Optional[CLIPModel] = None
        self._processor: Optional[CLIPProcessor] = None
        self._device: Optional[str] = None

    def _get_device(self) -> str:
        """추론 디바이스 결정"""
        if self._device is None:
            if self._settings.device == "auto":
                self._device = "cuda" if torch.cuda.is_available() else "cpu"
            else:
                self._device = self._settings.device
        return self._device

    def _load_model(self) -> None:
        """모델 지연 로딩

        첫 호출 시에만 모델을 로드하여 메모리 효율성 확보
        GPU 사용 가능 시 float16으로 로드하여 메모리 절약
        """
        if self._model is not None:
            return

        model_name = self._settings.clip_model
        device = self._get_device()

        # GPU에서는 float16 사용, CPU에서는 float32 사용
        dtype = torch.float16 if device == "cuda" else torch.float32

        self._model = CLIPModel.from_pretrained(
            model_name,
            torch_dtype=dtype,
        ).to(device)
        self._model.eval()

        self._processor = CLIPProcessor.from_pretrained(model_name)

    def encode_text(self, text: str) -> np.ndarray:
        """단일 텍스트를 CLIP 임베딩으로 인코딩

        Args:
            text: 인코딩할 텍스트

        Returns:
            L2 정규화된 768차원 임베딩 벡터
        """
        self._load_model()

        inputs = self._processor(
            text=[text],
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=self.CLIP_MAX_LENGTH,
        )

        # 디바이스로 이동
        inputs = {k: v.to(self._get_device()) for k, v in inputs.items()}

        with torch.no_grad():
            # CLIP 텍스트 특징 추출
            text_features = self._model.get_text_features(**inputs)
            # L2 정규화 (코사인 유사도 계산을 위해)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)

        return text_features.cpu().numpy().flatten().astype(np.float32)

    def encode_texts_batch(self, texts: List[str]) -> np.ndarray:
        """여러 텍스트를 배치로 인코딩

        Args:
            texts: 인코딩할 텍스트 목록

        Returns:
            (N, 768) 형태의 L2 정규화된 임베딩 행렬
        """
        if not texts:
            return np.array([], dtype=np.float32).reshape(0, self.get_embedding_dimension())

        self._load_model()

        inputs = self._processor(
            text=texts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=self.CLIP_MAX_LENGTH,
        )

        inputs = {k: v.to(self._get_device()) for k, v in inputs.items()}

        with torch.no_grad():
            text_features = self._model.get_text_features(**inputs)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)

        return text_features.cpu().numpy().astype(np.float32)

    def get_embedding_dimension(self) -> int:
        """임베딩 차원 반환

        CLIP ViT-large-patch14: 768차원
        CLIP ViT-base-patch32: 512차원
        """
        # ViT-large-patch14 기준
        return 768

    def encode_with_augmentation(self, text: str) -> np.ndarray:
        """텍스트 증강을 포함한 인코딩

        여러 형태의 쿼리를 생성하여 평균 임베딩 계산
        검색 견고성 향상에 도움

        Args:
            text: 원본 텍스트

        Returns:
            증강된 쿼리들의 평균 임베딩
        """
        if not text or not text.strip():
            return np.zeros(self.get_embedding_dimension(), dtype=np.float32)

        # 쿼리 변형 생성
        augmented_queries = [
            text,
            f"이미지: {text}",
            f"{text} 관련 그림",
        ]

        embeddings = self.encode_texts_batch(augmented_queries)

        # 평균 후 재정규화
        mean_embedding = np.mean(embeddings, axis=0)
        norm = np.linalg.norm(mean_embedding)
        if norm > 0:
            mean_embedding = mean_embedding / norm

        return mean_embedding.astype(np.float32)
