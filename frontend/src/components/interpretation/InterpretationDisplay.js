// src/components/interpretation/InterpretationDisplay.js
import React from 'react';

// 해석 결과 표시 컴포넌트
const InterpretationDisplay = ({ 
  interpretations, 
  selectedCards, 
  contextInfo, 
  method = 'ai'
}) => {
  return (
    <div className="interpretation-display">
      {/* 해석 헤더 */}
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
          {contextInfo.time && (
            <div className="context-item">
              <span className="context-label">시간:</span>
              <span className="context-value">{contextInfo.time}</span>
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
          <div 
            key={index}
            className="interpretation-item"
          >
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

// 해석 완료 결과 컴포넌트
const InterpretationResult = ({ 
  feedbackResult, 
  selectedCards, 
  contextInfo, 
  interpretations,
  onStartNewSession 
}) => {
  const getFinalInterpretation = () => {
    return feedbackResult?.selected_interpretation || 
           feedbackResult?.direct_feedback || 
           feedbackResult?.selectedInterpretation ||
           feedbackResult?.directFeedback ||
           '해석 결과를 찾을 수 없습니다.';
  };

  const getFeedbackType = () => {
    if (feedbackResult?.feedback_type === 'interpretation_selected' || 
        feedbackResult?.selectedInterpretation) {
      return '제시된 해석 선택';
    } else if (feedbackResult?.feedback_type === 'direct_feedback' || 
               feedbackResult?.directFeedback) {
      return '직접 피드백';
    }
    return '알 수 없음';
  };

  const getCompletionTime = () => {
    const timestamp = feedbackResult?.confirmed_at || 
                     feedbackResult?.timestamp || 
                     new Date().toISOString();
    return new Date(timestamp).toLocaleString('ko-KR');
  };

  return (
    <div className="interpretation-result">
      {/* 완료 헤더 */}
      <div className="result-header">
        <h2>해석 완료</h2>
        <div className="success-indicator">
          <span className="success-icon">✓</span>
          <span>성공적으로 완료되었습니다</span>
        </div>
      </div>

      {/* 최종 해석 */}
      <div className="final-interpretation">
        <h3>최종 해석</h3>
        <div className="interpretation-content">
          <p className="interpretation-text">
            "{getFinalInterpretation()}"
          </p>
          <div className="interpretation-meta">
            <span className="feedback-type">({getFeedbackType()})</span>
            <span className="completion-time">완료: {getCompletionTime()}</span>
          </div>
        </div>
      </div>

      {/* 세션 요약 */}
      <div className="session-summary">
        <h3>세션 요약</h3>
        <div className="summary-grid">
          <div className="summary-item">
            <span className="summary-label">사용자:</span>
            <span className="summary-value">{feedbackResult?.user_id || contextInfo.userId}</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">대화 상황:</span>
            <span className="summary-value">
              {contextInfo.place}에서 {contextInfo.interactionPartner}와
              {contextInfo.currentActivity && ` ${contextInfo.currentActivity} 중`}
            </span>
          </div>
          <div className="summary-item">
            <span className="summary-label">선택된 카드:</span>
            <span className="summary-value">{selectedCards.length}개</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">생성된 해석:</span>
            <span className="summary-value">{interpretations.length}개</span>
          </div>
        </div>
      </div>

      {/* 사용된 카드 표시 */}
      <div className="cards-used">
        <h3>사용된 카드</h3>
        <div className="cards-grid">
          {selectedCards.map((card, index) => (
            <div key={card.filename || index} className="card-item-result">
              <img 
                src={`http://localhost:8000${card.imagePath || `/api/images/${card.filename}`}`}
                alt={card.name}
                loading="lazy"
              />
              <div className="card-info">
                <span className="card-name">{card.name}</span>
                <span className="card-order">#{index + 1}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 해석 진행 과정 요약 */}
      <div className="process-summary">
        <h4>진행 과정</h4>
        <div className="process-steps">
          <div className="process-step">
            <span className="step-number">1</span>
            <span className="step-description">카드 추천 및 선택 ({selectedCards.length}개)</span>
          </div>
          <div className="process-step">
            <span className="step-number">2</span>
            <span className="step-description">AI 해석 생성 ({interpretations.length}가지)</span>
          </div>
          <div className="process-step">
            <span className="step-number">3</span>
            <span className="step-description">Partner 피드백 수집</span>
          </div>
          <div className="process-step">
            <span className="step-number">4</span>
            <span className="step-description">최종 해석 확정</span>
          </div>
        </div>
      </div>

      {/* 액션 버튼 */}
      <div className="result-actions">
        <button 
          onClick={onStartNewSession}
          className="primary-button large"
        >
          새로운 대화 시작
        </button>
      </div>

      {/* 완료 메시지 */}
      <div className="completion-message">
        <p>
          이번 대화에서 사용된 카드와 해석 정보가 시스템에 학습되어 
          다음 번에 더 정확한 추천을 받을 수 있습니다.
        </p>
        <small>
          선택된 카드들과 최종 해석은 메모리에 저장되어 향후 개인화 추천에 활용됩니다.
        </small>
      </div>
    </div>
  );
};

export default InterpretationDisplay;
export { InterpretationDisplay, InterpretationResult };