import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { feedbackAPI } from '../services/api';
import '../styles/FeedbackPage.css';

const FeedbackPage = () => {
  const [selectedInterpretation, setSelectedInterpretation] = useState(null);
  const [needsCustom, setNeedsCustom] = useState(false);
  const [customInterpretation, setCustomInterpretation] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const userId = localStorage.getItem('userId');
    const contextId = localStorage.getItem('contextId');
    const selectedCards = localStorage.getItem('selectedCards');

    if (!userId || !contextId || !selectedCards) {
      navigate('/user/create');
      return;
    }

    const storedInterpretation = localStorage.getItem('selectedInterpretation');
    const needsCustomInterpretation = localStorage.getItem('needsCustomInterpretation');

    if (storedInterpretation) {
      setSelectedInterpretation(JSON.parse(storedInterpretation));
    }

    if (needsCustomInterpretation === 'true') {
      setNeedsCustom(true);
    }
  }, [navigate]);

  const handleSubmitFeedback = async () => {
    if (needsCustom && !customInterpretation.trim()) {
      setError('올바른 해석을 입력해주세요.');
      return;
    }

    if (!needsCustom && !selectedInterpretation) {
      setError('해석을 선택해주세요.');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const userId = localStorage.getItem('userId');
      const contextId = localStorage.getItem('contextId');
      const selectedCards = JSON.parse(localStorage.getItem('selectedCards') || '[]');

      const feedbackData = {
        userId,
        contextId,
        selectedCards,
        interpretation: needsCustom ? customInterpretation : selectedInterpretation.text,
        isCustom: needsCustom,
        timestamp: new Date().toISOString()
      };

      await feedbackAPI.submitFeedback(feedbackData);
      await feedbackAPI.updateMemory({
        userId,
        cards: selectedCards,
        interpretation: feedbackData.interpretation,
        context: contextId
      });

      setSuccess(true);

      localStorage.removeItem('selectedInterpretation');
      localStorage.removeItem('needsCustomInterpretation');
      localStorage.removeItem('selectedCards');
      localStorage.removeItem('contextId');

      setTimeout(() => {
        navigate('/context/input');
      }, 2000);

    } catch (err) {
      setError('피드백 저장 중 오류가 발생했습니다.');
      console.error('Error submitting feedback:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartNewSession = () => {
    localStorage.removeItem('selectedInterpretation');
    localStorage.removeItem('needsCustomInterpretation');
    localStorage.removeItem('selectedCards');
    localStorage.removeItem('contextId');
    navigate('/context/input');
  };

  if (success) {
    return (
      <div className="feedback-page">
        <div className="container">
          <div className="success-message">
            <div className="success-icon">✓</div>
            <h2>피드백이 저장되었습니다!</h2>
            <p>시스템이 더 정확한 해석을 제공할 수 있도록 학습했습니다.</p>
            <p>새로운 대화 상황 페이지로 이동합니다...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="feedback-page">
      <div className="container">
        <h2>피드백</h2>
        <p className="subtitle">
          {needsCustom
            ? '올바른 해석을 직접 입력해주세요.'
            : '선택하신 해석에 대한 피드백을 확인해주세요.'
          }
        </p>

        {!needsCustom && selectedInterpretation && (
          <div className="selected-interpretation">
            <h3>선택된 해석</h3>
            <div className="interpretation-display">
              <p>{selectedInterpretation.text}</p>
              {selectedInterpretation.context && (
                <div className="context-info">
                  <strong>상황 분석:</strong> {selectedInterpretation.context}
                </div>
              )}
            </div>
          </div>
        )}

        {needsCustom && (
          <div className="custom-interpretation-section">
            <h3>올바른 해석 입력</h3>
            <textarea
              value={customInterpretation}
              onChange={(e) => setCustomInterpretation(e.target.value)}
              placeholder="선택한 카드들의 올바른 의미나 의도를 자세히 설명해주세요..."
              rows="4"
              disabled={isLoading}
              className="custom-interpretation-input"
            />
          </div>
        )}

        {error && <div className="error-message">{error}</div>}

        <div className="feedback-info">
          <h4>이 정보는 어떻게 사용되나요?</h4>
          <ul>
            <li>AI가 더 정확한 카드 해석을 제공하는데 사용됩니다</li>
            <li>사용자의 의사소통 패턴을 학습하여 개인화된 서비스를 제공합니다</li>
            <li>시스템의 전반적인 성능 향상에 기여합니다</li>
          </ul>
        </div>

        <div className="action-buttons">
          <button
            className="back-button"
            onClick={() => navigate('/cards/interpretation')}
            disabled={isLoading}
          >
            이전으로
          </button>
          <button
            className="submit-feedback-btn"
            onClick={handleSubmitFeedback}
            disabled={isLoading || (needsCustom && !customInterpretation.trim())}
          >
            {isLoading ? '저장 중...' : '피드백 저장'}
          </button>
        </div>

        <div className="new-session-section">
          <button
            className="new-session-btn"
            onClick={handleStartNewSession}
            disabled={isLoading}
          >
            새로운 대화 상황 시작하기
          </button>
        </div>
      </div>
    </div>
  );
};

export default FeedbackPage;
