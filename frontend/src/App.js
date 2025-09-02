// src/App.js
import React, { useState, useEffect } from 'react';
import AuthPage from './pages/AuthPage';
import DashboardPage from './pages/DashboardPage';
import CardSelectionPage from './pages/CardSelectionPage';
import InterpretationPage from './pages/InterpretationPage';
import './styles/App.css';

// 애플리케이션 진행 단계
const APP_STEPS = {
  AUTH: 'auth',
  DASHBOARD: 'dashboard', 
  CARDS: 'cards',
  INTERPRETATION: 'interpretation'
};

// 세션 저장 키
const SESSION_KEYS = {
  USER: 'aac_user',
  CONTEXT: 'aac_context', 
  SELECTED_CARDS: 'aac_selected_cards',
  CURRENT_STEP: 'aac_current_step'
};

const App = () => {
  const [currentUser, setCurrentUser] = useState(null);
  const [currentStep, setCurrentStep] = useState(APP_STEPS.AUTH);
  const [contextData, setContextData] = useState(null);
  const [selectedCards, setSelectedCards] = useState([]);

  // 세션 저장/불러오기
  const saveSession = (key, data) => {
    try {
      localStorage.setItem(key, JSON.stringify(data));
    } catch (error) {
      console.error(`세션 저장 실패: ${key}`, error);
    }
  };

  const loadSession = (key) => {
    try {
      const data = localStorage.getItem(key);
      return data ? JSON.parse(data) : null;
    } catch (error) {
      console.error(`세션 불러오기 실패: ${key}`, error);
      return null;
    }
  };

  const clearSession = () => {
    Object.values(SESSION_KEYS).forEach(key => {
      localStorage.removeItem(key);
    });
  };

  // 앱 시작 시 세션 복원
  useEffect(() => {
    const savedUser = loadSession(SESSION_KEYS.USER);
    if (!savedUser) return;

    setCurrentUser(savedUser);

    const savedContext = loadSession(SESSION_KEYS.CONTEXT);
    const savedCards = loadSession(SESSION_KEYS.SELECTED_CARDS);
    const savedStep = loadSession(SESSION_KEYS.CURRENT_STEP);

    if (savedContext && savedStep) {
      setContextData(savedContext);
      
      if (savedStep === APP_STEPS.INTERPRETATION && savedCards?.length > 0) {
        setSelectedCards(savedCards);
        setCurrentStep(APP_STEPS.INTERPRETATION);
      } else if (savedStep === APP_STEPS.CARDS) {
        setCurrentStep(APP_STEPS.CARDS);
      } else {
        setCurrentStep(APP_STEPS.DASHBOARD);
      }
    } else {
      setCurrentStep(APP_STEPS.DASHBOARD);
    }
  }, []);

  // 인증 성공 처리
  const handleAuthSuccess = (loginResponse) => {
    const userData = {
      userId: loginResponse.userId,
      authenticated: loginResponse.authenticated,
      ...loginResponse.user
    };
    
    setCurrentUser(userData);
    setCurrentStep(APP_STEPS.DASHBOARD);
    saveSession(SESSION_KEYS.USER, userData);
  };

  // 로그아웃
  const handleLogout = () => {
    setCurrentUser(null);
    setContextData(null);
    setSelectedCards([]);
    setCurrentStep(APP_STEPS.AUTH);
    clearSession();
  };

  // 사용자 정보 업데이트
  const handleUserUpdate = (updatedUser) => {
    setCurrentUser(updatedUser);
    saveSession(SESSION_KEYS.USER, updatedUser);
  };

  // 컨텍스트 생성 완료
  const handleContextCreated = (context) => {
    setContextData(context);
    setCurrentStep(APP_STEPS.CARDS);
    saveSession(SESSION_KEYS.CONTEXT, context);
    saveSession(SESSION_KEYS.CURRENT_STEP, APP_STEPS.CARDS);
  };

  // 카드 선택 완료
  const handleCardSelectionComplete = (cards) => {
    setSelectedCards(cards);
    setCurrentStep(APP_STEPS.INTERPRETATION);
    saveSession(SESSION_KEYS.SELECTED_CARDS, cards);
    saveSession(SESSION_KEYS.CURRENT_STEP, APP_STEPS.INTERPRETATION);
  };

  // 대화 세션 완료
  const handleSessionComplete = () => {
    setContextData(null);
    setSelectedCards([]);
    setCurrentStep(APP_STEPS.DASHBOARD);
    
    // 대화 관련 세션만 정리
    localStorage.removeItem(SESSION_KEYS.CONTEXT);
    localStorage.removeItem(SESSION_KEYS.SELECTED_CARDS);
    saveSession(SESSION_KEYS.CURRENT_STEP, APP_STEPS.DASHBOARD);
  };

  // 현재 단계에 따른 컴포넌트 렌더링
  const renderCurrentStep = () => {
    switch (currentStep) {
      case APP_STEPS.AUTH:
        return <AuthPage onAuthSuccess={handleAuthSuccess} />;
      
      case APP_STEPS.DASHBOARD:
        return currentUser ? (
          <DashboardPage 
            user={currentUser}
            onLogout={handleLogout}
            onUserUpdate={handleUserUpdate}
            onContextCreated={handleContextCreated}
          />
        ) : null;
      
      case APP_STEPS.CARDS:
        return (currentUser && contextData) ? (
          <CardSelectionPage 
            user={currentUser}
            contextData={contextData}
            onCardSelectionComplete={handleCardSelectionComplete}
          />
        ) : null;
      
      case APP_STEPS.INTERPRETATION:
        return (currentUser && contextData && selectedCards.length > 0) ? (
          <InterpretationPage 
            user={currentUser}
            contextData={contextData}
            selectedCards={selectedCards}
            onSessionComplete={handleSessionComplete}
          />
        ) : null;
      
      default:
        return <AuthPage onAuthSuccess={handleAuthSuccess} />;
    }
  };

  return (
    <div className="app">
      {renderCurrentStep()}
    </div>
  );
};

export default App;