import os
from pathlib import Path
from typing import List, Optional, Tuple

import huggingface_hub
import numpy as np
import torch
from dotenv import load_dotenv
from PIL import Image
from tqdm import tqdm
from transformers import AutoModel, AutoProcessor

from .utils import extract_keyword_from_filename, get_device, save_json


class CLIPEncoder:
    """CLIP 모델을 사용한 이미지-텍스트 임베딩 생성기.

    이미지와 해당 텍스트 키워드를 동시에 인코딩하여 멀티모달 임베딩을 생성합니다.
    설정은 config 딕셔너리를 통해 전달받습니다.
    """

    def __init__(self, model_name: str = None, config: Optional[dict] = None):
        """CLIPEncoder 초기화.

        Args:
            model_name: 사용할 CLIP 모델명 (config에서 우선 적용)
            config: 설정 딕셔너리
        """
        load_dotenv()

        self.config = config or {}

        # config에서 모델명 우선 적용
        if self.config and "clip_model" in self.config:
            self.model_name = self.config["clip_model"]
        else:
            self.model_name = model_name or "openai/clip-vit-base-patch32"

        hf_token = os.getenv("HUGGINGFACE_TOKEN")
        if hf_token:
            huggingface_hub.login(token=hf_token)

        self.device = get_device(self.config)
        print(f"Using device: {self.device}")

        self.model = AutoModel.from_pretrained(
            self.model_name, torch_dtype=torch.bfloat16, attn_implementation="sdpa"
        ).to(self.device)

        self.processor = AutoProcessor.from_pretrained(self.model_name)

    def _process_image(self, image_path: str) -> Image.Image:
        """이미지 파일을 PIL Image로 변환하고 RGB 형식으로 정규화.

        Args:
            image_path: 이미지 파일 경로

        Returns:
            PIL Image: RGB 형식으로 변환된 이미지
        """
        image = Image.open(image_path)
        if image.mode == "P" and "transparency" in image.info:
            image = image.convert("RGBA")
        return image.convert("RGB")

    def _extract_text(self, filename: str) -> str:
        """파일명에서 텍스트 키워드 추출."""
        return extract_keyword_from_filename(filename)

    def encode_single(
        self, image_path: str, text: str
    ) -> Tuple[np.ndarray, np.ndarray]:
        """단일 이미지-텍스트 쌍의 임베딩 생성.

        Args:
            image_path: 이미지 파일 경로
            text: 대응되는 텍스트

        Returns:
            Tuple[np.ndarray, np.ndarray]: (이미지_임베딩, 텍스트_임베딩)
        """
        image = self._process_image(image_path)

        inputs = self.processor(
            text=[text], images=image, return_tensors="pt", padding=True
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)

            image_embedding = outputs.image_embeds / outputs.image_embeds.norm(
                dim=-1, keepdim=True
            )
            text_embedding = outputs.text_embeds / outputs.text_embeds.norm(
                dim=-1, keepdim=True
            )

            return (
                image_embedding.float().cpu().numpy().flatten(),
                text_embedding.float().cpu().numpy().flatten(),
            )

    def encode_folder(
        self, folder_path: str
    ) -> Tuple[List[str], np.ndarray, np.ndarray]:
        """폴더 내 모든 PNG 이미지의 임베딩 생성.

        Args:
            folder_path: 이미지 폴더 경로

        Returns:
            Tuple: (파일명_리스트, 이미지_임베딩_배열, 텍스트_임베딩_배열)
        """
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

    def save_embeddings(
        self,
        filenames: List[str],
        image_embeddings: np.ndarray,
        text_embeddings: np.ndarray,
        output_path: str,
    ) -> None:
        """임베딩 결과를 JSON 파일로 저장.

        Args:
            filenames: 파일명 리스트
            image_embeddings: 이미지 임베딩 배열
            text_embeddings: 텍스트 임베딩 배열
            output_path: 출력 파일 경로
        """
        embedding_data = {
            "filenames": filenames,
            "image_embeddings": image_embeddings.tolist(),
            "text_embeddings": text_embeddings.tolist(),
        }
        save_json(embedding_data, output_path)
        print(f"Embeddings saved to {output_path}")

    def process_and_save(
        self, folder_path: str, output_path: str
    ) -> Tuple[List[str], np.ndarray, np.ndarray]:
        """폴더 처리 및 임베딩 저장을 한번에 수행.

        Args:
            folder_path: 입력 이미지 폴더 경로
            output_path: 출력 JSON 파일 경로

        Returns:
            Tuple: (파일명_리스트, 이미지_임베딩_배열, 텍스트_임베딩_배열)
        """
        filenames, image_embeddings, text_embeddings = self.encode_folder(folder_path)
        self.save_embeddings(filenames, image_embeddings, text_embeddings, output_path)
        return filenames, image_embeddings, text_embeddings
