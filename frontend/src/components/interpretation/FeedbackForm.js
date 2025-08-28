import React, { useState } from 'react';
import { feedbackService } from '../../services/feedbackService';

// Partner 피드백 폼 컴포넌트
// 흐름명세서: partner는 0~2 인덱스 중에 올바른 해석이라고 생각이 드는 해석을 고름. 어떠한 것도 맞지 않으면 직접 피드백 입력
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
    
    // 타입 변경 시 선택 상태 초기화
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
  // app.py의 /api/feedback/submit 호출
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

export default FeedbackForm;