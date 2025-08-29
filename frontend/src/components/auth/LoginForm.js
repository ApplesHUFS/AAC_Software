// LoginForm.js - 백엔드 검증에 의존하는 간소화된 로그인 폼
import React, { useState } from 'react';
import { authService } from '../../services/authService';

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
    
    if (error) {
      setError('');
    }
  };

  // 로그인 폼 제출 처리
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await authService.login(formData.userId.trim(), formData.password);
      
      if (response.success && response.data.authenticated) {
        onLoginSuccess(response.data);
      } else {
        setError('로그인에 실패했습니다.');
      }
    } catch (error) {
      console.error('로그인 에러:', error);
      setError(error.message || '로그인 중 오류가 발생했습니다.');
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

        {error && (
          <div className="error-message">
            <span className="error-icon">⚠</span>
            {error}
          </div>
        )}
        
        <button 
          type="submit" 
          className="primary-button"
          disabled={loading}
        >
          {loading ? '로그인 중...' : '로그인'}
        </button>
      </form>
      
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
    </div>
  );
};

export { LoginForm };