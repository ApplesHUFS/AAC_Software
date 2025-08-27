import React, { useState, useEffect } from 'react';
import { cardService } from '../../services/cardService';

const CardHistoryNavigation = ({ contextId, onPageChange }) => {
  const [historyInfo, setHistoryInfo] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistoryInfo = async () => {
      try {
        const response = await cardService.getHistorySummary(contextId);
        if (response.success) {
          setHistoryInfo(response.data);
          setCurrentPage(response.data.latestPage);
        }
      } catch (error) {
        console.error('Failed to fetch history info:', error);
      } finally {
        setLoading(false);
      }
    };

    if (contextId) {
      fetchHistoryInfo();
    }
  }, [contextId]);

  const handlePageChange = async (pageNumber) => {
    if (pageNumber === currentPage) return;
    
    try {
      const response = await cardService.getHistoryPage(contextId, pageNumber);
      if (response.success) {
        setCurrentPage(pageNumber);
        onPageChange(response.data.cards, pageNumber);
      }
    } catch (error) {
      console.error('Failed to load page:', error);
    }
  };

  if (loading || !historyInfo) {
    return <div className="card-history-navigation">히스토리 로딩 중...</div>;
  }

  return (
    <div className="card-history-navigation">
      <h4>카드 추천 히스토리</h4>
      <div className="page-controls">
        <button 
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={currentPage <= 1}
        >
          이전 페이지
        </button>
        
        <span className="page-info">
          {currentPage} / {historyInfo.totalPages}
        </span>
        
        <button 
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={currentPage >= historyInfo.totalPages}
        >
          다음 페이지
        </button>
      </div>
      
      <div className="page-list">
        {historyInfo.historySummary.map(summary => (
          <button
            key={summary.pageNumber}
            className={`page-button ${currentPage === summary.pageNumber ? 'active' : ''}`}
            onClick={() => handlePageChange(summary.pageNumber)}
          >
            페이지 {summary.pageNumber}
            <small>({summary.cardCount}개 카드)</small>
          </button>
        ))}
      </div>
    </div>
  );
};

export { ContextForm, CardItem, CardGrid, SelectedCardsDisplay, CardHistoryNavigation };