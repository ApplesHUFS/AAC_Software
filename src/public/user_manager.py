from typing import Dict, List, Optional, Any
import json
import os
from ..private.cluster_similarity_calculator import ClusterSimilarityCalculator


class UserManager:
    """사용자 페르소나 및 계정 관리 시스템.
    
    AAC 시스템 사용자의 페르소나 정보를 관리하고 인증을 처리합니다.
    페르소나는 개인화된 카드 추천과 해석에 핵심적으로 사용됩니다.
    
    Attributes:
        users_file_path: 사용자 데이터 저장 파일 경로
        users: 메모리상 사용자 데이터 딕셔너리
        next_id: 다음 사용자 ID
        config: 설정 딕셔너리
    """
    
    def __init__(self, users_file_path: Optional[str] = None, config: Optional[Dict] = None):
        """UserManager 초기화.
        
        Args:
            users_file_path: 사용자 데이터 파일 경로. None이면 기본값 사용.
            config: 설정 딕셔너리. None이면 기본값 사용.
        """
        self.users_file_path = users_file_path or "user_data/users.json"
        self.config = config or {}
        self.users = {}
        self.next_id = 1  # 사용자 ID는 1부터 시작

        # 클러스터 유사도 계산기 초기화
        cluster_tags_path = self.config.get('cluster_tags_path', 'dataset/processed/cluster_tags.json')
        try:
            self.cluster_calculator = ClusterSimilarityCalculator(cluster_tags_path, self.config)
        except FileNotFoundError as e:
            print(f"경고: {e}. preferred_category_types 계산 기능이 비활성화됩니다.")
            self.cluster_calculator = None

        # 기존 사용자 데이터 로드
        self._load_users()
    
    def _load_users(self):
        """사용자 데이터 파일 로드."""
        if os.path.exists(self.users_file_path):
            try:
                with open(self.users_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.users = {int(k): v for k, v in data.items()}
                    
                    if self.users:
                        self.next_id = max(self.users.keys()) + 1
            except Exception as e:
                print(f"사용자 데이터 파일 로드 실패: {e}")
                self.users = {}
                self.next_id = 1
    
    def _save_users(self):
        """사용자 데이터를 파일에 저장."""
        try:
            os.makedirs(os.path.dirname(self.users_file_path), exist_ok=True)
            with open(self.users_file_path, 'w', encoding='utf-8') as f:
                json.dump({str(k): v for k, v in self.users.items()}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise Exception(f'사용자 데이터 저장 실패: {str(e)}')
    
    def create_user(self, persona: Dict[str, Any]) -> Dict[str, Any]:
        """새 사용자 생성 및 페르소나 등록.
        
        데이터셋 스키마에 맞는 페르소나 정보를 검증하고 사용자를 생성합니다.
        preferred_category_types는 interesting_topics와 클러스터 태그의 유사도를 계산하여 자동 생성됩니다.
        
        Args:
            persona: 사용자 페르소나 정보. 다음 필드들이 필수:
                - age (int): 사용자 나이 (1-100)
                - gender (str): 성별 ('male' 또는 'female')
                - disability_type (str): 장애 유형
                  ('의사소통 장애', '자폐스펙트럼 장애', '지적 장애')
                - communication_characteristics (str): 의사소통 특징
                - interesting_topics (List[str]): 관심 주제 목록
                - password (str): 사용자 비밀번호
                
        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - user_id (int): 생성된 사용자 ID (-1 if error)
                - message (str): 결과 메시지
        """
        # 입력 검증
        validation_result = self._validate_persona(persona)
        if not validation_result['valid']:
            return {
                'status': 'error',
                'user_id': -1,
                'message': validation_result['message']
            }
        
        try:
            user_id = self.next_id
            
            # preferred_category_types 계산 (interesting_topics 기반)
            preferred_category_types = self._calculate_preferred_categories(persona['interesting_topics'])
            
            user_data = {
                'age': int(persona['age']),
                'gender': persona['gender'],
                'disability_type': persona['disability_type'],
                'communication_characteristics': persona['communication_characteristics'],
                'interesting_topics': persona['interesting_topics'],
                'preferred_category_types': preferred_category_types,
                'password': persona['password']
            }

            self.users[user_id] = user_data
            self.next_id += 1

            # 파일에 사용자 정보 저장
            self._save_users()
            
            return {
                'status': 'success',
                'user_id': user_id,
                'message': f'사용자 {user_id}가 성공적으로 생성되었습니다.'
            }
            
        except Exception as e:
            # 실패시 롤백
            if user_id in self.users:
                del self.users[user_id]
                self.next_id -= 1
            
            return {
                'status': 'error',
                'user_id': -1,
                'message': f'사용자 생성 중 오류 발생: {str(e)}'
            }
    
    def _validate_persona(self, persona: Dict[str, Any]) -> Dict[str, Any]:
        """페르소나 정보 유효성 검증.
        
        Args:
            persona: 검증할 페르소나 정보
            
        Returns:
            Dict containing:
                - valid (bool): 유효성 여부
                - message (str): 결과 메시지
        """
        # 필수 필드 검증
        required_fields = [
            'age', 'gender', 'disability_type', 
            'communication_characteristics', 'interesting_topics', 'password'
        ]
        missing_fields = [field for field in required_fields 
                        if field not in persona or not persona[field]]
        
        if missing_fields:
            return {
                'valid': False,
                'message': f'필수 필드가 누락되었습니다: {", ".join(missing_fields)}'
            }
        
        # 나이 검증
        min_age = self.config.get('min_age', 1)
        max_age = self.config.get('max_age', 100)
        try:
            age_int = int(persona['age'])
            if age_int < min_age or age_int > max_age:
                raise ValueError("나이 범위 오류")
        except (ValueError, TypeError):
            return {
                'valid': False,
                'message': f'나이는 {min_age}-{max_age} 사이의 정수여야 합니다.'
            }
        
        # 선택지 검증
        valid_genders = self.config.get('valid_genders', ['male', 'female'])
        valid_disability_types = self.config.get('valid_disability_types', 
                                               ['의사소통 장애', '자폐스펙트럼 장애', '지적 장애'])
        
        if persona['gender'] not in valid_genders:
            return {
                'valid': False,
                'message': f'성별은 다음 중 하나여야 합니다: {", ".join(valid_genders)}'
            }
        
        if persona['disability_type'] not in valid_disability_types:
            return {
                'valid': False,
                'message': f'장애유형은 다음 중 하나여야 합니다: {", ".join(valid_disability_types)}'
            }
        
        # 관심 주제 검증
        if not isinstance(persona['interesting_topics'], list) or len(persona['interesting_topics']) == 0:
            return {
                'valid': False,
                'message': '관심 주제는 최소 1개 이상의 리스트여야 합니다.'
            }
        
        return {
            'valid': True,
            'message': '페르소나 검증 완료'
        }
    
    def _calculate_preferred_categories(self, interesting_topics: List[str]) -> List[int]:
        """관심 주제를 기반으로 선호 클러스터 계산.
        
        Args:
            interesting_topics: 사용자의 관심 주제 리스트
            
        Returns:
            List[int]: 선호 클러스터 ID 리스트 (최대 6개)
        """
        if self.cluster_calculator is None:
            # 클러스터 계산기가 없으면 기본값 반환
            cluster_count = self.config.get('cluster_count', 6)
            required_cluster_count = self.config.get('required_cluster_count', 6)
            return list(range(min(cluster_count, required_cluster_count)))
        
        similarity_threshold = self.config.get('similarity_threshold', 0.3)
        required_cluster_count = self.config.get('required_cluster_count', 6)
        
        return self.cluster_calculator.calculate_preferred_categories(
            interesting_topics=interesting_topics,
            similarity_threshold=similarity_threshold,
            max_categories=required_cluster_count
        )
    
    def get_user(self, user_id: int) -> Dict[str, Any]:
        """사용자 정보 조회 (비밀번호 제외).
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - user (Dict): 사용자 정보 (성공시)
                - message (str): 결과 메시지
        """
        if user_id in self.users:
            # 보안을 위해 비밀번호 제외하고 반환
            user_data = self.users[user_id].copy()
            user_data.pop('password', None)
            
            return {
                'status': 'success',
                'user': user_data,
                'message': '사용자 정보를 성공적으로 조회했습니다.'
            }
        else:
            return {
                'status': 'error',
                'user': None,
                'message': f'사용자 ID {user_id}를 찾을 수 없습니다.'
            }
    
    def authenticate_user(self, user_id: int, password: str) -> Dict[str, Any]:
        """사용자 인증.
        
        Args:
            user_id: 사용자 ID
            password: 비밀번호
            
        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - authenticated (bool): 인증 성공 여부
                - message (str): 결과 메시지
        """
        if user_id not in self.users:
            return {
                'status': 'error',
                'authenticated': False,
                'message': f'사용자 ID {user_id}를 찾을 수 없습니다.'
            }
        
        user_password = self.users[user_id]['password']
        if user_password == password:
            return {
                'status': 'success',
                'authenticated': True,
                'message': '인증이 성공했습니다.'
            }
        else:
            return {
                'status': 'error',
                'authenticated': False,
                'message': '비밀번호가 올바르지 않습니다.'
            }