from typing import Dict, List, Optional, Any, Tuple
import json
import random
import numpy as np
from pathlib import Path
from .cluster_similarity_calculator import ClusterSimilarityCalculator

class CardRecommender:
    """페르소나 기반 AAC 카드 추천 시스템.

    사용자의 preferred_category_types(클러스터 6개)를 기반으로
    개인화된 AAC 카드를 추천하고, 화면 표시용 카드 선택 인터페이스를 제공합니다.

    Attributes:
        clustered_files: 클러스터 ID별 카드 파일 리스트
        all_cards: 전체 카드 리스트
        config: 설정 딕셔너리
        recommendation_history: 컨텍스트별 추천 히스토리
        cluster_calculator: 클러스터 유사도 계산기
        cluster_tags: 클러스터별 태그 정보
        n_clusters: 전체 클러스터 개수
    """

    def __init__(self, clustering_results_path: str, config: Dict[str, Any]):
        """CardRecommender 초기화.

        Args:
            clustering_results_path: 클러스터링 결과 JSON 파일 경로
            config: 설정 딕셔너리
        """
        self.config = config
        self.clustered_files = {}
        self.all_cards = []
        self.recommendation_history = {}
        
        # 클러스터 유사도 계산기 초기화
        self.cluster_calculator = ClusterSimilarityCalculator(
            cluster_tags_path=self.config['cluster_tags_path'],
            config=self.config
        )
        
        # 클러스터 태그 로드
        self._load_cluster_tags()
        
        # 클러스터링 결과 데이터 로드
        if Path(clustering_results_path).exists():
            with open(clustering_results_path, 'r', encoding='utf-8') as f:
                cluster_data = json.load(f)
            self.clustered_files = {int(k): v for k, v in cluster_data['clustered_files'].items()}
            self.all_cards = cluster_data.get('filenames', [])
            self.n_clusters = max(cluster_data["cluster_labels"]) + 1
        else:
            raise FileNotFoundError(f'클러스터링 결과 파일이 필요합니다: {clustering_results_path}')

    def _load_cluster_tags(self):
        """클러스터 태그 정보를 로드합니다."""
        try:
            cluster_tags_path = self.config.get('cluster_tags_path')
            if Path(cluster_tags_path).exists():
                with open(cluster_tags_path, 'r', encoding='utf-8') as f:
                    self.cluster_tags = {int(k): v for k, v in json.load(f).items()}
            else:
                self.cluster_tags = {}
        except Exception as e:
            print(f"클러스터 태그 로드 실패: {e}")
            self.cluster_tags = {}

    def get_card_selection_interface(self, persona: Dict[str, Any], context: Dict[str, Any], context_id: str) -> Dict[str, Any]:
        """화면 표시용 카드 선택 인터페이스 데이터 생성.

        페르소나와 상황의 의미적 유사도를 계산하여 최적의 카드 조합을 추천합니다.

        Args:
            persona: 사용자 페르소나 정보 중 일부 (preferred_category_types)
            context: 현재 상황 정보
            context_id: 현재 상황 정보 ID

        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - interface_data (Dict): 선택 인터페이스 데이터
                - message (str): 결과 메시지
        """
        try:
            # 설정값 조회
            total_cards = self.config.get('display_cards_total')
            context_ratio = self.config.get('context_persona_ratio')
            
            # 히스토리 초기화
            if context_id not in self.recommendation_history:
                self.recommendation_history[context_id] = []

            # 상황 기반 카드 추천
            context_cards = self._select_context_based_cards(context, int(total_cards * context_ratio))
            
            # 페르소나 기반 카드 추천
            persona_cards = self._select_persona_based_cards(persona, int(total_cards * (1 - context_ratio)))
            
            # 카드 조합 및 중복 제거
            all_selection_cards = self._combine_card_selections(
                context_cards, persona_cards, total_cards
            )
            
            # 카드 순서 섞기
            random.shuffle(all_selection_cards)

            # 추천 히스토리에 추가
            self._add_to_recommendation_history(context_id, all_selection_cards)

            # 인터페이스 데이터 구성
            interface_data = {
                'selection_options': all_selection_cards,
                'context_info': {
                    'time': context.get('time'),
                    'place': context.get('place'),
                    'interaction_partner': context.get('interaction_partner'),
                    'current_activity': context.get('current_activity')
                },
                'selection_rules': {
                    'min_cards': self.config.get('min_card_selection'),
                    'max_cards': self.config.get('max_card_selection'),
                    'total_options': len(all_selection_cards)
                },
                'total_pages': self.recommendation_history[context_id][-1]['page_number']
            }

            place = context.get('place', '알 수 없는 장소')
            activity_info = f" ({context.get('current_activity')} 활동 고려)" if context.get('current_activity') else ""
            
            return {
                'status': 'success',
                'interface_data': interface_data,
                'message': f'{place}에서의 대화를 위한 {total_cards}개 카드가 상황과 페르소나를 고려하여 준비되었습니다{activity_info}'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'interface_data': {},
                'message': f'카드 선택 인터페이스 생성 중 시스템 오류가 발생했습니다: {str(e)}'
            }

    def _select_context_based_cards(self, context: Dict[str, Any], target_count: int) -> List[str]:
        """현재 상황과 관련된 카드를 선택합니다.
        
        Args:
            context: 현재 상황 정보
            target_count: 목표 카드 수
            
        Returns:
            List[str]: 상황 기반 추천 카드 리스트
        """
        context_keywords = []
        
        # 상황 키워드 수집
        place = context.get('place', '').strip()
        activity = context.get('current_activity', '').strip()
        
        if place:
            context_keywords.append(place)
        if activity:
            context_keywords.append(activity)
            
        if not context_keywords:
            return self._select_random_cards([], target_count)
        
        try:
            # 상황과 관련성 높은 클러스터 찾기
            relevant_clusters = self._find_similar_clusters(
                context_keywords, 
                similarity_threshold=self.config.get('context_similarity_threshold'),
                max_clusters=self.config.get('context_max_clusters')
            )
            
            # 관련성 점수로 가중 선택
            selected_cards = self._select_cards_from_clusters(
                relevant_clusters, target_count
            )
            
            return selected_cards
            
        except Exception as e:
            print(f'상황 기반 카드 선택 중 오류: {e}')
            return self._select_random_cards([], target_count)

    def _select_persona_based_cards(self, persona: Dict[str, Any], target_count: int) -> List[str]:
        """사용자 페르소나에 기반한 카드를 선택합니다.
        
        Args:
            persona: 사용자 페르소나 정보
            target_count: 목표 카드 수
            
        Returns:
            List[str]: 페르소나 기반 추천 카드 리스트
        """
        preferred_clusters = persona.get('preferred_category_types', [])
        
        if not preferred_clusters:
            return self._select_random_cards([], target_count)
        
        # 선호 클러스터에서 균등하게 선택
        return self._select_from_preferred_clusters(preferred_clusters, target_count)

    def _find_similar_clusters(self, keywords: List[str], similarity_threshold: float, max_clusters: int) -> List[Tuple[int, float]]:
        """키워드와 의미적으로 유사한 클러스터를 찾습니다.
        
        Args:
            keywords: 검색할 키워드 리스트
            similarity_threshold: 유사도 임계값
            max_clusters: 최대 클러스터 수
            
        Returns:
            List[Tuple[int, float]]: (클러스터_ID, 유사도_점수) 리스트
        """
        cluster_similarities = {}
        
        for cluster_id, cluster_tags in self.cluster_tags.items():
            if not cluster_tags:
                continue
                
            # 클러스터 태그와 키워드 간 최대 유사도 계산
            max_similarity = 0.0
            for keyword in keywords:
                for tag in cluster_tags:
                    try:
                        similarity = self.cluster_calculator.compute_topic_similarity(keyword, tag)
                        max_similarity = max(max_similarity, similarity)
                    except:
                        continue
                        
            if max_similarity >= similarity_threshold:
                cluster_similarities[cluster_id] = max_similarity
        
        # 유사도 순으로 정렬하여 상위 클러스터 반환
        sorted_clusters = sorted(cluster_similarities.items(), key=lambda x: x[1], reverse=True)
        return sorted_clusters[:max_clusters]

    def _select_cards_from_clusters(self, cluster_scores: List[Tuple[int, float]], target_count: int) -> List[str]:
        """클러스터 점수에 따라 가중치를 적용하여 카드를 선택합니다.
        
        Args:
            cluster_scores: (클러스터_ID, 점수) 리스트
            target_count: 목표 카드 수
            
        Returns:
            List[str]: 선택된 카드 리스트
        """
        if not cluster_scores:
            return []
            
        selected_cards = []
        total_score = sum(score for _, score in cluster_scores)
        
        for cluster_id, score in cluster_scores:
            cluster_cards = self.clustered_files.get(cluster_id, [])
            if not cluster_cards:
                continue
                
            # 점수 비례 카드 수 계산
            cards_from_cluster = max(1, int((score / total_score) * target_count))
            cards_from_cluster = min(cards_from_cluster, len(cluster_cards))
            
            # 클러스터에서 랜덤 선택
            available_cards = [card for card in cluster_cards if card not in selected_cards]
            if available_cards:
                selected_count = min(cards_from_cluster, len(available_cards))
                selected_cards.extend(random.sample(available_cards, selected_count))
                
            if len(selected_cards) >= target_count:
                break
                
        return selected_cards[:target_count]

    def _combine_card_selections(self, context_cards: List[str], persona_cards: List[str], total_count: int) -> List[str]:
        """두 카드 리스트를 조합하여 중복을 제거하고 목표 수에 맞춥니다.
        
        Args:
            context_cards: 상황 기반 카드
            persona_cards: 페르소나 기반 카드  
            total_count: 총 카드 수
            
        Returns:
            List[str]: 최종 카드 리스트
        """
        combined_cards = []
        used_cards = set()
        
        # 중복 제거하면서 추가
        for card in context_cards:
            if card not in used_cards and len(combined_cards) < total_count:
                combined_cards.append(card)
                used_cards.add(card)
                
        for card in persona_cards:
            if card not in used_cards and len(combined_cards) < total_count:
                combined_cards.append(card)
                used_cards.add(card)
        
        # 부족한 카드 수만큼 랜덤 카드 추가
        remaining_count = total_count - len(combined_cards)
        if remaining_count > 0:
            additional_cards = self._select_random_cards(list(used_cards), remaining_count)
            combined_cards.extend(additional_cards)
            
        return combined_cards[:total_count]

    def _select_from_preferred_clusters(self, preferred_clusters: List[int], num_cards: int) -> List[str]:
        """선호 클러스터에서 카드를 골고루 선택합니다.

        Args:
            preferred_clusters: 선호 클러스터 ID 리스트
            num_cards: 선택할 카드 수

        Returns:
            List[str]: 선택된 카드 파일명들
        """
        selected_cards = []
        
        if not preferred_clusters:
            return self._select_random_cards([], num_cards)

        # 각 클러스터에서 순환하면서 카드 선택
        cluster_index = 0
        cards_per_cluster = {cluster_id: 0 for cluster_id in preferred_clusters}

        while len(selected_cards) < num_cards and cluster_index < self.n_clusters:
            cluster_id = preferred_clusters[cluster_index % len(preferred_clusters)]
            cluster_cards = self.clustered_files.get(cluster_id, [])

            if not cluster_cards:
                cluster_index += 1
                continue

            # 이미 선택된 카드와 중복되지 않는 카드 찾기
            available_cards = [card for card in cluster_cards if card not in selected_cards]

            if available_cards:
                selected_card = random.choice(available_cards)
                selected_cards.append(selected_card)
                cards_per_cluster[cluster_id] += 1

            cluster_index += 1

        return selected_cards

    def _select_random_cards(self, exclude_cards: List[str], num_cards: int) -> List[str]:
        """전체 카드에서 랜덤으로 선택합니다.

        Args:
            exclude_cards: 제외할 카드들
            num_cards: 선택할 카드 수

        Returns:
            List[str]: 선택된 랜덤 카드들
        """
        available_cards = [card for card in self.all_cards if card not in exclude_cards]

        if len(available_cards) <= num_cards:
            return available_cards

        return random.sample(available_cards, num_cards)

    def validate_card_selection(self, selected_cards: List[str], available_options: List[str]) -> Dict[str, Any]:
        """사용자 카드 선택 유효성을 검증합니다.

        Args:
            selected_cards: 사용자가 선택한 카드들
            available_options: 선택 가능한 카드 옵션들

        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - valid (bool): 유효성 여부
                - message (str): 결과 메시지
        """
        min_cards = self.config.get('min_card_selection')
        max_cards = self.config.get('max_card_selection')

        # 입력 검증
        if not selected_cards:
            return {
                'status': 'error',
                'valid': False,
                'message': '선택된 카드가 없습니다. 카드를 선택해주세요.'
            }

        if not available_options:
            return {
                'status': 'error',
                'valid': False,
                'message': '선택 가능한 카드 옵션 정보가 없습니다.'
            }

        # 선택 카드 수 검증
        if len(selected_cards) < min_cards:
            return {
                'status': 'error',
                'valid': False,
                'message': f'최소 {min_cards}개 이상의 카드를 선택해야 합니다. 현재 {len(selected_cards)}개가 선택되었습니다.'
            }

        if len(selected_cards) > max_cards:
            return {
                'status': 'error',
                'valid': False,
                'message': f'최대 {max_cards}개까지만 선택할 수 있습니다. 현재 {len(selected_cards)}개가 선택되었습니다.'
            }

        # 중복 선택 검증
        if len(selected_cards) != len(set(selected_cards)):
            return {
                'status': 'error',
                'valid': False,
                'message': '중복된 카드를 선택할 수 없습니다. 서로 다른 카드를 선택해주세요.'
            }

        # 선택 가능한 옵션 내에서 선택했는지 검증
        invalid_cards = [card for card in selected_cards if card not in available_options]
        if invalid_cards:
            return {
                'status': 'error',
                'valid': False,
                'message': f'선택할 수 없는 카드가 포함되어 있습니다: {", ".join(invalid_cards[:3])}{"..." if len(invalid_cards) > 3 else ""}'
            }

        return {
            'status': 'success',
            'valid': True,
            'message': f'{len(selected_cards)}개 카드가 성공적으로 선택되어 해석 준비가 완료되었습니다.'
        }

    def _add_to_recommendation_history(self, context_id: str, cards: List[str]) -> Dict[str, Any]:
        """카드 추천 히스토리에 추가합니다.

        Args:
            context_id: 컨텍스트 ID
            cards: 추천된 카드 리스트

        Returns:
            Dict containing:
                - status (str): 'success'
                - page_number (int): 추가된 페이지 번호
                - total_pages (int): 총 페이지 수
        """
        from datetime import datetime

        # 추천 결과 추가
        recommendation_entry = {
            'page_number': len(self.recommendation_history[context_id]) + 1,
            'cards': cards,
            'timestamp': datetime.now().isoformat()
        }

        self.recommendation_history[context_id].append(recommendation_entry)

        return {
            'status': 'success',
            'page_number': recommendation_entry['page_number'],
            'total_pages': len(self.recommendation_history[context_id])
        }

    def get_recommendation_history_page(self, context_id: str, page_number: int) -> Dict[str, Any]:
        """카드 추천 히스토리의 특정 페이지를 조회합니다.

        Args:
            context_id: 컨텍스트 ID
            page_number: 조회할 페이지 번호 (1-based)

        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - cards (List[str]): 카드 리스트
                - page_number (int): 현재 페이지 번호
                - total_pages (int): 총 페이지 수
                - timestamp (str): 생성 시간
                - message (str): 결과 메시지
        """
        if not context_id or not context_id.strip():
            return {
                'status': 'error',
                'cards': [],
                'page_number': 0,
                'total_pages': 0,
                'timestamp': '',
                'message': '컨텍스트 ID가 제공되지 않았습니다.'
            }

        if context_id not in self.recommendation_history:
            self.recommendation_history[context_id] = []

        history = self.recommendation_history[context_id]

        if not history:
            return {
                'status': 'error',
                'cards': [],
                'page_number': 0,
                'total_pages': 0,
                'timestamp': '',
                'message': f'컨텍스트 {context_id}에 대한 카드 추천 히스토리가 없습니다.'
            }
        
        total_pages = len(history)

        # 페이지 번호 검증
        if page_number < 1 or page_number > total_pages:
            return {
                'status': 'error',
                'cards': [],
                'page_number': 0,
                'total_pages': total_pages,
                'timestamp': '',
                'message': f'페이지 번호가 유효 범위(1-{total_pages})를 벗어났습니다. 페이지 {page_number}는 존재하지 않습니다.'
            }

        # 페이지 정보 반환
        page_data = history[page_number - 1]
        return {
            'status': 'success',
            'cards': page_data['cards'],
            'page_number': page_number,
            'total_pages': total_pages,
            'timestamp': page_data['timestamp'],
            'message': f'컨텍스트 {context_id}의 {page_number}번째 카드 추천 페이지를 조회했습니다 (총 {len(page_data["cards"])}개 카드)'
        }

    def get_recommendation_history_summary(self, context_id: str) -> Dict[str, Any]:
        """카드 추천 히스토리의 요약 정보를 조회합니다.

        Args:
            context_id: 컨텍스트 ID

        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - total_pages (int): 총 페이지 수
                - latest_page (int): 최신 페이지 번호
                - history_summary (List[Dict]): 페이지별 요약 정보
                - message (str): 결과 메시지
        """
        # 히스토리 존재 여부 확인
        if context_id not in self.recommendation_history:
            return {
                'status': 'error',
                'total_pages': 0,
                'latest_page': 0,
                'history_summary': [],
                'message': f'컨텍스트 {context_id}에 대한 카드 추천 히스토리가 없습니다.'
            }

        history = self.recommendation_history[context_id]
        total_pages = len(history)

        if total_pages == 0:
            return {
                'status': 'error',
                'total_pages': 0,
                'latest_page': 0,
                'history_summary': [],
                'message': f'컨텍스트 {context_id}에 추천된 카드가 없습니다.'
            }

        # 페이지별 요약 정보 생성
        history_summary = []
        for i, entry in enumerate(history):
            history_summary.append({
                'page_number': i + 1,
                'card_count': len(entry['cards']),
                'timestamp': entry['timestamp']
            })

        return {
            'status': 'success',
            'total_pages': total_pages,
            'latest_page': total_pages,
            'history_summary': history_summary,
            'message': f'컨텍스트 {context_id}의 카드 추천 히스토리 요약: 총 {total_pages}번의 추천이 진행되었습니다.'
        }