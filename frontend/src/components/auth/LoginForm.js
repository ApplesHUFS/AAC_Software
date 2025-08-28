import React, { useState } from 'react';
import { authService } from '../../services/authService';

// 로그인 폼 컴포넌트
// 사용자 인증 처리 및 로그인 성공 시 사용자 데이터 전달
const LoginForm = ({ onLoginSuccess, switchToRegister }) => {
  const [formData, setFormData] = useState({
    userId: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // 폼 입력 필드 변경 처리
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevData => ({
      ...prevData,
      [name]: value
    }));
    
    // 입력 시 에러 메시지 클리어
    if (error) {
      setError('');
    }
  };

  // 로그인 폼 제출 처리
  // app.py의 로그인 응답 구조에 맞게 처리
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // 입력 검증
    if (!formData.userId.trim()) {
      setError('사용자 ID를 입력해주세요.');
      setLoading(false);
      return;
    }

    if (!formData.password) {
      setError('비밀번호를 입력해주세요.');
      setLoading(false);
      return;
    }

    try {
      const response = await authService.login(formData.userId.trim(), formData.password);
      
      if (response.success && response.data.authenticated) {
        // app.py 응답 구조: response.data에 userId, authenticated, user 포함
        onLoginSuccess(response.data);
      } else {
        setError('로그인에 실패했습니다. 사용자 ID와 비밀번호를 확인해주세요.');
      }
    } catch (error) {
      console.error('로그인 에러:', error);
      
      // 네트워크 에러와 인증 에러 구분
      if (error.message.includes('fetch')) {
        setError('서버에 연결할 수 없습니다. 네트워크 연결을 확인해주세요.');
      } else if (error.message.includes('401')) {
        setError('사용자 ID 또는 비밀번호가 올바르지 않습니다.');
      } else {
        setError(error.message || '로그인 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-form">
      <h2>로그인</h2>
      
      <form onSubmit={handleSubmit} noValidate>
        <div className="form-group">
          <label htmlFor="userId">사용자 ID</label>
          <input
            type="text"
            id="userId"
            name="userId"
            value={formData.userId}
            onChange={handleChange}
            placeholder="사용자 ID를 입력하세요"
            required
            autoComplete="username"
            disabled={loading}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="password">비밀번호</label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="비밀번호를 입력하세요"
            required
            autoComplete="current-password"
            disabled={loading}
          />
        </div>

        {/* 에러 메시지 표시 */}
        {error && (
          <div className="error-message">
            <span className="error-icon">⚠</span>
            {error}
          </div>
        )}
        
        {/* 로그인 버튼 */}
        <button 
          type="submit" 
          className="primary-button"
          disabled={loading}
        >
          {loading ? '로그인 중...' : '로그인'}
        </button>
      </form>
      
      {/* 회원가입 링크 */}
      <div className="auth-switch">
        <p>
          계정이 없으신가요? 
          <button 
            type="button" 
            className="link-button" 
            onClick={switchToRegister}
            disabled={loading}
          >
            회원가입
          </button>
        </p>
      </div>

      {/* 로그인 도움말 */}
      <div className="auth-help">
        <p>
          <small>
            로그인에 문제가 있으신가요? 회원가입 시 입력한 사용자 ID와 비밀번호를 확인해주세요.
          </small>
        </p>
      </div>
    </div>
  );
};

export { LoginForm };