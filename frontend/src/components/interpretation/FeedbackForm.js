// src/components/interpretation/FeedbackForm.js
import React, { useState } from 'react';
import { feedbackService } from '../../services/feedbackService';

// Partner 피드백 폼 컴포넌트 (도움이가 올바른 해석 선택)
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

  // 피드백 타입 변경 처리
  const handleFeedbackTypeChange = (type) => {
    setFeedbackType(type);
    setError('');
    
    if (type === 'interpretation') {
      setDirectFeedback('');
    } else {
      setSelectedInterpretationIndex(null);
    }
  };

  // 해석 선택 처리
  const handleInterpretationSelect = (index) => {
    setSelectedInterpretationIndex(index);
    setError('');
  };

  // 직접 피드백 입력 변경 처리
  const handleDirectFeedbackChange = (e) => {
    setDirectFeedback(e.target.value);
    setError('');
  };

  // 피드백 제출 검증
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

  // 피드백 제출 처리
  const handleSubmitFeedback = async (e) => {
    e.preventDefault();
    setError('');
    
    const validationError = validateFeedback();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);

    try {
      const feedbackData = {};
      
      if (feedbackType === 'interpretation' && selectedInterpretationIndex !== null) {
        feedbackData.selectedInterpretationIndex = selectedInterpretationIndex;
      } else if (feedbackType === 'direct' && directFeedback.trim()) {
        feedbackData.directFeedback = directFeedback.trim();
      }

      const response = await feedbackService.submitPartnerFeedback(confirmationId, feedbackData);
      
      if (response.success) {
        onFeedbackSubmit(response);
      } else {
        setError(response.error || '피드백 제출에 실패했습니다.');
      }
    } catch (error) {
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
    <div className="feedback-form partner-theme">
      <div className="feedback-header">
        <div className="role-indicator partner-role">
          <img src="/images/logo_red.png" alt="로고" width="24" height="24" className="role-icon" />
          <span>도움이 해석 확인</span>
        </div>
        <h3>
          <img src="/images/logo_red.png" alt="로고" width="24" height="24" className="form-icon" />
          어떤 의미가 맞나요?
        </h3>
        <p>
          <strong>{contextInfo.interactionPartner}</strong>님께서 
          AI가 제안한 해석 중 가장 적절한 것을 선택하거나, 
          직접 올바른 의미를 입력해주세요.
        </p>
      </div>

      <form onSubmit={handleSubmitFeedback}>
        {/* 피드백 타입 선택 */}
        <div className="feedback-type-selection partner-selection">
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
            <label htmlFor="interpretation-feedback" className="option-label">
              <img src="/images/logo_red.png" alt="로고" width="20" height="20" className="option-icon" />
              제시된 해석 중 선택
            </label>
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
            <label htmlFor="direct-feedback" className="option-label">
              <img src="/images/logo_red.png" alt="로고" width="20" height="20" className="option-icon" />
              직접 입력
            </label>
          </div>
        </div>

        {/* 해석 선택 옵션 */}
        {feedbackType === 'interpretation' && (
          <div className="interpretation-selection">
            <h4>
              <img src="/images/logo_red.png" alt="로고" width="20" height="20" className="section-icon" />
              올바른 해석 선택
            </h4>
            <p className="selection-instruction">
              소통이가 선택한 카드가 실제로 표현하고자 한 의미와 가장 가까운 해석을 선택해주세요.
            </p>
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
                <label htmlFor={`interpretation-${index}`} className="interpretation-label">
                  <div className="interpretation-preview">
                    <div className="interpretation-number">{index + 1}</div>
                    <div className="interpretation-content">
                      <span>{interpretation.text || interpretation}</span>
                    </div>
                  </div>
                </label>
              </div>
            ))}
          </div>
        )}

        {/* 직접 입력 옵션 */}
        {feedbackType === 'direct' && (
          <div className="direct-feedback-section">
            <h4>
              <img src="/images/logo_red.png" alt="로고" width="20" height="20" className="section-icon" />
              올바른 의미 직접 입력
            </h4>
            <p className="input-instruction">
              소통이가 선택한 카드들이 실제로 표현하고자 한 의미를 직접 입력해주세요.
            </p>
            <textarea
              value={directFeedback}
              onChange={handleDirectFeedbackChange}
              placeholder="소통이가 카드로 표현하고 싶었던 정확한 의미를 구체적으로 써주세요. 예: '배가 고파서 밥을 먹고 싶어요', '친구와 같이 놀고 싶어요' 등"
              rows="4"
              disabled={loading}
              maxLength="500"
              className="feedback-textarea"
            />
            <div className="character-count">
              {directFeedback.length}/500자
            </div>
          </div>
        )}

        {/* 에러 메시지 */}
        {error && (
          <div className="error-message partner-error">
            <img src="/images/logo_red.png" alt="로고" width="16" height="16" className="error-icon" />
            {error}
          </div>
        )}

        {/* 제출 버튼 */}
        <div className="feedback-actions">
          <button 
            type="submit"
            className="primary-button partner-button large"
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="button-spinner"></span>
                확인 중...
              </>
            ) : (
              <>
                <img src="/images/logo_red.png" alt="로고" width="20" height="20" className="button-icon" />
                이 의미가 맞습니다
              </>
            )}
          </button>
        </div>

        {/* 도움말 */}
        <div className="feedback-help partner-help">
          <h5>
            <img src="/images/logo_red.png" alt="로고" width="16" height="16" className="help-icon" />
            피드백 작성 도움말
          </h5>
          <div className="help-grid">
            <div className="help-item">
              <strong>해석 선택 시</strong>
              <p>AI가 제안한 3가지 중 가장 정확한 의미를 선택해주세요</p>
            </div>
            <div className="help-item">
              <strong>직접 입력 시</strong>
              <p>모든 해석이 부정확하다면 올바른 의미를 직접 써주세요</p>
            </div>
            <div className="help-item">
              <strong>작성 팁</strong>
              <p>구체적이고 명확한 피드백이 AI 학습에 도움이 됩니다</p>
            </div>
          </div>
        </div>
      </form>
    </div>
  );
};

export default FeedbackForm;