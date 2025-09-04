// src/pages/AuthPage.js
import React, { useState } from 'react';
import { LoginForm } from '../components/auth/LoginForm';
import { RegisterForm } from '../components/auth/RegisterForm';

const AuthPage = ({ onAuthSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);

  // 로그인 성공 처리
  const handleLoginSuccess = (loginResponseData) => {
    onAuthSuccess(loginResponseData);
  };

  // 회원가입 성공 시 로그인 폼으로 전환
  const handleRegisterSuccess = () => {
    setIsLogin(true);
  };

  return (
    <div className="auth-page partner-theme">
      <div className="auth-container">
        <div className="auth-header">
          <div className="service-logo">
            <span className="logo-icon">💬</span>
            <h1>소통 도우미</h1>
          </div>
          <p className="service-description">
            AAC 사용자의 의사소통을 지원하는 <strong>도움이</strong> 전용 서비스
          </p>
          <div className="role-indicator partner-role">
            <span className="role-icon">👥</span>
            <span>도움이 (보호자/케어러) 로그인</span>
          </div>
        </div>
        
        <div className="auth-content">
          {isLogin ? (
            <LoginForm 
              onLoginSuccess={handleLoginSuccess}
              switchToRegister={() => setIsLogin(false)}
            />
          ) : (
            <RegisterForm 
              onRegisterSuccess={handleRegisterSuccess}
              switchToLogin={() => setIsLogin(true)}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default AuthPage;