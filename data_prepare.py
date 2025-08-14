import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from config.dataset_config import DATASET_CONFIG

from data.image_filter import ImageFilter
from data.embeddings import CLIPEncoder
from data.clustering import Clusterer
from data.schema import DatasetSchema
from data.card_generator import CardCombinationGenerator
from data.dataset_generator import DatasetGenerator


class DataPreparationPipeline:
    def __init__(self, config: dict):
        self.config = config
        self._validate_config()
        self._setup_paths()

    def _validate_config(self) -> None:
        required_keys = [
            'images_folder', 'persona_json_path', 'output_folder',
            'samples_per_persona', 'n_clusters'
        ]
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required config key: {key}")

    def _setup_paths(self) -> None:
        self.images_folder = Path(self.config['images_folder'])
        self.output_folder = Path(self.config['output_folder'])
        self.output_folder.mkdir(parents=True, exist_ok=True)

        self.embeddings_path = self.output_folder / 'embeddings.json'
        self.clustering_path = self.output_folder / 'clustering_results.json'
        self.dataset_path = self.output_folder / 'dataset.json'
        self.dataset_with_cards_path = self.output_folder / 'dataset_with_cards.json'
        self.final_dataset_path = self.output_folder / 'dataset_completed.json'

    def step1_filter_images(self, confirm: Optional[bool] = None) -> int:
        print("\n" + "="*50)
        print("STEP 1: Filtering inappropriate images")
        print("="*50)

        if confirm is None:
            confirm = self.config.get('filter_confirm', True)

        filter_tool = ImageFilter(str(self.images_folder))
        return filter_tool.filter_images(confirm=confirm)

    def step2_generate_embeddings(self) -> Tuple[List[str], Tuple[int, int], Tuple[int, int]]:
        print("\n" + "="*50)
        print("STEP 2: Generating CLIP embeddings")
        print("="*50)

        model_name = self.config.get('clip_model', 'openai/clip-vit-base-patch32')
        encoder = CLIPEncoder(model_name=model_name)
        return encoder.process_and_save(
            str(self.images_folder),
            str(self.embeddings_path)
        )

    def step3_perform_clustering(self, visualize: Optional[bool] = None) -> dict:
        print("\n" + "="*50)
        print("STEP 3: Performing K-means clustering")
        print("="*50)

        if visualize is None:
            visualize = self.config.get('visualize_clusters', True)

        clusterer = Clusterer(embeddings_path=str(self.embeddings_path))
        return clusterer.cluster_and_save(
            n_clusters=self.config['n_clusters'],
            output_folder=str(self.output_folder),
            visualize=visualize
        )

    def step4_generate_dataset_schema(self) -> int:
        print("\n" + "="*50)
        print("STEP 4: Generating dataset schema")
        print("="*50)

        return DatasetSchema.generate_dataset(
            persona_json_path=self.config['persona_json_path'],
            output_path=str(self.dataset_path),
            samples_per_persona=self.config['samples_per_persona']
        )

    def step5_generate_card_combinations(self) -> None:
        print("\n" + "="*50)
        print("STEP 5: Generating card combinations")
        print("="*50)

        generator = CardCombinationGenerator(
            embeddings_path=str(self.embeddings_path),
            clustering_results_path=str(self.clustering_path),
            similarity_threshold=self.config.get('similarity_threshold', 0.5),
            card_min_similarity=self.config.get('card_min_similarity', 0.3),
            config=self.config
        )

        generator.update_dataset(
            dataset_path=str(self.dataset_path),
            output_path=str(self.dataset_with_cards_path)
        )

    def step6_generate_final_dataset(self, start_idx: int = 0, end_idx: Optional[int] = None) -> None:
        print("\n" + "="*50)
        print("STEP 6: Generating final dataset with OpenAI")
        print("="*50)

        save_interval = self.config.get('save_interval', 10)

        generator = DatasetGenerator(
            dataset_path=str(self.dataset_with_cards_path),
            images_folder=str(self.images_folder),
            output_path=str(self.final_dataset_path),
            config=self.config
        )

        if self.config.get('show_sample', True):
            generator.print_sample(0)

        generator.process_dataset(
            start_idx=start_idx,
            end_idx=end_idx,
            save_interval=save_interval
        )

    def run_pipeline(self, steps: Optional[List[int]] = None, confirm_filter: Optional[bool] = None,
                    visualize: Optional[bool] = None, openai_start_idx: int = 0,
                    openai_end_idx: Optional[int] = None) -> None:
        if steps is None:
            steps = [1, 2, 3, 4, 5, 6]

        step_methods = {
            1: self.step1_filter_images,
            2: self.step2_generate_embeddings,
            3: self.step3_perform_clustering,
            4: self.step4_generate_dataset_schema,
            5: self.step5_generate_card_combinations,
            6: self.step6_generate_final_dataset
        }

        try:
            print("Starting AAC Dataset Preparation Pipeline")
            print(f"Configuration: {self.config}")
            print(f"Running steps: {steps}")

            for step in steps:
                if step not in step_methods:
                    print(f"Invalid step: {step}")
                    continue

                print(f"\nRunning step {step}...")

                if step == 1:
                    result = step_methods[step](confirm=confirm_filter)
                    print(f"Step 1 completed: {result} images filtered")
                elif step == 2:
                    filenames, img_emb, txt_emb = step_methods[step]()
                    print(f"Step 2 completed: {len(filenames)} images encoded")
                elif step == 3:
                    cluster_results = step_methods[step](visualize=visualize)
                    print(f"Step 3 completed: {cluster_results['n_clusters']} clusters created")
                elif step == 4:
                    total_samples = step_methods[step]()
                    print(f"Step 4 completed: {total_samples} samples created")
                elif step == 5:
                    step_methods[step]()
                    print("Step 5 completed: Card combinations generated")
                elif step == 6:
                    step_methods[step](
                        start_idx=openai_start_idx,
                        end_idx=openai_end_idx
                    )
                    print("Step 6 completed: Final dataset generated")

            print("\n" + "="*50)
            print("PIPELINE COMPLETED SUCCESSFULLY")
            print("="*50)
            print(f"Final outputs saved to: {self.output_folder}")

        except Exception as e:
            print(f"\nPipeline failed: {e}")
            raise


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description='AAC 데이터셋 준비 파이프라인')
    parser.add_argument('--steps', nargs='+', type=int, default=[1, 2, 3, 4, 5, 6],
                       help='실행할 단계 (1-6) 예: --steps 1 2 3')
    parser.add_argument('--no-confirm', action='store_true',
                       help='확인 과정 건너뛰기')
    parser.add_argument('--no-visualize', action='store_true',
                       help='시각화 건너뛰기')
    parser.add_argument('--openai-start', type=int, default=0,
                       help='OpenAI 처리 시작 인덱스')
    parser.add_argument('--openai-end', type=int, default=None,
                       help='OpenAI 처리 종료 인덱스')
    parser.add_argument('--overwrite', action='store_true',
                       help='기존 데이터 덮어쓰기')

    args = parser.parse_args()

    config = DATASET_CONFIG.copy()
    if args.overwrite:
        config['overwrite_mode'] = True

    if 6 in args.steps and config.get('skip_openai', False):
        print("Warning: Step 6 requested but skip_openai is True in config")
        response = input("Continue with OpenAI processing? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Removing step 6 from execution")
            args.steps = [s for s in args.steps if s != 6]

    pipeline = DataPreparationPipeline(config)

    pipeline.run_pipeline(
        steps=args.steps,
        confirm_filter=not args.no_confirm,
        visualize=not args.no_visualize,
        openai_start_idx=args.openai_start,
        openai_end_idx=args.openai_end
    )


if __name__ == "__main__":
    main()
