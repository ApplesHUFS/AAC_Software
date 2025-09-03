"""
AAC 멀티모달 모델 학습 스크립트

OpenAI API 대신 사용할 1-3B 규모의 멀티모달 모델을 학습합니다.
Phi-3.5-Vision 기반으로 AAC 카드 해석에 특화된 모델을 훈련합니다.
"""

import os
import json
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from transformers import AutoProcessor, get_linear_schedule_with_warmup
import wandb
from tqdm import tqdm
import numpy as np
from pathlib import Path
import argparse
from datetime import datetime
import logging
from typing import Dict, List, Optional

# 프로젝트 모듈들
import sys
sys.path.append(str(Path(__file__).parent))

from config.train_config import TRAIN_CONFIG
from models.aac_multimodal_model import AACMultimodalModel
from data.dataset import create_dataloaders
from utils.metrics import EvaluationMetrics, calculate_perplexity


class AACTrainer:
    """AAC 멀티모달 모델 훈련을 위한 트레이너"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.device = torch.device(config['device'])
        
        # 로깅 설정
        self.setup_logging()
        
        # 모델 및 프로세서 초기화
        self.model = None
        self.processor = None
        self.optimizer = None
        self.scheduler = None
        
        # 데이터로더
        self.train_loader = None
        self.val_loader = None
        self.test_loader = None
        
        # 평가 메트릭
        self.evaluator = EvaluationMetrics()
        
        # 학습 상태
        self.current_epoch = 0
        self.global_step = 0
        self.best_val_loss = float('inf')
        self.patience_counter = 0
        
        # 체크포인트 디렉토리
        self.checkpoint_dir = Path(config['checkpoint_dir'])
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # 로그 디렉토리
        self.log_dir = Path(config['log_dir'])
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_dir / 'training.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def initialize_model(self):
        """모델 초기화"""
        self.logger.info("모델 초기화 중...")
        
        # 프로세서 로드
        self.processor = AutoProcessor.from_pretrained(
            self.config['base_model'], 
            trust_remote_code=True
        )
        
        # 특수 토큰 추가
        special_tokens = list(self.config['special_tokens'].values())
        self.processor.tokenizer.add_special_tokens({
            'additional_special_tokens': special_tokens
        })
        
        # 모델 초기화
        self.model = AACMultimodalModel(self.config)
        
        # 모델을 디바이스로 이동
        self.model = self.model.to(self.device)
        
        # 멀티 GPU 설정
        if torch.cuda.device_count() > 1 and self.config.get('use_ddp', False):
            self.model = nn.DataParallel(self.model)
        
        self.logger.info(f"모델이 {self.device}에 로드되었습니다.")
        param_count = sum(p.numel() for p in self.model.parameters())
        self.logger.info(f"모델 파라미터 수: {param_count:,}")
    
    def initialize_data(self):
        """데이터로더 초기화"""
        self.logger.info("데이터로더 초기화 중...")
        
        # 데이터 경로 설정
        data_path = os.path.join(self.config['processed_data'], 'dataset_completed.json')
        images_folder = self.config['images_folder']
        
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"데이터셋 파일을 찾을 수 없습니다: {data_path}")
        
        # 데이터로더 생성
        self.train_loader, self.val_loader, self.test_loader = create_dataloaders(
            data_path=data_path,
            images_folder=images_folder,
            processor=self.processor,
            config=self.config
        )
        
        self.logger.info("데이터로더 초기화 완료")
    
    def initialize_optimizer(self):
        """옵티마이저 및 스케줄러 초기화"""
        self.logger.info("옵티마이저 초기화 중...")
        
        # 파라미터 그룹 설정 (LoRA인 경우 trainable parameters만)
        if self.config.get('use_lora', False):
            trainable_params = [p for p in self.model.parameters() if p.requires_grad]
            param_groups = [{'params': trainable_params}]
        else:
            param_groups = [{'params': self.model.parameters()}]
        
        # 옵티마이저
        self.optimizer = AdamW(
            param_groups,
            lr=self.config['learning_rate'],
            weight_decay=self.config['weight_decay'],
            betas=(self.config['beta1'], self.config['beta2']),
            eps=self.config['epsilon']
        )
        
        # 스케줄러
        total_steps = len(self.train_loader) * self.config['num_epochs']
        warmup_steps = self.config['warmup_steps']
        
        self.scheduler = get_linear_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=warmup_steps,
            num_training_steps=total_steps
        )
        
        self.logger.info("옵티마이저 초기화 완료")
    
    def train_epoch(self) -> Dict[str, float]:
        """한 에포크 학습"""
        self.model.train()
        
        total_loss = 0.0
        total_samples = 0
        
        progress_bar = tqdm(
            self.train_loader, 
            desc=f"Epoch {self.current_epoch + 1}/{self.config['num_epochs']}"
        )
        
        for batch_idx, batch in enumerate(progress_bar):
            # 배치를 디바이스로 이동
            batch = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v 
                    for k, v in batch.items()}
            
            # Forward pass
            outputs = self.model(
                input_ids=batch['input_ids'],
                pixel_values=batch.get('pixel_values'),
                attention_mask=batch['attention_mask'],
                labels=batch['labels']
            )
            
            loss = outputs['loss']
            
            # Gradient accumulation
            loss = loss / self.config['gradient_accumulation_steps']
            
            # Backward pass
            loss.backward()
            
            # Gradient clipping
            if self.config.get('gradient_clipping', 0) > 0:
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(), 
                    self.config['gradient_clipping']
                )
            
            # 옵티마이저 스텝
            if (batch_idx + 1) % self.config['gradient_accumulation_steps'] == 0:
                self.optimizer.step()
                self.scheduler.step()
                self.optimizer.zero_grad()
                self.global_step += 1
            
            # 통계 업데이트
            total_loss += loss.item() * self.config['gradient_accumulation_steps']
            total_samples += batch['input_ids'].size(0)
            
            # Progress bar 업데이트
            avg_loss = total_loss / (batch_idx + 1)
            progress_bar.set_postfix({
                'loss': f'{avg_loss:.4f}',
                'lr': f'{self.scheduler.get_last_lr()[0]:.2e}'
            })
            
            # 로깅
            if self.global_step % self.config['logging_steps'] == 0:
                self.logger.info(
                    f"Step {self.global_step}, Loss: {avg_loss:.4f}, "
                    f"LR: {self.scheduler.get_last_lr()[0]:.2e}"
                )
                
                # Wandb 로깅
                if wandb.run:
                    wandb.log({
                        'train/loss': avg_loss,
                        'train/learning_rate': self.scheduler.get_last_lr()[0],
                        'train/step': self.global_step
                    })
            
            # 체크포인트 저장
            if self.global_step % self.config['save_steps'] == 0:
                self.save_checkpoint()
        
        return {
            'loss': total_loss / len(self.train_loader),
            'perplexity': calculate_perplexity([total_loss / len(self.train_loader)])
        }
    
    def save_checkpoint(self):
        """체크포인트 저장"""
        checkpoint = {
            'epoch': self.current_epoch,
            'global_step': self.global_step,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'best_val_loss': self.best_val_loss,
            'config': self.config
        }
        
        checkpoint_path = self.checkpoint_dir / f"checkpoint_step_{self.global_step}.pt"
        torch.save(checkpoint, checkpoint_path)
        
        self.logger.info(f"체크포인트 저장: {checkpoint_path}")
    
    def train(self):
        """메인 학습 함수 - 간단한 버전"""
        self.logger.info("AAC 멀티모달 모델 학습을 시작합니다.")
        
        print("""
