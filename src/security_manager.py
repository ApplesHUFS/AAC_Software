import hashlib
import secrets
import time
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import re


class SecurityManager:
    """보안 관리 및 사용자 인증"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.session_duration = self.config.get('session_duration', 3600)
        self.max_login_attempts = self.config.get('max_login_attempts', 5)
        self.rate_limit_window = self.config.get('rate_limit_window', 300)
        self.rate_limit_max_requests = self.config.get('rate_limit_max_requests', 100)
        
        # In-memory 구현,,, 저장 로직 만들어야함.
        self.active_sessions = {}
        self.security_events = []
        self.rate_limit_data = {}
        self.login_attempts = {}
        
        self.security_log_path = self.config.get('security_log_path', 'security_events.json')
        self._load_security_events()
    
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
            
            if not hasattr(self, 'encryption_keys'):
                self.encryption_keys = {}
            self.encryption_keys[key_id] = key
            
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
            if not hasattr(self, 'encryption_keys') or encryption_key_id not in self.encryption_keys:
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