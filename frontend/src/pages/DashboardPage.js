import React, { useState } from 'react';
import { ContextForm } from '../components/context/ContextForm';

// 대시보드 페이지 컴포넌트
// 로그인된 사용자의 메인 페이지로 사용자 정보 표시 및 새 대화 세션 시작
const DashboardPage = ({ user, onLogout, onContextCreated }) => {
  const [showContextForm, setShowContextForm] = useState(false);

  // 새 대화 세션 시작 버튼 클릭 처리
  const handleStartNewSession = () => {
    setShowContextForm(true);
  };

  // 컨텍스트 생성 완료 처리
  // 부모 컴포넌트로 생성된 컨텍스트 데이터 전달
  const handleContextCreated = (contextData) => {
    onContextCreated(contextData);
  };

  // 프로필 수정 버튼 클릭 처리
  const handleEditProfile = () => {
    // 향후 프로필 수정 페이지 구현 시 사용
    console.log('프로필 수정 기능 준비 중');
  };

  return (
    <div className="dashboard-page">
      {/* 대시보드 헤더 */}
      <header className="dashboard-header">
        <div className="user-info">
          <h2>안녕하세요, {user.name}님!</h2>
          <p>AAC 카드를 사용한 개인화된 의사소통을 시작해보세요.</p>
        </div>
        <div className="header-actions">
          <button 
            className="secondary-button"
            onClick={handleEditProfile}
          >
            프로필 수정
          </button>
          <button 
            className="secondary-button" 
            onClick={onLogout}
          >
            로그아웃
          </button>
        </div>
      </header>

      {/* 메인 콘텐츠 */}
      <div className="dashboard-content">
        {!showContextForm ? (
          <div className="dashboard-welcome">
            {/* 대화 시작 카드 */}
            <div className="welcome-card">
              <h3>새로운 대화 세션 시작</h3>
              <p>
                현재 상황을 입력하고 개인화된 AAC 카드 추천을 받아보세요.
                AI가 당신의 관심사와 대화 맥락을 고려하여 최적의 카드를 추천해드립니다.
              </p>
              <button 
                className="primary-button large"
                onClick={handleStartNewSession}
              >
                대화 시작하기
              </button>
            </div>

            {/* 사용자 정보 통계 */}
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

            {/* 의사소통 특성 정보 */}
            {user.communicationCharacteristics && (
              <div className="communication-info">
                <h4>의사소통 특성</h4>
                <p>{user.communicationCharacteristics}</p>
              </div>
            )}

            {/* 관심 주제 목록 */}
            {user.interestingTopics && user.interestingTopics.length > 0 && (
              <div className="interests-section">
                <h4>관심 주제</h4>
                <div className="topics-list">
                  {user.interestingTopics.map((topic, index) => (
                    <span key={index} className="topic-tag">
                      {topic}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          /* 컨텍스트 입력 폼 */
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