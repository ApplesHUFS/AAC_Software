// src/components/auth/LoginForm.js
import React, { useState } from 'react';
import { authService } from '../../services/authService';

const LoginForm = ({ onLoginSuccess, switchToRegister }) => {
  const [formData, setFormData] = useState({
    userId: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.userId.trim() || !formData.password) {
      setError('사용자 ID와 비밀번호를 모두 입력해주세요.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await authService.login(formData.userId.trim(), formData.password);
      
      if (response.success && response.data.authenticated) {
        onLoginSuccess(response.data);
      } else {
        setError('로그인에 실패했습니다. 아이디와 비밀번호를 확인해주세요.');
      }
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-form partner-form">
      <h2>
        <span className="form-icon">🔑</span>
        도움이 로그인
      </h2>
      <p className="form-description">소통이와 함께하는 AAC 서비스에 접속하세요</p>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="userId">
            <span className="label-icon">👤</span>
            사용자 ID
          </label>
          <input
            type="text"
            id="userId"
            name="userId"
            value={formData.userId}
            onChange={handleChange}
            placeholder="등록한 사용자 ID를 입력하세요"
            disabled={loading}
            autoComplete="username"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="password">
            <span className="label-icon">🔒</span>
            비밀번호
          </label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="비밀번호를 입력하세요"
            disabled={loading}
            autoComplete="current-password"
          />
        </div>

        {error && (
          <div className="error-message partner-error">
            <span className="error-icon">⚠️</span>
            {error}
          </div>
        )}
        
        <button type="submit" className="primary-button partner-button" disabled={loading}>
          {loading ? '로그인 중...' : '로그인'}
        </button>
      </form>
      
      <div className="auth-switch">
        <p>
          아직 계정이 없으신가요? 
          <button 
            type="button" 
            className="link-button partner-link" 
            onClick={switchToRegister}
            disabled={loading}
          >
            회원가입하기
          </button>
        </p>
      </div>
    </div>
  );
};
