import React from 'react';

const CardItem = ({ card, isSelected, onSelect, disabled = false }) => {
  const handleClick = () => {
    if (!disabled) {
      onSelect(card);
    }
  };

  return (
    <div 
      className={`card-item ${isSelected ? 'selected' : ''} ${disabled ? 'disabled' : ''}`}
      onClick={handleClick}
    >
      <div className="card-image-container">
        <img 
          src={`http://localhost:8000${card.imagePath}`}
          alt={card.name}
          loading="lazy"
        />
        {isSelected && <div className="selection-indicator">✓</div>}
      </div>
      <div className="card-name">{card.name}</div>
    </div>
  );
};
