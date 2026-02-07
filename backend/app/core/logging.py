"""로깅 설정 모듈

구조화된 로깅 시스템 - JSON 포맷(프로덕션) / 컬러 콘솔(개발)
"""

import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional
import json


class JSONFormatter(logging.Formatter):
    """JSON 포맷터 (프로덕션용)

    로그를 JSON 형식으로 출력하여 로그 수집 시스템과 통합
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # 추가 필드
        if hasattr(record, "extra_data"):
            log_data["data"] = record.extra_data

        return json.dumps(log_data, ensure_ascii=False)


class ColorFormatter(logging.Formatter):
    """컬러 콘솔 포맷터 (개발용)

    ANSI 색상 코드로 로그 레벨 구분
    """

    COLORS = {
        "DEBUG": "\033[36m",     # cyan
        "INFO": "\033[32m",      # green
        "WARNING": "\033[33m",   # yellow
        "ERROR": "\033[31m",     # red
        "CRITICAL": "\033[35m",  # magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        levelname = f"{color}{record.levelname:8}{self.RESET}"

        # 로거 이름 축약
        logger_name = record.name
        if logger_name.startswith("app."):
            logger_name = logger_name[4:]

        timestamp = datetime.now().strftime("%H:%M:%S")
        message = record.getMessage()

        formatted = f"{timestamp} | {levelname} | {logger_name:30} | {message}"

        if record.exc_info:
            formatted += "\n" + self.formatException(record.exc_info)

        return formatted


def setup_logging(
    log_level: Optional[str] = None,
    json_format: Optional[bool] = None,
) -> None:
    """로깅 설정 초기화

    Args:
        log_level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR)
                   미지정시 LOG_LEVEL 환경변수 또는 INFO 사용
        json_format: JSON 포맷 사용 여부
                     미지정시 LOG_FORMAT 환경변수로 결정 (json/console)
    """
    # 환경변수에서 설정 읽기
    level_str = log_level or os.getenv("LOG_LEVEL", "INFO")
    level = getattr(logging, level_str.upper(), logging.INFO)

    if json_format is None:
        json_format = os.getenv("LOG_FORMAT", "console").lower() == "json"

    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # 기존 핸들러 제거
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 스트림 핸들러 추가
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    if json_format:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(ColorFormatter())

    root_logger.addHandler(handler)

    # 외부 라이브러리 로그 레벨 조정
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """로거 인스턴스 반환

    Args:
        name: 로거 이름 (보통 __name__ 사용)

    Returns:
        설정된 로거 인스턴스
    """
    return logging.getLogger(name)
