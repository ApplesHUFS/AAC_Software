import React, { useState } from 'react';
import { LoginForm, RegisterForm } from '../components/auth/LoginForm';

const AuthPage = ({ onAuthSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);

  const handleLoginSuccess = (userData) => {
    onAuthSuccess(userData);
  };

  const handleRegisterSuccess = (userData) => {
    setIsLogin(true);
    // 회원가입 후 로그인 페이지로 이동하거나 자동 로그인 가능
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <h1>AAC 카드 해석 시스템</h1>
          <p>개인화된 의사소통 지원 서비스</p>
        </div>
        
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
  );
};

export default AuthPage;
