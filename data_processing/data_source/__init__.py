"""데이터 프로세싱 모듈

CLIP 임베딩 기반 순수 벡터 검색을 위한 전처리 모듈
- ImageFilter: 부적절한 이미지 필터링
- CLIPEncoder: CLIP 멀티모달 임베딩 생성
"""

from .embeddings import CLIPEncoder
from .image_filter import ImageFilter

__all__ = [
    "CLIPEncoder",
    "ImageFilter",
]
