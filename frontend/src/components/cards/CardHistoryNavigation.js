// src/components/cards/CardHistoryNavigation.js
import React, { useState, useEffect } from 'react';
import { cardService } from '../../services/cardService';

const CardHistoryNavigation = ({ 
  contextId, 
  historyState, 
  onPageChange, 
  disabled = false,
}) => {
  const [historySummary, setHistorySummary] = useState([]);
  const [localLoading, setLocalLoading] = useState(false);
  const [localError, setLocalError] = useState('');

  const { currentPage, totalPages, isLoading } = historyState;

  // 히스토리 요약 정보 로드
  useEffect(() => {
    const loadHistorySummary = async () => {
      if (!contextId || totalPages <= 1) {
        setHistorySummary([]);
        return;
      }

      try {
        setLocalLoading(true);
        setLocalError('');
        
        const response = await cardService.getHistorySummary(contextId);
        
        if (response.success && response.data?.historySummary) {
          setHistorySummary(response.data.historySummary);
        } else {
          setHistorySummary([]);
        }
      } catch (error) {
        console.error('히스토리 요약 로드 실패:', error);
        setLocalError('히스토리 정보를 불러올 수 없습니다.');
        setHistorySummary([]);
      } finally {
        setLocalLoading(false);
      }
    };

    loadHistorySummary();
  }, [contextId, totalPages]);

  // 페이지 변경 핸들러
  const handlePageNavigation = (pageNumber) => {
    if (pageNumber === currentPage || disabled || isLoading || localLoading) return;
    
    if (pageNumber < 1 || pageNumber > totalPages) return;

    onPageChange(pageNumber);
  };

  // 로딩 상태
  if (localLoading || isLoading) {
    return (
      <div className="card-history-navigation loading communicator-navigation">
        <div className="navigation-loading">
          <img src="/images/logo_red.png" alt="로고" width="24" height="24" className="loading-icon" />
          <span>이전 카드들 찾는 중...</span>
        </div>
      </div>
    );
  }

  // 에러 상태
  if (localError) {
    return (
      <div className="card-history-navigation error communicator-navigation">
        <div className="navigation-error">
          <img src="/images/logo_red.png" alt="로고" width="24" height="24" className="error-icon" />
          <span>이전 카드를 불러올 수 없어요</span>
        </div>
      </div>
    );
  }

  // 페이지가 1개뿐인 경우
  if (totalPages <= 1) {
    return (
      <div className="card-history-navigation single communicator-navigation">
        <div className="navigation-info">
          <img src="/images/logo_red.png" alt="로고" width="24" height="24" className="info-icon" />
          <span>첫 번째 카드 추천이에요!</span>
        </div>
      </div>
    );
  }

  return (
    <div className="card-history-navigation communicator-navigation">
      <div className="navigation-header">
        <h4>
          <img src="/images/logo_red.png" alt="로고" width="20" height="20" className="nav-icon" />
          이전에 본 카드들
        </h4>
        <span className="page-indicator">
          {currentPage} / {totalPages} 묶음
        </span>
      </div>

      <div className="page-controls">
        <button 
          onClick={() => handlePageNavigation(currentPage - 1)}
          disabled={disabled || isLoading || currentPage <= 1}
          className="nav-button prev communicator-nav-btn"
        >
          이전 카드
        </button>
        
        <div className="page-info">
          <span className="current-page">{currentPage}</span>
          <span className="separator">/</span>
          <span className="total-pages">{totalPages}</span>
        </div>
        
        <button 
          onClick={() => handlePageNavigation(currentPage + 1)}
          disabled={disabled || isLoading || currentPage >= totalPages}
          className="nav-button next communicator-nav-btn"
        >
          다른 카드
        </button>
      </div>

      {/* 카드 묶음 목록 */}
      {historySummary.length > 0 && (
        <div className="page-list">
          <h5>
            <img src="/images/logo_red.png" alt="로고" width="16" height="16" className="list-icon" />
            카드 묶음 목록
          </h5>
          <div className="page-buttons">
            {historySummary.map((summary) => (
              <button
                key={summary.pageNumber}
                className={`page-button ${currentPage === summary.pageNumber ? 'active' : ''}`}
                onClick={() => handlePageNavigation(summary.pageNumber)}
                disabled={disabled || isLoading}
                title={`${summary.cardCount}개 카드 - ${summary.timestamp}`}
              >
                <span className="page-number">{summary.pageNumber}번째</span>
                <small className="card-count">({summary.cardCount}개)</small>
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="navigation-help">
        <small>
          <img src="/images/logo_red.png" alt="로고" width="12" height="12" className="help-icon" />
          이전에 추천받은 카드들을 다시 볼 수 있어요. 
          마음에 드는 카드가 있었다면 찾아보세요!
        </small>
      </div>
    </div>
  );
};

export default CardHistoryNavigation;