// src/pages/DashboardPage.js
import React, { useState } from 'react';
import ContextForm from '../components/context/ContextForm';
import ProfileEditForm from '../components/profile/ProfileEditForm';

const DashboardPage = ({ user, onLogout, onUserUpdate, onContextCreated }) => {
  const [currentView, setCurrentView] = useState('main');

  // 새 대화 세션 시작 (도움이가 상황 설정)
  const handleStartNewSession = () => {
    setCurrentView('context');
  };

  // 프로필 편집 시작 (도움이가 소통이 정보 수정)
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
    <div className="dashboard-page partner-theme">
      <header className="dashboard-header">
        <div className="user-info">
          <div className="role-indicator partner-role">
            <span>대시보드</span>
          </div>
          <h2>{user.name}님의 소통 도우미</h2>
          <p>소통이와 함께하는 AAC 카드 의사소통을 시작해보세요</p>
        </div>
        <div className="header-actions">
          {currentView !== 'main' && (
            <button className="secondary-button" onClick={handleBackToMain}>
              대시보드로
            </button>
          )}
          {currentView === 'main' && (
            <>
              <button className="secondary-button" onClick={handleEditProfile}>
                정보 수정
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
              <div className="welcome-card partner-card">
                <div className="card-header" style={{
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '4px'
                }}>
                  <img src="/images/new_chat.png" alt="로고" width="36" height="36" className="card-icon" />
                  <h3 style={{margin: 0}}>새로운 대화 세션 시작</h3>
                </div>
                <p>
                  현재 상황을 입력하고 소통이에게 개인화된 AAC 카드를 추천해주세요.
                  AI가 소통이의 관심사와 대화 맥락을 고려하여 최적의 카드를 제안합니다.
                </p>
                <button className="primary-button large" onClick={handleStartNewSession}>
                  대화 상황 입력하기
                </button>
              </div>

              <div className="user-stats partner-stats">
                <h4>소통이 정보</h4>
                <div className="stats-grid">
                  <div className="stat-item">
                    <label>이름 (닉네임)</label>
                    <span>{user.name}</span>
                  </div>
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
                    <label>등록된 관심 주제</label>
                    <span>{user.interestingTopics?.length || 0}개</span>
                  </div>
                </div>
              </div>
            </div>

            {/* 의사소통 특성 */}
            {user.communicationCharacteristics && (
              <div className="communication-section partner-section">
                <h4>
                  <img src="/images/logo_red.png" alt="로고" width="20" height="20" className="section-icon" />
                  소통이의 의사소통 특성
                </h4>
                <div className="communication-info">
                  <p>{user.communicationCharacteristics}</p>
                </div>
              </div>
            )}

            {/* 관심 주제 목록 */}
            {user.interestingTopics?.length > 0 && (
              <div className="interests-section partner-section">
                <h4>
                  <img src="/images/logo_red.png" alt="로고" width="20" height="20" className="section-icon" />
                  소통이의 관심 주제
                </h4>
                <div className="topic-list">
                  {user.interestingTopics.map((topic, index) => (
                    <span key={index} className="topic-tag partner-topic">
                      {topic}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* 사용 안내 */}
            <div className="usage-guide partner-section">
              <h4>
                <img src="/images/logo_red.png" alt="로고" width="20" height="20" className="section-icon" />
                사용 안내
              </h4>
              <div className="guide-steps">
                <div className="guide-step">
                  <span className="step-number">1</span>
                  <div className="step-content">
                    <strong>상황 입력</strong>
                    <p>도움이가 현재 장소, 대화 상대, 활동 상황을 입력합니다</p>
                  </div>
                </div>
                <div className="guide-step">
                  <span className="step-number">2</span>
                  <div className="step-content">
                    <strong>카드 선택</strong>
                    <p>소통이가 추천받은 카드 중 원하는 카드를 선택합니다</p>
                  </div>
                </div>
                <div className="guide-step">
                  <span className="step-number">3</span>
                  <div className="step-content">
                    <strong>의미 확인</strong>
                    <p>도움이가 AI 해석 중 올바른 의미를 선택하거나 직접 입력합니다</p>
                  </div>
                </div>
              </div>
            </div>
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