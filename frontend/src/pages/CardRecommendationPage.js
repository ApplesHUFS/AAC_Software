import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { cardAPI } from '../services/api';
import CardGrid from '../components/cards/CardGrid';
import '../styles/CardRecommendationPage.css';

const CardRecommendationPage = () => {
  const [cards, setCards] = useState([]);
  const [selectedCards, setSelectedCards] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const userId = localStorage.getItem('userId');
    const contextId = localStorage.getItem('contextId');

    if (!userId || !contextId) {
      navigate('/user/create');
      return;
    }

    loadRecommendations();
  }, [navigate]);

  const loadRecommendations = async () => {
    try {
      setIsLoading(true);
      const userId = localStorage.getItem('userId');
      const contextId = localStorage.getItem('contextId');

      const response = await cardAPI.getRecommendations(userId, { contextId });
      setCards(response.data.cards || []);
    } catch (err) {
      setError('카드 추천을 불러오는 중 오류가 발생했습니다.');
      console.error('Error loading recommendations:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCardSelect = (cardId, isSelected) => {
    if (isSelected) {
      if (selectedCards.length >= 4) {
        alert('최대 4개까지만 선택할 수 있습니다.');
        return false;
      }
      setSelectedCards(prev => [...prev, cardId]);
    } else {
      setSelectedCards(prev => prev.filter(id => id !== cardId));
    }
    return true;
  };

  const handleSubmit = async () => {
    if (selectedCards.length === 0) {
      alert('카드를 최소 1개 이상 선택해주세요.');
      return;
    }

    try {
      setIsLoading(true);
      const selectedCardObjects = cards.filter(card => selectedCards.includes(card.id));
      localStorage.setItem('selectedCards', JSON.stringify(selectedCardObjects));

      navigate('/cards/interpretation');
    } catch (err) {
      setError('카드 선택 처리 중 오류가 발생했습니다.');
      console.error('Error submitting cards:', err);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading && cards.length === 0) {
    return (
      <div className="card-recommendation-page">
        <div className="container">
          <div className="loading">카드를 추천하고 있습니다...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="card-recommendation-page">
      <div className="container">
        <h2>AAC 카드 추천</h2>
        <p className="subtitle">
          상황에 맞는 카드가 추천되었습니다. 원하는 카드를 1~4개 선택해주세요.
        </p>

        <div className="selection-info">
          <span>선택된 카드: {selectedCards.length}/4</span>
        </div>

        {error && <div className="error-message">{error}</div>}

        <CardGrid
          cards={cards}
          selectedCards={selectedCards}
          onCardSelect={handleCardSelect}
          maxSelection={4}
        />

        <div className="button-group">
          <button
            type="button"
            className="back-button"
            onClick={() => navigate('/context/input')}
            disabled={isLoading}
          >
            이전
          </button>
          <button
            type="button"
            className="submit-button"
            onClick={handleSubmit}
            disabled={isLoading || selectedCards.length === 0}
          >
            {isLoading ? '처리 중...' : '카드 해석하기'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CardRecommendationPage;
