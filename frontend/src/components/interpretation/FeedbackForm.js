import React, { useState } from 'react';
import { feedbackService } from '../../services/feedbackService';

const FeedbackForm = ({ 
  interpretations, 
  selectedCards, 
  contextInfo, 
  userId, 
  onFeedbackSubmit 
}) => {
  const [selectedInterpretationIndex, setSelectedInterpretationIndex] = useState(null);
  const [directFeedback, setDirectFeedback] = useState('');
  const [feedbackType, setFeedbackType] = useState('interpretation'); // 'interpretation' or 'direct'
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [confirmationId, setConfirmationId] = useState(null);

  const handleRequestConfirmation = async () => {
    setLoading(true);
    setError('');

    try {
      const requestData = {
        userId,
        cards: selectedCards.map(card => card.filename),
        context: contextInfo,
        interpretations: interpretations.map(interp => interp.text),
        partnerInfo: 'Partner'
      };

      const response = await feedbackService.requestPartnerConfirmation(requestData);
      if (response.success) {
        setConfirmationId(response.data.confirmationId);
      }
    } catch (error) {
      setError(error.message || '확인 요청에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitFeedback = async () => {
    setLoading(true);
    setError('');

    try {
      const feedbackData = {};
      
      if (feedbackType === 'interpretation' && selectedInterpretationIndex !== null) {
        feedbackData.selectedInterpretationIndex = selectedInterpretationIndex;
      } else if (feedbackType === 'direct' && directFeedback.trim()) {
        feedbackData.directFeedback = directFeedback.trim();
      } else {
        setError('해석을 선택하거나 직접 피드백을 입력해주세요.');
        setLoading(false);
        return;
      }

      const response = await feedbackService.submitPartnerFeedback(confirmationId, feedbackData);
      if (response.success) {
        onFeedbackSubmit(response.data);
      }
    } catch (error) {
      setError(error.message || '피드백 제출에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  if (!confirmationId) {
    return (
      <div className="feedback-form">
        <h3>Partner 피드백 요청</h3>
        <p>Partner에게 올바른 해석을 확인 요청하시겠습니까?</p>
        
        {error && <div className="error-message">{error}</div>}
        
        <button 
          onClick={handleRequestConfirmation}
          disabled={loading}
          className="primary-button"
        >
          {loading ? '요청 중...' : 'Partner 확인 요청'}
        </button>
      </div>
    );
  }

  return (
    <div className="feedback-form">
      <h3>Partner 피드백</h3>
      <p>다음 중 올바른 해석을 선택하거나, 직접 올바른 해석을 입력해주세요:</p>

      <div className="feedback-options">
        <div className="feedback-option">
          <input
            type="radio"
            id="interpretation-feedback"
            name="feedbackType"
            value="interpretation"
            checked={feedbackType === 'interpretation'}
            onChange={(e) => setFeedbackType(e.target.value)}
          />
          <label htmlFor="interpretation-feedback">제시된 해석 중 선택</label>
        </div>

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
                />
                <label htmlFor={`interpretation-${index}`}>
                  <strong>{index + 1}번:</strong> {interpretation.text}
                </label>
              </div>
            ))}
          </div>
        )}

        <div className="feedback-option">
          <input
            type="radio"
            id="direct-feedback"
            name="feedbackType"
            value="direct"
            checked={feedbackType === 'direct'}
            onChange={(e) => setFeedbackType(e.target.value)}
          />
          <label htmlFor="direct-feedback">직접 입력</label>
        </div>

        {feedbackType === 'direct' && (
          <div className="direct-feedback-input">
            <textarea
              value={directFeedback}
              onChange={(e) => setDirectFeedback(e.target.value)}
              placeholder="올바른 해석을 직접 입력해주세요..."
              rows="3"
            />
          </div>
        )}
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="feedback-actions">
        <button 
          onClick={handleSubmitFeedback}
          disabled={loading}
          className="primary-button"
        >
          {loading ? '제출 중...' : '피드백 제출'}
        </button>
      </div>
    </div>
  );
};
