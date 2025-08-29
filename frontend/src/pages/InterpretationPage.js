// InterpretationPage.js - 카드 해석 및 피드백 페이지
import React, { useState, useEffect, useCallback } from 'react';
import { cardService } from '../services/cardService';
import { feedbackService } from '../services/feedbackService';

// 해석 진행 단계 상수
const STEPS = {
  INTERPRETING: 'interpreting',    // AI가 카드 해석 중
  FEEDBACK: 'feedback',           // Partner 피드백 대기 중
  COMPLETED: 'completed'          // 해석 완료
};

// 흐름명세서: 카드 해석 → Partner 피드백 요청 → 피드백 수집 → 완료
const InterpretationPage = ({ user, contextData, selectedCards, onSessionComplete }) => {
  // 해석 관련 상태
  const [interpretations, setInterpretations] = useState([]);
  const [feedbackResult, setFeedbackResult] = useState(null);
  const [confirmationId, setConfirmationId] = useState(null);
  
  // UI 상태
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentStep, setCurrentStep] = useState(STEPS.INTERPRETING);
  
  // 해석 방법
  const [interpretationMethod, setInterpretationMethod] = useState('');

  // Partner 피드백 확인 요청
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

      const response = await feedbackService.requestPartnerConfirmation(requestPayload);
      
      if (response.success && response.data?.confirmationId) {
        setConfirmationId(response.data.confirmationId);
        setCurrentStep(STEPS.FEEDBACK);
      } else {
        throw new Error(response.error || 'Partner 확인 요청에 실패했습니다.');
      }
    } catch (error) {
      console.error('Partner 확인 요청 실패:', error);
      throw error;
    }
  }, [user.userId, selectedCards, contextData]);

  // AI 카드 해석 생성
  const generateInterpretations = useCallback(async () => {
    if (!user?.userId || !selectedCards?.length || !contextData?.contextId) {
      throw new Error('필수 정보가 누락되었습니다.');
    }

    try {
      setLoading(true);
      setError('');

      // cardService를 통한 해석 요청
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
        throw new Error(response.error || '서버에서 해석 생성을 거부했습니다.');
      }
    } catch (error) {
      console.error('해석 생성 에러:', error);
      throw error;
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
    
    return () => {
      isCancelled = true;
    };
  }, [generateInterpretations]);

  // Partner 피드백 제출 완료 처리
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

