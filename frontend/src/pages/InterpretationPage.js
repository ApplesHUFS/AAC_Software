import React, { useState, useEffect, useCallback } from 'react';
import { cardService } from '../services/cardService';
import { InterpretationDisplay, FeedbackForm, InterpretationResult } from '../components/interpretation/InterpretationDisplay';

// Google 표준: 상수 분리
const STEPS = {
  INTERPRETING: 'interpreting',
  FEEDBACK: 'feedback', 
  COMPLETED: 'completed'
};

const ERROR_MESSAGES = {
  NETWORK_ERROR: '네트워크 연결을 확인해주세요. 서버에 연결할 수 없습니다.',
  TIMEOUT_ERROR: '요청 시간이 초과되었습니다. 잠시 후 다시 시도해주세요.',
  SERVER_REJECT: '서버에서 해석 생성을 거부했습니다.',
  UNEXPECTED_ERROR: '해석 생성 중 예기치 못한 오류가 발생했습니다.',
  PARTNER_REQUEST_FAILED: 'Partner 확인 요청에 실패했습니다.'
};

/**
 * AAC 카드 해석 및 피드백 수집 페이지
 * @param {Object} props - 컴포넌트 props
 * @param {Object} props.user - 사용자 정보
 * @param {Object} props.contextData - 대화 컨텍스트 정보  
 * @param {Array} props.selectedCards - 선택된 카드 목록
 * @param {Function} props.onSessionComplete - 세션 완료 콜백
 */
const InterpretationPage = ({ user, contextData, selectedCards, onSessionComplete }) => {
  const [interpretations, setInterpretations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentStep, setCurrentStep] = useState(STEPS.INTERPRETING);
  const [feedbackResult, setFeedbackResult] = useState(null);
  const [confirmationId, setConfirmationId] = useState(null);

  useEffect(() => {
    let isCancelled = false;
    
    const runGeneration = async () => {
      if (!isCancelled) {
        await generateInterpretations();
      }
    };
    
    runGeneration();
    
    // Cleanup: API 호출 중 컴포넌트 언마운트 시 메모리 누수 방지
    return () => {
      isCancelled = true;
    };
  }, [generateInterpretations]); // Google 표준: 정확한 dependencies

  const generateInterpretations = useCallback(async () => {
    try {
      const response = await cardService.interpretCards(
        user.userId,
        selectedCards,
        contextData.contextId
      );

      if (response.success) {
        setInterpretations(response.data.interpretations);
        
        // 명세 준수: Partner 피드백 확인 요청 (4.5단계)
        await requestPartnerConfirmation(response.data.interpretations);
      } else {
        // API 에러 (서버에서 반환한 에러)
        setError(response.error || ERROR_MESSAGES.SERVER_REJECT);
      }
    } catch (error) {
      // 네트워크 에러 또는 예기치 못한 에러
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        setError(ERROR_MESSAGES.NETWORK_ERROR);
      } else if (error.message.includes('timeout')) {
        setError(ERROR_MESSAGES.TIMEOUT_ERROR);
      } else {
        setError(error.message || ERROR_MESSAGES.UNEXPECTED_ERROR);
      }
      console.error('해석 생성 에러:', error);
    } finally {
      setLoading(false);
    }
  }, [user.userId, selectedCards, contextData.contextId]); // Google 표준: useCallback dependencies

  const requestPartnerConfirmation = async (interpretations) => {
    try {
      const response = await fetch('/api/feedback/request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: user.userId,
          cards: selectedCards.map(card => card.filename || card),
          context: {
            time: contextData.time,
            place: contextData.place,
            interaction_partner: contextData.interactionPartner,
            current_activity: contextData.currentActivity
          },
          interpretations: interpretations.map(interp => interp.text || interp),
          partnerInfo: 'Partner'
        })
      });

      const result = await response.json();
      if (result.success) {
        // confirmationId를 상태에 저장
        setConfirmationId(result.data.confirmationId);
        setCurrentStep(STEPS.FEEDBACK);
      } else {
        setError(result.error || ERROR_MESSAGES.PARTNER_REQUEST_FAILED);
      }
    } catch (error) {
      setError(error.message || ERROR_MESSAGES.PARTNER_REQUEST_FAILED);
    }
  };

  const handleFeedbackSubmit = (result) => {
    setFeedbackResult(result.feedbackResult);
    setCurrentStep(STEPS.COMPLETED);
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
        <div className="error-actions">
          <button 
            className="primary-button"
            onClick={() => {
              setError('');
              setLoading(true);
              generateInterpretations();
            }}
          >
            다시 시도
          </button>
          <button 
            className="secondary-button"
            onClick={onSessionComplete}
          >
            새로운 대화 시작
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="interpretation-page">
      {currentStep === STEPS.FEEDBACK && (
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
            confirmationId={confirmationId}
            onFeedbackSubmit={handleFeedbackSubmit}
          />
        </>
      )}

      {currentStep === STEPS.COMPLETED && feedbackResult && (
        <InterpretationResult 
          feedbackResult={feedbackResult}
          onStartNewSession={handleStartNewSession}
        />
      )}
    </div>
  );
};

export default InterpretationPage;