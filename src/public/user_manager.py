from typing import Dict, List, Optional, Any
import json
import os


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
            users_file_path: 사용자 데이터 파일 경로.
            config: 설정 딕셔너리. None이면 기본값 사용.
        """
        self.users_file_path = users_file_path
        self.config = config
        self.users = {}
        self.next_id = 1  # 사용자 ID 1부터

        # 기존 사용자 데이터 로드
        self._load_users()

    def _load_users(self):
        """사용자 데이터 파일 로드."""
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
        """사용자 데이터 저장."""
        try:
            os.makedirs(os.path.dirname(self.users_file_path), exist_ok=True)
            with open(self.users_file_path, 'w', encoding='utf-8') as f:
                json.dump({str(k): v for k, v in self.users.items()}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise Exception(f'사용자 데이터 저장 실패: {str(e)}')

    def create_user(self, persona: Dict[str, Any]) -> Dict[str, Any]:
        """새 사용자 생성 및 페르소나 등록.

        데이터셋 스키마에 맞는 페르소나 정보를 검증하고 사용자를 생성합니다.
        preferred_category_types는 외부에서 계산되어 전달되어야 합니다.

        Args:
            persona: 사용자 페르소나 정보. 다음 필드들이 필수:
                - age (int): 사용자 나이 (1-100)
                - gender (str): 성별 ('male' 또는 'female')
                - disability_type (str): 장애 유형
                  ('의사소통장애', '자폐스펙트럼장애', '지적장애')
                - communication_characteristics (str): 의사소통 특징
                - interesting_topics (List[str]): 관심 주제 목록
                - preferred_category_types (List[int]): 선호 클러스터 ID 목록 (6개)
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

            user_data = {
                'name': persona.get('name'),
                'age': int(persona['age']),
                'gender': persona['gender'],
                'disability_type': persona['disability_type'],
                'communication_characteristics': persona['communication_characteristics'],
                'interesting_topics': persona['interesting_topics'],
                'preferred_category_types': persona['preferred_category_types'],
                'password': persona['password'],
                'created_at': __import__('datetime').datetime.now().isoformat(),
                'updated_at': __import__('datetime').datetime.now().isoformat()
            }

            self.users[user_id] = user_data
            self.next_id += 1

            # 저장
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

    def update_user_persona(self, user_id: int, persona_updates: Dict[str, Any]) -> Dict[str, Any]:
        """기존 사용자의 페르소나 정보 업데이트.

        Args:
            user_id: 업데이트할 사용자 ID
            persona_updates: 업데이트할 페르소나 필드들
                지원하는 필드:
                - name (str): 사용자 이름
                - age (int): 나이
                - gender (str): 성별
                - disability_type (str): 장애 유형
                - communication_characteristics (str): 의사소통 특징
                - interesting_topics (List[str]): 관심 주제
                - preferred_category_types (List[int]): 선호 클러스터 (자동 재계산됨)

        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - updated_fields (List[str]): 업데이트된 필드 목록
                - needs_category_recalculation (bool): 카테고리 재계산 필요 여부
                - message (str): 결과 메시지
        """
        # 사용자 존재 검증
        user_validation = self._validate_user_exists(user_id)
        if not user_validation['valid']:
            return {
                'status': 'error',
                'updated_fields': [],
                'needs_category_recalculation': False,
                'message': user_validation['message']
            }

        try:
            user_data = self.users[user_id]
            updated_fields = []
            needs_category_recalculation = False

            # 업데이트 가능한 필드들과 검증 규칙
            updatable_fields = {
                'name': lambda x: isinstance(x, str) and len(x.strip()) > 0,
                'age': lambda x: self._validate_age(x)['valid'],
                'gender': lambda x: self._validate_gender(x)['valid'],
                'disability_type': lambda x: self._validate_disability_type(x)['valid'],
                'communication_characteristics': lambda x: isinstance(x, str) and len(x.strip()) > 0,
                'interesting_topics': lambda x: self._validate_interesting_topics(x)['valid']
            }

            # 각 필드 업데이트
            for field, new_value in persona_updates.items():
                if field == 'password':
                    # 비밀번호는 필드 업데이트 로직 추가 필요함 !!! -> 나중에 로그인 기능 만들고 하는게 어떨까 싶긴 함.
                    continue

                if field in updatable_fields:
                    validator = updatable_fields[field]
                    if validator(new_value):
                        user_data[field] = new_value
                        updated_fields.append(field)

                        # interesting_topics가 업데이트된 경우 재계산 플래그 설정
                        if field == 'interesting_topics':
                            needs_category_recalculation = True
                    else:
                        # 검증 오류 메시지
                        if field == 'age':
                            error_msg = self._validate_age(new_value)['message']
                        elif field == 'gender':
                            error_msg = self._validate_gender(new_value)['message']
                        elif field == 'disability_type':
                            error_msg = self._validate_disability_type(new_value)['message']
                        elif field == 'interesting_topics':
                            error_msg = self._validate_interesting_topics(new_value)['message']
                        else: # communication_characteristics
                            error_msg = f'필드 {field}의 값이 유효하지 않습니다: {new_value}'

                        return {
                            'status': 'error',
                            'updated_fields': [],
                            'needs_category_recalculation': False,
                            'message': error_msg
                        }

            # 업데이트 시간 갱신
            user_data['updated_at'] = __import__('datetime').datetime.now().isoformat()

            # 저장
            self._save_users()

            return {
                'status': 'success',
                'updated_fields': updated_fields,
                'needs_category_recalculation': needs_category_recalculation,
                'message': f'사용자 {user_id}의 페르소나가 성공적으로 업데이트되었습니다. 업데이트된 필드: {", ".join(updated_fields)}'
            }

        except Exception as e:
            return {
                'status': 'error',
                'updated_fields': [],
                'needs_category_recalculation': False,
                'message': f'페르소나 업데이트 중 오류 발생: {str(e)}'
            }

    def update_preferred_categories(self, user_id: int, preferred_category_types: List[int]) -> Dict[str, Any]:
        """사용자의 선호 카테고리 업데이트 (외부에서 계산된 결과 적용).

        Args:
            user_id: 사용자 ID
            preferred_category_types: 새로 계산된 선호 클러스터 ID 목록

        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - message (str): 결과 메시지
        """
        user_data = self.users[user_id]
        user_data['preferred_category_types'] = preferred_category_types
        user_data['needs_category_recalculation'] = False
        user_data['updated_at'] = __import__('datetime').datetime.now().isoformat()

        self._save_users()

        return {
            'status': 'success',
            'message': f'사용자 {user_id}의 선호 카테고리가 업데이트되었습니다.'
        }

    def _validate_required_fields(self, persona: Dict[str, Any]) -> Dict[str, Any]:
        """필수 필드 검증.

        Args:
            persona: 검증할 페르소나 정보

        Returns:
            Dict containing validation result
        """
        required_fields = self.config.get('required_fields', [])
        missing_fields = [field for field in required_fields
                         if field not in persona or not persona[field]]

        if missing_fields:
            return {
                'valid': False,
                'message': f'필수 필드가 누락되었습니다: {", ".join(missing_fields)}'
            }

        return {'valid': True, 'message': '필수 필드 검증 완료'}

    def _validate_age(self, age_value: Any) -> Dict[str, Any]:
        """나이 검증.

        Args:
            age_value: 검증할 나이 값

        Returns:
            Dict containing validation result
        """
        min_age = self.config.get('min_age', 1)
        max_age = self.config.get('max_age', 100)

        try:
            age_int = int(age_value)
            if age_int < min_age or age_int > max_age:
                return {
                    'valid': False,
                    'message': f'나이는 {min_age}-{max_age} 사이의 정수여야 합니다.'
                }
        except (ValueError, TypeError):
            return {
                'valid': False,
                'message': f'나이는 {min_age}-{max_age} 사이의 정수여야 합니다.'
            }

        return {'valid': True, 'message': '나이 검증 완료'}

    def _validate_gender(self, gender: str) -> Dict[str, Any]:
        """성별 검증.

        Args:
            gender: 검증할 성별

        Returns:
            Dict containing validation result
        """
        valid_genders = self.config.get('valid_genders', [])
        if gender not in valid_genders:
            return {
                'valid': False,
                'message': f'성별은 다음 중 하나여야 합니다: {", ".join(valid_genders)}'
            }

        return {'valid': True, 'message': '성별 검증 완료'}

    def _validate_disability_type(self, disability_type: str) -> Dict[str, Any]:
        """장애 유형 검증.

        Args:
            disability_type: 검증할 장애 유형

        Returns:
            Dict containing validation result
        """
        valid_disability_types = self.config.get('valid_disability_types', [])
        if disability_type not in valid_disability_types:
            return {
                'valid': False,
                'message': f'장애유형은 다음 중 하나여야 합니다: {", ".join(valid_disability_types)}'
            }

        return {'valid': True, 'message': '장애 유형 검증 완료'}

    def _validate_interesting_topics(self, interesting_topics: Any) -> Dict[str, Any]:
        """관심 주제 검증.

        Args:
            interesting_topics: 검증할 관심 주제

        Returns:
            Dict containing validation result
        """
        if not isinstance(interesting_topics, list) or len(interesting_topics) == 0:
            return {
                'valid': False,
                'message': '관심 주제는 최소 1개 이상의 리스트여야 합니다.'
            }

        return {'valid': True, 'message': '관심 주제 검증 완료'}

    def _validate_user_exists(self, user_id: int) -> Dict[str, Any]:
        """사용자 존재 여부 검증.

        Args:
            user_id: 검증할 사용자 ID

        Returns:
            Dict containing validation result
        """
        if user_id not in self.users:
            return {
                'valid': False,
                'message': f'사용자 ID {user_id}를 찾을 수 없습니다.'
            }

        return {'valid': True, 'message': '사용자 존재 검증 완료'}

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
        required_fields_result = self._validate_required_fields(persona)
        if not required_fields_result['valid']:
            return required_fields_result

        # 나이 검증
        age_result = self._validate_age(persona.get('age'))
        if not age_result['valid']:
            return age_result

        # 성별 검증
        gender_result = self._validate_gender(persona.get('gender'))
        if not gender_result['valid']:
            return gender_result

        # 장애유형 검증
        disability_result = self._validate_disability_type(persona.get('disability_type'))
        if not disability_result['valid']:
            return disability_result

        # 관심 주제 검증
        topics_result = self._validate_interesting_topics(persona.get('interesting_topics'))
        if not topics_result['valid']:
            return topics_result

        return {
            'valid': True,
            'message': '페르소나 검증 완료'
        }

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
        # 사용자 존재 검증
        user_validation = self._validate_user_exists(user_id)
        if not user_validation['valid']:
            return {
                'status': 'error',
                'user': None,
                'message': user_validation['message']
            }

        # 보안을 위해 비밀번호 제외하고 반환
        user_data = self.users[user_id].copy()
        user_data.pop('password', None)

        return {
            'status': 'success',
            'user': user_data,
            'message': '사용자 정보를 성공적으로 조회했습니다.'
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
        # 사용자 존재 검증
        user_validation = self._validate_user_exists(user_id)
        if not user_validation['valid']:
            return {
                'status': 'error',
                'authenticated': False,
                'message': user_validation['message']
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
                'message': '비밀번호가 일치하지 않습니다.'
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
