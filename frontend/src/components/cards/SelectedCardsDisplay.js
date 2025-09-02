// frontend\src\components\cards\SelectedCardsDisplay.js
import React from 'react';

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

export default SelectedCardsDisplay;