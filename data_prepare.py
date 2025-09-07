import os
import sys
import json
from pathlib import Path
from typing import List, Optional, Tuple, Dict
from tqdm import tqdm

from data.dataset_config import DATASET_CONFIG

from data.data_source.image_filter import ImageFilter
from data.data_source.embeddings import CLIPEncoder
from data.data_source.clustering import Clusterer
from data.data_source.cluster_tagger import ClusterTagger


class DataPreparationPipeline:
    """AAC 이미지 클러스터링을 위한 데이터 준비 파이프라인
    
    이미지 필터링, 임베딩 생성, 클러스터링, 클러스터 태깅까지의 과정을 수행합니다.
    백엔드 서비스에서 사용할 클러스터 정보를 생성합니다.
    """
    
    def __init__(self, config: dict):
        """파이프라인 초기화
        
        Args:
            config: 설정 딕셔너리
        """
        self.config = config
        self._validate_config()
        self._setup_paths()

    def _validate_config(self) -> None:
        """필수 설정 키 검증"""
        required_keys = [
            'images_folder', 'output_folder', 'n_clusters'
        ]
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required config key: {key}")

    def _setup_paths(self) -> None:
        """파일 경로 설정"""
        self.images_folder = Path(self.config['images_folder'])
        self.output_folder = Path(self.config['output_folder'])
        self.output_folder.mkdir(parents=True, exist_ok=True)

        # 백엔드에서 사용할 파일들만 설정
        self.embeddings_path = self.output_folder / 'embeddings.json'
        self.clustering_path = self.output_folder / 'clustering_results.json'
        self.cluster_tags_path = self.output_folder / 'cluster_tags.json'

    def step1_filter_images(self, confirm: Optional[bool] = None) -> int:
        """부적절한 이미지 필터링
        
        Args:
            confirm: 필터링 확인 여부
            
        Returns:
            필터링된 이미지 수
        """
        print("\n" + "="*50)
        print("STEP 1: Filtering inappropriate images")
        print("="*50)

        if confirm is None:
            confirm = self.config.get('filter_confirm', True)

        filter_tool = ImageFilter(str(self.images_folder))
        return filter_tool.filter_images(confirm=confirm)

    def step2_generate_embeddings(self) -> Tuple[List[str], Tuple[int, int], Tuple[int, int]]:
        """CLIP 임베딩 생성
        
        이미지와 텍스트 임베딩을 생성하여 저장합니다.
        
        Returns:
            파일명 리스트, 이미지 임베딩 차원, 텍스트 임베딩 차원
        """
        print("\n" + "="*50)
        print("STEP 2: Generating CLIP embeddings")
        print("="*50)

        model_name = self.config.get('clip_model', 'openai/clip-vit-base-patch32')
        encoder = CLIPEncoder(model_name=model_name, config=self.config)
        return encoder.process_and_save(
            str(self.images_folder),
            str(self.embeddings_path)
        )

    def step3_perform_clustering(self, visualize: Optional[bool] = None) -> dict:
        """K-means 클러스터링 수행
        
        임베딩을 기반으로 이미지들을 클러스터링합니다.
        
        Args:
            visualize: 클러스터 시각화 여부
            
        Returns:
            클러스터링 결과 딕셔너리
        """
        print("\n" + "="*50)
        print("STEP 3: Performing K-means clustering")
        print("="*50)

        if visualize is None:
            visualize = self.config.get('visualize_clusters', True)

        clusterer = Clusterer(embeddings_path=str(self.embeddings_path), config=self.config)
        return clusterer.cluster_and_save(
            n_clusters=self.config['n_clusters'],
            output_folder=str(self.output_folder),
            visualize=visualize
        )

    def step4_tag_clusters(self) -> Dict[int, List[str]]:
        """클러스터에 주제 태그 할당
        
        각 클러스터의 대표 이미지들을 분석하여 주제 태그를 생성합니다.
        
        Returns:
            클러스터 ID와 태그 리스트의 딕셔너리
        """
        print("\n" + "="*50)
        print("STEP 4: Tagging clusters with topics")
        print("="*50)

        tagger = ClusterTagger(
            embeddings_path=str(self.embeddings_path),
            clustering_results_path=str(self.clustering_path),
            images_folder=str(self.images_folder),
            config=self.config
        )

        cluster_tags = tagger.tag_all_clusters()
        tagger.save_cluster_tags(cluster_tags, str(self.cluster_tags_path))

        return cluster_tags

    def run_pipeline(self, steps: Optional[List[str]] = None, confirm_filter: Optional[bool] = None,
                    visualize: Optional[bool] = None) -> None:
        """파이프라인 실행
        
        Args:
            steps: 실행할 단계 리스트 (1-4)
            confirm_filter: 이미지 필터링 확인 여부
            visualize: 클러스터 시각화 여부
        """
        if steps is None:
            steps = ['1', '2', '3', '4']

        step_methods = {
            '1': self.step1_filter_images,
            '2': self.step2_generate_embeddings,
            '3': self.step3_perform_clustering,
            '4': self.step4_tag_clusters
        }

        try:
            print("Starting AAC Clustering Pipeline")
            print(f"Configuration: {self.config}")
            print(f"Running steps: {steps}")

            with tqdm(total=len(steps), desc="Pipeline Progress") as pbar:
                for step in steps:
                    if step not in step_methods:
                        print(f"Invalid step: {step}")
                        continue

                    pbar.set_description(f"Running step {step}")

                    if step == '1':
                        result = step_methods[step](confirm=confirm_filter)
                        print(f"Step 1 completed: {result} images filtered")
                    elif step == '2':
                        filenames, img_emb, txt_emb = step_methods[step]()
                        print(f"Step 2 completed: {len(filenames)} images encoded")
                    elif step == '3':
                        cluster_results = step_methods[step](visualize=visualize)
                        print(f"Step 3 completed: {cluster_results['n_clusters']} clusters created")
                    elif step == '4':
                        cluster_tags = step_methods[step]()
                        print(f"Step 4 completed: {len(cluster_tags)} clusters tagged")

                    pbar.update(1)

            print("\n" + "="*50)
            print("CLUSTERING PIPELINE COMPLETED SUCCESSFULLY")
            print("="*50)
            print(f"Outputs saved to: {self.output_folder}")
            print(f"Generated files:")
            print(f"  - {self.embeddings_path}")
            print(f"  - {self.clustering_path}")
            print(f"  - {self.cluster_tags_path}")

        except Exception as e:
            print(f"\nPipeline failed: {e}")
            raise


