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
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <h1>AAC 카드 해석 시스템</h1>
          <p>개인화된 의사소통 지원 서비스</p>
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