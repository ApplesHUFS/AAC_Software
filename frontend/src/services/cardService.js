// frontend\src\services\cardService.js
import api from './api';

export const cardService = {
  // 개인화된 카드 추천 요청
  async getRecommendations(userId, contextId) {
    try {
      if (!userId?.trim() || !contextId?.trim()) {
        throw new Error('사용자 ID와 컨텍스트 ID가 필요합니다.');
      }

      const payload = {
        userId: userId.trim(),
        contextId: contextId.trim()
      };

      const response = await api.post('/api/cards/recommend', payload);

      if (response.success && response.data?.cards) {
        return response;
      } else {
        throw new Error(response.error || '카드 추천을 받을 수 없습니다.');
      }
    } catch (error) {
      console.error('카드 추천 요청 실패:', error);
      
      if (error.status === 404) {
        throw new Error('사용자 또는 컨텍스트를 찾을 수 없습니다.');
      } else if (error.status === 503) {
        throw new Error('카드 추천 시스템을 사용할 수 없습니다.');
      }
      
      throw error;
    }
  },

  // 카드 히스토리 요약 정보 조회
  async getHistorySummary(contextId) {
    try {
      if (!contextId?.trim()) {
        throw new Error('컨텍스트 ID가 필요합니다.');
      }

      const response = await api.get(`/api/cards/history/${contextId.trim()}`);
      
      if (response.success && response.data) {
        return response;
      } else {
        throw new Error(response.error || '히스토리 정보를 불러올 수 없습니다.');
      }
    } catch (error) {
      console.error('히스토리 요약 조회 실패:', error);
      throw error;
    }
  },

  // 특정 히스토리 페이지의 카드 목록 조회
  async getHistoryPage(contextId, pageNumber) {
    try {
      if (!contextId?.trim() || !pageNumber || pageNumber < 1) {
        throw new Error('유효한 컨텍스트 ID와 페이지 번호가 필요합니다.');
      }

      const response = await api.get(`/api/cards/history/${contextId.trim()}/page/${pageNumber}`);
      
      if (response.success && response.data?.cards) {
        return response;
      } else {
        throw new Error(response.error || '히스토리 페이지를 불러올 수 없습니다.');
      }
    } catch (error) {
      console.error('히스토리 페이지 조회 실패:', error);
      throw error;
    }
  },

  // 카드 선택 유효성 검증
  async validateSelection(selectedCards, availableOptions = []) {
    try {
      if (!selectedCards || selectedCards.length === 0) {
        throw new Error('선택된 카드가 없습니다.');
      }

      // 선택된 카드를 파일명 배열로 변환
      const selectedCardFilenames = selectedCards.map(card => {
        if (typeof card === 'string') {
          return card;
        } else if (card?.filename) {
          return card.filename;
        } else {
          throw new Error(`올바르지 않은 카드 형식: ${JSON.stringify(card)}`);
        }
      });

      // 사용 가능한 카드를 파일명 배열로 변환
      const availableCardFilenames = availableOptions.map(card => {
        if (typeof card === 'string') {
          return card;
        } else if (card?.filename) {
          return card.filename;
        } else {
          console.warn('알 수 없는 카드 형식:', card);
          return String(card);
        }
      });

      const payload = {
        selectedCards: selectedCardFilenames,
        availableOptions: availableCardFilenames
      };

      console.log('카드 검증 요청:', {
        selected: selectedCardFilenames.length,
        available: availableCardFilenames.length
      });

      const response = await api.post('/api/cards/validate', payload);
      
      if (response.success) {
        return response;
      } else {
        throw new Error(response.error || '카드 선택 검증에 실패했습니다.');
      }
    } catch (error) {
      console.error('카드 선택 검증 실패:', error);
      throw error;
    }
  },

  // 선택된 카드 해석 요청
  async interpretCards(userId, selectedCards, contextId) {
    try {
      if (!userId?.trim() || !selectedCards || selectedCards.length === 0) {
        throw new Error('사용자 ID와 선택된 카드가 필요합니다.');
      }

      // 카드를 파일명 배열로 변환
      const cardFilenames = selectedCards.map(card => {
        if (typeof card === 'string') {
          return card;
        } else if (card?.filename) {
          return card.filename;
        } else {
          throw new Error(`올바르지 않은 카드 형식: ${JSON.stringify(card)}`);
        }
      });

      const payload = {
        userId: userId.trim(),
        selectedCards: cardFilenames,
        contextId: contextId?.trim() || null
      };

      console.log('카드 해석 요청:', {
        userId: payload.userId,
        cardCount: cardFilenames.length,
        contextId: payload.contextId
      });

      const response = await api.post('/api/cards/interpret', payload);

      if (response.success && response.data?.interpretations) {
        return response;
      } else {
        throw new Error(response.error || '카드 해석에 실패했습니다.');
      }
    } catch (error) {
      console.error('카드 해석 요청 실패:', error);
      
      if (error.status === 503) {
        throw new Error('카드 해석 시스템을 사용할 수 없습니다.');
      }
      
      throw error;
    }
  },

  // 카드 이미지 URL 생성
  getCardImageUrl(filename) {
    if (!filename) {
      return '/placeholder-card.png';
    }
    return `http://localhost:8000/api/images/${filename}`;
  },

  // 카드 데이터 정규화
  normalizeCardData(rawCards) {
    if (!Array.isArray(rawCards)) {
      console.warn('카드 데이터가 배열이 아닙니다:', rawCards);
      return [];
    }

    return rawCards.map((card, index) => {
      if (typeof card === 'string') {
        // 파일명만 있는 경우
        const filename = card;
        const name = filename.replace('.png', '').replace(/_/g, ' ');
        return {
          id: filename.split('_')[0] || index.toString(),
          name: name,
          filename: filename,
          imagePath: `/api/images/${filename}`,
          index: index,
          selected: false
        };
      } else if (card && typeof card === 'object') {
        // 객체 형태인 경우
        return {
          id: card.id || card.filename?.split('_')[0] || index.toString(),
          name: card.name || card.filename?.replace('.png', '').replace(/_/g, ' ') || `Card ${index + 1}`,
          filename: card.filename || `${card.name?.replace(/ /g, '_')}.png`,
          imagePath: card.imagePath || `/api/images/${card.filename}`,
          index: card.index || index,
          selected: card.selected || false
        };
      } else {
        console.warn('올바르지 않은 카드 데이터 형식:', card);
        return null;
      }
    }).filter(Boolean);
  },

  // 카드 데이터 중복 제거
  deduplicateCards(cards) {
    if (!Array.isArray(cards)) return [];
    
    const seen = new Set();
    return cards.filter(card => {
      const key = card.filename || card.name || card.id;
      if (seen.has(key)) {
        return false;
      }
      seen.add(key);
      return true;
    });
  },

  // 카드 선택 상태 확인
  isCardSelected(card, selectedCards) {
    if (!card || !Array.isArray(selectedCards)) return false;
    
    return selectedCards.some(selected => {
      return (selected.filename === card.filename) || 
             (selected.id === card.id) ||
             (selected.name === card.name);
    });
  }
};