# AAC Card Interpretation System

An end-to-end system for AAC (Augmentative and Alternative Communication) card interpretation using AI. This project includes dataset preparation, model training, and real-time card interpretation capabilities.

## Project Overview

This system provides:
- **Dataset Preparation**: Automated pipeline for creating AAC datasets with CLIP embeddings and AI-generated interpretations
- **Model Training**: (Coming Soon) Training pipelines for AAC interpretation models  
- **Inference System**: (Coming Soon) Real-time AAC card sequence interpretation

## Current Status: Dataset Preparation Phase

Currently implementing the dataset preparation pipeline that processes AAC card images and generates training data.

## Project Structure

```
project/
├── config/                # Configuration files
│   ├── __init__.py
│   └── dataset_config.py  # Dataset preparation settings
├── data_src/              # Core modules
│   ├── image_filter.py    # Image filtering and cleanup
│   ├── embeddings.py      # CLIP encoding
│   ├── clustering.py      # K-means clustering
│   ├── schema.py          # Dataset schema generation
│   ├── card_generator.py  # Card combination generation
│   └── dataset_generator.py # AI-powered dataset completion
├── data_prepare.py        # Dataset preparation pipeline
└── README.md
```

## Setup

1. Install dependencies:
```bash
pip install torch transformers sklearn matplotlib tqdm openai python-dotenv pillow huggingface-hub
```

2. Create `.env` file:
```
HUGGINGFACE_TOKEN=your_token_here
OPENAI_API_KEY=your_openai_key_here
```

3. Prepare data structure:
```
data/
├── images/               # AAC card images (PNG format)
├── persona.json         # Persona definitions
└── processed/           # Output directory (auto-created)
```

## Usage

### Dataset Preparation
```bash
python data_prepare.py
```

### Custom Configuration
Edit `config/dataset_config.py` to adjust settings:
```python
DATASET_CONFIG = {
    'images_folder': 'data/images',
    'samples_per_persona': 200,
    'n_clusters': 96,
    'skip_openai': False  # Set True for testing without AI
}
```

### Advanced Usage
Modify `data_prepare.py` to run specific pipeline steps:
```python
# Run only steps 1-3 (skip AI processing)
pipeline.run_partial_pipeline(
    steps=[1, 2, 3],
    confirm_filter=True,
    visualize=True
)
```

## Dataset Pipeline Steps

1. **Image Filtering**: Remove inappropriate content, duplicates, and invalid files
2. **CLIP Encoding**: Generate image and text embeddings using CLIP
3. **Clustering**: Group similar cards using K-means clustering
4. **Schema Generation**: Create dataset structure with personas
5. **Card Combinations**: Generate meaningful card sequences
6. **AI Completion**: Use OpenAI to generate contexts and interpretations

## Image Requirements

Images should be named as: `{id}_{keyword}.png`
- Example: `001_apple.png`, `002_happy.png`
- Keywords will be used for text embedding generation
- Invalid formats will be filtered out automatically

## Roadmap

### Phase 1: Dataset Preparation ✅ (Current)
- [x] Image filtering and preprocessing
- [x] CLIP-based embedding generation
- [x] Intelligent card combination generation
- [x] AI-powered context and interpretation generation

### Phase 2: Model Training (Coming Soon)
- [ ] Training pipeline for sequence interpretation models
- [ ] Model evaluation and validation
- [ ] Hyperparameter optimization
- [ ] Model export and optimization

### Phase 3: Inference System (Coming Soon)
- [ ] Real-time card sequence interpretation
- [ ] Web API for integration
- [ ] Mobile app interface
- [ ] Performance monitoring

## Contributing

This is an early-stage project. The codebase will expand significantly as we add training and inference capabilities. 

Current focus areas:
- Dataset quality improvement
- Pipeline optimization
- Configuration management

## Output Files

The dataset preparation generates:
- `embeddings.json`: CLIP embeddings for all images
- `clustering_results.json`: Cluster assignments and metadata
- `dataset.json`: Basic dataset structure
- `dataset_with_cards.json`: Dataset with card combinations
- `dataset_completed.json`: Final dataset with AI-generated content
- `cluster_visualization.png`: Cluster visualization plots

## Performance Notes

- CLIP encoding: ~1-2 seconds per image on GPU
- Clustering: Fast after embeddings are generated
- OpenAI processing: ~3-5 seconds per sample (rate limited)
- Memory usage scales with number of images

## License

[To be determined]