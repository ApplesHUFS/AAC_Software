// src/pages/AuthPage.js
import React, { useState } from 'react';
import LoginForm from '../components/auth/LoginForm';
import RegisterForm from '../components/auth/RegisterForm';

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
            <img src="/images/logo_red.png" alt="로고" width="32" height="32" />
            <h1>소통 도우미</h1>
          </div>
          <p className="service-description">
            AAC 사용자의 의사소통을 지원하는 <strong>도움이</strong> 전용 서비스
          </p>
          <hr width="100%" color="black" size="1" />
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