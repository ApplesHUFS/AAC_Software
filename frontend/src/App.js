import React, { useState, useEffect } from 'react';
import AuthPage from './pages/AuthPage';
import DashboardPage from './pages/DashboardPage';
import CardSelectionPage from './pages/CardSelectionPage';
import InterpretationPage from './pages/InterpretationPage';
import './styles/App.css';

/**
 * AAC 카드 해석 시스템 메인 앱 컴포넌트
 * 전체 애플리케이션의 라우팅과 세션 관리를 담당
 */
const App = () => {
  // 애플리케이션 상태 관리
  const [currentUser, setCurrentUser] = useState(null);
  const [currentStep, setCurrentStep] = useState('auth');
  const [contextData, setContextData] = useState(null);
  const [selectedCards, setSelectedCards] = useState([]);

  /**
   * 컴포넌트 마운트 시 세션 복원
   * localStorage에서 사용자 정보와 진행 상태를 복원
   */
  useEffect(() => {
    const restoreSession = () => {
      try {
        const savedUser = localStorage.getItem('aac_user');
        const savedContext = localStorage.getItem('aac_context');
        const savedCards = localStorage.getItem('aac_selected_cards');
        const savedStep = localStorage.getItem('aac_current_step');
        
        if (savedUser) {
          const userData = JSON.parse(savedUser);
          setCurrentUser(userData);
          
          // 진행 중인 세션이 있는 경우 복원
          if (savedContext && savedStep) {
            const contextData = JSON.parse(savedContext);
            const currentStep = savedStep;
            
            setContextData(contextData);
            
            if (savedCards && currentStep === 'interpretation') {
              const cardsData = JSON.parse(savedCards);
              setSelectedCards(cardsData);
              setCurrentStep('interpretation');
            } else if (currentStep === 'cards') {
              setCurrentStep('cards');
            } else {
              setCurrentStep('dashboard');
            }
          } else {
            setCurrentStep('dashboard');
          }
        }
      } catch (error) {
        console.error('세션 복원 실패:', error);
        // 손상된 세션 데이터 정리
        clearSession();
      }
    };

    restoreSession();
  }, []);

  /**
   * 로그인 성공 시 사용자 데이터 설정
   * app.py의 login 응답 구조에 맞게 처리
   */
  const handleAuthSuccess = (loginResponse) => {
    // app.py에서 data.user 구조로 사용자 정보를 제공
    const userData = {
      userId: loginResponse.userId,
      authenticated: loginResponse.authenticated,
      ...loginResponse.user
    };
    
    setCurrentUser(userData);
    setCurrentStep('dashboard');
    localStorage.setItem('aac_user', JSON.stringify(userData));
  };

  /**
   * 로그아웃 처리
   * 모든 상태와 로컬 스토리지 정리
   */
  const handleLogout = () => {
    setCurrentUser(null);
    setContextData(null);
    setSelectedCards([]);
    setCurrentStep('auth');
    clearSession();
  };

  /**
   * 대화 컨텍스트 생성 완료 처리
   * 카드 선택 단계로 이동
   */
  const handleContextCreated = (context) => {
    setContextData(context);
    setCurrentStep('cards');
    // 세션 상태 저장
    localStorage.setItem('aac_context', JSON.stringify(context));
    localStorage.setItem('aac_current_step', 'cards');
  };

  /**
   * 카드 선택 완료 처리
   * 해석 단계로 이동
   */
  const handleCardSelectionComplete = (cards) => {
    setSelectedCards(cards);
    setCurrentStep('interpretation');
    // 세션 상태 저장
    localStorage.setItem('aac_selected_cards', JSON.stringify(cards));
    localStorage.setItem('aac_current_step', 'interpretation');
  };

  /**
   * 해석 세션 완료 처리
   * 대시보드로 돌아가고 세션 데이터 정리
   */
  const handleSessionComplete = () => {
    setContextData(null);
    setSelectedCards([]);
    setCurrentStep('dashboard');
    // 세션 데이터만 정리 (사용자 정보는 유지)
    localStorage.removeItem('aac_context');
    localStorage.removeItem('aac_selected_cards');
    localStorage.setItem('aac_current_step', 'dashboard');
  };

  /**
   * 전체 세션 정리
   * 모든 localStorage 데이터 제거
   */
  const clearSession = () => {
    localStorage.removeItem('aac_user');
    localStorage.removeItem('aac_context');
    localStorage.removeItem('aac_selected_cards');
    localStorage.removeItem('aac_current_step');
  };

  // 단계별 컴포넌트 렌더링
  const renderCurrentStep = () => {
    switch (currentStep) {
      case 'auth':
        return <AuthPage onAuthSuccess={handleAuthSuccess} />;
      
      case 'dashboard':
        return currentUser ? (
          <DashboardPage 
            user={currentUser}
            onLogout={handleLogout}
            onContextCreated={handleContextCreated}
          />
        ) : null;
      
      case 'cards':
        return (currentUser && contextData) ? (
          <CardSelectionPage 
            user={currentUser}
            contextData={contextData}
            onCardSelectionComplete={handleCardSelectionComplete}
          />
        ) : null;
      
      case 'interpretation':
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