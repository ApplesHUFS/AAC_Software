import { useState } from 'react';
import '../../styles/CardItem.css';

const CardItem = ({ card, isSelected, onSelect, disabled }) => {
  const [imageError, setImageError] = useState(false);

  const handleClick = () => {
    if (disabled && !isSelected) return;
    onSelect(!isSelected);
  };

  const handleImageError = () => {
    setImageError(true);
  };

  return (
    <div
      className={`card-item ${isSelected ? 'selected' : ''} ${disabled ? 'disabled' : ''}`}
      onClick={handleClick}
    >
      <div className="card-image-container">
        {!imageError ? (
          <img
            src={card.image_path || `/images/cards/${card.id}.png`}
            alt={card.name || card.label}
            onError={handleImageError}
            className="card-image"
          />
        ) : (
          <div className="card-image-placeholder">
            <span>이미지 없음</span>
          </div>
        )}

        {isSelected && (
          <div className="selection-overlay">
            <div className="checkmark">✓</div>
          </div>
        )}
      </div>

      <div className="card-info">
        <h3 className="card-name">{card.name || card.label}</h3>
        {card.category && (
          <span className="card-category">{card.category}</span>
        )}
      </div>
    </div>
  );
};

export default CardItem;
