"""
AAC 멀티모달 모델 학습 설정

OpenAI API 대신 사용할 1-3B 규모의 멀티모달 모델 학습을 위한 설정
"""

import torch
from pathlib import Path

TRAIN_CONFIG = {
    # ===== 기본 경로 설정 =====
    'project_root': Path(__file__).parent.parent.parent,
    'data_root': 'dataset',
    'images_folder': 'dataset/images',
    'processed_data': 'dataset/processed',
    'checkpoint_dir': 'train/checkpoints',
    'log_dir': 'train/logs',
    
    # ===== 모델 아키텍처 설정 =====
    'model_type': 'phi3_vision',  # 또는 'llava', 'minicpm', 'cogvlm2'
    'model_size': '3.8B',  # 3.8B parameter 모델 (Phi-3.5-Vision)
    'base_model': 'microsoft/Phi-3.5-vision-instruct',
    
    # 이미지 인코더 설정
    'vision_encoder': 'clip-vit-large-patch14-336',
    'image_size': 336,
    'patch_size': 14,
    'vision_hidden_size': 1024,
    
    # 텍스트 모델 설정  
    'text_model': 'microsoft/Phi-3.5-mini-instruct',
    'vocab_size': 32064,
    'hidden_size': 3072,
    'num_attention_heads': 32,
    'num_hidden_layers': 32,
    'max_position_embeddings': 131072,
    
    # ===== 데이터 설정 =====
    'max_image_tokens': 1024,
    'max_text_length': 512,
    'max_input_length': 2048,
    'train_split': 0.8,
    'val_split': 0.1,
    'test_split': 0.1,
    
    # ===== 학습 설정 =====
    'batch_size': 4,  # gradient_accumulation과 함께 effective batch size 조절
    'gradient_accumulation_steps': 8,  # effective batch size = 4 * 8 = 32
    'num_epochs': 10,
    'learning_rate': 2e-5,
    'warmup_steps': 1000,
    'weight_decay': 0.01,
    'gradient_clipping': 1.0,
    
    # ===== 최적화 설정 =====
    'optimizer': 'adamw',
    'scheduler': 'cosine_with_warmup',
    'beta1': 0.9,
    'beta2': 0.95,
    'epsilon': 1e-8,
    
    # ===== LoRA 파인튜닝 설정 (메모리 효율성을 위해) =====
    'use_lora': True,
    'lora_rank': 64,
    'lora_alpha': 16,
    'lora_dropout': 0.05,
    'lora_target_modules': [
        'q_proj', 'k_proj', 'v_proj', 'o_proj',
        'gate_proj', 'up_proj', 'down_proj'
    ],
    
    # ===== Mixed Precision 설정 =====
    'use_fp16': True,
    'use_deepspeed': False,  # 필요시 활성화
    
    # ===== 체크포인트 및 로깅 설정 =====
    'save_steps': 500,
    'eval_steps': 500,
    'logging_steps': 100,
    'max_checkpoints': 3,
    'early_stopping_patience': 5,
    
    # ===== 하드웨어 설정 =====
    'device': 'cuda' if torch.cuda.is_available() else 'cpu',
    'num_workers': 4,
    'pin_memory': True,
    
    # ===== AAC 특화 설정 =====
    'persona_embedding_dim': 128,
    'num_interpretation_styles': 3,  # 기존 시스템과 동일
    'context_window': 5,  # 이전 카드 선택 기록 고려
    'cluster_weight': 0.3,  # 클러스터 정보 활용 가중치
    
    # ===== 데이터 증강 설정 =====
    'use_data_augmentation': True,
    'image_augmentation': {
        'rotation_range': 10,
        'brightness_range': 0.2,
        'contrast_range': 0.2,
        'saturation_range': 0.2,
    },
    
    # ===== 평가 설정 =====
    'evaluation_metrics': [
        'bleu',
        'rouge',
        'bert_score',
        'semantic_similarity'
    ],
    
    # ===== 특수 토큰 설정 =====
    'special_tokens': {
        'image_token': '<image>',
        'persona_token': '<persona>',
        'context_token': '<context>',
        'interpretation_token': '<interpretation>',
        'eos_token': '<|endoftext|>',
        'pad_token': '<pad>',
    }
}

# 환경별 설정 오버라이드
if torch.cuda.device_count() > 1:
    TRAIN_CONFIG['use_ddp'] = True
    TRAIN_CONFIG['world_size'] = torch.cuda.device_count()
else:
    TRAIN_CONFIG['use_ddp'] = False
    TRAIN_CONFIG['world_size'] = 1

# 메모리가 부족한 경우 설정 조정
total_memory_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3 if torch.cuda.is_available() else 0
if total_memory_gb < 16:
    TRAIN_CONFIG['batch_size'] = 2
    TRAIN_CONFIG['gradient_accumulation_steps'] = 16
    TRAIN_CONFIG['use_fp16'] = True
    TRAIN_CONFIG['lora_rank'] = 32