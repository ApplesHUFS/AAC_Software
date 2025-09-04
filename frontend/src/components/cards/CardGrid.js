// src/components/cards/CardGrid.js
import React, { useState, useCallback } from 'react';

// 카드 그리드 컴포넌트 (소통이가 카드 선택하는 메인 영역)
const CardGrid = ({ cards, selectedCards, onCardSelect, maxSelection = 4, disabled = false }) => {
  const isCardSelected = useCallback((card) => {
    return selectedCards.some(selected => selected.filename === card.filename);
  }, [selectedCards]);

  const handleCardClick = useCallback((card) => {
    if (disabled) return;
    onCardSelect(card);
  }, [disabled, onCardSelect]);

  if (!cards?.length) {
    return (
      <div className="card-grid empty communicator-message">
        <div className="no-cards-message">
          <span className="message-icon">😊</span>
          <h3>아직 카드가 없어요</h3>
          <p>도움이가 카드를 준비해드릴게요!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card-grid communicator-grid">
      {cards.map((card) => (
        <CardItem
          key={card.filename || card.id}
          card={card}
          isSelected={isCardSelected(card)}
          onSelect={handleCardClick}
          disabled={disabled || (!isCardSelected(card) && selectedCards.length >= maxSelection)}
        />
      ))}
      
      <div className="grid-info communicator-info">
        <p>
          <span className="info-icon">🎨</span>
          {cards.length}개의 카드 중 <strong>{selectedCards.length}개</strong> 선택됨 
          (최대 {maxSelection}개까지)
        </p>
      </div>
    </div>
  );
};

// 개별 카드 아이템 컴포넌트
const CardItem = ({ card, isSelected, onSelect, disabled = false }) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);

  const handleClick = useCallback(() => {
    if (!disabled && !imageError) {
      onSelect(card);
    }
  }, [disabled, imageError, onSelect, card]);

  const handleKeyPress = useCallback((e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  }, [handleClick]);

  const handleImageLoad = useCallback(() => {
    setImageLoaded(true);
    setImageError(false);
  }, []);

  const handleImageError = useCallback(() => {
    setImageError(true);
    setImageLoaded(false);
  }, []);

  return (
    <div 
      className={`card-item communicator-card ${isSelected ? 'selected' : ''} ${disabled ? 'disabled' : ''} ${imageError ? 'error' : ''}`}
      onClick={handleClick}
      onKeyPress={handleKeyPress}
      tabIndex={disabled ? -1 : 0}
      role="button"
      aria-label={`${card.name} 카드 ${isSelected ? '선택됨' : '선택하기'}`}
    >
      <div className="card-image-container">
        {!imageLoaded && !imageError && (
          <div className="image-loading communicator-loading">
            <div className="loading-spinner small"></div>
            <small>이미지 로딩 중...</small>
          </div>
        )}
        
        {imageError ? (
          <div className="image-error communicator-error">
            <span className="error-icon">📷</span>
            <span>이미지를 불러올 수 없어요</span>
            <small>{card.name}</small>
          </div>
        ) : (
          <img 
            src={`http://localhost:8000${card.imagePath}`}
            alt={card.name}
            loading="lazy"
            onLoad={handleImageLoad}
            onError={handleImageError}
            style={{ visibility: imageLoaded ? 'visible' : 'hidden' }}
          />
        )}
        
        {/* 선택 표시 */}
        {isSelected && !imageError && (
          <div className="selection-indicator communicator-selected">
            <span className="checkmark">✓</span>
          </div>
        )}
        
        {/* 선택 불가 상태 표시 */}
        {disabled && !isSelected && (
          <div className="disabled-overlay">
            <span>선택 완료</span>
          </div>
        )}
      </div>
      
      <div className="card-name">{card.name}</div>
    </div>
  );
};

// 선택된 카드 표시 컴포넌트 (소통이 확인용)
const SelectedCardsDisplay = ({ selectedCards, onRemoveCard, maxCards = 4 }) => {
  if (selectedCards.length === 0) {
    return (
      <div className="selected-cards-display empty communicator-sidebar">
        <h3>
          <span className="title-icon">🎯</span>
          선택한 카드
        </h3>
        <div className="empty-state">
          <div className="empty-icon">📝</div>
          <p>원하는 카드를 선택해보세요</p>
          <small>1~{maxCards}개까지 선택할 수 있어요</small>
        </div>
      </div>
    );
  }

  return (
    <div className="selected-cards-display communicator-sidebar">
      <h3>
        <span className="title-icon">✨</span>
        선택한 카드 ({selectedCards.length}/{maxCards})
      </h3>
      
      <div className="selected-cards-list">
        {selectedCards.map((card, index) => (
          <div key={card.filename} className="selected-card-item communicator-selected-item">
            <div className="card-preview">
              <img 
                src={`http://localhost:8000${card.imagePath}`}
                alt={card.name}
                loading="lazy"
              />
              <div className="card-order communicator-order">{index + 1}</div>
            </div>
            
            <div className="card-details">
              <span className="card-name">{card.name}</span>
              <small className="card-position">{index + 1}번째 카드</small>
            </div>
            
            <button 
              className="remove-card-btn communicator-remove"
              onClick={() => onRemoveCard(card)}
              title={`${card.name} 카드 제거`}
            >
              ×
            </button>
          </div>
        ))}
      </div>
      
      <div className="selection-summary communicator-summary">
        <p>
          {maxCards - selectedCards.length > 0 ? (
            <>
              <span className="summary-icon">👍</span>
              <strong>{maxCards - selectedCards.length}개</strong> 더 선택할 수 있어요!
            </>
          ) : (
            <>
              <span className="summary-icon">🎉</span>
              모든 카드를 선택했어요!
            </>
          )}
        </p>
      </div>

      <div className="selection-guide communicator-guide">
        <h5>
          <span className="guide-icon">💡</span>
          카드 선택 안내
        </h5>
        <ul>
          <li>최소 1개, 최대 {maxCards}개까지 고를 수 있어요</li>
          <li>카드 순서가 의미 전달에 중요해요</li>
          <li>× 버튼으로 카드를 뺄 수 있어요</li>
        </ul>
      </div>
    </div>
  );
};

export default CardGrid;
export { CardItem, SelectedCardsDisplay };