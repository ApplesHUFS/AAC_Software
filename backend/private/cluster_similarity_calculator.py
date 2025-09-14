import json
import torch
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any
from sentence_transformers import SentenceTransformer
from tqdm import tqdm


class ClusterSimilarityCalculator:
    """클러스터 유사도 계산기.

    사용자의 interesting_topics와 클러스터 태그들 간의 유사도를 계산하여
    preferred_category_types를 생성합니다.

    Attributes:
        similarity_model: 문장 임베딩 모델
        cluster_tags: 클러스터 ID별 태그 리스트
        device: 연산 디바이스
        config: 설정 딕셔너리
    """

    def __init__(self, cluster_tags_path: str, config: Optional[Dict] = None):
        """ClusterSimilarityCalculator 초기화.

        Args:
            cluster_tags_path: 클러스터 태그 JSON 파일 경로
            config: 설정 딕셔너리

        Raises:
            FileNotFoundError: 클러스터 태그 파일이 없는 경우
            RuntimeError: 모델 초기화 실패시
        """
        self.config = config or {}
        self.cluster_tags = {}

        try:
            # 디바이스 설정
            device_setting = self.config.get('device', 'auto')
            if device_setting == 'auto':
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            else:
                self.device = device_setting

            # 문장 임베딩 모델 로드
            similarity_model_name = self.config.get('similarity_model')
            self.similarity_model = SentenceTransformer(similarity_model_name, device=self.device)

            # 클러스터 태그 데이터 로드
            self._load_cluster_tags(cluster_tags_path)
            
        except Exception as e:
            raise RuntimeError(f"ClusterSimilarityCalculator 초기화 실패: {str(e)}")

    def _load_cluster_tags(self, cluster_tags_path: str):
        """클러스터 태그 파일 로드.

        Args:
            cluster_tags_path: 클러스터 태그 JSON 파일 경로

        Raises:
            FileNotFoundError: 파일이 존재하지 않는 경우
        """
        if not Path(cluster_tags_path).exists():
            raise FileNotFoundError(f'클러스터 태그 파일이 필요합니다: {cluster_tags_path}')

        try:
            with open(cluster_tags_path, 'r', encoding='utf-8') as f:
                cluster_tags_raw = json.load(f)
            self.cluster_tags = {int(k): v for k, v in cluster_tags_raw.items()}
        except Exception as e:
            raise FileNotFoundError(f'클러스터 태그 파일 로드 실패: {str(e)}')

    def compute_topic_similarities_batch(self, topics1: List[str], topics2: List[str]) -> np.ndarray:
        """두 주제 리스트 간의 배치 유사도 계산.

        Args:
            topics1: 첫 번째 주제 리스트
            topics2: 두 번째 주제 리스트

        Returns:
            np.ndarray: 유사도 행렬 (0~1 범위)

        Raises:
            ValueError: 입력이 비어있는 경우
            RuntimeError: 유사도 계산 실패시

        Example:
            similarities = [
                #   0    1    2    3    4    5    6    7    8    9    10 -> cluster id
                [0.8, 0.9, 0.7, 0.2, 0.3, 0.1, 0.4, 0.5, 0.3, 0.85, 0.75],  # interesting topic 1
                [0.3, 0.4, 0.5, 0.8, 0.9, 0.7, 0.2, 0.1, 0.3, 0.35, 0.45],  # interesting topic 2
                [0.1, 0.2, 0.1, 0.3, 0.2, 0.4, 0.9, 0.8, 0.7, 0.15, 0.25]   # interesting topic 3
            ]
        """
        try:
            if not topics1 or not topics2:
                raise ValueError("topics1 또는 topics2가 비어 있습니다.")

            # 임베딩 생성 및 유사도 계산
            embeddings1 = self.similarity_model.encode(topics1, convert_to_tensor=True)
            embeddings2 = self.similarity_model.encode(topics2, convert_to_tensor=True)
            similarities = torch.mm(embeddings1, embeddings2.T)
            
            # -1~1 범위를 0~1 범위로 정규화
            similarities = (similarities + 1) / 2

            return similarities.cpu().numpy()

        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"배치 유사도 계산 오류: {str(e)}")

    def compute_topic_similarity(self, topic1: str, topic2: str) -> float:
        """두 토픽 간 유사도 계산.
        
        내부적으로 compute_topic_similarities_batch를 사용하여 일관성을 유지합니다.

        Args:
            topic1: 첫 번째 토픽
            topic2: 두 번째 토픽

        Returns:
            float: 유사도 점수 (0~1 범위)
        """
        try:
            similarities = self.compute_topic_similarities_batch([topic1], [topic2])
            return float(similarities[0, 0])
        except Exception:
            return 0.0

    def calculate_preferred_categories(self, interesting_topics: List[str],
                                     similarity_threshold: float = 0.3,
                                     max_categories: int = 6) -> List[int]:
        """사용자의 관심 주제를 기반으로 선호 카테고리 계산.

        Args:
            interesting_topics: 사용자의 관심 주제 리스트
            similarity_threshold: 유사도 임계값 (0.0-1.0)
            max_categories: 최대 카테고리 수

        Returns:
            List[int]: 선호 클러스터 ID 리스트 (유사도 높은 순)

        Raises:
            RuntimeError: 계산 과정에서 오류 발생시
        """
        try:
            # 모든 클러스터 태그를 하나의 리스트로 만들고 클러스터 매핑 정보 생성
            all_cluster_topics = []
            cluster_topic_mapping = []

            for cluster_id, cluster_topics in self.cluster_tags.items():
                for topic in cluster_topics:
                    all_cluster_topics.append(topic)
                    cluster_topic_mapping.append(cluster_id)

            # 토픽들과 태그들 유사도 계산
            similarities = self.compute_topic_similarities_batch(interesting_topics, all_cluster_topics)

            # 클러스터별 최대 유사도 계산
            cluster_max_similarities = {}
            for i, cluster_id in enumerate(cluster_topic_mapping):
                max_sim = float(similarities[:, i].max())
                if cluster_id not in cluster_max_similarities or max_sim > cluster_max_similarities[cluster_id]:
                    cluster_max_similarities[cluster_id] = max_sim

            # 임계값 이상의 클러스터 선택 및 유사도 순 정렬
            candidates = [(cluster_id, sim) for cluster_id, sim in cluster_max_similarities.items()
                         if sim >= similarity_threshold]

            candidates.sort(key=lambda x: x[1], reverse=True)
            preferred_categories = [cluster_id for cluster_id, _ in candidates[:max_categories]]

            # 충분하지 않다면 유사도가 낮더라도 추가
            if len(preferred_categories) < max_categories:
                remaining_clusters = [(cluster_id, sim) for cluster_id, sim in cluster_max_similarities.items()
                                    if cluster_id not in preferred_categories]
                remaining_clusters.sort(key=lambda x: x[1], reverse=True)

                needed_count = max_categories - len(preferred_categories)
                additional_clusters = [cluster_id for cluster_id, _ in remaining_clusters[:needed_count]]
                preferred_categories.extend(additional_clusters)

            return preferred_categories[:max_categories]

        except Exception as e:
            raise RuntimeError(f"선호 카테고리 계산 중 오류 발생: {str(e)}")