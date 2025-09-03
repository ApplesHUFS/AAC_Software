"""
AAC 특화 멀티모달 모델

Phi-3.5-Vision 기반으로 AAC 카드 해석에 특화된 멀티모달 모델 구현
페르소나 기반 개인화 및 컨텍스트 이해 기능 포함
"""

import torch
import torch.nn as nn
from transformers import (
    Phi3VForCausalLM, 
    AutoProcessor, 
    AutoTokenizer,
    Phi3VConfig
)
from peft import LoraConfig, get_peft_model, TaskType
from typing import Dict, List, Optional, Tuple, Any
import numpy as np


class PersonaEmbedding(nn.Module):
    """사용자 페르소나 임베딩 레이어"""
    
    def __init__(self, config: Dict):
        super().__init__()
        self.config = config
        self.embedding_dim = config['persona_embedding_dim']
        self.hidden_size = config['hidden_size']
        
        # 페르소나 특성별 임베딩
        self.age_embedding = nn.Embedding(101, self.embedding_dim)  # 0-100세
        self.gender_embedding = nn.Embedding(3, self.embedding_dim)  # male, female, other
        self.disability_embedding = nn.Embedding(20, self.embedding_dim)  # 주요 장애 유형들
        
        # 페르소나 통합 레이어
        self.persona_projector = nn.Sequential(
            nn.Linear(self.embedding_dim * 3, self.hidden_size),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(self.hidden_size, self.hidden_size)
        )
        
    def forward(self, persona_features: Dict[str, torch.Tensor]) -> torch.Tensor:
        """
        Args:
            persona_features: {'age': tensor, 'gender': tensor, 'disability': tensor}
        Returns:
            페르소나 임베딩 [batch_size, hidden_size]
        """
        age_emb = self.age_embedding(persona_features['age'])
        gender_emb = self.gender_embedding(persona_features['gender'])
        disability_emb = self.disability_embedding(persona_features['disability'])
        
        # 페르소나 임베딩 결합
        combined = torch.cat([age_emb, gender_emb, disability_emb], dim=-1)
        persona_emb = self.persona_projector(combined)
        
        return persona_emb


