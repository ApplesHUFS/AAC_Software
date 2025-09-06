// src/components/interpretation/InterpretationDisplay.js
import React from 'react';

// 해석 결과 표시 컴포넌트 (도움이가 AI 해석 확인)
const InterpretationDisplay = ({ 
  interpretations, 
  selectedCards, 
  contextInfo, 
  method = 'ai'
}) => {
  return (
    <div className="interpretation-display partner-theme">
      {/* 해석 헤더 */}
      <div className="interpretation-header">
        <h2>
          <img src="/images/logo_red.png" alt="로고" width="32" height="32" className="header-icon" />
          AI 해석 결과 - 어떤 의미가 맞나요?
        </h2>
        <div className="interpretation-method">
          <span className="method-badge partner-badge">
            {method === 'ai' ? 'AI 해석' : '규칙 기반 해석'}
          </span>
        </div>
      </div>

      {/* 상황 요약 */}
      <div className="context-summary partner-summary">
        <h3>
          <img src="/images/logo_red.png" alt="로고" width="24" height="24" className="summary-icon" />
          대화 상황
        </h3>
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
        <h3>
          <img src="/images/logo_red.png" alt="로고" width="24" height="24" className="summary-icon" />
          소통이가 선택한 카드 ({selectedCards.length}개)
        </h3>
        <div className="cards-preview">
          {selectedCards.map((card, index) => (
            <div key={card.filename || index} className="card-preview">
              <div className="card-image-container">
                <img 
                  src={`http://localhost:8000${card.imagePath || `/api/images/${card.filename}`}`} 
                  alt={card.name} 
                  loading="lazy"
                />
                <div className="card-order communicator-order">{index + 1}</div>
              </div>
              <span className="card-name">{card.name}</span>
            </div>
          ))}
        </div>
      </div>

      {/* 해석 목록과 선택 안내 통합 */}
      <div className="interpretations-list">
        <h3>
          <img src="/images/logo_red.png" alt="로고" width="24" height="24" className="list-icon" />
          AI가 제안한 해석 ({interpretations.length}가지) - 올바른 해석을 선택해주세요
        </h3>
        <p className="interpretation-instruction">
          다음 중에서 소통이가 실제로 표현하고 싶었던 의미와 가장 가까운 해석을 선택하거나, 
          모든 해석이 부정확하다면 아래에서 '직접 입력'을 선택해주세요:
        </p>
        
        <div className="interpretations-preview">
          {interpretations.map((interpretation, index) => (
            <div 
              key={index}
              className="interpretation-item partner-item"
            >
              <div className="interpretation-number partner-number">{index + 1}</div>
              <div className="interpretation-text">
                {interpretation.text || interpretation}
              </div>
              <div className="interpretation-confidence">
                <small>AI 신뢰도: 높음</small>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 참고 정보 */}
      <div className="interpretation-note partner-note">
        <h4>
          <img src="/images/logo_red.png" alt="로고" width="20" height="20" className="note-icon" />
          참고사항
        </h4>
        <div className="note-content">
          <p>
            AI는 소통이의 과거 대화 기록과 현재 상황을 종합적으로 분석했습니다
          </p>
          <p>
            정확한 피드백을 주시면 다음번에는 더 정확한 해석을 제공할 수 있습니다
          </p>
          <p>
            제시된 해석이 모두 부정확하다면 '직접 입력'을 선택해주세요
          </p>
        </div>
      </div>
    </div>
  );
};

// 해석 완료 결과 컴포넌트 (최종 결과 표시)
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
    <div className="interpretation-result partner-theme">
      {/* 완료 헤더 */}
      <div className="result-header">
        <div className="role-indicator partner-role">
          <img src="/images/logo_red.png" alt="로고" width="24" height="24" className="role-icon" />
          <span>소통 완료</span>
        </div>
        <h2>
          <img src="/images/logo_red.png" alt="로고" width="32" height="32" className="header-icon" />
          소통이의 마음을 확인했어요!
        </h2>
        <div className="success-indicator partner-success">
          <img src="/images/logo_red.png" alt="로고" width="24" height="24" className="success-icon" />
          <span>성공적으로 완료되었습니다</span>
        </div>
      </div>

      {/* 최종 해석 */}
      <div className="final-interpretation partner-final">
        <h3>
          <img src="/images/logo_red.png" alt="로고" width="24" height="24" className="final-icon" />
          소통이가 전하고 싶었던 마음
        </h3>
        <div className="interpretation-content">
          <div className="final-message">
            "{getFinalInterpretation()}"
          </div>
          <div className="interpretation-meta">
            <span className="feedback-type">({getFeedbackType()})</span>
            <span className="completion-time">완료시간: {getCompletionTime()}</span>
          </div>
        </div>
      </div>

      {/* 세션 요약 */}
      <div className="session-summary partner-session">
        <h3>
          <img src="/images/logo_red.png" alt="로고" width="24" height="24" className="summary-icon" />
          이번 대화 요약
        </h3>
        <div className="summary-grid">
          <div className="summary-item">
            <span className="summary-label">대화 상황:</span>
            <span className="summary-value">
              {contextInfo.place}에서 {contextInfo.interactionPartner}와
              {contextInfo.currentActivity && ` ${contextInfo.currentActivity} 중`}
            </span>
          </div>
          <div className="summary-item">
            <span className="summary-label">선택한 카드:</span>
            <span className="summary-value">{selectedCards.length}개</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">AI 제안 해석:</span>
            <span className="summary-value">{interpretations.length}개</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">확인 방식:</span>
            <span className="summary-value">{getFeedbackType()}</span>
          </div>
        </div>
      </div>

      {/* 사용된 카드 표시 */}
      <div className="cards-used">
        <h3>
          <img src="/images/logo_red.png" alt="로고" width="24" height="24" className="cards-icon" />
          소통에 사용된 카드
        </h3>
        <div className="cards-grid result-cards">
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

      {/* 진행 과정 요약 */}
      <div className="process-summary partner-process">
        <h4>
          <img src="/images/logo_red.png" alt="로고" width="20" height="20" className="process-icon" />
          진행 과정
        </h4>
        <div className="process-steps">
          <div className="process-step completed">
            <img src="/images/logo_red.png" alt="로고" width="16" height="16" className="step-icon" />
            <span className="step-description">도움이가 상황 입력</span>
          </div>
          <div className="process-step completed">
            <img src="/images/logo_red.png" alt="로고" width="16" height="16" className="step-icon" />
            <span className="step-description">소통이가 카드 선택 ({selectedCards.length}개)</span>
          </div>
          <div className="process-step completed">
            <img src="/images/logo_red.png" alt="로고" width="16" height="16" className="step-icon" />
            <span className="step-description">AI 해석 생성 ({interpretations.length}가지)</span>
          </div>
          <div className="process-step completed">
            <img src="/images/logo_red.png" alt="로고" width="16" height="16" className="step-icon" />
            <span className="step-description">도움이가 의미 확인</span>
          </div>
        </div>
      </div>

      {/* 액션 버튼 */}
      <div className="result-actions">
        <button 
          onClick={onStartNewSession}
          className="primary-button partner-button large"
        >
          <img src="/images/logo_red.png" alt="로고" width="20" height="20" className="button-icon" />
          새로운 대화 시작하기
        </button>
      </div>

      {/* 완료 메시지 */}
      <div className="completion-message partner-completion">
        <div className="completion-content">
          <p>
            <img src="/images/logo_red.png" alt="로고" width="20" height="20" className="message-icon" />
            이번 대화에서 사용된 카드와 해석 정보가 시스템에 학습되어 
            다음번에는 더 정확한 추천을 받을 수 있습니다.
          </p>
          <small>
            소통이의 카드 선택과 최종 해석이 메모리에 저장되어 
            향후 개인화 추천에 활용됩니다.
          </small>
        </div>
      </div>
    </div>
  );
};

export default InterpretationDisplay;
export { InterpretationResult };