import React, { useState, useEffect } from 'react';
import { cardService } from '../services/cardService';
import { InterpretationDisplay, FeedbackForm, InterpretationResult } from '../components/interpretation/InterpretationDisplay';

const InterpretationPage = ({ user, contextData, selectedCards, onSessionComplete }) => {
  const [interpretations, setInterpretations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentStep, setCurrentStep] = useState('interpreting'); // 'interpreting', 'feedback', 'completed'
  const [feedbackResult, setFeedbackResult] = useState(null);

  useEffect(() => {
    generateInterpretations();
  }, []);

  const generateInterpretations = async () => {
    try {
      const response = await cardService.interpretCards(
        user.userId,
        selectedCards,
        contextData.contextId
      );

      if (response.success) {
        setInterpretations(response.data.interpretations);
        setCurrentStep('feedback');
      }
    } catch (error) {
      setError(error.message || '해석 생성에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleFeedbackSubmit = (result) => {
    setFeedbackResult(result.feedbackResult);
    setCurrentStep('completed');
  };

  const handleStartNewSession = () => {
    onSessionComplete();
  };

  if (loading) {
    return (
      <div className="interpretation-page loading">
        <div className="loading-content">
          <h2>카드 해석 중...</h2>
          <p>AI가 선택하신 카드들을 분석하고 있습니다.</p>
          <div className="loading-spinner"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="interpretation-page error">
        <h2>해석 생성 실패</h2>
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>다시 시도</button>
      </div>
    );
  }

  return (
    <div className="interpretation-page">
      {currentStep === 'feedback' && (
        <>
          <InterpretationDisplay 
            interpretations={interpretations}
            selectedCards={selectedCards}
            contextInfo={contextData}
          />
          
          <FeedbackForm 
            interpretations={interpretations}
            selectedCards={selectedCards}
            contextInfo={contextData}
            userId={user.userId}
            onFeedbackSubmit={handleFeedbackSubmit}
          />
        </>
      )}

      {currentStep === 'completed' && feedbackResult && (
        <InterpretationResult 
          feedbackResult={feedbackResult}
          onStartNewSession={handleStartNewSession}
        />
      )}
    </div>
  );
};

export default InterpretationPage;