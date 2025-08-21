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
from data.data_source.schema import DatasetSchema
from data.data_source.cluster_tagger import ClusterTagger
from data.data_source.persona_card_selector import PersonaCardSelector
from data.data_source.dataset_generator import DatasetGenerator


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
        self.cluster_tags_path = self.output_folder / 'cluster_tags.json'
        self.enhanced_persona_path = self.output_folder / 'enhanced_persona.json'
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
        encoder = CLIPEncoder(model_name=model_name, config=self.config)
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

        clusterer = Clusterer(embeddings_path=str(self.embeddings_path), config=self.config)
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

    def step5_tag_clusters(self) -> Dict[int, List[str]]:
        print("\n" + "="*50)
        print("STEP 5: Tagging clusters with topics")
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

    def step6_assign_persona_categories(self, cluster_tags: Optional[Dict[int, List[str]]] = None) -> None:
        print("\n" + "="*50)
        print("STEP 6: Assigning persona preferred categories")
        print("="*50)

        with open(self.config['persona_json_path'], 'r', encoding='utf-8') as f:
            personas = json.load(f)

        if not cluster_tags:
            if not self.cluster_tags_path.exists():
                raise FileNotFoundError(
                    f"Cluster tags file not found: {self.cluster_tags_path}\n"
                    f"Please run step 5 first to generate cluster tags."
                )

            print(f"Loading cluster tags from {self.cluster_tags_path}")
            with open(self.cluster_tags_path, 'r', encoding='utf-8') as f:
                cluster_tags_raw = json.load(f)
                cluster_tags = {int(k): v for k, v in cluster_tags_raw.items()}

        if not cluster_tags:
            raise ValueError(
                "No cluster tags available. Cannot assign preferred categories.\n"
                "Please run step 5 first to generate cluster tags."
            )

        tagger = ClusterTagger(
            embeddings_path=str(self.embeddings_path),
            clustering_results_path=str(self.clustering_path),
            images_folder=str(self.images_folder),
            config=self.config
        )

        enhanced_personas = tagger.assign_preferred_categories(
            cluster_tags,
            personas,
            self.config.get('topic_similarity_threshold', 0.75)
        )

        with open(str(self.enhanced_persona_path), 'w', encoding='utf-8') as f:
            json.dump(enhanced_personas, f, ensure_ascii=False, indent=2)

        print(f"Enhanced personas saved to {self.enhanced_persona_path}")

        total_categories = sum(len(p['persona']['preferred_category_types']) for p in enhanced_personas)
        print(f"Total preferred categories assigned: {total_categories}")
        print(f"Average per persona: {total_categories/len(enhanced_personas):.1f}")

    def step7_generate_persona_card_combinations(self) -> None:
        print("\n" + "="*50)
        print("STEP 7: Generating persona-based card combinations")
        print("="*50)

        if not self.cluster_tags_path.exists():
            print("Warning: No cluster tags found, creating empty tags...")
            with open(str(self.cluster_tags_path), 'w', encoding='utf-8') as f:
                json.dump({}, f)

        selector = PersonaCardSelector(
            embeddings_path=str(self.embeddings_path),
            clustering_results_path=str(self.clustering_path),
            cluster_tags_path=str(self.cluster_tags_path),
            config=self.config
        )

        selector.update_dataset_with_personas(
            dataset_path=str(self.dataset_path),
            output_path=str(self.dataset_with_cards_path),
            personas_path=str(self.enhanced_persona_path)
        )

    def step8_generate_final_dataset(self, start_idx: int = 0, end_idx: Optional[int] = None) -> None:
        print("\n" + "="*50)
        print("STEP 8: Generating final dataset with OpenAI")
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

    def run_pipeline(self, steps: Optional[List[str]] = None, confirm_filter: Optional[bool] = None,
                    visualize: Optional[bool] = None, openai_start_idx: int = 0,
                    openai_end_idx: Optional[int] = None) -> None:
        if steps is None:
            steps = ['1', '2', '3', '4', '5', '6', '7', '8']

        step_methods = {
            '1': self.step1_filter_images,
            '2': self.step2_generate_embeddings,
            '3': self.step3_perform_clustering,
            '4': self.step4_generate_dataset_schema,
            '5': self.step5_tag_clusters,
            '6': self.step6_assign_persona_categories,
            '7': self.step7_generate_persona_card_combinations,
            '8': self.step8_generate_final_dataset
        }

        try:
            print("Starting AAC Dataset Preparation Pipeline")
            print(f"Configuration: {self.config}")
            print(f"Running steps: {steps}")

            cluster_tags = {}

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
                        total_samples = step_methods[step]()
                        print(f"Step 4 completed: {total_samples} samples created")
                    elif step == '5':
                        cluster_tags = step_methods[step]()
                        print(f"Step 5 completed: {len(cluster_tags)} clusters tagged")
                    elif step == '6':
                        step_methods[step]()
                        print("Step 6 completed: Persona categories assigned")
                    elif step == '7':
                        step_methods[step]()
                        print("Step 7 completed: Persona-based card combinations generated")
                    elif step == '8':
                        step_methods[step](
                            start_idx=openai_start_idx,
                            end_idx=openai_end_idx
                        )
                        print("Step 8 completed: Final dataset generated")

                    pbar.update(1)

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
    parser.add_argument('--steps', nargs='+', type=str,
                       default=['1', '2', '3', '4', '5', '6', '7', '8'],
                       help='실행할 단계 (1-8) 예: --steps 1 2 3 5 6 7')
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

    if '8' in args.steps and config.get('skip_openai', False):
        print("Warning: Step 8 requested but skip_openai is True in config")
        response = input("Continue with OpenAI processing? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Removing step 8 from execution")
            args.steps = [s for s in args.steps if s != '8']

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
