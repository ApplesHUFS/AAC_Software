// src/pages/CardSelectionPage.js
import React, { useState, useRef, useEffect, useCallback } from 'react';
import { cardService } from '../services/cardService';
import { CardGrid, SelectedCardsDisplay } from '../components/cards/CardGrid';
import CardHistoryNavigation from '../components/cards/CardHistoryNavigation';

const CardSelectionPage = ({ user, contextData, onCardSelectionComplete }) => {
  // 카드 관련 상태
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

  // 중복 호출 방지용 ref
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
        
        // 페이지 정보 업데이트
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

  // 컴포넌트 마운트 시 초기 카드 로드
  useEffect(() => {
    isComponentMounted.current = true;

    if (!isInitialLoadDone.current && isComponentMounted.current) {
      isInitialLoadDone.current = true;
      loadInitialCards();
    }

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
      <div className="card-selection-page communicator-theme loading">
        <div className="loading-content communicator-loading">
          <div className="loading-header">
            <span className="loading-icon">✨</span>
            <h2>소통이를 위한 카드를 준비하고 있어요!</h2>
          </div>
          <p>소통이의 관심사와 현재 상황을 분석해서 딱 맞는 카드들을 골라드릴게요.</p>
          <div className="loading-spinner"></div>
          <div className="loading-tips">
            <p>💡 <strong>{user.name}</strong>님이 좋아하는 주제를 고려하고 있어요</p>
            <p>🎯 <strong>{contextData.place}</strong>에서 쓰기 좋은 카드들을 찾고 있어요</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="card-selection-page communicator-theme">
      {/* 페이지 헤더 */}
      <header className="selection-header communicator-header">
        <div className="role-indicator communicator-role">
          <span className="role-icon">💬</span>
          <span>소통이 카드 선택</span>
        </div>
        <h2>어떤 카드로 소통할까요?</h2>
        <div className="context-info">
          <span className="context-item">📍 {contextData.place}</span>
          <span className="context-item">👥 {contextData.interactionPartner}와 함께</span>
          {contextData.currentActivity && (
            <span className="context-item">🎯 {contextData.currentActivity} 중</span>
          )}
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
              className="secondary-button reroll-button"
              onClick={handleRerollCards}
              disabled={loading || isRerolling}
            >
              {isRerolling ? '🔄 새 카드 찾는 중...' : '🔄 다른 카드 보기'}
            </button>
            
            <button 
              className="primary-button proceed-button"
              onClick={handleProceedToInterpretation}
              disabled={selectedCards.length === 0 || loading}
            >
              <span className="button-icon">✅</span>
              이 카드로 소통하기 ({selectedCards.length}개)
            </button>
          </div>

          {error && (
            <div className="error-message communicator-error">
              <span className="error-icon">⚠️</span>
              {error}
            </div>
          )}

          {/* 추천 카드 정보 */}
          {allRecommendedCards.length > 0 && (
            <div className="recommendation-info communicator-info">
              <div className="info-content">
                <span className="info-icon">🎨</span>
                <small>
                  지금까지 <strong>{allRecommendedCards.length}개</strong>의 
                  소통이 맞춤 카드가 준비되었어요!
                </small>
              </div>
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
            <div className="no-cards-message communicator-message">
              <span className="message-icon">😅</span>
              <h3>앗! 카드를 불러올 수 없어요</h3>
              <p>잠깐만 기다렸다가 다시 시도해주세요.</p>
              <button 
                className="secondary-button retry-button"
                onClick={loadInitialCards}
                disabled={loading}
              >
                🔄 다시 시도하기
              </button>
            </div>
          )}

          {/* 카드 정보 */}
          {cards.length > 0 && (
            <div className="cards-info communicator-guide">
              <div className="guide-content">
                <p>
                  <span className="guide-icon">🎯</span>
                  <strong>{cards.length}개</strong>의 카드가 소통이를 위해 준비되었어요! 
                </p>
                <p>
                  <span className="guide-icon">❤️</span>
                  <strong>{user.interestingTopics?.slice(0, 3).join(', ')}</strong> 같은 
                  관심사를 고려해서 골랐어요.
                </p>
                <p>
                  <span className="guide-icon">📄</span>
                  현재 페이지: <strong>{currentPage} / {totalPages}</strong>
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CardSelectionPage;