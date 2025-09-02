// src/pages/DashboardPage.js
import React, { useState } from 'react';
import { ContextForm } from '../components/context/ContextForm';
import ProfileEditForm from '../components/profile/ProfileEditForm';

const DashboardPage = ({ user, onLogout, onUserUpdate, onContextCreated }) => {
  const [currentView, setCurrentView] = useState('main'); // 'main', 'context', 'profile'

  // 새 대화 세션 시작
  const handleStartNewSession = () => {
    setCurrentView('context');
  };

  // 프로필 편집 시작
  const handleEditProfile = () => {
    setCurrentView('profile');
  };

  // 메인 뷰로 돌아가기
  const handleBackToMain = () => {
    setCurrentView('main');
  };

  // 컨텍스트 생성 완료
  const handleContextCreated = (contextData) => {
    onContextCreated(contextData);
  };

  // 프로필 업데이트 완료
  const handleProfileUpdated = (updatedUser) => {
    onUserUpdate(updatedUser);
    setCurrentView('main');
  };

  return (
    <div className="dashboard-page">
      <header className="dashboard-header">
        <div className="user-info">
          <h2>안녕하세요, {user.name}님!</h2>
          <p>AAC 카드를 활용한 개인화된 의사소통을 시작해보세요.</p>
        </div>
        <div className="header-actions">
          {currentView !== 'main' && (
            <button className="secondary-button" onClick={handleBackToMain}>
              메인으로
            </button>
          )}
          {currentView === 'main' && (
            <>
              <button className="secondary-button" onClick={handleEditProfile}>
                프로필 편집
              </button>
              <button className="secondary-button" onClick={onLogout}>
                로그아웃
              </button>
            </>
          )}
        </div>
      </header>

      <div className="dashboard-content">
        {/* 메인 화면 */}
        {currentView === 'main' && (
          <div className="dashboard-main">
            <div className="welcome-section">
              <div className="welcome-card">
                <h3>새로운 대화 세션 시작</h3>
                <p>
                  현재 상황을 입력하고 개인화된 AAC 카드 추천을 받아보세요.
                  AI가 당신의 관심사와 대화 맥락을 고려하여 최적의 카드를 제안합니다.
                </p>
                <button className="primary-button large" onClick={handleStartNewSession}>
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
                    <label>성별</label>
                    <span>{user.gender}</span>
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

            {/* 의사소통 특성 */}
            {user.communicationCharacteristics && (
              <div className="communication-section">
                <h4>의사소통 특성</h4>
                <div className="communication-info">
                  <p>{user.communicationCharacteristics}</p>
                </div>
              </div>
            )}

            {/* 관심 주제 목록 */}
            {user.interestingTopics?.length > 0 && (
              <div className="interests-section">
                <h4>관심 주제</h4>
                <div className="topic-list">
                  {user.interestingTopics.map((topic, index) => (
                    <span key={index} className="topic-tag">
                      {topic}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* 컨텍스트 입력 화면 */}
        {currentView === 'context' && (
          <ContextForm 
            userId={user.userId}
            onContextCreated={handleContextCreated}
          />
        )}

        {/* 프로필 편집 화면 */}
        {currentView === 'profile' && (
          <ProfileEditForm 
            user={user}
            onProfileUpdated={handleProfileUpdated}
            onCancel={handleBackToMain}
          />
        )}
      </div>
    </div>
  );
};

export default DashboardPage;