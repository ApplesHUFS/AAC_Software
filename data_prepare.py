import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "data_src"))

from config import DATASET_CONFIG

from image_filter import ImageFilter
from embeddings import CLIPEncoder
from clustering import Clusterer
from schema import DatasetSchema
from card_generator import CardCombinationGenerator
from dataset_generator import DatasetGenerator


class DataPreparationPipeline:
    def __init__(self, config: dict):
        self.config = config
        self._validate_config()
        self._setup_paths()
    
    def _validate_config(self):
        required_keys = [
            'images_folder', 'persona_json_path', 'output_folder',
            'samples_per_persona', 'n_clusters', 'similarity_range'
        ]
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required config key: {key}")
    
    def _setup_paths(self):
        self.images_folder = Path(self.config['images_folder'])
        self.output_folder = Path(self.config['output_folder'])
        self.output_folder.mkdir(parents=True, exist_ok=True)
        
        self.embeddings_path = self.output_folder / 'embeddings.json'
        self.clustering_path = self.output_folder / 'clustering_results.json'
        self.dataset_path = self.output_folder / 'dataset.json'
        self.dataset_with_cards_path = self.output_folder / 'dataset_with_cards.json'
        self.final_dataset_path = self.output_folder / 'dataset_completed.json'
    
    def step1_filter_images(self, confirm: bool = True) -> int:
        print("\n" + "="*50)
        print("STEP 1: Filtering inappropriate images")
        print("="*50)
        
        filter_tool = ImageFilter(str(self.images_folder))
        return filter_tool.filter_images(confirm=confirm)
    
    def step2_generate_embeddings(self) -> tuple:
        print("\n" + "="*50)
        print("STEP 2: Generating CLIP embeddings")
        print("="*50)
        
        encoder = CLIPEncoder()
        return encoder.process_and_save(
            str(self.images_folder), 
            str(self.embeddings_path)
        )
    
    def step3_perform_clustering(self, visualize: bool = True) -> dict:
        print("\n" + "="*50)
        print("STEP 3: Performing K-means clustering")
        print("="*50)
        
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
    
    def step5_generate_card_combinations(self):
        print("\n" + "="*50)
        print("STEP 5: Generating card combinations")
        print("="*50)
        
        generator = CardCombinationGenerator(
            embeddings_path=str(self.embeddings_path),
            clustering_results_path=str(self.clustering_path),
            similarity_range=tuple(self.config['similarity_range'])
        )
        
        generator.update_dataset(
            dataset_path=str(self.dataset_path),
            output_path=str(self.dataset_with_cards_path)
        )
        
        if self.config.get('analyze_diversity', True):
            generator.analyze_diversity(n_samples=100)
    
    def step6_generate_final_dataset(self, start_idx: int = 0, end_idx: int = None, 
                                   save_interval: int = 10):
        print("\n" + "="*50)
        print("STEP 6: Generating final dataset with OpenAI")
        print("="*50)
        
        generator = DatasetGenerator(
            dataset_path=str(self.dataset_with_cards_path),
            images_folder=str(self.images_folder),
            output_path=str(self.final_dataset_path)
        )
        
        if self.config.get('show_sample', True):
            generator.print_sample(0)
        
        generator.process_dataset(
            start_idx=start_idx,
            end_idx=end_idx,
            save_interval=save_interval
        )
    
    def run_full_pipeline(self, confirm_filter: bool = True, visualize: bool = True,
                         openai_start_idx: int = 0, openai_end_idx: int = None):
        try:
            print("Starting AAC Dataset Preparation Pipeline")
            print(f"Configuration: {self.config}")
            
            # Step 1: Filter images
            filtered_count = self.step1_filter_images(confirm=confirm_filter)
            print(f"Step 1 completed: {filtered_count} images filtered")
            
            # Step 2: Generate embeddings
            filenames, img_emb, txt_emb = self.step2_generate_embeddings()
            print(f"Step 2 completed: {len(filenames)} images encoded")
            
            # Step 3: Perform clustering
            cluster_results = self.step3_perform_clustering(visualize=visualize)
            print(f"Step 3 completed: {cluster_results['n_clusters']} clusters created")
            
            # Step 4: Generate dataset schema
            total_samples = self.step4_generate_dataset_schema()
            print(f"Step 4 completed: {total_samples} samples created")
            
            # Step 5: Generate card combinations
            self.step5_generate_card_combinations()
            print("Step 5 completed: Card combinations generated")
            
            # Step 6: Generate final dataset with OpenAI
            if self.config.get('skip_openai', False):
                print("Step 6 skipped: OpenAI processing disabled")
            else:
                self.step6_generate_final_dataset(
                    start_idx=openai_start_idx,
                    end_idx=openai_end_idx
                )
                print("Step 6 completed: Final dataset generated")
            
            print("\n" + "="*50)
            print("PIPELINE COMPLETED SUCCESSFULLY")
            print("="*50)
            print(f"Final outputs saved to: {self.output_folder}")
            
        except Exception as e:
            print(f"\nPipeline failed at step: {e}")
            raise
    
    def run_partial_pipeline(self, steps: list, **kwargs):
        step_methods = {
            1: self.step1_filter_images,
            2: self.step2_generate_embeddings, 
            3: self.step3_perform_clustering,
            4: self.step4_generate_dataset_schema,
            5: self.step5_generate_card_combinations,
            6: self.step6_generate_final_dataset
        }
        
        for step in steps:
            if step in step_methods:
                print(f"\nRunning step {step}...")
                if step == 1:
                    step_methods[step](confirm=kwargs.get('confirm_filter', True))
                elif step == 3:
                    step_methods[step](visualize=kwargs.get('visualize', True))
                elif step == 6:
                    step_methods[step](
                        start_idx=kwargs.get('openai_start_idx', 0),
                        end_idx=kwargs.get('openai_end_idx', None)
                    )
                else:
                    step_methods[step]()
            else:
                print(f"Invalid step: {step}")


def main():
    pipeline = DataPreparationPipeline(DATASET_CONFIG)
    
    pipeline.run_full_pipeline(
        confirm_filter=True,
        visualize=True,
        openai_start_idx=0,
        openai_end_idx=None
    )


if __name__ == "__main__":
    main()