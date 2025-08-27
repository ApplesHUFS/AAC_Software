import React from 'react';
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
