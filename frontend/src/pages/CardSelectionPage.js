import React, { useState, useEffect } from 'react';
import { cardService } from '../services/cardService';
import { CardGrid, SelectedCardsDisplay, CardHistoryNavigation } from '../components/cards/CardGrid';

const CardSelectionPage = ({ user, contextData, onCardSelectionComplete }) => {
  const [cards, setCards] = useState([]);
  const [selectedCards, setSelectedCards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    loadInitialCards();
  }, []);

  const loadInitialCards = async () => {
    try {
      const response = await cardService.getRecommendations(user.userId, contextData.contextId);
      if (response.success) {
        setCards(response.data.cards);
        setCurrentPage(response.data.pagination.currentPage);
      }
    } catch (error) {
      setError(error.message || '카드 로딩에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (newCards, pageNumber) => {
    setCards(newCards.map((filename, index) => ({
      id: filename.split('_')[0] || filename.replace('.png', ''),
      name: filename.replace('.png', '').replace('_', ' '),
      filename,
      imagePath: `/api/images/${filename}`,
      index,
      selected: false
    })));
    setCurrentPage(pageNumber);
  };

  const handleRerollCards = async () => {
    setLoading(true);
    try {
      const response = await cardService.getRecommendations(user.userId, contextData.contextId);
      if (response.success) {
        setCards(response.data.cards);
      }
    } catch (error) {
      setError(error.message || '카드 재추천에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleCardSelection = (newSelectedCards) => {
    setSelectedCards(newSelectedCards);
  };

  const handleRemoveSelectedCard = (cardToRemove) => {
    setSelectedCards(selectedCards.filter(card => card.filename !== cardToRemove.filename));
  };

  const handleProceedToInterpretation = async () => {
    if (selectedCards.length === 0) {
      setError('최소 1개의 카드를 선택해주세요.');
      return;
    }

    try {
      // 카드 선택 검증
      const validationResponse = await cardService.validateSelection(
        selectedCards.map(card => card.filename),
        cards.map(card => card.filename)
      );

      if (validationResponse.success && validationResponse.data.valid) {
        onCardSelectionComplete(selectedCards);
      } else {
        setError('카드 선택이 유효하지 않습니다.');
      }
    } catch (error) {
      setError(error.message || '카드 검증에 실패했습니다.');
    }
  };

  if (loading) {
    return <div className="loading">카드를 불러오는 중...</div>;
  }

  return (
    <div className="card-selection-page">
      <header className="selection-header">
        <h2>AAC 카드 선택</h2>
        <div className="context-info">
          <span><strong>장소:</strong> {contextData.place}</span>
          <span><strong>대화상대:</strong> {contextData.interactionPartner}</span>
          {contextData.currentActivity && (
            <span><strong>활동:</strong> {contextData.currentActivity}</span>
          )}
        </div>
      </header>

      <div className="selection-content">
        <div className="selection-sidebar">
          <SelectedCardsDisplay 
            selectedCards={selectedCards}
            onRemoveCard={handleRemoveSelectedCard}
          />
          
          <div className="selection-actions">
            <button 
              className="secondary-button"
              onClick={handleRerollCards}
              disabled={loading}
            >
              다른 카드 추천받기
            </button>
            
            <button 
              className="primary-button"
              onClick={handleProceedToInterpretation}
              disabled={selectedCards.length === 0}
            >
              해석하기 ({selectedCards.length}개 선택됨)
            </button>
          </div>

          {error && <div className="error-message">{error}</div>}
        </div>

        <div className="selection-main">
          <CardHistoryNavigation 
            contextId={contextData.contextId}
            onPageChange={handlePageChange}
          />
          
          <CardGrid 
            cards={cards}
            selectedCards={selectedCards}
            onCardSelect={handleCardSelection}
            maxSelection={4}
          />
        </div>
      </div>
    </div>
  );
};

export default CardSelectionPage;
