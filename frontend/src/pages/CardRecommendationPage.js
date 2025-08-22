import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { cardAPI } from '../services/api';
import CardGrid from '../components/cards/CardGrid';
import '../styles/CardRecommendationPage.css';

const CardRecommendationPage = () => {
  const [cards, setCards] = useState([]);
  const [selectedCardIds, setSelectedCardIds] = useState([]);
  const [selectedCardObjects, setSelectedCardObjects] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [historyInfo, setHistoryInfo] = useState({ currentPage: 1, totalPages: 1 });
  const [isRefreshing, setIsRefreshing] = useState(false);
  const navigate = useNavigate();
  const hasInitialized = useRef(false);

  useEffect(() => {
    // Strict Mode에서의 중복 실행 방지
    if (hasInitialized.current) {
      return;
    }
    hasInitialized.current = true;

    const userId = localStorage.getItem('userId');
    const contextId = localStorage.getItem('contextId');

    if (!userId || !contextId) {
      navigate('/user/create');
      return;
    }

    loadRecommendations();
  }, [navigate]); // navigate를 dependency array에 추가

  const loadRecommendations = async () => {
    try {
      setIsLoading(true);
      setError(''); // 에러 메시지 초기화
      const userId = localStorage.getItem('userId');
      const contextId = localStorage.getItem('contextId');

      if (!userId || !contextId) {
        setError('사용자 ID 또는 컨텍스트 ID를 찾을 수 없습니다.');
        return;
      }

      const response = await cardAPI.getRecommendations({
        userId: parseInt(userId),
        contextId: contextId
      });

      const cardsData = response.data.cards || [];
      setCards(cardsData);

      // 히스토리 정보 업데이트
      const pageInfo = response.data.page_info;
      if (pageInfo) {
        setHistoryInfo({
          currentPage: pageInfo.current_page,
          totalPages: pageInfo.total_pages
        });
      }

    } catch (err) {
      const errorMessage = err.response?.data?.error || '카드 추천을 불러오는 중 오류가 발생했습니다.';
      setError(errorMessage);
      console.error('Error loading recommendations:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefreshRecommendations = async () => {
    setIsRefreshing(true);
    await loadRecommendations();
    setIsRefreshing(false);
  };

  const loadHistoryPage = async (pageNumber) => {
    try {
      setIsLoading(true);
      setError(''); // 에러 메시지 초기화
      const contextId = localStorage.getItem('contextId');

      if (!contextId) {
        setError('컨텍스트 ID를 찾을 수 없습니다.');
        return;
      }

      const response = await cardAPI.getRecommendationHistoryPage(contextId, pageNumber);
      const cardsData = response.data.cards || [];

      setCards(cardsData);
      setHistoryInfo({
        currentPage: response.data.page_number,
        totalPages: response.data.total_pages
      });

    } catch (err) {
      const errorMessage = err.response?.data?.error || '히스토리 페이지를 불러오는 중 오류가 발생했습니다.';
      setError(errorMessage);
      console.error('Error loading history page:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCardSelect = (cardId, isSelected) => {
    if (isSelected) {
      if (selectedCardIds.length >= 4) {
        alert('최대 4개까지만 선택할 수 있습니다.');
        return false;
      }

      // 현재 카드 세트에서 해당 카드 찾기
      const selectedCard = cards.find(card => card.id === cardId);
      if (selectedCard) {
        setSelectedCardIds(prev => [...prev, cardId]);
        setSelectedCardObjects(prev => [...prev, selectedCard]);
      }
    } else {
      setSelectedCardIds(prev => prev.filter(id => id !== cardId));
      setSelectedCardObjects(prev => prev.filter(card => card.id !== cardId));
    }
    return true;
  };

  const handleSubmit = async () => {
    if (selectedCardIds.length === 0) {
      alert('카드를 최소 1개 이상 선택해주세요.');
      return;
    }

    try {
      setIsLoading(true);
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

        {/* 선택된 카드 상단 표시 영역 */}
        {selectedCardObjects.length > 0 && (
          <div className="selected-cards-area">
            <h3>선택한 카드 ({selectedCardObjects.length}/4)</h3>
            <div className="selected-cards-display">
              {selectedCardObjects.map(card => (
                <div key={card.id} className="selected-card-item">
                  <img
                    src={`http://localhost:8000/${card.image_path}`}
                    alt={card.name}
                    className="selected-card-image"
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'flex';
                    }}
                  />
                  <div className="card-placeholder" style={{display: 'none'}}>
                    <span>이미지 없음</span>
                  </div>
                  <span className="card-name">{card.name}</span>
                  <button
                    className="remove-card-btn"
                    onClick={() => handleCardSelect(card.id, false)}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 추천 제어 영역 */}
        <div className="recommendation-controls">
          <div className="page-info">
            <span>추천 세트: {historyInfo.currentPage}/{historyInfo.totalPages}</span>
          </div>
          <div className="control-buttons">
            <button
              className="refresh-btn"
              onClick={handleRefreshRecommendations}
              disabled={isRefreshing || isLoading}
            >
              {isRefreshing ? '새로운 카드 추천 중...' : '🔄 카드 다시 추천받기'}
            </button>
          </div>
        </div>

        {/* 히스토리 페이지네이션 */}
        {historyInfo.totalPages > 1 && (
          <div className="history-pagination">
            <span className="pagination-label">이전 추천 결과:</span>
            <div className="pagination-buttons">
              {Array.from({ length: historyInfo.totalPages }, (_, i) => i + 1).map(pageNum => (
                <button
                  key={pageNum}
                  className={`page-btn ${pageNum === historyInfo.currentPage ? 'active' : ''}`}
                  onClick={() => loadHistoryPage(pageNum)}
                  disabled={isLoading}
                >
                  {pageNum}
                </button>
              ))}
            </div>
          </div>
        )}

        {error && <div className="error-message">{error}</div>}

        <CardGrid
          cards={cards}
          selectedCards={selectedCardIds}
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
            disabled={isLoading || selectedCardIds.length === 0}
          >
            {isLoading ? '처리 중...' : '카드 해석하기'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CardRecommendationPage;
