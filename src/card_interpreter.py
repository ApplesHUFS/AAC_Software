from typing import Dict, List, Optional, Any


class CardInterpreter:
    """AAC 카드 해석 시스템 (온라인/오프라인 분기)"""
    
    def __init__(self, config: Optional[Dict] = None):
        pass
    
    def interpret_cards(self, 
                       persona: Dict[str, Any],
                       context: Dict[str, Any],
                       cards: List[str],
                       past_interpretation: str = "") -> Dict[str, Any]:
        """
        AAC 카드 해석
        
        Args:
            persona: 사용자 페르소나 정보
            context: 상황 정보 {
                'time': str,
                'place': str,
                'interaction_partner': str,
                'current_activity': str
            }
            cards: 선택된 카드 리스트 (1-4개)
            past_interpretation: 과거 해석 이력 요약
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'interpretations': List[str],  # 항상 3개
                'method': str,  # 'online' or 'offline'
                'timestamp': str,
                'message': str
            }
        """
        pass
    
    def validate_interpretation_input(self, 
                                   persona: Dict[str, Any],
                                   context: Dict[str, Any],
                                   cards: List[str]) -> Dict[str, Any]:
        """
        해석 입력 데이터 유효성 검사
        
        Args:
            persona: 사용자 페르소나
            context: 상황 정보
            cards: 선택된 카드들
            
        Returns:
            Dict[str, Any]: {
                'valid': bool,
                'errors': List[str]
            }
        """
        pass