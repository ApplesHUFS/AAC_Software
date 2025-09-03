"""
AAC 멀티모달 모델 평가 메트릭

BLEU, ROUGE, BERTScore 등 다양한 텍스트 생성 평가 메트릭 구현
"""

import torch
import numpy as np
from typing import List, Dict, Tuple
from collections import Counter
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class EvaluationMetrics:
    """AAC 해석 생성 평가를 위한 메트릭 집합"""
    
    def __init__(self):
        # 의미 유사도 계산을 위한 모델
        self.similarity_model = SentenceTransformer('Snowflake/snowflake-arctic-embed-l')
        
    def compute_bleu(self, predictions: List[str], references: List[str], n_gram: int = 4) -> float:
        """BLEU 점수 계산"""
        total_score = 0.0
        count = 0
        
        for pred, ref in zip(predictions, references):
            score = self._sentence_bleu(pred, ref, n_gram)
            total_score += score
            count += 1
        
        return total_score / count if count > 0 else 0.0
    
    def _sentence_bleu(self, prediction: str, reference: str, n_gram: int = 4) -> float:
        """개별 문장의 BLEU 점수 계산"""
        pred_tokens = self._tokenize(prediction)
        ref_tokens = self._tokenize(reference)
        
        if len(pred_tokens) == 0:
            return 0.0
        
        # n-gram precision 계산
        precisions = []
        for n in range(1, n_gram + 1):
            pred_ngrams = self._get_ngrams(pred_tokens, n)
            ref_ngrams = self._get_ngrams(ref_tokens, n)
            
            if len(pred_ngrams) == 0:
                precisions.append(0.0)
                continue
                
            overlap = 0
            for ngram in pred_ngrams:
                if ngram in ref_ngrams:
                    overlap += min(pred_ngrams[ngram], ref_ngrams[ngram])
            
            precision = overlap / sum(pred_ngrams.values())
            precisions.append(precision)
        
        # Brevity penalty
        bp = min(1.0, np.exp(1 - len(ref_tokens) / len(pred_tokens)))
        
        # 기하평균 계산
        if min(precisions) > 0:
            geometric_mean = np.exp(np.mean([np.log(p) for p in precisions]))
            return bp * geometric_mean
        else:
            return 0.0
    
    def compute_rouge(self, predictions: List[str], references: List[str]) -> Dict[str, float]:
        """ROUGE 점수 계산 (ROUGE-1, ROUGE-2, ROUGE-L)"""
        rouge_1_scores = []
        rouge_2_scores = []
        rouge_l_scores = []
        
        for pred, ref in zip(predictions, references):
            pred_tokens = self._tokenize(pred)
            ref_tokens = self._tokenize(ref)
            
            # ROUGE-1
            rouge_1 = self._rouge_n(pred_tokens, ref_tokens, 1)
            rouge_1_scores.append(rouge_1)
            
            # ROUGE-2
            rouge_2 = self._rouge_n(pred_tokens, ref_tokens, 2)
            rouge_2_scores.append(rouge_2)
            
            # ROUGE-L
            rouge_l = self._rouge_l(pred_tokens, ref_tokens)
            rouge_l_scores.append(rouge_l)
        
        return {
            'rouge-1': np.mean(rouge_1_scores),
            'rouge-2': np.mean(rouge_2_scores),
            'rouge-l': np.mean(rouge_l_scores)
        }
    
    def _rouge_n(self, pred_tokens: List[str], ref_tokens: List[str], n: int) -> float:
        """ROUGE-N 점수 계산"""
        pred_ngrams = self._get_ngrams(pred_tokens, n)
        ref_ngrams = self._get_ngrams(ref_tokens, n)
        
        if sum(ref_ngrams.values()) == 0:
            return 0.0
        
        overlap = 0
        for ngram in pred_ngrams:
            if ngram in ref_ngrams:
                overlap += min(pred_ngrams[ngram], ref_ngrams[ngram])
        
        recall = overlap / sum(ref_ngrams.values())
        return recall
    
    def _rouge_l(self, pred_tokens: List[str], ref_tokens: List[str]) -> float:
        """ROUGE-L 점수 계산 (Longest Common Subsequence)"""
        lcs_length = self._lcs(pred_tokens, ref_tokens)
        
        if len(ref_tokens) == 0:
            return 0.0
        
        recall = lcs_length / len(ref_tokens)
        return recall
    
    def _lcs(self, seq1: List[str], seq2: List[str]) -> int:
        """Longest Common Subsequence 계산"""
        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i - 1] == seq2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
        
        return dp[m][n]
    
    def compute_semantic_similarity(self, predictions: List[str], references: List[str]) -> float:
        """의미적 유사도 계산"""
        if len(predictions) == 0 or len(references) == 0:
            return 0.0
        
        # 임베딩 계산
        pred_embeddings = self.similarity_model.encode(predictions)
        ref_embeddings = self.similarity_model.encode(references)
        
        # 코사인 유사도 계산
        similarities = []
        for pred_emb, ref_emb in zip(pred_embeddings, ref_embeddings):
            sim = cosine_similarity([pred_emb], [ref_emb])[0][0]
            similarities.append(sim)
        
        return np.mean(similarities)
    
    def compute_persona_consistency(
        self, 
        predictions: List[str], 
        personas: List[Dict]
    ) -> float:
        """페르소나 일관성 평가"""
        consistency_scores = []
        
        for pred, persona in zip(predictions, personas):
            score = self._evaluate_persona_consistency(pred, persona)
            consistency_scores.append(score)
        
        return np.mean(consistency_scores)
    
    def _evaluate_persona_consistency(self, prediction: str, persona: Dict) -> float:
        """개별 예측의 페르소나 일관성 평가"""
        score = 0.0
        total_checks = 0
        
        # 나이대 적절성 체크
        age = persona.get('age', 25)
        if age < 10:
            # 어린이: 간단한 표현 선호
            if len(prediction.split()) <= 15 and any(word in prediction for word in ['좋아', '싫어', '해요', '이에요']):
                score += 1
        elif age < 18:
            # 청소년: 중간 복잡도
            if 10 <= len(prediction.split()) <= 25:
                score += 1
        else:
            # 성인: 복잡한 표현 가능
            score += 1
        total_checks += 1
        
        # 의사소통 특징 반영 체크
        comm_char = persona.get('communication_characteristics', '')
        if '간단한' in comm_char or '단순한' in comm_char:
            if len(prediction.split()) <= 10:
                score += 1
        elif '상세한' in comm_char or '풍부한' in comm_char:
            if len(prediction.split()) >= 15:
                score += 1
        else:
            score += 0.5  # 중립적인 경우
        total_checks += 1
        
        # 관심 주제 연관성 체크
        interests = persona.get('interesting_topics', [])
        if interests:
            for topic in interests:
                if topic in prediction:
                    score += 1
                    break
            else:
                # 직접적 매칭이 없으면 의미적 유사도 확인
                topic_text = ' '.join(interests)
                sim = self.compute_semantic_similarity([prediction], [topic_text])
                if sim > 0.3:
                    score += 0.5
        total_checks += 1
        
        return score / total_checks if total_checks > 0 else 0.0
    
    def compute_contextual_relevance(
        self, 
        predictions: List[str], 
        contexts: List[str]
    ) -> float:
        """컨텍스트 관련성 평가"""
        relevance_scores = []
        
        for pred, context in zip(predictions, contexts):
            # 컨텍스트와의 의미적 유사도 계산
            sim = self.compute_semantic_similarity([pred], [context])
            relevance_scores.append(sim)
        
        return np.mean(relevance_scores)
    
    def _tokenize(self, text: str) -> List[str]:
        """한국어 토큰화"""
        # 간단한 한국어 토큰화 (공백 기반)
        text = re.sub(r'[^\w\s]', '', text.lower())
        return text.split()
    
    def _get_ngrams(self, tokens: List[str], n: int) -> Counter:
        """N-gram 생성"""
        ngrams = []
        for i in range(len(tokens) - n + 1):
            ngram = ' '.join(tokens[i:i + n])
            ngrams.append(ngram)
        return Counter(ngrams)
    
    def compute_all_metrics(
        self,
        predictions: List[str],
        references: List[str],
        personas: List[Dict] = None,
        contexts: List[str] = None
    ) -> Dict[str, float]:
        """모든 메트릭 계산"""
        metrics = {}
        
        # 기본 텍스트 생성 메트릭
        metrics['bleu-4'] = self.compute_bleu(predictions, references)
        rouge_scores = self.compute_rouge(predictions, references)
        metrics.update(rouge_scores)
        
        # 의미적 유사도
        metrics['semantic_similarity'] = self.compute_semantic_similarity(predictions, references)
        
        # AAC 특화 메트릭
        if personas:
            metrics['persona_consistency'] = self.compute_persona_consistency(predictions, personas)
        
        if contexts:
            metrics['contextual_relevance'] = self.compute_contextual_relevance(predictions, contexts)
        
        return metrics


def calculate_perplexity(loss_values: List[float]) -> float:
    """Perplexity 계산"""
    avg_loss = np.mean(loss_values)
    return np.exp(avg_loss)


def calculate_accuracy(predictions: torch.Tensor, targets: torch.Tensor, ignore_index: int = -100) -> float:
    """토큰 수준 정확도 계산"""
    mask = targets != ignore_index
    correct = (predictions == targets) & mask
    accuracy = correct.sum().float() / mask.sum().float()
    return accuracy.item()