// src/pages/AuthPage.js
import React, { useState } from "react";
import LoginForm from "../components/auth/LoginForm";
import RegisterForm from "../components/auth/RegisterForm";

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
            <img
              src="/images/basic_logo.png"
              alt="로고"
              width="48"
              height="48"
            />
            <h1>
              소통<span style={{ marginRight: "2px" }}>,</span>이룸
            </h1>
          </div>
          <p className="service-description">
            개인화된 AAC 의사소통을 지원하는 <strong>소통 도우미</strong> 서비스
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
