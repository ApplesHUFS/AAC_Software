// CardSelectionPage.js - 카드 선택 페이지 컴포넌트
import React, { useState, useEffect, useCallback } from 'react';
import { cardService } from '../services/cardService';
import { CardGrid, SelectedCardsDisplay } from '../components/cards/CardGrid';
import CardHistoryNavigation from '../components/cards/CardHistoryNavigation';

// 흐름명세서: 개인화된 카드 추천(70% 관련 + 30% 랜덤), 선택, 히스토리 관리
const CardSelectionPage = ({ user, contextData, onCardSelectionComplete }) => {
  // 카드 관련 상태
  const [cards, setCards] = useState([]);
  const [selectedCards, setSelectedCards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // 페이지 히스토리 관리 상태
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  
  // UI 상태
  const [isRerolling] = useState(false);

  // 초기 카드 추천 로드
  const loadInitialCards = useCallback(async () => {
    if (!user?.userId || !contextData?.contextId) {
      setError('사용자 정보 또는 컨텍스트 정보가 없습니다.');
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError('');

      const response = await cardService.getRecommendations(user.userId, contextData.contextId);
      
      if (response.success && response.data) {
        const normalizedCards = cardService.normalizeCardData(response.data.cards || []);
        setCards(normalizedCards);
        
        // 히스토리 정보 업데이트
        const pagination = response.data.pagination || {};
        setCurrentPage(pagination.currentPage || 1);
        setTotalPages(pagination.totalPages || 1);
      } else {
        setError(response.error || '카드 추천을 받을 수 없습니다.');
      }
    } catch (error) {
      console.error('카드 로딩 에러:', error);
      setError(error.message || '카드 로딩 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  }, [user?.userId, contextData?.contextId]);

  // 컴포넌트 마운트 시 초기 카드 로드
  useEffect(() => {
    loadInitialCards();
  }, [loadInitialCards]);

  // 히스토리 페이지 변경 처리
  const handlePageChange = useCallback(async (pageNumber) => {
    if (!contextData?.contextId || pageNumber === currentPage || loading) return;
    
    try {
      setLoading(true);
      setError('');

      const response = await cardService.getHistoryPage(contextData.contextId, pageNumber);
      
      if (response.success && response.data) {
        const normalizedCards = cardService.normalizeCardData(response.data.cards || []);
        setCards(normalizedCards);
        setCurrentPage(pageNumber);
      } else {
        setError(response.error || '히스토리 페이지를 불러올 수 없습니다.');
      }
    } catch (error) {
      console.error('히스토리 페이지 로드 에러:', error);
      setError(error.message || '히스토리 페이지 로딩 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  }, [contextData?.contextId, currentPage, loading]);

  // 카드 재추천 (리롤) 처리
  const handleRerollCards = useCallback(async () => {
    if (isRerolling || !user?.userId || !contextData?.contextId) return;

    setIsRerolling(true);
    setError('');

    try {
      const response = await cardService.getRecommendations(user.userId, contextData.contextId);
      
      if (response.success && response.data) {
        const normalizedCards = cardService.normalizeCardData(response.data.cards || []);
        setCards(normalizedCards);
        
        // 리롤 시 페이지 정보 업데이트
        const pagination = response.data.pagination || {};
        const newCurrentPage = pagination.currentPage || 1;
        const newTotalPages = pagination.totalPages || 1;
        
        setCurrentPage(newCurrentPage);
        setTotalPages(newTotalPages);

        // 새로 추가
        setHistoryRefreshTrigger(prev => prev +1);
        
        // 히스토리가 업데이트되었음을 표시
        setHistoryLoaded(false);
        setTimeout(() => setHistoryLoaded(true), 100);
      } else {
        setError(response.error || '카드 재추천에 실패했습니다.');
      }
    } catch (error) {
      console.error('카드 재추천 에러:', error);
      setError(error.message || '카드 재추천 중 오류가 발생했습니다.');
    } finally {
      setIsRerolling(false);
    }
  }, [isRerolling, user?.userId, contextData?.contextId]);

  // 카드 선택/해제 처리
  const handleCardSelection = useCallback((card) => {
    if (loading) return;

    const isSelected = selectedCards.some(selected => selected.filename === card.filename);
    
    if (isSelected) {
      // 카드 선택 해제
      setSelectedCards(prev => prev.filter(selected => selected.filename !== card.filename));
    } else if (selectedCards.length < 4) {
      // 카드 선택 추가
      setSelectedCards(prev => [...prev, card]);
    }
    
    // 에러 메시지 클리어
    if (error) {
      setError('');
    }
  }, [selectedCards, loading, error]);

  // 선택된 카드 개별 제거 처리
  const handleRemoveSelectedCard = useCallback((cardToRemove) => {
    setSelectedCards(prev => prev.filter(card => card.filename !== cardToRemove.filename));
  }, []);

  // 카드 선택 완료 및 해석 단계로 진행
  const handleProceedToInterpretation = useCallback(async () => {
    // 선택된 카드 검증
    if (selectedCards.length === 0) {
      setError('최소 1개의 카드를 선택해주세요.');
      return;
    }

    if (selectedCards.length > 4) {
      setError('최대 4개까지만 선택할 수 있습니다.');
      return;
    }

    try {
      setLoading(true);
      setError('');

      // 백엔드에서 카드 선택 유효성 검증
      const availableOptions = cards; // 현재 표시된 모든 카드
      const validationResponse = await cardService.validateSelection(selectedCards, availableOptions);

      if (validationResponse.success && validationResponse.data?.valid) {
        // 선택 완료 - 해석 단계로 이동
        onCardSelectionComplete(selectedCards);
      } else {
        setError('선택한 카드가 유효하지 않습니다. 다시 선택해주세요.');
      }
    } catch (error) {
      console.error('카드 검증 에러:', error);
      setError(error.message || '카드 검증 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  }, [selectedCards, cards, onCardSelectionComplete]);

  // 로딩 상태 렌더링
  if (loading && cards.length === 0) {
    return (
      <div className="card-selection-page loading">
        <div className="loading-content">
          <h2>카드 추천 중...</h2>
          <p>당신의 관심사와 현재 상황을 분석하여 최적의 카드를 준비하고 있습니다.</p>
          <div className="loading-spinner"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="card-selection-page">
      {/* 페이지 헤더 */}
      <header className="selection-header">
        <div className="header-content">
          <h2>AAC 카드 선택</h2>
          <div className="context-info">
            <div className="context-item">
              <span className="context-label">장소:</span>
              <span className="context-value">{contextData.place}</span>
            </div>
            <div className="context-item">
              <span className="context-label">대화상대:</span>
              <span className="context-value">{contextData.interactionPartner}</span>
            </div>
            {contextData.currentActivity && (
              <div className="context-item">
                <span className="context-label">활동:</span>
                <span className="context-value">{contextData.currentActivity}</span>
              </div>
            )}
            {contextData.time && (
              <div className="context-item">
                <span className="context-label">시간:</span>
                <span className="context-value">{contextData.time}</span>
              </div>
            )}
          </div>
        </div>
      </header>

      <div className="selection-content">
        {/* 사이드바 - 선택된 카드 및 액션 */}
        <div className="selection-sidebar">
          <SelectedCardsDisplay 
            selectedCards={selectedCards}
            onRemoveCard={handleRemoveSelectedCard}
            maxCards={4}
          />
          
          <div className="selection-actions">
            <button 
              className="secondary-button"
              onClick={handleRerollCards}
              disabled={loading || isRerolling}
              title="다른 카드 조합을 추천받습니다"
            >
              {isRerolling ? '추천 중...' : '다른 카드 추천받기'}
            </button>
            
            <button 
              className="primary-button"
              onClick={handleProceedToInterpretation}
              disabled={selectedCards.length === 0 || loading}
            >
              해석하기 ({selectedCards.length}개 선택됨)
            </button>
          </div>

          {/* 에러 메시지 */}
          {error && (
            <div className="error-message">
              <span className="error-icon">⚠</span>
              {error}
            </div>
          )}
        </div>

        {/* 메인 영역 - 카드 그리드 및 히스토리 */}
        <div className="selection-main">
          {/* 히스토리 네비게이션 */}
          {historyLoaded && (
            <CardHistoryNavigation 
              contextId={contextData.contextId}
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={handlePageChange}
              disabled={loading}
              refreshTrigger={historyRefreshTrigger} // 새로 추가
            />
          )}
          
          {/* 카드 그리드 */}
          {cards.length > 0 ? (
            <CardGrid 
              cards={cards}
              selectedCards={selectedCards}
              onCardSelect={handleCardSelection}
              maxSelection={4}
              disabled={loading}
            />
          ) : (
            <div className="no-cards-message">
              <h3>카드를 불러올 수 없습니다</h3>
              <p>잠시 후 다시 시도해주세요.</p>
              <button 
                className="secondary-button"
                onClick={loadInitialCards}
                disabled={loading}
              >
                다시 시도
              </button>
            </div>
          )}

          {/* 카드 정보 */}
          {cards.length > 0 && (
            <div className="cards-info">
              <p>
                <strong>{cards.length}개</strong>의 카드가 추천되었습니다. 
                당신의 관심사 "<strong>{user.interestingTopics?.slice(0, 3).join(', ')}</strong>"와 
                현재 상황을 고려한 결과입니다.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CardSelectionPage;