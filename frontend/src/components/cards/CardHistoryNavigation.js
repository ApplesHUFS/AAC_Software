// src/components/cards/CardHistoryNavigation.js
import React, { useState, useEffect, useCallback } from 'react';
import { cardService } from '../../services/cardService';

// 이전 추천 결과들을 탐색하는 히스토리 네비게이션
const CardHistoryNavigation = ({ 
  contextId, 
  currentPage = 1, 
  totalPages = 1, 
  onPageChange, 
  disabled = false,
}) => {
  const [historyInfo, setHistoryInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // 히스토리 정보 로드
  const fetchHistoryInfo = useCallback(async () => {
    if (!contextId) {
      setHistoryInfo(null);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError('');

      const response = await cardService.getHistorySummary(contextId);
      
      if (response.success && response.data) {
        setHistoryInfo(response.data);
      } else {
        setHistoryInfo(null);
      }
    } catch (error) {
      console.error('히스토리 조회 실패:', error);
      setError(error.message || '히스토리 조회 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  }, [contextId]);

  useEffect(() => {
    fetchHistoryInfo();
  }, [fetchHistoryInfo]);

  // 페이지 변경 처리
  const handlePageNavigation = useCallback(async (pageNumber) => {
    if (pageNumber === currentPage || disabled || loading) return;
    
    if (pageNumber < 1 || (historyInfo && pageNumber > historyInfo.totalPages)) return;

    if (onPageChange) {
      onPageChange(pageNumber);
    }
  }, [currentPage, disabled, loading, historyInfo, onPageChange]);

  // 로딩 상태
  if (loading) {
    return (
      <div className="card-history-navigation loading communicator-navigation">
        <div className="navigation-loading">
          <span className="loading-icon">⏳</span>
          <span>이전 카드들 찾는 중...</span>
        </div>
      </div>
    );
  }

  // 에러 상태
  if (error) {
    return (
      <div className="card-history-navigation error communicator-navigation">
        <div className="navigation-error">
          <span className="error-icon">😅</span>
          <span>이전 카드를 불러올 수 없어요</span>
          <button onClick={fetchHistoryInfo} className="retry-btn secondary-button">
            다시 시도
          </button>
        </div>
      </div>
    );
  }

  // 히스토리가 없거나 페이지가 1개뿐인 경우
  if (!historyInfo || totalPages <= 1) {
    return (
      <div className="card-history-navigation single communicator-navigation">
        <div className="navigation-info">
          <span className="info-icon">🆕</span>
          <span>첫 번째 카드 추천이에요!</span>
        </div>
      </div>
    );
  }

  return (
    <div className="card-history-navigation communicator-navigation">
      <div className="navigation-header">
        <h4>
          <span className="nav-icon">📚</span>
          이전에 본 카드들
        </h4>
        <span className="page-indicator">
          {currentPage} / {totalPages} 묶음
        </span>
      </div>

      <div className="page-controls">
        <button 
          onClick={() => handlePageNavigation(currentPage - 1)}
          disabled={disabled || loading || currentPage <= 1}
          className="nav-button prev communicator-nav-btn"
        >
          ← 이전 카드
        </button>
        
        <div className="page-info">
          <span className="current-page">{currentPage}</span>
          <span className="separator">/</span>
          <span className="total-pages">{totalPages}</span>
        </div>
        
        <button 
          onClick={() => handlePageNavigation(currentPage + 1)}
          disabled={disabled || loading || currentPage >= totalPages}
          className="nav-button next communicator-nav-btn"
        >
          다른 카드 →
        </button>
      </div>

      {historyInfo.historySummary?.length > 0 && (
        <div className="page-list">
          <h5>
            <span className="list-icon">📝</span>
            카드 묶음 목록
          </h5>
          <div className="page-buttons">
            {historyInfo.historySummary.map((summary) => (
              <button
                key={summary.pageNumber}
                className={`page-button ${currentPage === summary.pageNumber ? 'active' : ''}`}
                onClick={() => handlePageNavigation(summary.pageNumber)}
                disabled={disabled || loading}
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
          <span className="help-icon">💡</span>
          이전에 추천받은 카드들을 다시 볼 수 있어요. 
          마음에 드는 카드가 있었다면 찾아보세요!
        </small>
      </div>
    </div>
  );
};

export default CardHistoryNavigation;