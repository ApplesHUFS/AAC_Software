import React from 'react';

const InterpretationResult = ({ feedbackResult, onStartNewSession }) => {
  const getFinalInterpretation = () => {
    return feedbackResult.selected_interpretation || feedbackResult.direct_feedback;
  };

  const getFeedbackType = () => {
    return feedbackResult.feedback_type === 'interpretation_selected' 
      ? '제시된 해석 선택' 
      : '직접 피드백';
  };

  return (
    <div className="interpretation-result">
      <div className="result-header">
        <h2>해석 완료</h2>
        <div className="success-indicator">✓</div>
      </div>

      <div className="result-content">
        <div className="final-interpretation">
          <h3>최종 해석</h3>
          <p className="interpretation-text">{getFinalInterpretation()}</p>
          <small className="feedback-type">({getFeedbackType()})</small>
        </div>

        <div className="session-summary">
          <h4>세션 정보</h4>
          <ul>
            <li><strong>사용자:</strong> {feedbackResult.user_id}</li>
            <li><strong>선택된 카드 수:</strong> {feedbackResult.cards.length}개</li>
            <li><strong>생성된 해석 수:</strong> {feedbackResult.interpretations.length}개</li>
            <li><strong>완료 시간:</strong> {new Date(feedbackResult.confirmed_at).toLocaleString()}</li>
          </ul>
        </div>

        <div className="cards-used">
          <h4>사용된 카드</h4>
          <div className="cards-list">
            {feedbackResult.cards.map((cardFilename, index) => {
              const cardName = cardFilename.replace('.png', '').replace('_', ' ');
              return (
                <div key={index} className="card-item-small">
                  <img 
                    src={`http://localhost:8000/api/images/${cardFilename}`}
                    alt={cardName}
                  />
                  <span>{cardName}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <div className="result-actions">
        <button 
          onClick={onStartNewSession}
          className="primary-button"
        >
          새로운 대화 시작
        </button>
      </div>
    </div>
  );
};

export { InterpretationDisplay, FeedbackForm, InterpretationResult };