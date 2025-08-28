import React, { useState } from 'react';
import { feedbackService } from '../../services/feedbackService';

/**
 * 해석 결과 표시 컴포넌트
 * AI가 생성한 카드 해석들을 사용자에게 표시
 */
const InterpretationDisplay = ({ 
  interpretations, 
  selectedCards, 
  contextInfo, 
  method = 'ai',
  onSelectInterpretation = null, 
  selectedIndex = null 
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
            className={`interpretation-item ${selectedIndex === index ? 'selected' : ''} ${onSelectInterpretation ? 'clickable' : ''}`}
            onClick={onSelectInterpretation ? () => onSelectInterpretation(index) : undefined}
          >
            <div className="interpretation-header">
              <div className="interpretation-number">{index + 1}</div>
              {selectedIndex === index && (
                <div className="selection-indicator">선택됨</div>
              )}
            </div>
            <div className="interpretation-content">
              <p className="interpretation-text">
                {interpretation.text || interpretation}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* 해석 가이드 */}
      <div className="interpretation-guide">
        <h4>해석 가이드</h4>
        <ul>
          <li>각 해석은 선택된 카드들의 조합과 현재 상황을 고려하여 생성되었습니다</li>
          <li>Partner가 가장 적절하다고 생각하는 해석을 선택해주세요</li>
          <li>적절한 해석이 없다면 직접 입력할 수 있습니다</li>
        </ul>
      </div>
    </div>
  );
};

/**
 * Partner 피드백 폼 컴포넌트
 * 해석 선택 또는 직접 피드백 입력 처리
 */
