// src/pages/CardSelectionPage.js
import React, { useState, useRef, useEffect, useCallback } from 'react';
import { cardService } from '../services/cardService';
import { CardGrid, SelectedCardsDisplay } from '../components/cards/CardGrid';
import CardHistoryNavigation from '../components/cards/CardHistoryNavigation';

const CardSelectionPage = ({ user, contextData, onCardSelectionComplete }) => {
  // 상태 관리
  const [cards, setCards] = useState([]);
  const [selectedCards, setSelectedCards] = useState([]);
  const [allRecommendedCards, setAllRecommendedCards] = useState([]); 
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // 페이지 히스토리 관리
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  
  // UI 상태
  const [isRerolling, setIsRerolling] = useState(false);

  // 중복 호출 방지를 위한 ref
  const isInitialLoadDone = useRef(false);
  const isComponentMounted = useRef(false);

  // 추천받은 카드를 전체 카드 풀에 추가
  const addToRecommendedCards = useCallback((newCards) => {
    if (!newCards?.length) return;
    
    setAllRecommendedCards(prev => {
      const existingFilenames = new Set(prev.map(card => card.filename));
      const uniqueNewCards = newCards.filter(card => !existingFilenames.has(card.filename));
      return [...prev, ...uniqueNewCards];
    });
  }, []);

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
        addToRecommendedCards(normalizedCards);
        
        // 페이지 정보 업데이트 - 초기 로드 시에는 항상 1페이지부터 시작
        const pagination = response.data.pagination || {};
        const latestPage = pagination.totalPages || 1;
        setCurrentPage(latestPage);
        setTotalPages(latestPage);
      } else {
        setError(response.error || '카드 추천을 받을 수 없습니다.');
      }
    } catch (error) {
      setError(error.message || '카드 로딩 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  }, [user?.userId, contextData?.contextId, addToRecommendedCards]);

  // 컴포넌트 마운트 시 초기 카드 로드 (중복 호출 방지)
  useEffect(() => {
    isComponentMounted.current = true;

    // React StrictMode에서 중복 실행 방지
    if (!isInitialLoadDone.current && isComponentMounted.current) {
      isInitialLoadDone.current = true;
      loadInitialCards();
    }

    // cleanup 함수
    return () => {
      isComponentMounted.current = false;
    };
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
        addToRecommendedCards(normalizedCards);
      } else {
        setError(response.error || '히스토리 페이지를 불러올 수 없습니다.');
      }
    } catch (error) {
      setError(error.message || '히스토리 페이지 로딩 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  }, [contextData?.contextId, currentPage, loading, addToRecommendedCards]);

  // 카드 재추천 처리
  const handleRerollCards = useCallback(async () => {
    if (isRerolling || !user?.userId || !contextData?.contextId) return;

    setIsRerolling(true);
    setError('');

    try {
      const response = await cardService.getRecommendations(user.userId, contextData.contextId);
      
      if (response.success && response.data) {
        const normalizedCards = cardService.normalizeCardData(response.data.cards || []);
        setCards(normalizedCards);
        addToRecommendedCards(normalizedCards);
        
        // 페이지 정보 업데이트
        const pagination = response.data.pagination || {};
        const latestPage = pagination.totalPages || totalPages + 1;
        setCurrentPage(latestPage);
        setTotalPages(latestPage);
      } else {
        setError(response.error || '카드 재추천에 실패했습니다.');
      }
    } catch (error) {
      setError(error.message || '카드 재추천 중 오류가 발생했습니다.');
    } finally {
      setIsRerolling(false);
    }
  }, [isRerolling, user?.userId, contextData?.contextId, totalPages, addToRecommendedCards]);

  // 카드 선택/해제 처리
  const handleCardSelection = useCallback((card) => {
    if (loading) return;

    const isSelected = selectedCards.some(selected => selected.filename === card.filename);
    
    if (isSelected) {
      setSelectedCards(prev => prev.filter(selected => selected.filename !== card.filename));
    } else if (selectedCards.length < 4) {
      setSelectedCards(prev => [...prev, card]);
    }
    
    if (error) setError('');
  }, [selectedCards, loading, error]);

  // 선택된 카드 개별 제거
  const handleRemoveSelectedCard = useCallback((cardToRemove) => {
    setSelectedCards(prev => prev.filter(card => card.filename !== cardToRemove.filename));
  }, []);

  // 카드 선택 완료 및 해석 단계로 진행
  const handleProceedToInterpretation = useCallback(async () => {
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
      const validationResponse = await cardService.validateSelection(selectedCards, allRecommendedCards);

      if (validationResponse.success && validationResponse.data?.valid) {
        onCardSelectionComplete(selectedCards);
      } else {
        setError('선택한 카드가 유효하지 않습니다. 다시 선택해주세요.');
      }
    } catch (error) {
      setError(error.message || '카드 검증 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  }, [selectedCards, allRecommendedCards, onCardSelectionComplete]);

  // 로딩 상태
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
        <h2>AAC 카드 선택</h2>
        <div className="context-info">
          <span>{contextData.place}</span>
          <span>{contextData.interactionPartner}와</span>
          {contextData.currentActivity && <span>{contextData.currentActivity} 중</span>}
        </div>
      </header>

      <div className="selection-content">
        {/* 사이드바 */}
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

          {error && <div className="error-message">{error}</div>}

          {/* 추천 카드 정보 */}
          {allRecommendedCards.length > 0 && (
            <div className="recommendation-info">
              <small>
                지금까지 <strong>{allRecommendedCards.length}개</strong>의 카드가 추천되었습니다.
              </small>
            </div>
          )}
        </div>

        {/* 메인 영역 */}
        <div className="selection-main">
          {/* 히스토리 네비게이션 */}
          {totalPages > 1 && (
            <CardHistoryNavigation 
              contextId={contextData.contextId}
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={handlePageChange}
              disabled={loading}
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
              <p>현재 페이지: <strong>{currentPage}/{totalPages}</strong></p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CardSelectionPage;