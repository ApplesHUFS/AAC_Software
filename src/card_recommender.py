from typing import Dict, List, Optional, Any


class CardRecommender:
    """페르소나 기반 카드 추천 시스템"""
    
    def __init__(self, 
                 cluster_tags_path: Optional[str] = None,
                 embeddings_path: Optional[str] = None,
                 clustering_results_path: Optional[str] = None):
        pass
    
    
    
    
    
    def recommend_cards(self, persona: Dict[str, Any], num_cards: int = 4) -> Dict[str, Any]:
        """
        페르소나 기반 카드 추천
        
        Args:
            persona: 사용자 페르소나 정보 {
                'interesting_topics': List[str],
                'preferred_category_types': List[int],
                'selection_complexity': str  # 'simple', 'moderate', 'complex'
            }
            num_cards: 추천할 카드 수 (1-4)
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'cards': List[str],
                'clusters_used': List[int],
                'message': str
            }
        """
        pass
    
    def get_cluster_info(self, cluster_id: int) -> Dict[str, Any]:
        """
        특정 클러스터 정보 조회
        
        Args:
            cluster_id: 클러스터 ID
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'cluster_info': Dict or None,
                'message': str
            }
        """
        pass
    
    def get_all_clusters_info(self) -> Dict[str, Any]:
        """
        모든 클러스터 정보 조회
        
        Returns:
            Dict[str, Any]: {
                'status': str,
                'clusters': List[Dict],
                'total_count': int
            }
        """
        pass