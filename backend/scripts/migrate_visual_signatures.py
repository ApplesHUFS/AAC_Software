#!/usr/bin/env python3
"""기존 피드백에 시각적 서명 추가 마이그레이션 스크립트

사용법:
    cd backend
    source venv/bin/activate
    python scripts/migrate_visual_signatures.py

이 스크립트는:
1. 기존 피드백 데이터를 백업
2. 각 피드백의 카드들에 대해 CLIP 임베딩 조합으로 시각적 서명 계산
3. visualSignature 필드 추가
"""

import asyncio
import json
import logging
import shutil
import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config.settings import get_settings
from app.domain.card.vector_searcher import create_vector_index
from app.domain.feedback.visual_analyzer import CLIPVisualPatternAnalyzer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def migrate_existing_feedbacks() -> int:
    """기존 피드백에 시각적 서명 추가

    Returns:
        마이그레이션된 피드백 수
    """
    settings = get_settings()
    feedback_path = settings.feedback_file_path

    if not feedback_path.exists():
        logger.warning("피드백 파일이 존재하지 않습니다: %s", feedback_path)
        return 0

    # 백업 생성
    backup_path = feedback_path.with_suffix(".json.bak")
    shutil.copy(feedback_path, backup_path)
    logger.info("백업 생성 완료: %s", backup_path)

    # 피드백 데이터 로드
    with open(feedback_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    feedbacks = data.get("feedbacks", [])
    if not feedbacks:
        logger.info("마이그레이션할 피드백이 없습니다.")
        return 0

    # 시각적 패턴 분석기 초기화
    logger.info("벡터 인덱스 로딩 중...")
    vector_index = create_vector_index(settings)
    logger.info("벡터 인덱스 로드 완료: %d개 카드", vector_index.size)

    analyzer = CLIPVisualPatternAnalyzer(
        vector_index=vector_index,
        feedback_file_path=feedback_path,
        signature_method=settings.visual_pattern.signature_method,
        similarity_threshold=settings.visual_pattern.similarity_threshold,
        decay_days=settings.visual_pattern.recency_decay_days,
    )

    # 마이그레이션 수행
    migrated_count = 0
    skipped_count = 0

    for i, feedback in enumerate(feedbacks):
        fb_id = feedback.get("feedbackId", i)

        # 이미 시각적 서명이 있으면 스킵
        if "visualSignature" in feedback and feedback["visualSignature"]:
            skipped_count += 1
            continue

        cards = feedback.get("cards", [])
        if not cards:
            logger.warning("피드백 %d: 카드가 없어서 스킵", fb_id)
            continue

        try:
            # 시각적 서명 계산
            signature = await analyzer.compute_visual_signature(cards)
            feedback["visualSignature"] = signature.tolist()
            migrated_count += 1

            if migrated_count % 5 == 0:
                logger.info("마이그레이션 진행: %d개 완료", migrated_count)

        except Exception as e:
            logger.error("피드백 %d 시각적 서명 계산 실패: %s", fb_id, e)

    # 저장
    with open(feedback_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info("=" * 50)
    logger.info("마이그레이션 완료!")
    logger.info("  - 마이그레이션됨: %d개", migrated_count)
    logger.info("  - 스킵됨 (이미 있음): %d개", skipped_count)
    logger.info("  - 백업 파일: %s", backup_path)
    logger.info("=" * 50)

    return migrated_count


def verify_migration() -> None:
    """마이그레이션 결과 검증"""
    settings = get_settings()
    feedback_path = settings.feedback_file_path

    with open(feedback_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    feedbacks = data.get("feedbacks", [])
    total = len(feedbacks)
    with_signature = sum(1 for fb in feedbacks if fb.get("visualSignature"))

    logger.info("검증 결과:")
    logger.info("  - 전체 피드백: %d개", total)
    logger.info("  - 시각적 서명 있음: %d개 (%.1f%%)", with_signature, with_signature / total * 100 if total > 0 else 0)

    # 첫 번째 시각적 서명 차원 확인
    for fb in feedbacks:
        if fb.get("visualSignature"):
            sig_len = len(fb["visualSignature"])
            logger.info("  - 시각적 서명 차원: %d", sig_len)
            break


if __name__ == "__main__":
    logger.info("시각적 서명 마이그레이션 시작")
    migrated = asyncio.run(migrate_existing_feedbacks())

    if migrated > 0:
        verify_migration()
