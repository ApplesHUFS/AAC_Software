import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { cardAPI } from '../services/api';
import '../styles/CardInterpretationPage.css';

const CardInterpretationPage = () => {
  const [selectedCards, setSelectedCards] = useState([]);
  const [interpretations, setInterpretations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const userId = localStorage.getItem('userId');
    const contextId = localStorage.getItem('contextId');
    const storedCards = localStorage.getItem('selectedCards');

    if (!userId || !contextId || !storedCards) {
      navigate('/user/create');
      return;
    }

    const cards = JSON.parse(storedCards);
    setSelectedCards(cards);
    interpretCards(cards, userId, contextId);
  }, [navigate]);

  const interpretCards = async (cards, userId, contextId) => {
    try {
      setIsLoading(true);
      const response = await cardAPI.interpretCards(cards, parseInt(userId), contextId);

      const interpretationsData = response.data.interpretations || [];

      // 백엔드에서 문자열 배열로 받은 해석을 객체 형태로 변환
      const formattedInterpretations = interpretationsData.map((text, index) => ({
        text: text,
        confidence: 0.9 - (index * 0.1), // 순서대로 신뢰도 설정
        rank: index + 1
      }));

      setInterpretations(formattedInterpretations);

      // 피드백 ID를 저장 (백엔드에서 추가 피드백 처리용)
      if (response.data.feedback_id) {
        localStorage.setItem('feedbackId', response.data.feedback_id);
      }

    } catch (err) {
      const errorMessage = err.response?.data?.error || '카드 해석 중 오류가 발생했습니다.';
      setError(errorMessage);
      console.error('Error interpreting cards:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectInterpretation = (interpretation) => {
    localStorage.setItem('selectedInterpretation', JSON.stringify(interpretation));
    navigate('/feedback');
  };

  const handleCustomInterpretation = () => {
    localStorage.setItem('needsCustomInterpretation', 'true');
    navigate('/feedback');
  };

  if (isLoading) {
    return (
      <div className="interpretation-page">
        <div className="container">
          <div className="loading">
            <div className="loading-spinner"></div>
            <p>AI가 카드를 해석하고 있습니다...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="interpretation-page">
      <div className="container">
        <h2>카드 해석 결과</h2>
        <p className="subtitle">선택하신 카드에 대한 해석 결과입니다. 가장 적절한 해석을 선택해주세요.</p>

        <div className="selected-cards">
          <h3>선택한 카드</h3>
          <div className="cards-display">
            {selectedCards.map((card, index) => (
              <div key={index} className="selected-card">
                <img
                  src={`http://localhost:8000/${card.image_path}` || `/images/cards/${card.filename}` || `/images/cards/${card.id}.png`}
                  alt={card.name || card.label}
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'flex';
                  }}
                />
                <div className="card-placeholder" style={{display: 'none'}}>
                  <span>이미지 없음</span>
                </div>
                <span className="card-name">{card.name || card.label}</span>
              </div>
            ))}
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}

        <div className="interpretations">
          <h3>해석 결과 (상위 3개)</h3>
          {interpretations.length > 0 ? (
            <div className="interpretation-list">
              {interpretations.slice(0, 3).map((interpretation, index) => (
                <div key={index} className="interpretation-item">
                  <div className="interpretation-header">
                    <span className="interpretation-rank">#{index + 1}</span>
                    <span className="interpretation-confidence">
                      신뢰도: {Math.round((interpretation.confidence || 0.8) * 100)}%
                    </span>
                  </div>
                  <div className="interpretation-content">
                    <p>{interpretation.text}</p>
                    {interpretation.context && (
                      <div className="interpretation-context">
                        <strong>상황 분석:</strong> {interpretation.context}
                      </div>
                    )}
                  </div>
                  <button
                    className="select-interpretation-btn"
                    onClick={() => handleSelectInterpretation(interpretation)}
                  >
                    이 해석 선택
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="no-interpretations">
              <p>해석 결과를 생성하지 못했습니다.</p>
            </div>
          )}
        </div>

        <div className="action-buttons">
          <button
            className="custom-interpretation-btn"
            onClick={handleCustomInterpretation}
          >
            위의 해석이 모두 틀렸습니다
          </button>
          <button
            className="back-button"
            onClick={() => navigate('/cards/recommendation')}
          >
            카드 다시 선택
          </button>
        </div>
      </div>
    </div>
  );
};

export default CardInterpretationPage;
