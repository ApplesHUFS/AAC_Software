"""AAC 카드 데이터 전처리 파이프라인

CLIP 임베딩 기반 순수 벡터 검색을 위한 간소화된 파이프라인
- 단계 1: 부적절한 이미지 필터링
- 단계 2: CLIP 멀티모달 임베딩 생성
"""

from pathlib import Path
from typing import List, Optional, Tuple

from data_source import CLIPEncoder, ImageFilter
from dataset_config import DATASET_CONFIG
from tqdm import tqdm


class DataPreparationPipeline:
    """AAC 카드 데이터 전처리 파이프라인

    이미지 필터링 → CLIP 임베딩 생성의 2단계 파이프라인
    클러스터링 없이 순수 벡터 검색을 위한 임베딩만 생성
    """

    def __init__(self, config: dict):
        self.config = config
        self._validate_config()
        self._setup_paths()

    def _validate_config(self) -> None:
        """필수 설정 검증"""
        required_keys = ["images_folder", "output_folder"]
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"필수 설정 누락: {key}")

    def _setup_paths(self) -> None:
        """경로 설정"""
        self.images_folder = Path(self.config["images_folder"])
        self.output_folder = Path(self.config["output_folder"])
        self.output_folder.mkdir(parents=True, exist_ok=True)

        self.embeddings_path = self.output_folder / "embeddings.json"

    def step1_filter_images(self, confirm: Optional[bool] = None) -> int:
        """부적절한 이미지 필터링

        Args:
            confirm: 대화형 확인 여부

        Returns:
            필터링된 이미지 수
        """
        if confirm is None:
            confirm = self.config.get("filter_confirm", True)

        filter_tool = ImageFilter(str(self.images_folder))
        return filter_tool.filter_images(confirm=confirm)

    def step2_generate_embeddings(
        self,
    ) -> Tuple[List[str], Tuple[int, int], Tuple[int, int]]:
        """CLIP 멀티모달 임베딩 생성

        이미지와 텍스트(파일명에서 추출)를 동시에 인코딩하여
        통합 CLIP 임베딩 공간에 매핑

        Returns:
            (파일명 목록, 이미지 임베딩 shape, 텍스트 임베딩 shape)
        """
        model_name = self.config.get("clip_model", "openai/clip-vit-large-patch14")
        encoder = CLIPEncoder(model_name=model_name, config=self.config)
        return encoder.process_and_save(
            str(self.images_folder), str(self.embeddings_path)
        )

    def run_pipeline(
        self,
        steps: Optional[List[str]] = None,
        confirm_filter: Optional[bool] = None,
    ) -> None:
        """파이프라인 실행

        Args:
            steps: 실행할 단계 목록 (기본: ["1", "2"])
            confirm_filter: 필터링 확인 여부
        """
        if steps is None:
            steps = ["1", "2"]

        step_methods = {
            "1": self.step1_filter_images,
            "2": self.step2_generate_embeddings,
        }

        try:
            print("AAC 카드 임베딩 파이프라인 시작")

            with tqdm(total=len(steps), desc="진행") as pbar:
                for step in steps:
                    if step not in step_methods:
                        print(f"잘못된 단계: {step}")
                        continue

                    if step == "1":
                        result = step_methods[step](confirm_filter)
                        print(f"단계 1: {result}개 이미지 필터링")
                    elif step == "2":
                        filenames, img_emb, txt_emb = step_methods[step]()
                        print(f"단계 2: {len(filenames)}개 이미지 CLIP 임베딩 완료")

                    pbar.update(1)

            print("파이프라인 완료")
            print(f"출력: {self.embeddings_path}")

        except Exception as e:
            print(f"파이프라인 실패: {e}")
            raise


def main() -> None:
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="AAC 카드 임베딩 파이프라인")
    parser.add_argument(
        "--steps",
        nargs="+",
        type=str,
        default=["1", "2"],
        help="실행할 단계 (1: 필터링, 2: 임베딩)",
    )
    parser.add_argument("--no-confirm", action="store_true", help="필터링 확인 생략")
    parser.add_argument("--overwrite", action="store_true", help="기존 파일 덮어쓰기")

    args = parser.parse_args()

    config = DATASET_CONFIG.copy()
    if args.overwrite:
        config["overwrite_mode"] = True

    valid_steps = ["1", "2"]
    args.steps = [s for s in args.steps if s in valid_steps]

    if not args.steps:
        print("유효한 단계 없음. 사용 가능: 1 (필터링), 2 (임베딩)")
        return

    pipeline = DataPreparationPipeline(config)
    pipeline.run_pipeline(
        steps=args.steps,
        confirm_filter=not args.no_confirm,
    )


if __name__ == "__main__":
    main()
