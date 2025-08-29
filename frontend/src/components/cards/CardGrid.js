// CardGrid.js
import React, { useState, useCallback } from 'react';

// 카드 그리드 컴포넌트
// 추천된 카드들을 격자 형태로 표시하고 선택 기능 제공
const CardGrid = ({ cards, selectedCards, onCardSelect, maxSelection = 4, disabled = false }) => {
  // 카드가 선택되었는지 확인
  const isCardSelected = useCallback((card) => {
    return selectedCards.some(selected => selected.filename === card.filename);
  }, [selectedCards]);

  // 카드 선택/해제 처리
  const handleCardClick = useCallback((card) => {
    if (disabled) return;

    // 부모 컴포넌트에 카드 객체를 전달 (선택 상태는 부모에서 관리)
    onCardSelect(card);
  }, [disabled, onCardSelect]);

  if (!cards || cards.length === 0) {
    return (
      <div className="card-grid empty">
        <div className="no-cards-message">
          <h3>표시할 카드가 없습니다</h3>
          <p>카드를 다시 추천받아 주세요.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card-grid">
      {cards.map((card) => (
        <CardItem
          key={card.filename || card.id}
          card={card}
          isSelected={isCardSelected(card)}
          onSelect={handleCardClick}
          disabled={disabled || (!isCardSelected(card) && selectedCards.length >= maxSelection)}
        />
      ))}
      
      {/* 그리드 정보 */}
      <div className="grid-info">
        <p>
          {cards.length}개의 카드 중 {selectedCards.length}개 선택됨 
          (최대 {maxSelection}개)
        </p>
      </div>
    </div>
  );
};

// 개별 카드 아이템 컴포넌트
// 흐름명세서: 선택된 카드들은 카드 위에 체크 표시가 뜸
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
            style={{ visibility: imageLoaded ? 'visible' : 'hidden' }}
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

// 선택된 카드 표시 컴포넌트
// 흐름명세서: 선택된 카드들은 상위의 특수 공간에서도 보임, 카드 페이지가 리롤되어도 이미 선택된 카드들이 바뀌지 않음
const SelectedCardsDisplay = ({ selectedCards, onRemoveCard, maxCards = 4 }) => {
  if (selectedCards.length === 0) {
    return (
      <div className="selected-cards-display empty">
        <h3>선택된 카드</h3>
        <div className="empty-state">
          <p>카드를 선택해주세요</p>
          <small>(1-{maxCards}개 선택 가능)</small>
        </div>
      </div>
    );
  }

  return (
    <div className="selected-cards-display">
      <h3>
        선택된 카드 ({selectedCards.length}/{maxCards})
      </h3>
      
      <div className="selected-cards-list">
        {selectedCards.map((card, index) => (
          <div key={card.filename} className="selected-card-item">
            <div className="card-preview">
              <img 
                src={`http://localhost:8000${card.imagePath}`}
                alt={card.name}
                loading="lazy"
              />
              <div className="card-order">{index + 1}</div>
            </div>
            
            <div className="card-details">
              <span className="card-name">{card.name}</span>
            </div>
            
            <button 
              className="remove-card-btn"
              onClick={() => onRemoveCard(card)}
              title={`${card.name} 카드 제거`}
              aria-label={`${card.name} 카드 제거`}
            >
              ×
            </button>
          </div>
        ))}
      </div>
      
      <div className="selection-summary">
        <p>
          {maxCards - selectedCards.length > 0 
            ? `${maxCards - selectedCards.length}개 더 선택할 수 있습니다` 
            : '최대 선택 수에 도달했습니다'
          }
        </p>
      </div>

      {/* 선택 가이드 */}
      <div className="selection-guide">
        <h5>선택 안내</h5>
        <ul>
          <li>최소 1개, 최대 {maxCards}개까지 선택 가능</li>
          <li>카드 순서는 의미 전달에 영향을 줄 수 있습니다</li>
          <li>× 버튼으로 개별 카드를 제거할 수 있습니다</li>
        </ul>
      </div>
    </div>
  );
};

export default CardGrid;
export { CardGrid, CardItem, SelectedCardsDisplay };