========================================
  AAC 멀티모달 모델 학습 스크립트
========================================

이 스크립트는 OpenAI API를 대체할 1-3B 규모의
멀티모달 모델을 훈련합니다.

주요 기능:
- Phi-3.5-Vision 기반 아키텍처
- AAC 카드 이미지 해석 특화
- 페르소나 기반 개인화
- LoRA 파인튜닝 지원

필요한 데이터:
- dataset/processed/dataset_completed.json
- dataset/images/ (AAC 카드 이미지들)

설정 파일: train/config/train_config.py
        """)
        
        # 기본 설정 출력
        print(f"\n현재 설정:")
        print(f"- 모델: {self.config['model_type']} ({self.config['model_size']})")
        print(f"- 배치 크기: {self.config['batch_size']}")
        print(f"- 학습률: {self.config['learning_rate']}")
        print(f"- 에포크: {self.config['num_epochs']}")
        print(f"- LoRA 사용: {self.config.get('use_lora', False)}")
        print(f"- 디바이스: {self.device}")
        
        # 데이터 경로 체크
        data_path = os.path.join(self.config['processed_data'], 'dataset_completed.json')
        images_path = self.config['images_folder']
        
        if not os.path.exists(data_path):
            print(f"\n❌ 오류: 데이터셋 파일을 찾을 수 없습니다.")
            print(f"경로: {data_path}")
            print(f"\n먼저 data_prepare.py를 실행하여 데이터셋을 준비해주세요.")
            return
        
        if not os.path.exists(images_path):
            print(f"\n❌ 오류: 이미지 폴더를 찾을 수 없습니다.")
            print(f"경로: {images_path}")
            return
        
        print(f"\n✅ 데이터 경로 확인 완료")
        print(f"- 데이터셋: {data_path}")
        print(f"- 이미지: {images_path}")
        
        # 필요한 패키지 체크
        try:
            from transformers import Phi3VForCausalLM
            print(f"✅ Transformers 패키지 확인")
        except ImportError:
            print(f"❌ 오류: transformers 패키지가 설치되어 있지 않습니다.")
            print(f"pip install transformers 를 실행해주세요.")
            return
        
        try:
            from peft import LoraConfig
            print(f"✅ PEFT 패키지 확인")
        except ImportError:
            print(f"❌ 오류: peft 패키지가 설치되어 있지 않습니다.")
            print(f"pip install peft 를 실행해주세요.")
            return
        
        print(f"\n🚀 모든 준비가 완료되었습니다!")
        print(f"\n실제 학습을 시작하려면 아래 단계를 따라하세요:")
        print(f"1. 필요한 패키지 설치: pip install -r train/requirements.txt")
        print(f"2. GPU 메모리 확인 (16GB+ 권장)")
        print(f"3. 학습 실행: python train/train.py --wandb --full-train")
        
        print(f"\n⚠️  주의사항:")
        print(f"- 첫 실행시 Phi-3.5-Vision 모델 다운로드 (약 7GB)")
        print(f"- 학습 시간: GPU에 따라 수 시간~수일")
        print(f"- 체크포인트는 train/checkpoints/에 저장됩니다")

        # --full-train 플래그가 있을 때만 실제 학습 실행
        if hasattr(self, 'full_train') and self.full_train:
            print(f"\n🏋️‍♂️ 실제 학습을 시작합니다...")
            
            # 실제 학습 로직
            try:
                # 초기화
                self.initialize_model()
                self.initialize_data()
                self.initialize_optimizer()
                
                # Wandb 초기화
                if self.config.get('use_wandb', False):
                    wandb.init(
                        project="aac-multimodal",
                        config=self.config,
                        name=f"aac_train_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    )
                
                # 학습 루프
                for epoch in range(self.config['num_epochs']):
                    self.current_epoch = epoch
                    
                    # 에포크 학습
                    train_metrics = self.train_epoch()
                    
                    self.logger.info(
                        f"Epoch {epoch + 1}/{self.config['num_epochs']} - "
                        f"Train Loss: {train_metrics['loss']:.4f}"
                    )
                    
                    # Early stopping 체크
                    if self.patience_counter >= self.config['early_stopping_patience']:
                        self.logger.info("Early stopping triggered")
                        break
                
                self.logger.info("학습 완료")
                
            except Exception as e:
                self.logger.error(f"학습 중 오류 발생: {e}")
                raise


def main():
    parser = argparse.ArgumentParser(description='AAC 멀티모달 모델 학습')
    parser.add_argument('--config', type=str, help='설정 파일 경로 (선택사항)')
    parser.add_argument('--wandb', action='store_true', help='Wandb 로깅 사용')
    parser.add_argument('--resume', type=str, help='체크포인트에서 재시작')
    parser.add_argument('--full-train', action='store_true', help='실제 학습 실행')
    args = parser.parse_args()
    
    # 설정 로드
    config = TRAIN_CONFIG.copy()
    
    if args.config:
        with open(args.config, 'r') as f:
            custom_config = json.load(f)
        config.update(custom_config)
    
    if args.wandb:
        config['use_wandb'] = True
    
    # 트레이너 초기화 및 학습
    trainer = AACTrainer(config)
    trainer.full_train = args.full_train  # 실제 학습 여부 설정
    trainer.train()


if __name__ == "__main__":
    main()