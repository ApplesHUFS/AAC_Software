import React, { useState, useEffect, useCallback } from 'react';
import { cardService } from '../../services/cardService';

/**
 * 카드 그리드 컴포넌트
 * 추천된 카드들을 격자 형태로 표시하고 선택 기능 제공
 */
const CardGrid = ({ cards, selectedCards, onCardSelect, maxSelection = 4, disabled = false }) => {
  /**
   * 카드가 선택되었는지 확인
   */
  const isCardSelected = useCallback((card) => {
    return selectedCards.some(selected => selected.filename === card.filename);
  }, [selectedCards]);

  /**
   * 카드 선택/해제 처리
   */
  const handleCardSelect = useCallback((card) => {
    if (disabled) return;

    const isSelected = isCardSelected(card);
    
    if (isSelected) {
      // 카드 선택 해제
      const newSelection = selectedCards.filter(selected => selected.filename !== card.filename);
      onCardSelect(newSelection);
    } else if (selectedCards.length < maxSelection) {
      // 카드 선택 추가
      const newSelection = [...selectedCards, card];
      onCardSelect(newSelection);
    }
  }, [disabled, isCardSelected, selectedCards, maxSelection, onCardSelect]);

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
          onSelect={handleCardSelect}
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

/**
 * 개별 카드 아이템 컴포넌트
 * 카드 이미지, 이름, 선택 상태 표시
 */
const CardItem = ({ card, isSelected, onSelect, disabled = false }) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);

  /**
   * 카드 클릭 처리
   */
  const handleClick = useCallback(() => {
    if (!disabled && !imageError) {
      onSelect(card);
    }
  }, [disabled, imageError, onSelect, card]);

  /**
   * 키보드 접근성 처리
   */
  const handleKeyPress = useCallback((e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  }, [handleClick]);

  /**
   * 이미지 로드 완료 처리
   */
  const handleImageLoad = useCallback(() => {
    setImageLoaded(true);
    setImageError(false);
  }, []);

  /**
   * 이미지 로드 에러 처리
   */
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

/**
 * 선택된 카드 표시 컴포넌트
 * 사이드바에서 선택된 카드들을 관리
 */
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
    </div>
  );
};

/**
 * 카드 히스토리 내비게이션 컴포넌트
 * 이전 추천 결과들을 탐색할 수 있는 기능
 */
const CardHistoryNavigation = ({ 
  contextId, 
  currentPage = 1, 
  totalPages = 1, 
  onPageChange, 
  disabled = false 
}) => {
  const [historyInfo, setHistoryInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  /**
   * 히스토리 정보 로드
   */
  const fetchHistoryInfo = useCallback(async () => {
    if (!contextId) return;

    try {
      setLoading(true);
      setError('');

      const response = await cardService.getHistorySummary(contextId);
      
      if (response.success && response.data) {
        setHistoryInfo(response.data);
      } else {
        setError(response.error || '히스토리 정보를 불러올 수 없습니다.');
      }
    } catch (error) {
      console.error('히스토리 조회 실패:', error);
      setError(error.message || '히스토리 조회 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  }, [contextId]);

  /**
   * 컴포넌트 마운트 시 히스토리 정보 로드
   */
  useEffect(() => {
    fetchHistoryInfo();
  }, [fetchHistoryInfo]);

  /**
   * 페이지 변경 처리
   */
  const handlePageChange = useCallback(async (pageNumber) => {
    if (pageNumber === currentPage || disabled || loading) return;
    
    if (pageNumber < 1 || pageNumber > totalPages) return;

    try {
      const response = await cardService.getHistoryPage(contextId, pageNumber);
      
      if (response.success && response.data) {
        onPageChange(response.data.cards, pageNumber);
      } else {
        console.error('페이지 로드 실패:', response.error);
      }
    } catch (error) {
      console.error('히스토리 페이지 로드 실패:', error);
    }
  }, [contextId, currentPage, totalPages, disabled, loading, onPageChange]);

  if (loading) {
    return (
      <div className="card-history-navigation loading">
        <div className="navigation-loading">
          <span>히스토리 로딩 중...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card-history-navigation error">
        <div className="navigation-error">
          <span>히스토리를 불러올 수 없습니다</span>
          <button onClick={fetchHistoryInfo} className="retry-btn">
            다시 시도
          </button>
        </div>
      </div>
    );
  }

  if (!historyInfo || historyInfo.totalPages <= 1) {
    return (
      <div className="card-history-navigation single">
        <div className="navigation-info">
          <span>첫 번째 카드 추천</span>
        </div>
      </div>
    );
  }

  return (
    <div className="card-history-navigation">
      <div className="navigation-header">
        <h4>카드 추천 히스토리</h4>
        <span className="page-indicator">
          {currentPage} / {historyInfo.totalPages} 페이지
        </span>
      </div>

      {/* 페이지 컨트롤 */}
      <div className="page-controls">
        <button 
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={disabled || loading || currentPage <= 1}
          className="nav-button prev"
          title="이전 카드셋"
        >
          ← 이전
        </button>
        
        <div className="page-info">
          <span className="current-page">{currentPage}</span>
          <span className="separator">/</span>
          <span className="total-pages">{historyInfo.totalPages}</span>
        </div>
        
        <button 
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={disabled || loading || currentPage >= historyInfo.totalPages}
          className="nav-button next"
          title="다음 카드셋"
        >
          다음 →
        </button>
      </div>

      {/* 히스토리 페이지 목록 */}
      {historyInfo.historySummary && historyInfo.historySummary.length > 0 && (
        <div className="page-list">
          <h5>추천 기록</h5>
          <div className="page-buttons">
            {historyInfo.historySummary.map((summary) => (
              <button
                key={summary.pageNumber}
                className={`page-button ${currentPage === summary.pageNumber ? 'active' : ''}`}
                onClick={() => handlePageChange(summary.pageNumber)}
                disabled={disabled || loading}
                title={`${summary.cardCount}개 카드 - ${summary.timestamp}`}
              >
                <span className="page-number">{summary.pageNumber}</span>
                <small className="card-count">({summary.cardCount}개)</small>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 내비게이션 도움말 */}
      <div className="navigation-help">
        <small>
          이전에 추천받은 카드들을 다시 볼 수 있습니다. 
          마음에 드는 카드가 있었다면 이전 추천에서 찾아보세요.
        </small>
      </div>
    </div>
  );
};

export default CardGrid;
export { CardGrid, CardItem, SelectedCardsDisplay, CardHistoryNavigation };