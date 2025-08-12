import torch
import os
import json
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Tuple, List, Optional
from transformers import AutoProcessor, AutoModel
from tqdm import tqdm
from dotenv import load_dotenv
import huggingface_hub


class CLIPEncoder:
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32", config: Optional[dict] = None):
        load_dotenv()

        self.config = config or {}

        hf_token = os.getenv("HUGGINGFACE_TOKEN")
        if hf_token:
            huggingface_hub.login(token=hf_token)

        device_setting = self.config.get('device', 'auto')
        if device_setting == 'auto':
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device_setting

        print(f"Using device: {self.device}")

        self.model = AutoModel.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16,
            attn_implementation="sdpa"
        ).to(self.device)

        self.processor = AutoProcessor.from_pretrained(model_name)

    def _process_image(self, image_path: str) -> Image.Image:
        image = Image.open(image_path)
        if image.mode == 'P' and 'transparency' in image.info:
            image = image.convert('RGBA')
        return image.convert("RGB")

    def _extract_text(self, filename: str) -> str:
        stem = Path(filename).stem
        if '_' not in stem:
            return ""
        return stem.split('_', 1)[1]

    def encode_single(self, image_path: str, text: str) -> Tuple[np.ndarray, np.ndarray]:
        image = self._process_image(image_path)

        inputs = self.processor(
            text=[text],
            images=image,
            return_tensors="pt",
            padding=True
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)

            image_embedding = outputs.image_embeds / outputs.image_embeds.norm(dim=-1, keepdim=True)
            text_embedding = outputs.text_embeds / outputs.text_embeds.norm(dim=-1, keepdim=True)

            return (
                image_embedding.float().cpu().numpy().flatten(),
                text_embedding.float().cpu().numpy().flatten()
            )

    def encode_folder(self, folder_path: str) -> Tuple[List[str], np.ndarray, np.ndarray]:
        folder_path = Path(folder_path)
        filenames = []
        image_embeddings = []
        text_embeddings = []

        png_files = list(folder_path.glob("*.png"))

        for file_path in tqdm(png_files, desc="Encoding images"):
            filename = file_path.name
            text = self._extract_text(filename)

            if not text:
                continue

            try:
                img_emb, txt_emb = self.encode_single(file_path, text)
                filenames.append(filename)
                image_embeddings.append(img_emb)
                text_embeddings.append(txt_emb)
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                continue

        image_embeddings_array = np.array(image_embeddings)
        text_embeddings_array = np.array(text_embeddings)

        print(f"Encoded {len(filenames)} files")
        return filenames, image_embeddings_array, text_embeddings_array

    def save_embeddings(self, filenames: List[str], image_embeddings: np.ndarray,
                       text_embeddings: np.ndarray, output_path: str) -> None:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        embedding_data = {
            'filenames': filenames,
            'image_embeddings': image_embeddings.tolist(),
            'text_embeddings': text_embeddings.tolist()
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(embedding_data, f, ensure_ascii=False, indent=2)

        print(f"Embeddings saved to {output_path}")

    def process_and_save(self, folder_path: str, output_path: str) -> Tuple[List[str], np.ndarray, np.ndarray]:
        filenames, image_embeddings, text_embeddings = self.encode_folder(folder_path)
        self.save_embeddings(filenames, image_embeddings, text_embeddings, output_path)
        return filenames, image_embeddings, text_embeddings
