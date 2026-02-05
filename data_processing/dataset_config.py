"""AAC 카드 임베딩 시스템 설정

CLIP 기반 순수 벡터 검색을 위한 간소화된 설정
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_CONFIG = {
    # 경로 설정
    "images_folder": str(PROJECT_ROOT / "dataset" / "images"),
    "output_folder": str(PROJECT_ROOT / "dataset" / "processed"),
    # CLIP 임베딩 설정
    "clip_model": "openai/clip-vit-large-patch14",
    "image_weight": 0.8,  # 이미지-텍스트 임베딩 융합 가중치
    # 이미지 필터링
    "filter_confirm": True,
    # GPU/CPU 설정
    "device": "auto",
    # 파이프라인 옵션
    "overwrite_mode": False,
}


def get_project_root() -> Path:
    """프로젝트 루트 디렉토리 반환"""
    return PROJECT_ROOT


def get_data_paths() -> dict:
    """데이터 관련 경로들을 반환"""
    return {
        "project_root": PROJECT_ROOT,
        "dataset_folder": PROJECT_ROOT / "dataset",
        "images_folder": Path(DATASET_CONFIG["images_folder"]),
        "output_folder": Path(DATASET_CONFIG["output_folder"]),
        "filtered_images": Path(DATASET_CONFIG["images_folder"]).parent
        / "filtered_images",
    }


def validate_config(config: dict) -> bool:
    """설정 유효성 검사"""
    required_keys = ["images_folder", "output_folder", "clip_model"]

    for key in required_keys:
        if key not in config:
            raise ValueError(f"필수 설정 누락: {key}")

    images_path = Path(config["images_folder"])
    if not images_path.parent.exists():
        print(f"경고: 데이터셋 폴더가 존재하지 않습니다: {images_path.parent}")

    if config["image_weight"] < 0.0 or config["image_weight"] > 1.0:
        raise ValueError("image_weight는 0.0과 1.0 사이 값이어야 합니다")

    return True


if __name__ == "__main__":
    validate_config(DATASET_CONFIG)

    paths = get_data_paths()
    print("프로젝트 경로 정보:")
    for name, path in paths.items():
        print(f"  {name}: {path}")

    print("\n설정 검증 완료")
