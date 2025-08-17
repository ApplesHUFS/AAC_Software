import hashlib
import secrets
import time
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import re
import sys

# config 모듈 import
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.server_config import get_security_config


class SecurityManager:
    """보안 관리 및 사용자 인증"""
    
    def __init__(self, config: Optional[Dict] = None):
        # 서버 설정과 사용자 설정 병합
        default_config = get_security_config()
        self.config = {**default_config, **(config or {})}
        
        self.session_duration = self.config.get('session_duration', 3600)
        self.max_login_attempts = self.config.get('max_login_attempts', 5)
        self.rate_limit_window = self.config.get('rate_limit_window', 300)
        self.rate_limit_max_requests = self.config.get('rate_limit_max_requests', 100)
        
        # In-memory 구현,,, 저장 로직 만들어야함.
        self.active_sessions = {}
        self.security_events = []
        self.rate_limit_data = {}
        self.login_attempts = {}
        
        # 사용자 데이터 저장 경로 설정
        self.user_data_dir = self.config.get('user_data_dir', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'user_data'))
        self.users_file = os.path.join(self.user_data_dir, 'users.json')
        self.sessions_file = os.path.join(self.user_data_dir, 'sessions.json')
        self.security_log_path = self.config.get('security_log_path', os.path.join(self.user_data_dir, 'security_events.json'))
        
        # 디렉토리 생성
        os.makedirs(self.user_data_dir, exist_ok=True)
        
        # 데이터 로드
        self.users = self._load_users()
        self.next_user_id = max([user['user_id'] for user in self.users.values()], default=0) + 1
        self._load_security_events()
        self._load_sessions()
        self.encryption_keys = self._load_encryption_keys()
    
    def _load_security_events(self):
        if os.path.exists(self.security_log_path):
            try:
                with open(self.security_log_path, 'r', encoding='utf-8') as f:
                    self.security_events = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.security_events = []
    
    def _save_security_events(self):
        try:
            with open(self.security_log_path, 'w', encoding='utf-8') as f:
                json.dump(self.security_events, f, ensure_ascii=False, indent=2)
        except IOError:
            pass
    
    def _load_users(self):
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_users(self):
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
        except IOError:
            pass
    
    def _load_sessions(self):
        if os.path.exists(self.sessions_file):
            try:
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                    # Convert string timestamps back to datetime objects
                    for token, session in session_data.items():
                        session['expires_at'] = datetime.fromisoformat(session['expires_at'])
                        session['created_at'] = datetime.fromisoformat(session['created_at'])
                    self.active_sessions = session_data
            except (json.JSONDecodeError, IOError):
                self.active_sessions = {}
    
    def _save_sessions(self):
        try:
            # Convert datetime objects to strings for JSON serialization
            session_data = {}
            for token, session in self.active_sessions.items():
                session_data[token] = {
                    'user_id': session['user_id'],
                    'session_id': session['session_id'],
                    'expires_at': session['expires_at'].isoformat(),
                    'created_at': session['created_at'].isoformat()
                }
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
        except IOError:
            pass
    
    def _load_encryption_keys(self):
        keys_file = os.path.join(self.user_data_dir, 'encryption_keys.json')
        if os.path.exists(keys_file):
            try:
                with open(keys_file, 'r', encoding='utf-8') as f:
                    key_data = json.load(f)
                    # Convert hex strings back to bytes
                    return {key_id: bytes.fromhex(key_hex) for key_id, key_hex in key_data.items()}
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_encryption_keys(self):
        try:
            keys_file = os.path.join(self.user_data_dir, 'encryption_keys.json')
            # Convert bytes to hex strings for JSON serialization
            key_data = {key_id: key.hex() for key_id, key in self.encryption_keys.items()}
            with open(keys_file, 'w', encoding='utf-8') as f:
                json.dump(key_data, f, ensure_ascii=False, indent=2)
        except IOError:
            pass
    
    def create_user(self, persona: Dict[str, Any]) -> Dict[str, Any]:
        """
        새 사용자 생성 (User Manager 연동)
        
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
            if 'password' not in persona or not persona['password']:
                return {
                    'status': 'error',
                    'user_id': -1,
                    'message': 'Password is required'
                }
            
            # 비밀번호 강도 검사
            password_validation = self.validate_password_strength(persona['password'])
            if not password_validation['valid']:
                return {
                    'status': 'error',
                    'user_id': -1,
                    'message': f"Password validation failed: {', '.join(password_validation['suggestions'])}"
                }
            
            # 비밀번호 해시화
            hash_result = self.hash_password(persona['password'])
            if hash_result['status'] != 'success':
                return {
                    'status': 'error',
                    'user_id': -1,
                    'message': 'Failed to hash password'
                }
            
            user_id = self.next_user_id
            self.next_user_id += 1
            
            # 사용자 데이터 생성 (비밀번호 제외)
            user_data = {
                'user_id': user_id,
                'age': persona.get('age', ''),
                'gender': persona.get('gender', ''),
                'disability_type': persona.get('disability_type', ''),
                'communication_characteristics': persona.get('communication_characteristics', ''),
                'selection_complexity': persona.get('selection_complexity', ''),
                'interesting_topics': persona.get('interesting_topics', []),
                'password_hash': hash_result['hashed_password'],
                'password_salt': hash_result['salt'],
                'created_at': datetime.now().isoformat(),
                'last_login': None
            }
            
            self.users[str(user_id)] = user_data
            self._save_users()
            
            # 보안 이벤트 로깅
            self.log_security_event('user_created', user_id, {'action': 'user_registration'})
            
            return {
                'status': 'success',
                'user_id': user_id,
                'message': 'User created successfully'
            }
        except Exception as e:
            return {
                'status': 'error',
                'user_id': -1,
                'message': f'User creation failed: {str(e)}'
            }
    
    def get_user(self, user_id: int) -> Dict[str, Any]:
        """
        사용자 정보 조회 (User Manager 연동)
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'user': Dict or None,
                'message': str
            }
        """
        try:
            user_key = str(user_id)
            if user_key not in self.users:
                return {
                    'status': 'error',
                    'user': None,
                    'message': 'User not found'
                }
            
            user_data = self.users[user_key].copy()
            # 보안을 위해 비밀번호 해시와 솔트 제거
            user_data.pop('password_hash', None)
            user_data.pop('password_salt', None)
            
            return {
                'status': 'success',
                'user': user_data,
                'message': 'User found'
            }
        except Exception as e:
            return {
                'status': 'error',
                'user': None,
                'message': f'Failed to get user: {str(e)}'
            }
    
    def authenticate_user(self, user_id: int, password: str) -> Dict[str, Any]:
        """
        사용자 인증 (User Manager 연동)
        
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
            user_key = str(user_id)
            if user_key not in self.users:
                self.log_security_event('failed_login', user_id, {'reason': 'user_not_found'})
                return {
                    'status': 'error',
                    'authenticated': False,
                    'message': 'Invalid user ID or password'
                }
            
            user_data = self.users[user_key]
            
            # 로그인 시도 횟수 확인
            if user_key not in self.login_attempts:
                self.login_attempts[user_key] = {'count': 0, 'last_attempt': None}
            
            current_time = datetime.now()
            if (self.login_attempts[user_key]['last_attempt'] and 
                (current_time - datetime.fromisoformat(self.login_attempts[user_key]['last_attempt'])).total_seconds() < 300):
                if self.login_attempts[user_key]['count'] >= self.max_login_attempts:
                    self.log_security_event('blocked_login', user_id, {'reason': 'too_many_attempts'})
                    return {
                        'status': 'error',
                        'authenticated': False,
                        'message': 'Account temporarily locked due to too many failed attempts'
                    }
            else:
                # 5분이 지났으면 카운터 리셋
                self.login_attempts[user_key]['count'] = 0
            
            # 비밀번호 검증
            verification_result = self.verify_password(password, user_data['password_hash'], user_data['password_salt'])
            
            if verification_result['verified']:
                # 로그인 성공
                self.login_attempts[user_key]['count'] = 0
                self.users[user_key]['last_login'] = current_time.isoformat()
                self._save_users()
                
                self.log_security_event('login', user_id, {'success': True})
                
                return {
                    'status': 'success',
                    'authenticated': True,
                    'message': 'Authentication successful'
                }
            else:
                # 로그인 실패
                self.login_attempts[user_key]['count'] += 1
                self.login_attempts[user_key]['last_attempt'] = current_time.isoformat()
                
                self.log_security_event('failed_login', user_id, {'reason': 'invalid_password'})
                
                return {
                    'status': 'error',
                    'authenticated': False,
                    'message': 'Invalid user ID or password'
                }
        except Exception as e:
            self.log_security_event('failed_login', user_id, {'reason': 'system_error', 'error': str(e)})
            return {
                'status': 'error',
                'authenticated': False,
                'message': 'Authentication failed due to system error'
            }
    
    def update_user_persona(self, user_id: int, persona: Dict[str, Any]) -> Dict[str, Any]:
        """
        사용자 페르소나 정보 업데이트 (User Manager 연동)
        
        Args:
            user_id: 사용자 ID
            persona: 업데이트할 페르소나 정보
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'message': str
            }
        """
        try:
            user_key = str(user_id)
            if user_key not in self.users:
                return {
                    'status': 'error',
                    'message': 'User not found'
                }
            
            # 업데이트 가능한 필드들
            updatable_fields = ['age', 'gender', 'disability_type', 'communication_characteristics', 
                              'selection_complexity', 'interesting_topics']
            
            for field in updatable_fields:
                if field in persona:
                    self.users[user_key][field] = persona[field]
            
            self.users[user_key]['updated_at'] = datetime.now().isoformat()
            self._save_users()
            
            self.log_security_event('user_updated', user_id, {'updated_fields': list(persona.keys())})
            
            return {
                'status': 'success',
                'message': 'User persona updated successfully'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to update user persona: {str(e)}'
            }
    
    def update_user_password(self, user_id: int, old_password: str, new_password: str) -> Dict[str, Any]:
        """
        사용자 비밀번호 변경 (User Manager 연동)
        
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
            user_key = str(user_id)
            if user_key not in self.users:
                return {
                    'status': 'error',
                    'message': 'User not found'
                }
            
            user_data = self.users[user_key]
            
            # 기존 비밀번호 확인
            verification_result = self.verify_password(old_password, user_data['password_hash'], user_data['password_salt'])
            if not verification_result['verified']:
                self.log_security_event('password_change_failed', user_id, {'reason': 'invalid_old_password'})
                return {
                    'status': 'error',
                    'message': 'Invalid old password'
                }
            
            # 새 비밀번호 강도 검사
            password_validation = self.validate_password_strength(new_password)
            if not password_validation['valid']:
                return {
                    'status': 'error',
                    'message': f"New password validation failed: {', '.join(password_validation['suggestions'])}"
                }
            
            # 새 비밀번호 해시화
            hash_result = self.hash_password(new_password)
            if hash_result['status'] != 'success':
                return {
                    'status': 'error',
                    'message': 'Failed to hash new password'
                }
            
            # 비밀번호 업데이트
            self.users[user_key]['password_hash'] = hash_result['hashed_password']
            self.users[user_key]['password_salt'] = hash_result['salt']
            self.users[user_key]['password_changed_at'] = datetime.now().isoformat()
            self._save_users()
            
            self.log_security_event('password_changed', user_id, {'success': True})
            
            return {
                'status': 'success',
                'message': 'Password updated successfully'
            }
        except Exception as e:
            self.log_security_event('password_change_failed', user_id, {'reason': 'system_error', 'error': str(e)})
            return {
                'status': 'error',
                'message': f'Failed to update password: {str(e)}'
            }
    
    def get_all_users(self) -> Dict[str, Any]:
        """
        모든 사용자 조회 (User Manager 연동)
        
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
                user_copy = user_data.copy()
                # 보안을 위해 비밀번호 해시와 솔트 제거
                user_copy.pop('password_hash', None)
                user_copy.pop('password_salt', None)
                users_list.append(user_copy)
            
            return {
                'status': 'success',
                'users': users_list,
                'count': len(users_list)
            }
        except Exception as e:
            return {
                'status': 'error',
                'users': [],
                'count': 0,
                'message': f'Failed to get users: {str(e)}'
            }
    
    def delete_user(self, user_id: int) -> Dict[str, Any]:
        """
        사용자 삭제 (User Manager 연동)
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'message': str
            }
        """
        try:
            user_key = str(user_id)
            if user_key not in self.users:
                return {
                    'status': 'error',
                    'message': 'User not found'
                }
            
            # 사용자의 모든 세션 무효화
            tokens_to_remove = []
            for token, session in self.active_sessions.items():
                if session['user_id'] == user_id:
                    tokens_to_remove.append(token)
            
            for token in tokens_to_remove:
                del self.active_sessions[token]
            
            # 사용자 데이터 삭제
            del self.users[user_key]
            self._save_users()
            self._save_sessions()
            
            # 로그인 시도 기록 삭제
            if user_key in self.login_attempts:
                del self.login_attempts[user_key]
            
            self.log_security_event('user_deleted', user_id, {'success': True})
            
            return {
                'status': 'success',
                'message': 'User deleted successfully'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to delete user: {str(e)}'
            }
    
    def hash_password(self, password: str) -> Dict[str, Any]:
        """
        비밀번호 해시화
        
        Args:
            password: 원본 비밀번호
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'hashed_password': str,
                'salt': str
            }
        """
        try:
            salt = secrets.token_hex(32)
            password_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            hashed_password = password_hash.hex()
            
            return {
                'status': 'success',
                'hashed_password': hashed_password,
                'salt': salt
            }
        except Exception as e:
            return {
                'status': 'error',
                'hashed_password': '',
                'salt': '',
                'message': f'Password hashing failed: {str(e)}'
            }
    
    def verify_password(self, password: str, hashed_password: str, salt: str) -> Dict[str, Any]:
        """
        비밀번호 검증
        
        Args:
            password: 입력된 비밀번호
            hashed_password: 저장된 해시
            salt: 솔트값
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'verified': bool,
                'message': str
            }
        """
        try:
            password_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            computed_hash = password_hash.hex()
            
            verified = computed_hash == hashed_password
            
            return {
                'status': 'success',
                'verified': verified,
                'message': 'Password verified' if verified else 'Password verification failed'
            }
        except Exception as e:
            return {
                'status': 'error',
                'verified': False,
                'message': f'Password verification error: {str(e)}'
            }
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """
        비밀번호 강도 검사
        
        Args:
            password: 검사할 비밀번호
            
        Returns:
            Dict[str, Any]: {
                'valid': bool,
                'strength_score': int,  # 0-100
                'requirements_met': Dict[str, bool],
                'suggestions': List[str]
            }
        """
        requirements = {
            'min_length': len(password) >= 8,
            'has_lowercase': bool(re.search(r'[a-z]', password)),
            'has_uppercase': bool(re.search(r'[A-Z]', password)),
            'has_digits': bool(re.search(r'\d', password)),
            'has_special': bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        }
        
        suggestions = []
        if not requirements['min_length']:
            suggestions.append('비밀번호는 최소 8자 이상이어야 합니다')
        if not requirements['has_lowercase']:
            suggestions.append('소문자를 포함해야 합니다')
        if not requirements['has_uppercase']:
            suggestions.append('대문자를 포함해야 합니다')
        if not requirements['has_digits']:
            suggestions.append('숫자를 포함해야 합니다')
        if not requirements['has_special']:
            suggestions.append('특수문자를 포함해야 합니다')
        
        met_count = sum(requirements.values())
        strength_score = min(100, (met_count * 20) + (len(password) * 2))
        valid = met_count >= 4 and requirements['min_length']
        
        return {
            'valid': valid,
            'strength_score': strength_score,
            'requirements_met': requirements,
            'suggestions': suggestions
        }
    
    def generate_session_token(self, user_id: int) -> Dict[str, Any]:
        """
        세션 토큰 생성
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'token': str,
                'expires_at': str,
                'session_id': str
            }
        """
        try:
            session_id = secrets.token_urlsafe(32)
            token = secrets.token_urlsafe(64)
            expires_at = datetime.now() + timedelta(seconds=self.session_duration)
            
            self.active_sessions[token] = {
                'user_id': user_id,
                'session_id': session_id,
                'expires_at': expires_at,
                'created_at': datetime.now()
            }
            
            self._save_sessions()
            
            return {
                'status': 'success',
                'token': token,
                'expires_at': expires_at.isoformat(),
                'session_id': session_id
            }
        except Exception as e:
            return {
                'status': 'error',
                'token': '',
                'expires_at': '',
                'session_id': '',
                'message': f'Token generation failed: {str(e)}'
            }
            return {
                'status': 'error',
                'token': '',
                'expires_at': '',
                'session_id': '',
                'message': f'Token generation failed: {str(e)}'
            }
    
    def validate_session_token(self, token: str) -> Dict[str, Any]:
        """
        세션 토큰 검증
        
        Args:
            token: 검증할 토큰
            
        Returns:
            Dict[str, Any]: {
                'valid': bool,
                'user_id': int or None,
                'expires_at': str or None,
                'remaining_time': int or None  # seconds
            }
        """
        if token not in self.active_sessions:
            return {
                'valid': False,
                'user_id': None,
                'expires_at': None,
                'remaining_time': None
            }
        
        session = self.active_sessions[token]
        current_time = datetime.now()
        
        if current_time > session['expires_at']:
            del self.active_sessions[token]
            self._save_sessions()
            return {
                'valid': False,
                'user_id': None,
                'expires_at': None,
                'remaining_time': None
            }
        
        remaining_time = int((session['expires_at'] - current_time).total_seconds())
        
        return {
            'valid': True,
            'user_id': session['user_id'],
            'expires_at': session['expires_at'].isoformat(),
            'remaining_time': remaining_time
        }
    
    def revoke_session(self, session_id: str) -> Dict[str, Any]:
        """
        세션 무효화
        
        Args:
            session_id: 세션 ID
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'message': str
            }
        """
        revoked = False
        for token, session in list(self.active_sessions.items()):
            if session['session_id'] == session_id:
                del self.active_sessions[token]
                revoked = True
                break
        
        if revoked:
            self._save_sessions()
            return {
                'status': 'success',
                'message': 'Session revoked successfully'
            }
        else:
            return {
                'status': 'error',
                'message': 'Session not found'
            }
    
    def log_security_event(self, event_type: str, user_id: Optional[int], details: Dict[str, Any]) -> Dict[str, Any]:
        """
        보안 이벤트 로깅
        
        Args:
            event_type: 이벤트 유형 ('login', 'logout', 'failed_login', etc.)
            user_id: 사용자 ID
            details: 이벤트 상세 정보
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'event_id': str,
                'timestamp': str
            }
        """
        event_id = secrets.token_hex(16)
        timestamp = datetime.now().isoformat()
        
        security_event = {
            'event_id': event_id,
            'event_type': event_type,
            'user_id': user_id,
            'timestamp': timestamp,
            'details': details
        }
        
        self.security_events.append(security_event)
        self._save_security_events()
        
        return {
            'status': 'success',
            'event_id': event_id,
            'timestamp': timestamp
        }
    
    def detect_suspicious_activity(self, user_id: int) -> Dict[str, Any]:
        """
        의심스러운 활동 탐지
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            Dict[str, Any]: {
                'suspicious': bool,
                'risk_score': int,  # 0-100
                'detected_patterns': List[str],
                'recommended_actions': List[str]
            }
        """
        current_time = datetime.now()
        recent_events = [
            event for event in self.security_events
            if event.get('user_id') == user_id and
               (current_time - datetime.fromisoformat(event['timestamp'])).total_seconds() < 3600
        ]
        
        detected_patterns = []
        risk_score = 0
        
        failed_logins = [e for e in recent_events if e['event_type'] == 'failed_login']
        if len(failed_logins) >= 3:
            detected_patterns.append('Multiple failed login attempts')
            risk_score += 30
        
        login_events = [e for e in recent_events if e['event_type'] == 'login']
        if len(login_events) >= 5:
            detected_patterns.append('Frequent login activity')
            risk_score += 20
        
        unique_ips = set()
        for event in recent_events:
            if 'ip_address' in event.get('details', {}):
                unique_ips.add(event['details']['ip_address'])
        if len(unique_ips) > 3:
            detected_patterns.append('Multiple IP addresses')
            risk_score += 25
        
        suspicious = risk_score >= 50
        
        recommended_actions = []
        if suspicious:
            recommended_actions.extend([
                'Require additional authentication',
                'Monitor user activity closely',
                'Consider temporary account restrictions'
            ])
        
        return {
            'suspicious': suspicious,
            'risk_score': min(100, risk_score),
            'detected_patterns': detected_patterns,
            'recommended_actions': recommended_actions
        }
    
    def rate_limit_check(self, user_id: int, action: str) -> Dict[str, Any]:
        """
        사용량 제한 확인
        
        Args:
            user_id: 사용자 ID
            action: 행동 유형
            
        Returns:
            Dict[str, Any]: {
                'allowed': bool,
                'remaining_requests': int,
                'reset_time': str,
                'message': str
            }
        """
        current_time = time.time()
        key = f"{user_id}:{action}"
        
        if key not in self.rate_limit_data:
            self.rate_limit_data[key] = {
                'requests': [],
                'reset_time': current_time + self.rate_limit_window
            }
        
        rate_data = self.rate_limit_data[key]
        
        if current_time > rate_data['reset_time']:
            rate_data['requests'] = []
            rate_data['reset_time'] = current_time + self.rate_limit_window
        
        rate_data['requests'] = [
            req_time for req_time in rate_data['requests']
            if current_time - req_time < self.rate_limit_window
        ]
        
        if len(rate_data['requests']) >= self.rate_limit_max_requests:
            return {
                'allowed': False,
                'remaining_requests': 0,
                'reset_time': datetime.fromtimestamp(rate_data['reset_time']).isoformat(),
                'message': 'Rate limit exceeded'
            }
        
        rate_data['requests'].append(current_time)
        remaining = self.rate_limit_max_requests - len(rate_data['requests'])
        
        return {
            'allowed': True,
            'remaining_requests': remaining,
            'reset_time': datetime.fromtimestamp(rate_data['reset_time']).isoformat(),
            'message': 'Request allowed'
        }
    
    def encrypt_sensitive_data(self, data: str) -> Dict[str, Any]:
        """
        민감한 데이터 암호화
        
        Args:
            data: 암호화할 데이터
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'encrypted_data': str,
                'encryption_key_id': str
            }
        """
        try:
            key = secrets.token_bytes(32)
            key_id = secrets.token_hex(16)
            
            encrypted_bytes = bytearray()
            data_bytes = data.encode('utf-8')
            
            for i, byte in enumerate(data_bytes):
                encrypted_bytes.append(byte ^ key[i % len(key)])
            
            encrypted_data = encrypted_bytes.hex()
            
            self.encryption_keys[key_id] = key
            self._save_encryption_keys()
            
            return {
                'status': 'success',
                'encrypted_data': encrypted_data,
                'encryption_key_id': key_id
            }
        except Exception as e:
            return {
                'status': 'error',
                'encrypted_data': '',
                'encryption_key_id': '',
                'message': f'Encryption failed: {str(e)}'
            }
    
    def decrypt_sensitive_data(self, encrypted_data: str, encryption_key_id: str) -> Dict[str, Any]:
        """
        암호화된 데이터 복호화
        
        Args:
            encrypted_data: 암호화된 데이터
            encryption_key_id: 암호화 키 ID
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'decrypted_data': str,
                'message': str
            }
        """
        try:
            if encryption_key_id not in self.encryption_keys:
                return {
                    'status': 'error',
                    'decrypted_data': '',
                    'message': 'Encryption key not found'
                }
            
            key = self.encryption_keys[encryption_key_id]
            encrypted_bytes = bytes.fromhex(encrypted_data)
            
            decrypted_bytes = bytearray()
            for i, byte in enumerate(encrypted_bytes):
                decrypted_bytes.append(byte ^ key[i % len(key)])
            
            decrypted_data = decrypted_bytes.decode('utf-8')
            
            return {
                'status': 'success',
                'decrypted_data': decrypted_data,
                'message': 'Data decrypted successfully'
            }
        except Exception as e:
            return {
                'status': 'error',
                'decrypted_data': '',
                'message': f'Decryption failed: {str(e)}'
            }