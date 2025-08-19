from typing import Dict, List, Optional, Any
import json
import os

class UserManager:
    """사용자 관리를 담당하는 추상화된 클래스"""
    
    def __init__(self, users_file_path: Optional[str] = None):
        self.users_file_path=users_file_path or "users.json"
        self.users={}
        self.next_id=1  # 1부터 user id 시작

        # 기존에 파일이 존재하면 로드하기
        if os.path.exists(self.users_file_path):
            try:
                with open(self.users_file_path, 'r', encoding='utf-8') as f:
                    data=json.load(f)
                    self.users={int(k):v for k,v in data.items()}   # users에 기존 사용자 정보들 저장
                    
                    if self.users:
                        self.next_id=max(self.users.keys()) +1  # 만약 users에 정보가 있다면 다음 user id는 +1
            except Exception as e:
                # 의도: 사용자 데이터 로드 실패 시 명확한 에러로 문제 파악
                print(f"사용자 데이터 파일 로드 실패: {e}")
                self.users={}
                self.next_id=1
    
    def create_user(self, persona: Dict[str, Any]) -> Dict[str, Any]:
        """
        새 사용자 생성
        
        Args:
            persona: 사용자 페르소나 정보 {
                'age': str (필수),
                'gender': str (선택지, 필수),
                'disability_type': str (선택지, 필수),
                'communication_characteristics': str (직접입력, 필수),
                'interesting_topics': List[str] (직접입력, 필수),
                'password': str (필수)
            }
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'user_id': int,
                'message': str
            }
        """
        try:
            # 필수 필드 검증 (데이터셋 스키마 기준)
            required_fields = ['age', 'gender', 'disability_type', 'communication_characteristics', 'interesting_topics', 'password']
            missing_fields = []
            
            for field in required_fields:
                if field not in persona or not persona[field]:
                    missing_fields.append(field)
            
            if missing_fields:
                return {
                    'status': 'error',
                    'user_id': -1,
                    'message': f'필수 필드가 누락되었습니다: {", ".join(missing_fields)}'
                }
            
            # age는 정수형이어야 함 (데이터셋 스키마)
            try:
                age_int = int(persona['age'])
                if age_int < 1 or age_int > 100:
                    raise ValueError("나이 범위 오류")
            except (ValueError, TypeError):
                return {
                    'status': 'error',
                    'user_id': -1,
                    'message': '나이는 1-100 사이의 정수여야 합니다.'
                }
            
            # 선택지 검증 (데이터셋 스키마 기준)
            valid_genders = ['male', 'female']  # 데이터셋 스키마
            valid_disability_types = ['의사소통 장애', '자폐스펙트럼 장애', '지적 장애']  # 데이터셋 스키마
            valid_selection_complexity = ['simple', 'moderate', 'complex']  # 데이터셋 스키마
            
            if persona['gender'] not in valid_genders:
                return {
                    'status': 'error',
                    'user_id': -1,
                    'message': f'성별은 다음 중 하나여야 합니다: {", ".join(valid_genders)}'
                }
            
            if persona['disability_type'] not in valid_disability_types:
                return {
                    'status': 'error',
                    'user_id': -1,
                    'message': f'장애유형은 다음 중 하나여야 합니다: {", ".join(valid_disability_types)}'
                }
            
            # selection_complexity 검증 (있는 경우)
            if 'selection_complexity' in persona and persona['selection_complexity'] not in valid_selection_complexity:
                return {
                    'status': 'error',
                    'user_id': -1,
                    'message': f'선택 복잡도는 다음 중 하나여야 합니다: {", ".join(valid_selection_complexity)}'
                }
            
            # interesting_topics가 리스트인지 확인
            if not isinstance(persona['interesting_topics'], list) or len(persona['interesting_topics']) == 0:
                return {
                    'status': 'error',
                    'user_id': -1,
                    'message': '관심 주제는 최소 1개 이상의 리스트여야 합니다.'
                }
            
            # preferred_category_types 검증 (cluster id 6개, 있는 경우)
            if 'preferred_category_types' in persona:
                if not isinstance(persona['preferred_category_types'], list):
                    return {
                        'status': 'error',
                        'user_id': -1,
                        'message': '선호 카테고리 타입은 리스트여야 합니다.'
                    }
                if len(persona['preferred_category_types']) != 6:
                    return {
                        'status': 'error',
                        'user_id': -1,
                        'message': '선호 카테고리 타입은 정확히 6개의 cluster id여야 합니다.'
                    }
                # cluster id들이 모두 정수인지 확인
                try:
                    cluster_ids = [int(cid) for cid in persona['preferred_category_types']]
                except (ValueError, TypeError):
                    return {
                        'status': 'error',
                        'user_id': -1,
                        'message': '선호 카테고리 타입의 cluster id들은 정수여야 합니다.'
                    }
            
            user_id = self.next_id
            user_data = {
                'id': user_id,
                'age': int(persona['age']),  # 정수로 저장 (데이터셋 스키마)
                'gender': persona['gender'],
                'disability_type': persona['disability_type'],
                'communication_characteristics': persona['communication_characteristics'],
                'selection_complexity': persona.get('selection_complexity', 'moderate'),  # 기본값
                'interesting_topics': persona['interesting_topics'],
                'preferred_category_types': persona.get('preferred_category_types', []),  # 선택사항
                'password': persona['password']
            }

            self.users[user_id]=user_data
            self.next_id+=1 # 다음 user의 id를 위해 +1

            # 파일에 사용자 정보 저장
            try:
                with open(self.users_file_path, 'w') as f:
                    json.dump({k: v for k,v in self.users.items()},f)
                return {
                    'status':'success',
                    'user_id':user_id,
                    'message': f'사용자 {user_id}가 성공적으로 생성되었습니다.'
                }
            except Exception as e: # 의도: 사용자 생성 실패 시 정확한 에러 메시지로 문제 파악
                del self.users[user_id]
                self.next_id-=1
                return {
                    'status': 'error',
                    'user_id': -1,
                    'message': f'사용자 생성 중 파일 저장 실패: {str(e)}'
                }
        except Exception as e:
            return {
                'status': 'error',
                'user_id': -1,
                'message': f'오류가 발생: {str(e)}'
            }
    
    def get_user(self, user_id: int) -> Dict[str, Any]:
        """
        사용자 정보 조회 (비밀번호 제외)
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'user': Dict or None,
                'message': str
            }
        """
        if user_id in self.users:
            # 보안을 위해 비밀번호 제외하고 반환
            user_data = self.users[user_id].copy()
            user_data.pop('password', None)
            
            return {
                'status':'success',
                'user': user_data,
                'message':'사용자 정보를 성공적으로 조회했습니다.'
            }
        else:
            return {
                'status':'error',
                'user':None,
                'message':'사용자 정보를 조회할 수 없습니다.'
            }
    
    
    
    
    def authenticate_user(self, user_id: int, password: str) -> Dict[str, Any]:
        """
        사용자 인증
        
        Args:
            user_id: 사용자 ID
            password: 비밀번호
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'authenticated': bool,
                'message': str
            }
        """
        try:
            if user_id not in self.users:
                return {
                    'status': 'error',
                    'authenticated': False,
                    'message': f'사용자 ID {user_id}를 찾을 수 없습니다.'
                }
            
            # 의도: 평문 비밀번호 검증 (보안상 해싱 필요하지만 현재는 단순 비교)
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
                
        except Exception as e: 
            return {
                'status': 'error',
                'authenticated': False,
                'message': f'오류가 발생했습니다: {str(e)}'
            }
    
