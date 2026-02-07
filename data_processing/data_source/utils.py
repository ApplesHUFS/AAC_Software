"""데이터 소스 공통 유틸리티

디바이스 설정, 파일명 처리, JSON 저장 등 공통 기능 제공
"""

import json
from pathlib import Path
from typing import Any, Optional

import torch


def get_device(config: Optional[dict] = None) -> str:
    """설정에서 디바이스 결정 (cuda/cpu auto 지원)

    Args:
        config: device 키를 포함하는 설정 딕셔너리
            - "auto": CUDA 사용 가능 시 cuda, 아니면 cpu
            - "cuda"/"cpu": 해당 디바이스 직접 지정

    Returns:
        "cuda" 또는 "cpu"
    """
    if config and "device" in config:
        device_setting = config["device"]
        if device_setting == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        return device_setting
    return "cuda" if torch.cuda.is_available() else "cpu"


def extract_keyword_from_filename(filename: str) -> str:
    """파일명에서 키워드 추출 (prefix_keyword.ext -> keyword)

    파일명 패턴: {id}_{keyword}.png에서 keyword 부분 추출

    Args:
        filename: 파일명 (예: "123_사과.png")

    Returns:
        추출된 키워드 (예: "사과"), 언더스코어가 없으면 빈 문자열
    """
    stem = Path(filename).stem
    if "_" not in stem:
        return ""
    return stem.split("_", 1)[1]


def save_json(
    data: Any,
    output_path: str,
    ensure_ascii: bool = False,
    indent: int = 2,
) -> None:
    """JSON 파일 저장 (디렉토리 자동 생성)

    Args:
        data: 저장할 데이터 (JSON 직렬화 가능)
        output_path: 출력 파일 경로
        ensure_ascii: ASCII가 아닌 문자 이스케이프 여부
        indent: 들여쓰기 칸 수
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=ensure_ascii, indent=indent)