// 해석 결과 표시 컴포넌트
const InterpretationDisplay = ({ interpretations, selectedCards, contextInfo, method = 'ai' }) => {
  return (
    <div className="interpretation-display">
      <div className="interpretation-header">
        <h2>카드 해석 결과</h2>
        <div className="interpretation-method">
          <span className="method-badge">
            {method === 'ai' ? 'AI 해석' : '규칙 기반 해석'}
          </span>
        </div>
      </div>

      {/* 상황 요약 */}
      <div className="context-summary">
        <h3>대화 상황</h3>
        <div className="context-details">
          <div className="context-item">
            <span className="context-label">장소:</span>
            <span className="context-value">{contextInfo.place}</span>
          </div>
          <div className="context-item">
            <span className="context-label">대화상대:</span>
            <span className="context-value">{contextInfo.interactionPartner}</span>
          </div>
          {contextInfo.currentActivity && (
            <div className="context-item">
              <span className="context-label">활동:</span>
              <span className="context-value">{contextInfo.currentActivity}</span>
            </div>
          )}
        </div>
      </div>

      {/* 선택된 카드 미리보기 */}
      <div className="selected-cards-summary">
        <h3>선택된 카드 ({selectedCards.length}개)</h3>
        <div className="cards-preview">
          {selectedCards.map((card, index) => (
            <div key={card.filename || index} className="card-preview">
              <div className="card-image-container">
                <img 
                  src={`http://localhost:8000${card.imagePath || `/api/images/${card.filename}`}`} 
                  alt={card.name} 
                  loading="lazy"
                />
                <div className="card-order">{index + 1}</div>
              </div>
              <span className="card-name">{card.name}</span>
            </div>
          ))}
        </div>
      </div>

      {/* 해석 목록 */}
      <div className="interpretations-list">
        <h3>가능한 해석 ({interpretations.length}가지)</h3>
        <p className="interpretation-instruction">
          다음 중에서 가장 적절한 해석을 Partner가 선택해주세요:
        </p>
        
        {interpretations.map((interpretation, index) => (
          <div key={index} className="interpretation-item">
            <div className="interpretation-number">{index + 1}</div>
            <div className="interpretation-text">
              {interpretation.text || interpretation}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Partner 피드백 폼 컴포넌트
const FeedbackForm = ({ interpretations, contextInfo, confirmationId, onFeedbackSubmit }) => {
  const [selectedInterpretationIndex, setSelectedInterpretationIndex] = useState(null);
  const [directFeedback, setDirectFeedback] = useState('');
  const [feedbackType, setFeedbackType] = useState('interpretation');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // 피드백 제출 처리
  const handleSubmitFeedback = async (e) => {
    e.preventDefault();
    setError('');
    
    // 입력 검증
    if (feedbackType === 'interpretation' && selectedInterpretationIndex === null) {
      setError('해석을 선택해주세요.');
      return;
    }
    
    if (feedbackType === 'direct' && !directFeedback.trim()) {
      setError('피드백 내용을 입력해주세요.');
      return;
    }

    setLoading(true);

    try {
      const feedbackData = {};
      
      if (feedbackType === 'interpretation') {
        feedbackData.selectedInterpretationIndex = selectedInterpretationIndex;
      } else {
        feedbackData.directFeedback = directFeedback.trim();
      }

      const response = await feedbackService.submitPartnerFeedback(confirmationId, feedbackData);
      
      if (response.success) {
        onFeedbackSubmit(response);
      } else {
        setError(response.error || '피드백 제출에 실패했습니다.');
      }
    } catch (error) {
      console.error('피드백 제출 에러:', error);
      setError(error.message || '피드백 제출 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="feedback-form">
      <div className="feedback-header">
        <h3>Partner 피드백</h3>
        <p>
          <strong>{contextInfo.interactionPartner}</strong>님, 
          위의 해석 중 가장 적절한 것을 선택하거나 직접 입력해주세요.
        </p>
      </div>

      <form onSubmit={handleSubmitFeedback}>
        {/* 피드백 타입 선택 */}
        <div className="feedback-type-selection">
          <div className="feedback-option">
            <input
              type="radio"
              id="interpretation-feedback"
              name="feedbackType"
              value="interpretation"
              checked={feedbackType === 'interpretation'}
              onChange={() => setFeedbackType('interpretation')}
              disabled={loading}
            />
            <label htmlFor="interpretation-feedback">제시된 해석 중 선택</label>
          </div>

          <div className="feedback-option">
            <input
              type="radio"
              id="direct-feedback"
              name="feedbackType"
              value="direct"
              checked={feedbackType === 'direct'}
              onChange={() => setFeedbackType('direct')}
              disabled={loading}
            />
            <label htmlFor="direct-feedback">직접 입력</label>
          </div>
        </div>

        {/* 해석 선택 */}
        {feedbackType === 'interpretation' && (
          <div className="interpretation-selection">
            {interpretations.map((interpretation, index) => (
              <div key={index} className="interpretation-option">
                <input
                  type="radio"
                  id={`interpretation-${index}`}
                  name="selectedInterpretation"
                  value={index}
                  checked={selectedInterpretationIndex === index}
                  onChange={() => setSelectedInterpretationIndex(index)}
                  disabled={loading}
                />
                <label htmlFor={`interpretation-${index}`}>
                  <strong>{index + 1}번:</strong>
                  <span>{interpretation.text || interpretation}</span>
                </label>
              </div>
            ))}
          </div>
        )}

        {/* 직접 입력 */}
        {feedbackType === 'direct' && (
          <div className="direct-feedback-section">
            <textarea
              value={directFeedback}
              onChange={(e) => setDirectFeedback(e.target.value)}
              placeholder="올바른 해석을 직접 입력해주세요."
              rows="4"
              disabled={loading}
              maxLength="500"
            />
            <div className="character-count">
              {directFeedback.length}/500자
            </div>
          </div>
        )}

        {error && (
          <div className="error-message">
            <span className="error-icon">⚠</span>
            {error}
          </div>
        )}

        <button 
          type="submit"
          className="primary-button"
          disabled={loading}
        >
          {loading ? '제출 중...' : '피드백 제출'}
        </button>
      </form>
    </div>
  );
};

// 해석 완료 결과 컴포넌트
const InterpretationResult = ({ feedbackResult, selectedCards, contextInfo, onStartNewSession }) => {
  const getFinalInterpretation = () => {
    return feedbackResult?.selected_interpretation || 
           feedbackResult?.direct_feedback || 
           '해석 결과를 찾을 수 없습니다.';
  };

  return (
    <div className="interpretation-result">
      <div className="result-header">
        <h2>해석 완료</h2>
        <div className="success-indicator">
          <span className="success-icon">✓</span>
          <span>성공적으로 완료되었습니다</span>
        </div>
      </div>

      <div className="final-interpretation">
        <h3>최종 해석</h3>
        <div className="interpretation-content">
          <p className="interpretation-text">
            "{getFinalInterpretation()}"
          </p>
        </div>
      </div>

      <div className="result-actions">
        <button 
          onClick={onStartNewSession}
          className="primary-button large"
        >
          새로운 대화 시작
        </button>
      </div>
    </div>
  );
};

export default InterpretationPage;