class ContextualAttention(nn.Module):
    """컨텍스트 정보를 활용한 어텐션 메커니즘"""
    
    def __init__(self, config: Dict):
        super().__init__()
        self.hidden_size = config['hidden_size']
        self.num_attention_heads = config['num_attention_heads']
        self.head_dim = self.hidden_size // self.num_attention_heads
        
        self.context_projector = nn.Linear(self.hidden_size, self.hidden_size)
        self.attention = nn.MultiheadAttention(
            self.hidden_size, 
            self.num_attention_heads,
            dropout=0.1,
            batch_first=True
        )
        
    def forward(
        self, 
        hidden_states: torch.Tensor,
        context_embedding: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Args:
            hidden_states: [batch_size, seq_len, hidden_size]
            context_embedding: [batch_size, hidden_size]
            attention_mask: [batch_size, seq_len]
        Returns:
            컨텍스트가 반영된 hidden states
        """
        batch_size, seq_len = hidden_states.shape[:2]
        
        # 컨텍스트를 시퀀스 길이만큼 확장
        context_projected = self.context_projector(context_embedding)
        context_expanded = context_projected.unsqueeze(1).expand(-1, seq_len, -1)
        
        # 컨텍스트 정보를 query로 사용한 어텐션
        attended_output, _ = self.attention(
            query=context_expanded,
            key=hidden_states,
            value=hidden_states,
            key_padding_mask=~attention_mask.bool() if attention_mask is not None else None
        )
        
        # 잔차 연결
        output = hidden_states + attended_output
        
        return output


class AACMultimodalModel(nn.Module):
    """AAC 카드 해석을 위한 멀티모달 모델"""
    
    def __init__(self, config: Dict):
        super().__init__()
        self.config = config
        
        # 기본 Phi-3.5-Vision 모델 로드
        model_name = config['base_model']
        self.backbone = Phi3VForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if config.get('use_fp16', False) else torch.float32,
            device_map="auto" if config.get('device') == 'cuda' else None,
            trust_remote_code=True
        )
        
        # 프로세서 설정
        self.processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
        
        # AAC 특화 컴포넌트
        self.persona_embedding = PersonaEmbedding(config)
        self.contextual_attention = ContextualAttention(config)
        
        # 해석 스타일 분류기 (3가지 해석 스타일)
        self.interpretation_classifier = nn.Sequential(
            nn.Linear(config['hidden_size'], 512),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(512, config['num_interpretation_styles'])
        )
        
        # 클러스터 정보 활용을 위한 어텐션
        self.cluster_attention = nn.MultiheadAttention(
            config['hidden_size'],
            config['num_attention_heads'] // 2,
            dropout=0.1,
            batch_first=True
        )
        
        # LoRA 설정 (메모리 효율성)
        if config.get('use_lora', False):
            self._setup_lora()
    
    def _setup_lora(self):
        """LoRA 파인튜닝 설정"""
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=self.config['lora_rank'],
            lora_alpha=self.config['lora_alpha'],
            lora_dropout=self.config['lora_dropout'],
            target_modules=self.config['lora_target_modules'],
            bias="none"
        )
        
        self.backbone = get_peft_model(self.backbone, lora_config)
        
    def encode_persona(self, persona_info: List[Dict]) -> torch.Tensor:
        """페르소나 정보를 인코딩"""
        batch_size = len(persona_info)
        device = next(self.parameters()).device
        
        # 페르소나 특성 추출 및 텐서화
        ages = torch.tensor([p.get('age', 25) for p in persona_info], device=device)
        genders = torch.tensor([
            0 if p.get('gender') == 'male' else 1 if p.get('gender') == 'female' else 2 
            for p in persona_info
        ], device=device)
        disabilities = torch.tensor([
            self._disability_to_id(p.get('disability_type', '기타')) 
            for p in persona_info
        ], device=device)
        
        persona_features = {
            'age': ages,
            'gender': genders,
            'disability': disabilities
        }
        
        return self.persona_embedding(persona_features)
    
    def _disability_to_id(self, disability_type: str) -> int:
        """장애 유형을 ID로 매핑"""
        disability_map = {
            '지적장애': 0, '자폐스펙트럼': 1, '뇌성마비': 2, '언어장애': 3,
            '청각장애': 4, '시각장애': 5, '학습장애': 6, '발달지연': 7,
            '다운증후군': 8, '뇌손상': 9, '근육병': 10, '척수손상': 11,
            '간질': 12, '정신장애': 13, '치매': 14, 'ADHD': 15,
            '기타': 19
        }
        return disability_map.get(disability_type, 19)
    
    def forward(
        self,
        input_ids: torch.Tensor,
        pixel_values: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        labels: Optional[torch.Tensor] = None,
        persona_info: Optional[List[Dict]] = None,
        cluster_context: Optional[torch.Tensor] = None,
        return_interpretation_logits: bool = False
    ) -> Dict[str, torch.Tensor]:
        """
        Args:
            input_ids: 토큰 ID [batch_size, seq_len]
            pixel_values: 이미지 픽셀 값 [batch_size, num_images, channels, height, width]
            attention_mask: 어텐션 마스크 [batch_size, seq_len]
            labels: 학습용 라벨 [batch_size, seq_len]
            persona_info: 페르소나 정보 리스트
            cluster_context: 클러스터 컨텍스트 임베딩 [batch_size, hidden_size]
            return_interpretation_logits: 해석 스타일 로짓 반환 여부
        """
        outputs = {}
        
        # 기본 Phi-3.5-Vision 모델 forward
        backbone_outputs = self.backbone(
            input_ids=input_ids,
            pixel_values=pixel_values,
            attention_mask=attention_mask,
            labels=labels,
            output_hidden_states=True,
            return_dict=True
        )
        
        # 기본 출력
        outputs['logits'] = backbone_outputs.logits
        outputs['loss'] = backbone_outputs.loss if labels is not None else None
        
        # 마지막 히든 스테이트 추출
        hidden_states = backbone_outputs.hidden_states[-1]  # [batch_size, seq_len, hidden_size]
        
        # 페르소나 임베딩 추가
        if persona_info is not None:
            persona_emb = self.encode_persona(persona_info)
            
            # 컨텍스트 어텐션 적용
            hidden_states = self.contextual_attention(
                hidden_states, persona_emb, attention_mask
            )
            
            # 해석 스타일 분류
            if return_interpretation_logits:
                # 시퀀스의 마지막 토큰 사용
                last_hidden = hidden_states[:, -1, :]  # [batch_size, hidden_size]
                interpretation_logits = self.interpretation_classifier(last_hidden)
                outputs['interpretation_logits'] = interpretation_logits
        
        # 클러스터 컨텍스트 활용
        if cluster_context is not None:
            cluster_attended, _ = self.cluster_attention(
                query=hidden_states,
                key=cluster_context.unsqueeze(1).expand(-1, hidden_states.size(1), -1),
                value=cluster_context.unsqueeze(1).expand(-1, hidden_states.size(1), -1),
                key_padding_mask=~attention_mask.bool() if attention_mask is not None else None
            )
            
            # 클러스터 정보가 반영된 최종 로짓 계산
            enhanced_hidden = hidden_states + cluster_attended * self.config.get('cluster_weight', 0.3)
            
            # 언어 모델 헤드를 통과
            lm_head = self.backbone.get_output_embeddings()
            outputs['enhanced_logits'] = lm_head(enhanced_hidden)
        
        outputs['hidden_states'] = hidden_states
        
        return outputs
    
    def generate_interpretation(
        self,
        images: List,
        persona_info: Dict,
        context_info: str,
        max_length: int = 400,
        temperature: float = 0.8,
        num_beams: int = 3
    ) -> List[str]:
        """AAC 카드 해석 생성"""
        self.eval()
        
        with torch.no_grad():
            # 입력 텍스트 구성
            input_text = self._build_prompt(persona_info, context_info, len(images))
            
            # 프로세서를 통한 전처리
            inputs = self.processor(
                text=input_text,
                images=images,
                return_tensors="pt",
                padding=True
            )
            
            # GPU로 이동
            inputs = {k: v.to(next(self.parameters()).device) for k, v in inputs.items()}
            
            # 생성
            with torch.no_grad():
                generated_ids = self.backbone.generate(
                    **inputs,
                    max_length=max_length,
                    temperature=temperature,
                    num_beams=num_beams,
                    num_return_sequences=self.config.get('num_interpretation_styles', 3),
                    do_sample=True,
                    pad_token_id=self.processor.tokenizer.eos_token_id
                )
            
            # 디코딩
            interpretations = []
            for generated_seq in generated_ids:
                # 입력 길이만큼 제거
                input_length = inputs['input_ids'].shape[1]
                generated_text = self.processor.tokenizer.decode(
                    generated_seq[input_length:], 
                    skip_special_tokens=True
                ).strip()
                interpretations.append(generated_text)
            
            return interpretations
    
    def _build_prompt(self, persona_info: Dict, context_info: str, num_images: int) -> str:
        """프롬프트 구성"""
        persona_text = f"사용자 정보: {persona_info.get('name', '익명')}, {persona_info.get('age', 25)}세, "
        persona_text += f"{persona_info.get('gender', '기타')}, {persona_info.get('disability_type', '기타')}"
        
        if 'communication_characteristics' in persona_info:
            persona_text += f", 의사소통 특징: {persona_info['communication_characteristics']}"
        
        image_tokens = ' '.join(['<image>'] * num_images)
        
        prompt = f"""
{persona_text}

상황 정보: {context_info}

선택된 AAC 카드들: {image_tokens}

위 사용자의 특성을 고려하여 선택된 AAC 카드들이 전달하고자 하는 의미를 자연스럽고 이해하기 쉬운 한국어로 해석해주세요.

해석:"""
        
        return prompt.strip()
    
    def save_model(self, save_path: str):
        """모델 저장"""
        if self.config.get('use_lora', False):
            # LoRA 어댑터만 저장
            self.backbone.save_pretrained(save_path)
        else:
            # 전체 모델 저장
            torch.save({
                'model_state_dict': self.state_dict(),
                'config': self.config
            }, save_path)
    
    @classmethod
    def load_model(cls, load_path: str, config: Dict):
        """모델 로드"""
        model = cls(config)
        
        if config.get('use_lora', False):
            # LoRA 어댑터 로드
            model.backbone = model.backbone.from_pretrained(load_path)
        else:
            # 전체 모델 로드
            checkpoint = torch.load(load_path, map_location='cpu')
            model.load_state_dict(checkpoint['model_state_dict'])
        
        return model