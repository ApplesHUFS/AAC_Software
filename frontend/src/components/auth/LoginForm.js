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
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await authService.login(formData.userId, formData.password);
      if (response.success) {
        onLoginSuccess(response.data);
      }
    } catch (error) {
      setError(error.message || '로그인에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-form">
      <h2>로그인</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="userId">사용자 ID</label>
          <input
            type="text"
            id="userId"
            name="userId"
            value={formData.userId}
            onChange={handleChange}
            required
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
            required
          />
        </div>

        {error && <div className="error-message">{error}</div>}
        
        <button type="submit" disabled={loading}>
          {loading ? '로그인 중...' : '로그인'}
        </button>
      </form>
      
      <p>
        계정이 없으신가요? 
        <button type="button" className="link-button" onClick={switchToRegister}>
          회원가입
        </button>
      </p>
    </div>
  );
};
