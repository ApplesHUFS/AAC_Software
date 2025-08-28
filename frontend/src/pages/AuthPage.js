import React, { useState } from 'react';
import { LoginForm } from '../components/auth/LoginForm';
import { RegisterForm } from '../components/auth/RegisterForm';

// 인증 페이지 컴포넌트
// 로그인과 회원가입 폼을 전환하여 표시
const AuthPage = ({ onAuthSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);

  // 로그인 성공 처리
  // App.js로 로그인 성공 이벤트 전달
  const handleLoginSuccess = (loginResponseData) => {
    onAuthSuccess(loginResponseData);
  };

  // 회원가입 성공 처리
  // 성공 후 로그인 페이지로 자동 전환
  const handleRegisterSuccess = (registerData) => {
    // 회원가입 성공 후 로그인 페이지로 이동
    setIsLogin(true);
  };

  // 로그인/회원가입 폼 전환 처리
  const switchToRegister = () => setIsLogin(false);
  const switchToLogin = () => setIsLogin(true);

  return (
    <div className="auth-page">
      <div className="auth-container">
        {/* 페이지 헤더 */}
        <div className="auth-header">
          <h1>AAC 카드 해석 시스템</h1>
          <p>개인화된 의사소통 지원 서비스</p>
          <div className="auth-description">
            {isLogin ? (
              <span>기존 계정으로 로그인하여 개인화된 AAC 서비스를 이용하세요</span>
            ) : (
              <span>새로운 계정을 생성하여 맞춤형 의사소통 지원을 시작하세요</span>
            )}
          </div>
        </div>
        
        {/* 로그인/회원가입 폼 전환 */}
        <div className="auth-content">
          {isLogin ? (
            <LoginForm 
              onLoginSuccess={handleLoginSuccess}
              switchToRegister={switchToRegister}
            />
          ) : (
            <RegisterForm 
              onRegisterSuccess={handleRegisterSuccess}
              switchToLogin={switchToLogin}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default AuthPage;