def main() -> None:
    """메인 함수 - 명령행 인터페이스 제공"""
    import argparse

    parser = argparse.ArgumentParser(description='AAC 이미지 클러스터링 파이프라인')
    parser.add_argument('--steps', nargs='+', type=str,
                       default=['1', '2', '3', '4'],
                       help='실행할 단계 (1-4) 예: --steps 1 2 3 4')
    parser.add_argument('--no-confirm', action='store_true',
                       help='확인 과정 건너뛰기')
    parser.add_argument('--no-visualize', action='store_true',
                       help='시각화 건너뛰기')
    parser.add_argument('--overwrite', action='store_true',
                       help='기존 데이터 덮어쓰기')

    args = parser.parse_args()

    # 설정 로드 및 수정
    config = DATASET_CONFIG.copy()
    if args.overwrite:
        config['overwrite_mode'] = True

    # 유효하지 않은 단계 필터링
    valid_steps = ['1', '2', '3', '4']
    args.steps = [s for s in args.steps if s in valid_steps]
    
    if not args.steps:
        print("No valid steps specified. Available steps: 1, 2, 3, 4")
        return

    # 파이프라인 실행
    pipeline = DataPreparationPipeline(config)
    pipeline.run_pipeline(
        steps=args.steps,
        confirm_filter=not args.no_confirm,
        visualize=not args.no_visualize
    )


if __name__ == "__main__":
    main()