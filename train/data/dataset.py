"""
AAC 멀티모달 모델 학습용 데이터셋 클래스

기존 data_prepare.py로 생성된 데이터를 활용하여 
멀티모달 학습에 적합한 형태로 변환
"""

import json
import torch
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import random
from transformers import AutoProcessor, AutoTokenizer
import numpy as np
from torchvision import transforms

class AACMultimodalDataset(Dataset):
    """AAC 카드 해석을 위한 멀티모달 데이터셋"""
    
    def __init__(
        self, 
        data_path: str,
        images_folder: str,
        processor: AutoProcessor,
        config: Dict,
        split: str = "train"
    ):
        """
        Args:
            data_path: dataset_completed.json 파일 경로
            images_folder: 이미지 폴더 경로
            processor: 멀티모달 프로세서 (이미지+텍스트)
            config: 학습 설정
            split: 'train', 'val', 'test' 중 하나
        """
        self.data_path = data_path
        self.images_folder = Path(images_folder)
        self.processor = processor
        self.config = config
        self.split = split
        
        # 데이터 로드
        self.data = self._load_data()
        
        # 특수 토큰 설정
        self.image_token = config['special_tokens']['image_token']
        self.persona_token = config['special_tokens']['persona_token']
        self.context_token = config['special_tokens']['context_token']
        self.interpretation_token = config['special_tokens']['interpretation_token']
        
        # 이미지 변환 설정
        self.image_transforms = self._setup_transforms()
        
    def _load_data(self) -> List[Dict]:
        """완성된 데이터셋 로드 및 분할"""
        with open(self.data_path, 'r', encoding='utf-8') as f:
            full_data = json.load(f)
        
        # 데이터 분할
        random.seed(42)  # 재현 가능한 분할을 위해
        random.shuffle(full_data)
        
        total = len(full_data)
        train_end = int(total * self.config['train_split'])
        val_end = train_end + int(total * self.config['val_split'])
        
        if self.split == "train":
            return full_data[:train_end]
        elif self.split == "val":
            return full_data[train_end:val_end]
        else:  # test
            return full_data[val_end:]
    
    def _setup_transforms(self):
        """이미지 변환 파이프라인 설정"""
        if self.split == "train" and self.config.get('use_data_augmentation', False):
            # 학습용 데이터 증강
            aug_config = self.config['image_augmentation']
            return transforms.Compose([
                transforms.Resize((self.config['image_size'], self.config['image_size'])),
                transforms.RandomRotation(aug_config['rotation_range']),
                transforms.ColorJitter(
                    brightness=aug_config['brightness_range'],
                    contrast=aug_config['contrast_range'],
                    saturation=aug_config['saturation_range']
                ),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
        else:
            # 검증/테스트용 변환
            return transforms.Compose([
                transforms.Resize((self.config['image_size'], self.config['image_size'])),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
    
    def __len__(self) -> int:
        return len(self.data)
    
    def __getitem__(self, idx: int) -> Dict[str, Any]:
        """개별 데이터 샘플 반환"""
        item = self.data[idx]
        
        try:
            # 이미지 로드
            images = self._load_images(item['selected_cards'])
            
            # 페르소나 정보 추출
            persona_info = self._format_persona(item['persona'])
            
            # 컨텍스트 정보 구성
            context_info = self._build_context(item)
            
            # 입력 텍스트 구성
            input_text = self._build_input_text(persona_info, context_info, len(item['selected_cards']))
            
            # 타겟 해석 추출 (학습 목표)
            target_text = self._format_interpretations(item['interpretations'])
            
            # 프로세서를 통한 전처리
            processed = self.processor(
                text=input_text,
                images=images,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=self.config['max_input_length']
            )
            
            # 타겟 토큰화
            target_encoding = self.processor.tokenizer(
                target_text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=self.config['max_text_length']
            )
            
            return {
                'input_ids': processed['input_ids'].squeeze(0),
                'attention_mask': processed['attention_mask'].squeeze(0),
                'pixel_values': processed['pixel_values'].squeeze(0) if 'pixel_values' in processed else None,
                'target_ids': target_encoding['input_ids'].squeeze(0),
                'target_attention_mask': target_encoding['attention_mask'].squeeze(0),
                'persona_info': persona_info,
                'num_cards': len(item['selected_cards']),
                'original_item': item  # 디버깅용
            }
            
        except Exception as e:
            print(f"Error processing item {idx}: {e}")
            # 에러 발생 시 다음 항목 반환
            return self.__getitem__((idx + 1) % len(self.data))
    
    def _load_images(self, selected_cards: List[str]) -> List[Image.Image]:
        """선택된 카드 이미지들 로드"""
        images = []
        for card_name in selected_cards:
            image_path = self.images_folder / card_name
            if image_path.exists():
                try:
                    image = Image.open(image_path).convert('RGB')
                    if self.image_transforms:
                        image = self.image_transforms(image)
                    images.append(image)
                except Exception as e:
                    print(f"Error loading image {image_path}: {e}")
                    # 기본 이미지 생성 (검은색)
                    images.append(Image.new('RGB', (self.config['image_size'], self.config['image_size'])))
            else:
                print(f"Image not found: {image_path}")
                images.append(Image.new('RGB', (self.config['image_size'], self.config['image_size'])))
        
        return images
    
    def _format_persona(self, persona: Dict) -> str:
        """페르소나 정보를 텍스트로 포맷팅"""
        persona_parts = []
        
        if 'name' in persona:
            persona_parts.append(f"이름: {persona['name']}")
        if 'age' in persona:
            persona_parts.append(f"나이: {persona['age']}세")
        if 'gender' in persona:
            persona_parts.append(f"성별: {persona['gender']}")
        if 'disability_type' in persona:
            persona_parts.append(f"장애 유형: {persona['disability_type']}")
        if 'communication_characteristics' in persona:
            persona_parts.append(f"의사소통 특징: {persona['communication_characteristics']}")
        if 'interesting_topics' in persona:
            topics = ', '.join(persona['interesting_topics'])
            persona_parts.append(f"관심 주제: {topics}")
        if 'preferred_category_types' in persona:
            categories = ', '.join(persona['preferred_category_types'])
            persona_parts.append(f"선호 카테고리: {categories}")
        
        return ' | '.join(persona_parts)
    
    def _build_context(self, item: Dict) -> str:
        """컨텍스트 정보 구성"""
        context_parts = []
        
        # 클러스터 정보 (있다면)
        if 'cluster_info' in item:
            context_parts.append(f"관련 주제: {', '.join(item['cluster_info'])}")
        
        # 카드 개수 정보
        context_parts.append(f"선택된 카드 수: {len(item['selected_cards'])}")
        
        # 카드 이름들
        card_names = [card.replace('.png', '').replace('.jpg', '') for card in item['selected_cards']]
        context_parts.append(f"카드: {', '.join(card_names)}")
        
        return ' | '.join(context_parts)
    
    def _build_input_text(self, persona_info: str, context_info: str, num_images: int) -> str:
        """모델 입력용 텍스트 구성"""
        # 이미지 토큰들
        image_tokens = ' '.join([self.image_token] * num_images)
        
        input_parts = [
            f"{self.persona_token} {persona_info}",
            f"{self.context_token} {context_info}",
            f"이미지: {image_tokens}",
            f"{self.interpretation_token}"
        ]
        
        return ' '.join(input_parts)
    
    def _format_interpretations(self, interpretations: List[Dict]) -> str:
        """해석들을 학습 타겟 형태로 포맷팅"""
        if not interpretations:
            return "해석을 생성할 수 없습니다."
        
        # 첫 번째 해석을 주로 사용하되, 가끔 다른 해석도 사용
        if len(interpretations) > 1 and random.random() < 0.3:
            interpretation = random.choice(interpretations)
        else:
            interpretation = interpretations[0]
        
        return interpretation.get('content', '해석을 생성할 수 없습니다.')


def create_dataloaders(
    data_path: str,
    images_folder: str,
    processor: AutoProcessor,
    config: Dict
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """학습, 검증, 테스트 데이터로더 생성"""
    
    # 데이터셋 생성
    train_dataset = AACMultimodalDataset(data_path, images_folder, processor, config, "train")
    val_dataset = AACMultimodalDataset(data_path, images_folder, processor, config, "val")
    test_dataset = AACMultimodalDataset(data_path, images_folder, processor, config, "test")
    
    # 데이터로더 생성
    train_loader = DataLoader(
        train_dataset,
        batch_size=config['batch_size'],
        shuffle=True,
        num_workers=config['num_workers'],
        pin_memory=config['pin_memory'],
        drop_last=True
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=config['batch_size'],
        shuffle=False,
        num_workers=config['num_workers'],
        pin_memory=config['pin_memory']
    )
    
    test_loader = DataLoader(
        test_dataset,
        batch_size=config['batch_size'],
        shuffle=False,
        num_workers=config['num_workers'],
        pin_memory=config['pin_memory']
    )
    
    print(f"데이터셋 크기 - 학습: {len(train_dataset)}, 검증: {len(val_dataset)}, 테스트: {len(test_dataset)}")
    
    return train_loader, val_loader, test_loader


def collate_fn(batch: List[Dict]) -> Dict[str, Any]:
    """배치 데이터 콜레이트 함수"""
    # 배치 내 최대 길이 계산
    max_input_len = max([item['input_ids'].size(0) for item in batch])
    max_target_len = max([item['target_ids'].size(0) for item in batch])
    
    batch_input_ids = []
    batch_attention_mask = []
    batch_pixel_values = []
    batch_target_ids = []
    batch_target_attention_mask = []
    
    for item in batch:
        # 입력 패딩
        input_ids = item['input_ids']
        attention_mask = item['attention_mask']
        
        if input_ids.size(0) < max_input_len:
            padding_length = max_input_len - input_ids.size(0)
            input_ids = torch.cat([input_ids, torch.zeros(padding_length, dtype=input_ids.dtype)])
            attention_mask = torch.cat([attention_mask, torch.zeros(padding_length, dtype=attention_mask.dtype)])
        
        batch_input_ids.append(input_ids)
        batch_attention_mask.append(attention_mask)
        
        # 이미지 데이터
        if item['pixel_values'] is not None:
            batch_pixel_values.append(item['pixel_values'])
        
        # 타겟 패딩
        target_ids = item['target_ids']
        target_attention_mask = item['target_attention_mask']
        
        if target_ids.size(0) < max_target_len:
            padding_length = max_target_len - target_ids.size(0)
            target_ids = torch.cat([target_ids, torch.full((padding_length,), -100, dtype=target_ids.dtype)])  # -100은 loss 계산에서 무시됨
            target_attention_mask = torch.cat([target_attention_mask, torch.zeros(padding_length, dtype=target_attention_mask.dtype)])
        
        batch_target_ids.append(target_ids)
        batch_target_attention_mask.append(target_attention_mask)
    
    result = {
        'input_ids': torch.stack(batch_input_ids),
        'attention_mask': torch.stack(batch_attention_mask),
        'labels': torch.stack(batch_target_ids),
        'target_attention_mask': torch.stack(batch_target_attention_mask)
    }
    
    if batch_pixel_values:
        result['pixel_values'] = torch.stack(batch_pixel_values)
    
    return result