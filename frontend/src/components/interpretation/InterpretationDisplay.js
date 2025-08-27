import React, { useState } from 'react';

const InterpretationDisplay = ({ interpretations, selectedCards, contextInfo, onSelectInterpretation = null, selectedIndex = null }) => {
  return (
    <div className="interpretation-display">
      <div className="interpretation-header">
        <h2>카드 해석 결과</h2>
        <div className="context-summary">
          <p><strong>상황:</strong> {contextInfo.place}에서 {contextInfo.interactionPartner}와</p>
          {contextInfo.currentActivity && (
            <p><strong>활동:</strong> {contextInfo.currentActivity}</p>
          )}
          <p><strong>시간:</strong> {contextInfo.time}</p>
        </div>
      </div>

      <div className="selected-cards-summary">
        <h3>선택된 카드</h3>
        <div className="cards-preview">
          {selectedCards.map((card) => (
            <div key={card.filename} className="card-preview">
              <img src={`http://localhost:8000${card.imagePath}`} alt={card.name} />
              <span>{card.name}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="interpretations-list">
        <h3>가능한 해석 (3가지)</h3>
        <p>Partner가 가장 적절한 해석을 선택해주세요:</p>
        
        {interpretations.map((interpretation, index) => (
          <div 
            key={index}
            className={`interpretation-item ${selectedIndex === index ? 'selected' : ''}`}
            onClick={onSelectInterpretation ? () => onSelectInterpretation(index) : undefined}
            style={{ cursor: onSelectInterpretation ? 'pointer' : 'default' }}
          >
            <div className="interpretation-number">{index + 1}</div>
            <div className="interpretation-text">{interpretation.text || interpretation}</div>
            {selectedIndex === index && <div className="selection-indicator">선택됨</div>}
          </div>
        ))}
      </div>
    </div>
  );
};

const FeedbackForm = ({ interpretations, selectedCards, contextInfo, userId, confirmationId, onFeedbackSubmit }) => {
  const [selectedIndex, setSelectedIndex] = useState(null);
  const [directFeedback, setDirectFeedback] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    // Google 표준: 필수 데이터 검증
    if (!confirmationId) {
      console.error('confirmationId가 필요합니다');
      setLoading(false);
      return;
    }

    if (selectedIndex === null && !directFeedback.trim()) {
      console.error('해석 선택 또는 직접 피드백이 필요합니다');
      setLoading(false);
      return;
    }

    try {
      // 명세 준수: confirmationId와 함께 피드백 제출
      const feedbackData = {
        confirmationId: confirmationId,
        selectedInterpretationIndex: selectedIndex,
        directFeedback: directFeedback.trim() || null
      };

      const result = await fetch('/api/feedback/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(feedbackData)
      });

      const response = await result.json();
      if (response.success) {
        onFeedbackSubmit(response);
      }
    } catch (error) {
      console.error('피드백 제출 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="feedback-form">
      <h3>Partner 피드백</h3>
      <p>가장 적절한 해석을 선택하거나 직접 입력해주세요.</p>
      
      <form onSubmit={handleSubmit}>
        <div className="interpretation-options">
          {interpretations.map((interpretation, index) => (
            <label key={index} className="interpretation-option">
              <input
                type="radio"
                name="interpretation"
                value={index}
                checked={selectedIndex === index}
                onChange={() => setSelectedIndex(index)}
              />
              <span>{interpretation.text || interpretation}</span>
            </label>
          ))}
        </div>

        <div className="direct-feedback-section">
          <label htmlFor="directFeedback">직접 입력 (선택사항)</label>
          <textarea
            id="directFeedback"
            value={directFeedback}
            onChange={(e) => setDirectFeedback(e.target.value)}
            placeholder="적절한 해석이 없다면 직접 입력해주세요"
          />
        </div>

        <button 
          type="submit" 
          disabled={loading || (selectedIndex === null && !directFeedback.trim())}
        >
          {loading ? '제출 중...' : '피드백 제출'}
        </button>
      </form>
    </div>
  );
};

const InterpretationResult = ({ feedbackResult, onStartNewSession }) => {
  return (
    <div className="interpretation-result">
      <h2>해석 완료</h2>
      <div className="result-summary">
        <h3>최종 해석</h3>
        <p>{feedbackResult.selectedInterpretation || feedbackResult.directFeedback}</p>
        
        <div className="session-actions">
          <button 
            className="primary-button"
            onClick={onStartNewSession}
          >
            새로운 대화 시작
          </button>
        </div>
      </div>
    </div>
  );
};

export default InterpretationDisplay;
export { InterpretationDisplay, FeedbackForm, InterpretationResult };
