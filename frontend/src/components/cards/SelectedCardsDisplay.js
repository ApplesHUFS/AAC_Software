import React from 'react';

const SelectedCardsDisplay = ({ selectedCards, onRemoveCard }) => {
  if (selectedCards.length === 0) {
    return (
      <div className="selected-cards-display empty">
        <p>카드를 선택해주세요 (1-4개)</p>
      </div>
    );
  }

  return (
    <div className="selected-cards-display">
      <h3>선택된 카드 ({selectedCards.length}/4)</h3>
      <div className="selected-cards-list">
        {selectedCards.map((card) => (
          <div key={card.filename} className="selected-card-item">
            <img 
              src={`http://localhost:8000${card.imagePath}`}
              alt={card.name}
            />
            <span>{card.name}</span>
            <button 
              className="remove-card-btn"
              onClick={() => onRemoveCard(card)}
              title="카드 제거"
            >
              ×
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
