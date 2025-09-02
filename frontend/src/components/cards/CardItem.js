// frontend\src\components\cards\CardItem.js
import React, { useState, useCallback } from 'react';

// 개별 카드 아이템 컴포넌트
// 흐름명세서: 선택된 카드들은 카드 위에 체크 표시가 뜨며, 상위의 특수 공간에서도 보임
const CardItem = ({ card, isSelected, onSelect, disabled = false }) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);

  // 카드 클릭 처리
  const handleClick = useCallback(() => {
    if (!disabled && !imageError) {
      onSelect(card);
    }
  }, [disabled, imageError, onSelect, card]);

  // 키보드 접근성 처리
  const handleKeyPress = useCallback((e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  }, [handleClick]);

  // 이미지 로드 완료 처리
  const handleImageLoad = useCallback(() => {
    setImageLoaded(true);
    setImageError(false);
  }, []);

  // 이미지 로드 에러 처리
  const handleImageError = useCallback(() => {
    setImageError(true);
    setImageLoaded(false);
  }, []);

  return (
    <div 
      className={`card-item ${isSelected ? 'selected' : ''} ${disabled ? 'disabled' : ''} ${imageError ? 'error' : ''}`}
      onClick={handleClick}
      onKeyPress={handleKeyPress}
      tabIndex={disabled ? -1 : 0}
      role="button"
      aria-label={`${card.name} 카드 ${isSelected ? '선택됨' : '선택하기'}`}
      aria-pressed={isSelected}
    >
      <div className="card-image-container">
        {!imageLoaded && !imageError && (
          <div className="image-loading">
            <div className="loading-spinner small"></div>
          </div>
        )}
        
        {imageError ? (
          <div className="image-error">
            <span>이미지를 불러올 수 없습니다</span>
            <small>{card.name}</small>
          </div>
        ) : (
          <img 
            src={`http://localhost:8000${card.imagePath}`}
            alt={card.name}
            loading="lazy"
            onLoad={handleImageLoad}
            onError={handleImageError}
            style={{ display: imageLoaded ? 'block' : 'none' }}
          />
        )}
        
        {/* 흐름명세서: 선택된 카드들은 카드 위에 체크 표시가 뜸 */}
        {isSelected && !imageError && (
          <div className="selection-indicator">
            <span className="checkmark">✓</span>
          </div>
        )}
        
        {disabled && !isSelected && (
          <div className="disabled-overlay">
            <span>최대 선택 수 초과</span>
          </div>
        )}
      </div>
      
      <div className="card-name">{card.name}</div>
    </div>
  );
};

export default CardItem;