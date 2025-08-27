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
    // 로컬 스토리지에서 사용자 정보 복원 시도
    const savedUser = localStorage.getItem('aac_user');
    if (savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        setCurrentUser(userData);
        setCurrentStep('dashboard');
      } catch (error) {
        console.error('Failed to restore user session:', error);
        localStorage.removeItem('aac_user');
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
    localStorage.removeItem('aac_user');
  };

  const handleContextCreated = (context) => {
    setContextData(context);
    setCurrentStep('cards');
  };

  const handleCardSelectionComplete = (cards) => {
    setSelectedCards(cards);
    setCurrentStep('interpretation');
  };

  const handleSessionComplete = () => {
    setContextData(null);
    setSelectedCards([]);
    setCurrentStep('dashboard');
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
