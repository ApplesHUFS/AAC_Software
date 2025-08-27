import React, { useState, useEffect } from 'react';
import AuthPage from './pages/AuthPage';
import DashboardPage from './pages/DashboardPage';
import CardSelectionPage from './pages/CardSelectionPage';
import InterpretationPage from './pages/InterpretationPage';
import './styles/App.css';

const App = () => {
  const [currentUser, setCurrentUser] = useState(null);
  const [currentStep, setCurrentStep] = useState('auth'); // 'auth', 'dashboard', 'cards', 'interpretation'
  const [contextData, setContextData] = useState(null);
  const [selectedCards, setSelectedCards] = useState([]);

  useEffect(() => {
    // Google 표준: 안전한 세션 복원
    const savedUser = localStorage.getItem('aac_user');
    const savedContext = localStorage.getItem('aac_context');
    const savedCards = localStorage.getItem('aac_selected_cards');
    const savedStep = localStorage.getItem('aac_current_step');
    
    if (savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        setCurrentUser(userData);
        
        // 컨텍스트와 카드 데이터가 있으면 복원
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
      } catch (error) {
        console.error('Failed to restore user session:', error);
        // 손상된 데이터 정리
        localStorage.removeItem('aac_user');
        localStorage.removeItem('aac_context');
        localStorage.removeItem('aac_selected_cards');
        localStorage.removeItem('aac_current_step');
      }
    }
  }, []);

  const handleAuthSuccess = (userData) => {
    setCurrentUser(userData);
    setCurrentStep('dashboard');
    localStorage.setItem('aac_user', JSON.stringify(userData));
  };

  const handleLogout = () => {
    setCurrentUser(null);
    setContextData(null);
    setSelectedCards([]);
    setCurrentStep('auth');
    // Google 표준: 완전한 데이터 정리
    localStorage.removeItem('aac_user');
    localStorage.removeItem('aac_context');
    localStorage.removeItem('aac_selected_cards');
    localStorage.removeItem('aac_current_step');
  };

  const handleContextCreated = (context) => {
    setContextData(context);
    setCurrentStep('cards');
    // 세션 상태 저장
    localStorage.setItem('aac_context', JSON.stringify(context));
    localStorage.setItem('aac_current_step', 'cards');
  };

  const handleCardSelectionComplete = (cards) => {
    setSelectedCards(cards);
    setCurrentStep('interpretation');
    // 세션 상태 저장
    localStorage.setItem('aac_selected_cards', JSON.stringify(cards));
    localStorage.setItem('aac_current_step', 'interpretation');
  };

  const handleSessionComplete = () => {
    setContextData(null);
    setSelectedCards([]);
    setCurrentStep('dashboard');
    // 세션 데이터 정리 (사용자 정보는 유지)
    localStorage.removeItem('aac_context');
    localStorage.removeItem('aac_selected_cards');
    localStorage.setItem('aac_current_step', 'dashboard');
  };

  return (
    <div className="app">
      {currentStep === 'auth' && (
        <AuthPage onAuthSuccess={handleAuthSuccess} />
      )}
      
      {currentStep === 'dashboard' && currentUser && (
        <DashboardPage 
          user={currentUser}
          onLogout={handleLogout}
          onContextCreated={handleContextCreated}
        />
      )}
      
      {currentStep === 'cards' && currentUser && contextData && (
        <CardSelectionPage 
          user={currentUser}
          contextData={contextData}
          onCardSelectionComplete={handleCardSelectionComplete}
        />
      )}
      
      {currentStep === 'interpretation' && currentUser && contextData && selectedCards.length > 0 && (
        <InterpretationPage 
          user={currentUser}
          contextData={contextData}
          selectedCards={selectedCards}
          onSessionComplete={handleSessionComplete}
        />
      )}
    </div>
  );
};

export default App;
