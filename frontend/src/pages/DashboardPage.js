import React, { useState } from 'react';
import { ContextForm } from '../components/context/ContextForm';

const DashboardPage = ({ user, onLogout, onContextCreated }) => {
  const [showContextForm, setShowContextForm] = useState(false);

  const handleStartNewSession = () => {
    setShowContextForm(true);
  };

  const handleContextCreated = (contextData) => {
    onContextCreated(contextData);
  };

  return (
    <div className="dashboard-page">
      <header className="dashboard-header">
        <div className="user-info">
          <h2>안녕하세요, {user.name}님!</h2>
          <p>AAC 카드를 사용한 의사소통을 시작해보세요.</p>
        </div>
        <div className="header-actions">
          <button className="secondary-button">프로필 수정</button>
          <button className="secondary-button" onClick={onLogout}>로그아웃</button>
        </div>
      </header>

      <div className="dashboard-content">
        {!showContextForm ? (
          <div className="dashboard-welcome">
            <div className="welcome-card">
              <h3>새로운 대화 세션 시작</h3>
              <p>
                대화 상황을 입력하고 개인화된 AAC 카드 추천을 받아보세요.
                AI가 당신의 관심사와 현재 상황을 고려하여 최적의 카드를 추천해드립니다.
              </p>
              <button 
                className="primary-button large"
                onClick={handleStartNewSession}
              >
                대화 시작하기
              </button>
            </div>

            <div className="user-stats">
              <h4>내 정보</h4>
              <div className="stats-grid">
                <div className="stat-item">
                  <label>나이</label>
                  <span>{user.age}세</span>
                </div>
                <div className="stat-item">
                  <label>장애 유형</label>
                  <span>{user.disabilityType}</span>
                </div>
                <div className="stat-item">
                  <label>관심 주제</label>
                  <span>{user.interestingTopics?.length || 0}개</span>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <ContextForm 
            userId={user.userId}
            onContextCreated={handleContextCreated}
          />
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
