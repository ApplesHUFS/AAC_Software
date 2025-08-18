from typing import Dict, List, Optional, Any
import json
import os

class UserManager:
    """사용자 관리를 담당하는 추상화된 클래스"""
    
    def __init__(self, users_file_path: Optional[str] = None):
        self.users_file_path=users_file_path or "users.json"
        self.users={}
        self.next_id=0  # 1부터 user id 시작

        # 기존에 파일이 존재하면 로드하기
        if os.path.exists(self.users_file_path):
            try:
                with open(self.users_file_path, 'r', encoding='utf-8') as f:
                    data=json.load(f)
                    self.users={int(k):v for k,v in data.items()}   # users에 기존 사용자 정보들 저장
                    
                    if self.users:
                        self.next_id=max(self.users.keys()) +1  # 만약 users에 정보가 있다면 다음 user id는 +1
            except:
                self.users={}
                self.next_id=1
    
    #                                               # 키(문자열) / 값(딕셔너리)
    def create_user(self, persona: Dict[str, Any]) -> Dict[str, Any]:
        """
        새 사용자 생성
        
        Args:
            persona: 사용자 페르소나 정보 {
                'age': str,
                'gender': str,
                'disability_type': str,
                'communication_characteristics': str,
                'selection_complexity': str,
                'interesting_topics': List[str],
                'password': str
            }
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'user_id': int,
                'message': str
            }
        """
        try:
            user_id=self.next_id
            user_data={
                'id': user_id,
                'age': persona.get('age', ''),
                'gender': persona.get('gender', ''),
                'disability_type': persona.get('disability_type', ''),
                'communication_characteristics': persona.get('communication_characteristics', ''),
                'selection_complexity': persona.get('selection_complexity', ''),
                'interesting_topics': persona.get('interesting_topics', []),
                'password': persona.get('password', '')
            }   # user 정보 안에 usser_id도 들어 있음

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
            except: # 실패할 경우 아예 해당 사용자 정보를 삭제
                del self.users[user_id]
                self.next_id-=1
                return {
                    'status': 'error',
                    'user_id': -1,
                    'message': '오류가 발생했습니다.'
                }
        except Exception as e:
            return {
                'status': 'error',
                'user_id': -1,
                'message': f'오류가 발생: {str(e)}'
            }
    
    def get_user(self, user_id: int) -> Dict[str, Any]:
        """
        사용자 정보 조회
        
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
            return {
                'status':'success',
                'user':self.users[user_id], # user_id가 존재한다면 사용자 정보 가져오기 (비밀번호까지 포함되어 있음) -> pw 제외하는 방향으로 수정하기
                'message':'사용자 정보를 성공적으로 조회했습니다.'
            }
        else:
            return {
                'status':'error',
                'user':None,
                'message':'사용자 정보를 조회할 수 없습니다.'
            }
    
    def update_user_persona(self, user_id: int, persona: Dict[str, Any]) -> Dict[str, Any]:
        """
        사용자 페르소나 정보 업데이트
        
        Args:
            user_id: 사용자 ID
            persona: 업데이트할 페르소나 정보
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'message': str
            }
        """
        try:    # 사용자 정보 확인
            if user_id not in self.users:
                return {
                    'status': 'error',
                    'message': f'사용자 ID {user_id}를 찾을 수 없습니다.'
                }
            
            # 업데이트 가능한 필드들
            updatable_fields = ['age', 'gender', 'disability_type', 'communication_characteristics',
                              'selection_complexity', 'interesting_topics']
            
            updated_fields = []
            for field, value in persona.items():
                if field in updatable_fields: # upadatable_fields에 있다면 새로운 value 값으로 업데이터
                    self.users[user_id][field] = value
                    updated_fields.append(field)
            
            if not updated_fields:
                return {
                    'status': 'error',
                    'message': '업데이트 가능한 필드가 없습니다.'
                }
            
            # 파일에 저장
            try:
                with open(self.users_file_path, 'w', encoding='utf-8') as f:
                    json.dump({k: v for k, v in self.users.items()}, f)
                
                return {
                    'status': 'success',
                    'message': '페르소나 정보가 성공적으로 업데이트되었습니다.'
                }
            except:
                return {
                    'status': 'error',
                    'message': '데이터 저장 중 오류가 발생했습니다.'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'오류가 발생했습니다: {str(e)}'
            }
    
    def get_all_users(self) -> Dict[str, Any]:
        """
        모든 사용자 조회
        
        Returns:
            Dict[str, Any]: {
                'status': str,
                'users': List[Dict],
                'count': int
            }
        """
        try:
            users_list = []
            for user_data in self.users.values():
                users_list.append(user_data)
                #                 ▲ user의 비밀번호까지 포함되어 있음
            
            return {
                'status': 'success',
                'users': users_list,
                'count': len(users_list)
            }
        except Exception as e:
            return {
                'status': 'error',
                'users': [],
                'count': 0
            }
    
    def delete_user(self, user_id: int) -> Dict[str, Any]:
        """
        사용자 삭제
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'message': str
            }
        """
        try: # 사용자 존재 확인
            if user_id not in self.users:
                return {
                    'status': 'error',
                    'message': f'사용자 ID {user_id}를 찾을 수 없습니다.'
                }
            
            # 사용자 삭제 후 파일에 변경 사항 저장
            del self.users[user_id]
            try:
                with open(self.users_file_path, 'w', encoding='utf-8') as f:
                    json.dump({k: v for k, v in self.users.items()}, f)
                
                return {
                    'status': 'success',
                    'message': f'사용자 ID {user_id}가 성공적으로 삭제되었습니다.'
                }
            except:
                return {
                    'status': 'error',
                    'message': '오류가 발생했습니다.'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'오류가 발생했습니다: {str(e)}'
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
            if user_id not in self.users: # id 검증
                return {
                    'status': 'error',
                    'authenticated': False,
                    'message': f'사용자 ID {user_id}를 찾을 수 없습니다.'
                }
            
            # 비밀번호 검증
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
    
    def update_user_password(self, user_id: int, old_password: str, new_password: str) -> Dict[str, Any]:
        """
        사용자 비밀번호 변경
        
        Args:
            user_id: 사용자 ID
            old_password: 기존 비밀번호
            new_password: 새 비밀번호
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'message': str
            }
        """
        try:
            if user_id not in self.users: # 1. 사용자 id가 존재하는지
                return {
                    'status': 'error',
                    'message': f'사용자 ID {user_id}를 찾을 수 없습니다.'
                }
            
            # 기존 비밀번호 확인
            old_user_password = self.users[user_id]['password']
            if old_user_password != old_password:   # 2. 기존 비밀번호가 올바른지
                return {
                    'status': 'error',
                    'message': '기존 비밀번호가 올바르지 않습니다.'
                }
            
            # 새 비밀번호 설정 후 업데이트
            self.users[user_id]['password'] = new_password
            try:
                with open(self.users_file_path, 'w', encoding='utf-8') as f:
                    json.dump({k: v for k, v in self.users.items()}, f)
                
                return {
                    'status': 'success',
                    'message': '비밀번호가 성공적으로 변경되었습니다.'
                }
            except:
                return {
                    'status': 'error',
                    'message': '데이터 저장 중 오류가 발생했습니다.'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'오류가 발생했습니다: {str(e)}'
            }