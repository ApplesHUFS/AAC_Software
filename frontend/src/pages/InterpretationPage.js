import React, { useState, useEffect, useCallback } from 'react';
import { cardService } from '../services/cardService';
import { InterpretationDisplay, FeedbackForm, InterpretationResult } from '../components/interpretation/InterpretationDisplay';

// 해석 진행 단계 상수
const STEPS = {
  INTERPRETING: 'interpreting',    // AI가 카드 해석 중
  FEEDBACK: 'feedback',           // Partner 피드백 대기 중
  COMPLETED: 'completed'          // 해석 완료
};

// 에러 메시지 상수
const ERROR_MESSAGES = {
  NETWORK_ERROR: '네트워크 연결을 확인해주세요. 서버에 연결할 수 없습니다.',
  TIMEOUT_ERROR: '요청 시간이 초과되었습니다. 잠시 후 다시 시도해주세요.',
  SERVER_REJECT: '서버에서 해석 생성을 거부했습니다.',
  UNEXPECTED_ERROR: '해석 생성 중 예기치 못한 오류가 발생했습니다.',
  PARTNER_REQUEST_FAILED: 'Partner 확인 요청에 실패했습니다.',
  INVALID_CARDS: '선택된 카드 정보가 올바르지 않습니다.',
  MISSING_CONTEXT: '대화 컨텍스트 정보가 없습니다.'
};

