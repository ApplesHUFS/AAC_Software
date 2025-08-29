// CardHistoryNavigation.js
import React, { useState, useEffect, useCallback } from 'react';
import { cardService } from '../../services/cardService';

// 카드 히스토리 네비게이션 컴포넌트
// 흐름명세서: 이전 추천 결과들을 탐색할 수 있는 기능
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
        setError(response.error || '히스토리 정보를 불러올 수 없습니다.');
      }
    } catch (error) {
      console.error('히스토리 조회 실패:', error);
      setError(error.message || '히스토리 조회 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  }, [contextId]);

  // 컴포넌트 마운트 및 contextId 변경 시 히스토리 정보 로드
  useEffect(() => {
    fetchHistoryInfo();
  }, [fetchHistoryInfo]);

  // 페이지 변경 처리
  const handlePageNavigation = useCallback(async (pageNumber) => {
    if (pageNumber === currentPage || disabled || loading) return;
    
    if (pageNumber < 1 || (historyInfo && pageNumber > historyInfo.totalPages)) return;

    // 부모 컴포넌트의 페이지 변경 함수 호출
    if (onPageChange) {
      onPageChange(pageNumber);
    }
  }, [currentPage, disabled, loading, historyInfo, onPageChange]);

  // 로딩 상태
  if (loading) {
    return (
      <div className="card-history-navigation loading">
        <div className="navigation-loading">
          <span>히스토리 로딩 중...</span>
        </div>
      </div>
    );
  }

  // 에러 상태
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

  // 히스토리가 없거나 페이지가 1개뿐인 경우
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
          onClick={() => handlePageNavigation(currentPage - 1)}
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
          onClick={() => handlePageNavigation(currentPage + 1)}
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
                onClick={() => handlePageNavigation(summary.pageNumber)}
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

      {/* 네비게이션 도움말 */}
      <div className="navigation-help">
        <small>
          이전에 추천받은 카드들을 다시 볼 수 있습니다. 
          마음에 드는 카드가 있었다면 이전 추천에서 찾아보세요.
        </small>
      </div>
    </div>
  );
};

export default CardHistoryNavigation;