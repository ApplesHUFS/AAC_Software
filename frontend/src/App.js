// frontend\src\App.js
import React, { useState, useEffect } from 'react';
import AuthPage from './pages/AuthPage';
import DashboardPage from './pages/DashboardPage';
import CardSelectionPage from './pages/CardSelectionPage';
import InterpretationPage from './pages/InterpretationPage';
import './styles/App.css';

// 세션 스토리지 키 상수
const SESSION_KEYS = {
  USER: 'aac_user',
  CONTEXT: 'aac_context', 
  SELECTED_CARDS: 'aac_selected_cards',
  CURRENT_STEP: 'aac_current_step'
};

// 애플리케이션 단계 상수
const APP_STEPS = {
  AUTH: 'auth',
  DASHBOARD: 'dashboard', 
  CARDS: 'cards',
  INTERPRETATION: 'interpretation'
};

// 전체 애플리케이션의 라우팅과 세션 관리를 담당
const App = () => {
  // 애플리케이션 상태 관리
  const [currentUser, setCurrentUser] = useState(null);
  const [currentStep, setCurrentStep] = useState(APP_STEPS.AUTH);
  const [contextData, setContextData] = useState(null);
  const [selectedCards, setSelectedCards] = useState([]);

  // 세션 저장
  const saveSession = (key, data) => {
    try {
      localStorage.setItem(key, JSON.stringify(data));
    } catch (error) {
      console.error(`세션 저장 실패 (${key}):`, error);
    }
  };

  // 세션 불러오기
  const loadSession = (key) => {
    try {
      const data = localStorage.getItem(key);
      return data ? JSON.parse(data) : null;
    } catch (error) {
      console.error(`세션 불러오기 실패 (${key}):`, error);
      return null;
    }
  };

  // 전체 세션 정리
  const clearSession = () => {
    Object.values(SESSION_KEYS).forEach(key => {
      localStorage.removeItem(key);
    });
  };

  // 컴포넌트 마운트 시 세션 복원
  useEffect(() => {
    const restoreSession = () => {
      try {
        const savedUser = loadSession(SESSION_KEYS.USER);
        if (!savedUser) return;

        setCurrentUser(savedUser);

        const savedContext = loadSession(SESSION_KEYS.CONTEXT);
        const savedCards = loadSession(SESSION_KEYS.SELECTED_CARDS);
        const savedStep = loadSession(SESSION_KEYS.CURRENT_STEP);

        // 진행 중인 세션이 있는 경우 복원
        if (savedContext && savedStep) {
          setContextData(savedContext);

          switch (savedStep) {
            case APP_STEPS.INTERPRETATION:
              if (savedCards && Array.isArray(savedCards) && savedCards.length > 0) {
                setSelectedCards(savedCards);
                setCurrentStep(APP_STEPS.INTERPRETATION);
              } else {
                setCurrentStep(APP_STEPS.CARDS);
              }
              break;
            case APP_STEPS.CARDS:
              setCurrentStep(APP_STEPS.CARDS);
              break;
            default:
              setCurrentStep(APP_STEPS.DASHBOARD);
          }
        } else {
          setCurrentStep(APP_STEPS.DASHBOARD);
        }
      } catch (error) {
        console.error('세션 복원 실패:', error);
        clearSession();
        setCurrentStep(APP_STEPS.AUTH);
      }
    };

    restoreSession();
  }, []);

  // 로그인 성공 처리
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

  // 로그아웃 처리
  const handleLogout = () => {
    setCurrentUser(null);
    setContextData(null);
    setSelectedCards([]);
    setCurrentStep(APP_STEPS.AUTH);
    clearSession();
  };

  // 대화 컨텍스트 생성 완료 처리
  const handleContextCreated = (context) => {
    setContextData(context);
    setCurrentStep(APP_STEPS.CARDS);
    // 세션 상태 저장
    saveSession(SESSION_KEYS.CONTEXT, context);
    saveSession(SESSION_KEYS.CURRENT_STEP, APP_STEPS.CARDS);
  };

  // 카드 선택 완료 처리
  const handleCardSelectionComplete = (cards) => {
    setSelectedCards(cards);
    setCurrentStep(APP_STEPS.INTERPRETATION);
    // 세션 상태 저장
    saveSession(SESSION_KEYS.SELECTED_CARDS, cards);
    saveSession(SESSION_KEYS.CURRENT_STEP, APP_STEPS.INTERPRETATION);
  };

  // 해석 세션 완료 처리
  const handleSessionComplete = () => {
    setContextData(null);
    setSelectedCards([]);
    setCurrentStep(APP_STEPS.DASHBOARD);
    // 세션 데이터만 정리 (사용자 정보는 유지)
    localStorage.removeItem(SESSION_KEYS.CONTEXT);
    localStorage.removeItem(SESSION_KEYS.SELECTED_CARDS);
    saveSession(SESSION_KEYS.CURRENT_STEP, APP_STEPS.DASHBOARD);
  };

  // 단계별 컴포넌트 렌더링
  const renderCurrentStep = () => {
    switch (currentStep) {
      case APP_STEPS.AUTH:
        return <AuthPage onAuthSuccess={handleAuthSuccess} />;
      
      case APP_STEPS.DASHBOARD:
        return currentUser ? (
          <DashboardPage 
            user={currentUser}
            onLogout={handleLogout}
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