const FeedbackForm = ({ 
  interpretations, 
  selectedCards, 
  contextInfo, 
  userId, 
  confirmationId,
  onFeedbackSubmit 
}) => {
  const [selectedInterpretationIndex, setSelectedInterpretationIndex] = useState(null);
  const [directFeedback, setDirectFeedback] = useState('');
  const [feedbackType, setFeedbackType] = useState('interpretation');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  /**
   * 피드백 타입 변경 처리
   */
  const handleFeedbackTypeChange = (type) => {
    setFeedbackType(type);
    setError('');
    
    // 타입 변경 시 선택 상태 초기화
    if (type === 'interpretation') {
      setDirectFeedback('');
    } else {
      setSelectedInterpretationIndex(null);
    }
  };

  /**
   * 해석 선택 처리
   */
  const handleInterpretationSelect = (index) => {
    setSelectedInterpretationIndex(index);
    setError('');
  };

  /**
   * 직접 피드백 입력 변경 처리
   */
  const handleDirectFeedbackChange = (e) => {
    setDirectFeedback(e.target.value);
    setError('');
  };

  /**
   * 피드백 제출 검증
   */
  const validateFeedback = () => {
    if (!confirmationId) {
      return '피드백 요청 정보가 없습니다. 페이지를 새로고침해주세요.';
    }

    if (feedbackType === 'interpretation') {
      if (selectedInterpretationIndex === null) {
        return '해석을 선택해주세요.';
      }
    } else if (feedbackType === 'direct') {
      if (!directFeedback.trim()) {
        return '피드백 내용을 입력해주세요.';
      }
      if (directFeedback.trim().length < 5) {
        return '피드백은 5글자 이상 입력해주세요.';
      }
    }

    return null;
  };

  /**
   * 피드백 제출 처리
   */
  const handleSubmitFeedback = async (e) => {
    e.preventDefault();
    setError('');
    
    // 입력 검증
    const validationError = validateFeedback();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);

    try {
      // 피드백 데이터 준비
      const feedbackData = {};
      
      if (feedbackType === 'interpretation' && selectedInterpretationIndex !== null) {
        feedbackData.selectedInterpretationIndex = selectedInterpretationIndex;
      } else if (feedbackType === 'direct' && directFeedback.trim()) {
        feedbackData.directFeedback = directFeedback.trim();
      }

      // app.py의 /api/feedback/submit 호출
      const response = await feedbackService.submitPartnerFeedback(confirmationId, feedbackData);
      
      if (response.success) {
        onFeedbackSubmit(response);
      } else {
        setError(response.error || '피드백 제출에 실패했습니다.');
      }
    } catch (error) {
      console.error('피드백 제출 에러:', error);
      
      if (error.message.includes('fetch')) {
        setError('서버에 연결할 수 없습니다. 네트워크 연결을 확인해주세요.');
      } else {
        setError(error.message || '피드백 제출 중 오류가 발생했습니다.');
      }
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

      <form onSubmit={handleSubmitFeedback} noValidate>
        {/* 피드백 타입 선택 */}
        <div className="feedback-type-selection">
          <div className="feedback-option">
            <input
              type="radio"
              id="interpretation-feedback"
              name="feedbackType"
              value="interpretation"
              checked={feedbackType === 'interpretation'}
              onChange={() => handleFeedbackTypeChange('interpretation')}
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
              onChange={() => handleFeedbackTypeChange('direct')}
              disabled={loading}
            />
            <label htmlFor="direct-feedback">직접 입력</label>
          </div>
        </div>

        {/* 해석 선택 옵션 */}
        {feedbackType === 'interpretation' && (
          <div className="interpretation-selection">
            <h4>해석 선택</h4>
            {interpretations.map((interpretation, index) => (
              <div key={index} className="interpretation-option">
                <input
                  type="radio"
                  id={`interpretation-${index}`}
                  name="selectedInterpretation"
                  value={index}
                  checked={selectedInterpretationIndex === index}
                  onChange={() => handleInterpretationSelect(index)}
                  disabled={loading}
                />
                <label htmlFor={`interpretation-${index}`}>
                  <div className="interpretation-preview">
                    <strong>{index + 1}번:</strong>
                    <span>{interpretation.text || interpretation}</span>
                  </div>
                </label>
              </div>
            ))}
          </div>
        )}

        {/* 직접 입력 옵션 */}
        {feedbackType === 'direct' && (
          <div className="direct-feedback-section">
            <h4>직접 입력</h4>
            <textarea
              value={directFeedback}
              onChange={handleDirectFeedbackChange}
              placeholder="올바른 해석을 직접 입력해주세요. 선택된 카드들이 실제로 표현하고자 하는 의미를 구체적으로 적어주세요."
              rows="4"
              disabled={loading}
              maxLength="500"
            />
            <div className="character-count">
              {directFeedback.length}/500자
            </div>
          </div>
        )}

        {/* 에러 메시지 */}
        {error && (
          <div className="error-message">
            <span className="error-icon">⚠</span>
            {error}
          </div>
        )}

        {/* 제출 버튼 */}
        <div className="feedback-actions">
          <button 
            type="submit"
            className="primary-button"
            disabled={loading}
          >
            {loading ? '제출 중...' : '피드백 제출'}
          </button>
        </div>

        {/* 도움말 */}
        <div className="feedback-help">
          <h5>피드백 가이드</h5>
          <ul>
            <li>가장 적절한 해석이 있다면 해당 번호를 선택해주세요</li>
            <li>모든 해석이 부정확하다면 '직접 입력'을 선택하여 올바른 해석을 입력해주세요</li>
            <li>구체적이고 명확한 피드백이 AI 학습에 도움이 됩니다</li>
          </ul>
        </div>
      </form>
    </div>
  );
};

/**
 * 해석 완료 결과 컴포넌트
 * 최종 해석 결과와 세션 요약 표시
 */
const InterpretationResult = ({ 
  feedbackResult, 
  selectedCards, 
  contextInfo, 
  interpretations,
  onStartNewSession 
}) => {
  /**
   * 최종 해석 텍스트 추출
   */
  const getFinalInterpretation = () => {
    return feedbackResult?.selected_interpretation || 
           feedbackResult?.direct_feedback || 
           feedbackResult?.selectedInterpretation ||
           feedbackResult?.directFeedback ||
           '해석 결과를 찾을 수 없습니다.';
  };

  /**
   * 피드백 타입 추출
   */
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

  /**
   * 완료 시간 포맷팅
   */
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
      </div>
    </div>
  );
};

export default InterpretationDisplay;
export { InterpretationDisplay, FeedbackForm, InterpretationResult };