// AAC 카드 해석 및 피드백 수집 페이지
// 흐름명세서에 따른 카드 해석 → Partner 피드백 요청 → 피드백 수집 → 완료
const InterpretationPage = ({ user, contextData, selectedCards, onSessionComplete }) => {
  // 해석 관련 상태
  const [interpretations, setInterpretations] = useState([]);
  const [feedbackResult, setFeedbackResult] = useState(null);
  const [confirmationId, setConfirmationId] = useState(null);
  
  // UI 상태
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentStep, setCurrentStep] = useState(STEPS.INTERPRETING);
  
  // 진행 상태 추적
  const [interpretationMethod, setInterpretationMethod] = useState('');

  // Partner 피드백 확인 요청
  // 흐름명세서 4.5단계: partner에게 해석 확인 요청
  const requestPartnerConfirmation = useCallback(async (interpretationData) => {
    try {
      const requestPayload = {
        userId: user.userId,
        cards: selectedCards.map(card => card.filename || card.name || card),
        context: {
          time: contextData.time,
          place: contextData.place,
          interactionPartner: contextData.interactionPartner,
          currentActivity: contextData.currentActivity
        },
        interpretations: interpretationData.map(interp => interp.text || interp),
        partnerInfo: contextData.interactionPartner || 'Partner'
      };

      const response = await fetch('http://localhost:8000/api/feedback/request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestPayload)
      });

      const result = await response.json();
      
      if (result.success && result.data?.confirmationId) {
        setConfirmationId(result.data.confirmationId);
        setCurrentStep(STEPS.FEEDBACK);
      } else {
        throw new Error(result.error || ERROR_MESSAGES.PARTNER_REQUEST_FAILED);
      }
    } catch (error) {
      console.error('Partner 확인 요청 실패:', error);
      throw error;
    }
  }, [user.userId, selectedCards, contextData]);

  // AI 카드 해석 생성
  // 흐름명세서 4.4단계: 선택된 카드들을 상황에 맞게 해석 (OpenAI API로 3가지 해석 생성)
  const generateInterpretations = useCallback(async () => {
    // 입력 검증
    if (!user?.userId) {
      throw new Error('사용자 정보가 없습니다.');
    }
    
    if (!selectedCards || selectedCards.length === 0) {
      throw new Error(ERROR_MESSAGES.INVALID_CARDS);
    }
    
    if (!contextData?.contextId) {
      throw new Error(ERROR_MESSAGES.MISSING_CONTEXT);
    }

    try {
      setLoading(true);
      setError('');

      // app.py의 /api/cards/interpret 호출
      const response = await cardService.interpretCards(
        user.userId,
        selectedCards,
        contextData.contextId
      );

      if (response.success && response.data) {
        const interpretationData = response.data.interpretations || [];
        const method = response.data.method || 'ai';

        setInterpretations(interpretationData);
        setInterpretationMethod(method);

        // 흐름명세서 준수: 해석 생성 후 즉시 Partner 피드백 요청
        await requestPartnerConfirmation(interpretationData);
        
      } else {
        throw new Error(response.error || ERROR_MESSAGES.SERVER_REJECT);
      }
    } catch (error) {
      console.error('해석 생성 에러:', error);
      
      // 에러 타입별 처리
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        throw new Error(ERROR_MESSAGES.NETWORK_ERROR);
      } else if (error.message.includes('timeout')) {
        throw new Error(ERROR_MESSAGES.TIMEOUT_ERROR);
      } else {
        throw new Error(error.message || ERROR_MESSAGES.UNEXPECTED_ERROR);
      }
    }
  }, [user, selectedCards, contextData, requestPartnerConfirmation]);

  // 컴포넌트 마운트 시 해석 생성 시작
  useEffect(() => {
    let isCancelled = false;
    
    const runInterpretation = async () => {
      try {
        if (!isCancelled) {
          await generateInterpretations();
        }
      } catch (error) {
        if (!isCancelled) {
          setError(error.message);
        }
      } finally {
        if (!isCancelled) {
          setLoading(false);
        }
      }
    };
    
    runInterpretation();
    
    // Cleanup: API 호출 중 컴포넌트 언마운트 시 메모리 누수 방지
    return () => {
      isCancelled = true;
    };
  }, [generateInterpretations]);

  // Partner 피드백 제출 완료 처리
  // 흐름명세서 마지막 단계: 피드백 수집 완료 후 세션 종료
  const handleFeedbackSubmit = useCallback((feedbackResponse) => {
    if (feedbackResponse?.data?.feedbackResult) {
      setFeedbackResult(feedbackResponse.data.feedbackResult);
      setCurrentStep(STEPS.COMPLETED);
    } else {
      setError('피드백 처리 중 오류가 발생했습니다.');
    }
  }, []);

  // 새 대화 세션 시작
  const handleStartNewSession = useCallback(() => {
    onSessionComplete();
  }, [onSessionComplete]);

  // 해석 재시도
  const handleRetry = useCallback(() => {
    setError('');
    setLoading(true);
    setCurrentStep(STEPS.INTERPRETING);
    setInterpretations([]);
    setConfirmationId(null);
    setFeedbackResult(null);
    
    // 재시도 실행
    generateInterpretations().catch((error) => {
      setError(error.message);
      setLoading(false);
    });
  }, [generateInterpretations]);

  // 로딩 상태 렌더링
  if (loading && currentStep === STEPS.INTERPRETING) {
    return (
      <div className="interpretation-page loading">
        <div className="loading-content">
          <h2>AI가 카드를 해석하고 있습니다...</h2>
          <div className="loading-details">
            <p>선택하신 <strong>{selectedCards.length}개</strong>의 카드를 분석 중입니다.</p>
            <ul>
              {selectedCards.slice(0, 3).map((card, index) => (
                <li key={index}>{card.name}</li>
              ))}
              {selectedCards.length > 3 && <li>외 {selectedCards.length - 3}개...</li>}
            </ul>
            <p>
              <strong>{contextData.place}</strong>에서 <strong>{contextData.interactionPartner}</strong>와의 
              대화 상황을 고려하여 최적의 해석을 생성하고 있습니다.
            </p>
          </div>
          <div className="loading-spinner"></div>
        </div>
      </div>
    );
  }

  // 에러 상태 렌더링
  if (error) {
    return (
      <div className="interpretation-page error">
        <div className="error-content">
          <h2>해석 생성 실패</h2>
          <div className="error-message">
            <span className="error-icon">⚠</span>
            <p>{error}</p>
          </div>
          
          <div className="error-actions">
            <button 
              className="primary-button"
              onClick={handleRetry}
            >
              다시 시도
            </button>
            <button 
              className="secondary-button"
              onClick={handleStartNewSession}
            >
              새로운 대화 시작
            </button>
          </div>

          {/* 디버깅 정보 (개발 환경에서만 표시) */}
          {process.env.NODE_ENV === 'development' && (
            <div className="debug-info">
              <details>
                <summary>디버그 정보</summary>
                <pre>
                  사용자: {user?.userId}
                  컨텍스트: {contextData?.contextId}
                  선택된 카드: {selectedCards?.length}개
                  현재 단계: {currentStep}
                </pre>
              </details>
            </div>
          )}
        </div>
      </div>
    );
  }

  // 단계별 컴포넌트 렌더링
  return (
    <div className="interpretation-page">
      {/* Partner 피드백 대기 단계 */}
      {currentStep === STEPS.FEEDBACK && interpretations.length > 0 && (
        <>
          <InterpretationDisplay 
            interpretations={interpretations}
            selectedCards={selectedCards}
            contextInfo={contextData}
            method={interpretationMethod}
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

      {/* 해석 완료 단계 */}
      {currentStep === STEPS.COMPLETED && feedbackResult && (
        <InterpretationResult 
          feedbackResult={feedbackResult}
          selectedCards={selectedCards}
          contextInfo={contextData}
          interpretations={interpretations}
          onStartNewSession={handleStartNewSession}
        />
      )}

      {/* 진행 상태 표시 */}
      <div className="interpretation-progress">
        <div className="progress-steps">
          <div className={`progress-step ${currentStep === STEPS.INTERPRETING ? 'active' : 'completed'}`}>
            AI 해석 생성
          </div>
          <div className={`progress-step ${currentStep === STEPS.FEEDBACK ? 'active' : currentStep === STEPS.COMPLETED ? 'completed' : ''}`}>
            Partner 피드백
          </div>
          <div className={`progress-step ${currentStep === STEPS.COMPLETED ? 'active' : ''}`}>
            해석 완료
          </div>
        </div>
      </div>
    </div>
  );
};

export default InterpretationPage;