import React, { useState, useEffect, useCallback } from 'react';
import CardItem from './CardItem';

const CardGrid = ({ cards, selectedCards, onCardSelect, maxSelection = 4 }) => {
  const isCardSelected = (card) => {
    return selectedCards.some(selected => selected.filename === card.filename);
  };

  const handleCardSelect = (card) => {
    const isSelected = isCardSelected(card);
    
    if (isSelected) {
      // 카드 선택 해제
      onCardSelect(selectedCards.filter(selected => selected.filename !== card.filename));
    } else if (selectedCards.length < maxSelection) {
      // 카드 선택 추가
      onCardSelect([...selectedCards, card]);
    }
  };

  return (
    <div className="card-grid">
      {cards.map((card) => (
        <CardItem
          key={card.filename}
          card={card}
          isSelected={isCardSelected(card)}
          onSelect={handleCardSelect}
          disabled={!isCardSelected(card) && selectedCards.length >= maxSelection}
        />
      ))}
    </div>
  );
};

const SelectedCardsDisplay = ({ selectedCards, onRemoveCard }) => {
  return (
    <div className="selected-cards-display">
      <h3>선택된 카드 ({selectedCards.length}/4)</h3>
      <div className="selected-cards-list">
        {selectedCards.map((card) => (
          <div key={card.filename} className="selected-card-item">
            <img src={`http://localhost:8000${card.imagePath}`} alt={card.name} />
            <span>{card.name}</span>
            <button onClick={() => onRemoveCard(card)}>×</button>
          </div>
        ))}
      </div>
    </div>
  );
};

const CardHistoryNavigation = ({ contextId, onPageChange }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(false);

  const loadHistorySummary = useCallback(async () => {
    try {
      const response = await fetch(`/api/cards/history/${contextId}`);
      const result = await response.json();
      if (result.success) {
        setTotalPages(result.data.totalPages);
        setCurrentPage(result.data.latestPage);
      }
    } catch (error) {
      console.error('히스토리 조회 실패:', error);
    }
  }, [contextId]);

  useEffect(() => {
    loadHistorySummary();
  }, [contextId, loadHistorySummary]);

  const loadHistoryPage = async (pageNumber) => {
    if (loading || pageNumber < 1 || pageNumber > totalPages) return;
    
    setLoading(true);
    try {
      const response = await fetch(`/api/cards/history/${contextId}/page/${pageNumber}`);
      const result = await response.json();
      if (result.success) {
        setCurrentPage(pageNumber);
        onPageChange(result.data.cards.map(card => card.filename), pageNumber);
      }
    } catch (error) {
      console.error('히스토리 페이지 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card-history-navigation">
      <button 
        onClick={() => loadHistoryPage(currentPage - 1)} 
        disabled={loading || currentPage <= 1}
        className="nav-button prev"
      >
        ← 이전 카드셋
      </button>
      <span className="page-info">
        {currentPage} / {totalPages}
      </span>
      <button 
        onClick={() => loadHistoryPage(currentPage + 1)} 
        disabled={loading || currentPage >= totalPages}
        className="nav-button next"
      >
        다음 카드셋 →
      </button>
    </div>
  );
};

export default CardGrid;
export { CardGrid, SelectedCardsDisplay, CardHistoryNavigation };
