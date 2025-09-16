import os
import sys
import json
from pathlib import Path
from typing import List, Optional, Tuple, Dict
from tqdm import tqdm

from dataset_config import DATASET_CONFIG

from data_source.image_filter import ImageFilter
from data_source.embeddings import CLIPEncoder
from data_source.clustering import Clusterer
from data_source.cluster_tagger import ClusterTagger


class DataPreparationPipeline:
    """AAC 클러스터링 데이터 준비 파이프라인"""
    
    def __init__(self, config: dict):
        self.config = config
        self._validate_config()
        self._setup_paths()

    def _validate_config(self) -> None:
        """필수 설정 검증"""
        required_keys = ['images_folder', 'output_folder']
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"필수 설정 누락: {key}")

    def _setup_paths(self) -> None:
        """경로 설정"""
        self.images_folder = Path(self.config['images_folder'])
        self.output_folder = Path(self.config['output_folder'])
        self.output_folder.mkdir(parents=True, exist_ok=True)

        self.embeddings_path = self.output_folder / 'embeddings.json'
        self.clustering_path = self.output_folder / 'clustering_results.json'
        self.cluster_tags_path = self.output_folder / 'cluster_tags.json'

    def step1_filter_images(self, confirm: Optional[bool] = None) -> int:
        """부적절한 이미지 필터링"""
        if confirm is None:
            confirm = self.config.get('filter_confirm', True)

        filter_tool = ImageFilter(str(self.images_folder))
        return filter_tool.filter_images(confirm=confirm)

    def step2_generate_embeddings(self) -> Tuple[List[str], Tuple[int, int], Tuple[int, int]]:
        """CLIP 임베딩 생성"""
        model_name = self.config.get('clip_model', 'openai/clip-vit-base-patch32')
        encoder = CLIPEncoder(model_name=model_name, config=self.config)
        return encoder.process_and_save(str(self.images_folder), str(self.embeddings_path))

    def step3_perform_clustering(self, visualize: Optional[bool] = None) -> dict:
        """계층적 Spherical K-means 클러스터링"""
        if visualize is None:
            visualize = self.config.get('visualize_clusters', True)

        clusterer = Clusterer(embeddings_path=str(self.embeddings_path), config=self.config)
        return clusterer.cluster_and_save(
            n_clusters=self.config.get('n_clusters'),
            output_folder=str(self.output_folder),
            visualize=visualize
        )

    def step4_tag_clusters(self) -> Dict[int, List[str]]:
        """클러스터 태깅"""
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
        """파이프라인 실행"""
        if steps is None:
            steps = ['1', '2', '3', '4']

        step_methods = {
            '1': self.step1_filter_images,
            '2': self.step2_generate_embeddings,
            '3': self.step3_perform_clustering,
            '4': self.step4_tag_clusters
        }

        try:
            print("AAC 클러스터링 파이프라인 시작")
            
            with tqdm(total=len(steps), desc="진행") as pbar:
                for step in steps:
                    if step not in step_methods:
                        print(f"잘못된 단계: {step}")
                        continue

                    if step == '1':
                        result = step_methods[step](confirm_filter)
                        print(f"단계 1: {result}개 이미지 필터링")
                    elif step == '2':
                        filenames, img_emb, txt_emb = step_methods[step]()
                        print(f"단계 2: {len(filenames)}개 이미지 인코딩")
                    elif step == '3':
                        cluster_results = step_methods[step](visualize)
                        print(f"단계 3: {cluster_results['n_clusters']}개 클러스터 생성")
                    elif step == '4':
                        cluster_tags = step_methods[step]()
                        tagged_count = sum(1 for tags in cluster_tags.values() if tags)
                        print(f"단계 4: {tagged_count}개 클러스터 태깅")

                    pbar.update(1)

            print("파이프라인 완료")
            print(f"출력: {self.output_folder}")

        except Exception as e:
            print(f"파이프라인 실패: {e}")
            raise


def main() -> None:
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description='AAC 클러스터링 파이프라인')
    parser.add_argument('--steps', nargs='+', type=str, default=['1', '2', '3', '4'],
                       help='실행할 단계 (1-4)')
    parser.add_argument('--no-confirm', action='store_true', help='확인 생략')
    parser.add_argument('--no-visualize', action='store_true', help='시각화 생략')
    parser.add_argument('--overwrite', action='store_true', help='기존 파일 덮어쓰기')

    args = parser.parse_args()

    config = DATASET_CONFIG.copy()
    if args.overwrite:
        config['overwrite_mode'] = True

    valid_steps = ['1', '2', '3', '4']
    args.steps = [s for s in args.steps if s in valid_steps]
    
    if not args.steps:
        print("유효한 단계 없음. 사용 가능: 1, 2, 3, 4")
        return

    pipeline = DataPreparationPipeline(config)
    pipeline.run_pipeline(
        steps=args.steps,
        confirm_filter=not args.no_confirm,
        visualize=not args.no_visualize
    )


if __name__ == "__main__":
    main()