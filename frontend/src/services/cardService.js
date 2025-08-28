import api from './api';

// 카드 관련 서비스
// app.py의 카드 추천, 선택, 해석 API와 통신
export const cardService = {
  // 개인화된 카드 추천 요청
  // 흐름명세서: 70% 관련 카드 + 30% 랜덤 카드로 20개 묶음 추천
  // app.py의 /api/cards/recommend 엔드포인트와 통신
  async getRecommendations(userId, contextId) {
    try {
      // 입력 검증
      if (!userId || !userId.trim()) {
        throw new Error('사용자 ID가 필요합니다.');
      }

      if (!contextId || !contextId.trim()) {
        throw new Error('컨텍스트 ID가 필요합니다.');
      }

      const payload = {
        userId: userId.trim(),
        contextId: contextId.trim()
      };

      const response = await api.post('/api/cards/recommend', payload);

      if (response.success && response.data) {
        // app.py 응답 구조 검증
        if (!response.data.cards || !Array.isArray(response.data.cards)) {
          throw new Error('올바르지 않은 카드 추천 응답 형식입니다.');
        }

        return response;
      } else {
        throw new Error(response.error || '카드 추천을 받을 수 없습니다.');
      }
    } catch (error) {
      console.error('카드 추천 요청 실패:', error);
      
      // 특정 에러 처리
      if (error.message.includes('404')) {
        throw new Error('사용자 또는 컨텍스트를 찾을 수 없습니다.');
      } else if (error.message.includes('503')) {
        throw new Error('카드 추천 시스템을 사용할 수 없습니다. 잠시 후 다시 시도해주세요.');
      }
      
      throw error;
    }
  },

  // 카드 선택 유효성 검증
  // app.py의 /api/cards/validate 엔드포인트와 통신
  async validateSelection(selectedCards, availableOptions = []) {
    try {
      // 입력 검증
      if (!selectedCards || !Array.isArray(selectedCards)) {
        throw new Error('선택된 카드 목록이 올바르지 않습니다.');
      }

      if (selectedCards.length === 0) {
        throw new Error('최소 1개의 카드를 선택해야 합니다.');
      }

      if (selectedCards.length > 4) {
        throw new Error('최대 4개까지만 선택할 수 있습니다.');
      }

      // 카드 filename 추출
      const cardFilenames = selectedCards.map(card => {
        if (typeof card === 'string') {
          return card;
        } else if (card && card.filename) {
          return card.filename;
        } else if (card && card.name) {
          // name에서 filename 생성 (임시 처리)
          return card.name.replace(/ /g, '_') + '.png';
        } else {
          throw new Error('올바르지 않은 카드 형식입니다.');
        }
      });

      const payload = {
        selectedCards: cardFilenames,
        availableOptions: Array.isArray(availableOptions) ? availableOptions : []
      };

      const response = await api.post('/api/cards/validate', payload);

      if (response.success) {
        return response;
      } else {
        // 422 상태코드 (Unprocessable Entity)는 유효하지 않은 선택을 의미
        if (response.status === 422) {
          throw new Error('선택한 카드 조합이 유효하지 않습니다.');
        }
        throw new Error(response.error || '카드 선택 검증에 실패했습니다.');
      }
    } catch (error) {
      console.error('카드 선택 검증 실패:', error);
      throw error;
    }
  },

  // 선택된 카드 해석 요청
  // 흐름명세서: OpenAI API로 3가지 해석 생성
  // app.py의 /api/cards/interpret 엔드포인트와 통신
  async interpretCards(userId, selectedCards, contextId) {
    try {
      // 입력 검증
      if (!userId || !userId.trim()) {
        throw new Error('사용자 ID가 필요합니다.');
      }

      if (!selectedCards || !Array.isArray(selectedCards) || selectedCards.length === 0) {
        throw new Error('선택된 카드가 없습니다.');
      }

      if (selectedCards.length > 4) {
        throw new Error('최대 4개까지만 해석할 수 있습니다.');
      }

      // 카드 filename 추출 (CardSelectionPage에서 보낸 형태 처리)
      const cardFilenames = selectedCards.map(card => {
        if (typeof card === 'string') {
          return card;
        } else if (card && card.filename) {
          return card.filename;
        } else if (card && card.name) {
          return card.name.replace(/ /g, '_') + '.png';
        } else {
          throw new Error(`올바르지 않은 카드 형식: ${JSON.stringify(card)}`);
        }
      });

      const payload = {
        userId: userId.trim(),
        selectedCards: cardFilenames,
        contextId: contextId ? contextId.trim() : null
      };

      const response = await api.post('/api/cards/interpret', payload);

      if (response.success && response.data) {
        // app.py 응답 구조 검증
        if (!response.data.interpretations || !Array.isArray(response.data.interpretations)) {
          throw new Error('올바르지 않은 해석 응답 형식입니다.');
        }

        if (response.data.interpretations.length === 0) {
          throw new Error('해석을 생성할 수 없습니다.');
        }

        return response;
      } else {
        throw new Error(response.error || '카드 해석에 실패했습니다.');
      }
    } catch (error) {
      console.error('카드 해석 요청 실패:', error);
      
      // 특정 에러 처리
      if (error.message.includes('503')) {
        throw new Error('카드 해석 시스템을 사용할 수 없습니다. 잠시 후 다시 시도해주세요.');
      } else if (error.message.includes('timeout')) {
        throw new Error('해석 생성 시간이 초과되었습니다. 다시 시도해주세요.');
      }
      
      throw error;
    }
  },

  // 카드 추천 히스토리 요약 조회
  // 흐름명세서: 이전 페이지를 볼 수 있음
  // app.py의 /api/cards/history/{contextId} 엔드포인트와 통신
  async getHistorySummary(contextId) {
    try {
      if (!contextId || !contextId.trim()) {
        throw new Error('컨텍스트 ID가 필요합니다.');
      }

      const response = await api.get(`/api/cards/history/${contextId.trim()}`);

      if (response.success && response.data) {
        // 응답 구조 검증
        if (typeof response.data.totalPages !== 'number') {
          throw new Error('올바르지 않은 히스토리 응답 형식입니다.');
        }

        return response;
      } else {
        throw new Error(response.error || '히스토리 정보를 불러올 수 없습니다.');
      }
    } catch (error) {
      console.error('히스토리 요약 조회 실패:', error);
      
      if (error.message.includes('404')) {
        throw new Error('해당 컨텍스트의 히스토리를 찾을 수 없습니다.');
      }
      
      throw error;
    }
  },

  // 특정 히스토리 페이지의 카드 목록 조회
  // app.py의 /api/cards/history/{contextId}/page/{pageNumber} 엔드포인트와 통신
  async getHistoryPage(contextId, pageNumber) {
    try {
      if (!contextId || !contextId.trim()) {
        throw new Error('컨텍스트 ID가 필요합니다.');
      }

      if (!pageNumber || pageNumber < 1) {
        throw new Error('올바른 페이지 번호가 필요합니다.');
      }

      const response = await api.get(`/api/cards/history/${contextId.trim()}/page/${pageNumber}`);

      if (response.success && response.data) {
        // 응답 구조 검증
        if (!response.data.cards || !Array.isArray(response.data.cards)) {
          throw new Error('올바르지 않은 히스토리 페이지 응답 형식입니다.');
        }

        return response;
      } else {
        throw new Error(response.error || '히스토리 페이지를 불러올 수 없습니다.');
      }
    } catch (error) {
      console.error('히스토리 페이지 조회 실패:', error);
      
      if (error.message.includes('404')) {
        throw new Error('요청한 히스토리 페이지를 찾을 수 없습니다.');
      }
      
      throw error;
    }
  },

  // 카드 이미지 URL 생성
  getCardImageUrl(filename) {
    if (!filename) {
      console.warn('카드 파일명이 제공되지 않았습니다.');
      return '/placeholder-card.png'; // 기본 이미지
    }

    // app.py의 이미지 서빙 경로
    return `http://localhost:8000/api/images/${filename}`;
  },

  // 카드 정보 검증
  validateCardObject(card) {
    if (!card || typeof card !== 'object') {
      return false;
    }

    // 필수 필드 검증
    const requiredFields = ['name', 'filename', 'imagePath'];
    for (const field of requiredFields) {
      if (!card[field]) {
        return false;
      }
    }

    // 파일명 형식 검증 (간단한 검증)
    if (!card.filename.endsWith('.png')) {
      return false;
    }

    return true;
  },

  // 선택된 카드들의 메타데이터 생성
  generateSelectionMetadata(selectedCards) {
    if (!Array.isArray(selectedCards)) {
      return { count: 0, valid: false };
    }

    const metadata = {
      count: selectedCards.length,
      valid: selectedCards.length >= 1 && selectedCards.length <= 4,
      filenames: selectedCards.map(card => card.filename || card).filter(Boolean),
      names: selectedCards.map(card => card.name || card).filter(Boolean)
    };

    metadata.hasValidStructure = metadata.filenames.length === selectedCards.length;
    
    return metadata;
  },

  // 카드 추천 결과 정규화
  // app.py에서 받은 카드 데이터를 프론트엔드에서 사용하기 좋은 형태로 변환
  normalizeCardData(rawCards) {
    if (!Array.isArray(rawCards)) {
      console.warn('카드 데이터가 배열이 아닙니다:', rawCards);
      return [];
    }

    return rawCards.map((card, index) => {
      // app.py에서 보내는 형식에 맞춰 처리
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
    }).filter(Boolean); // null 값 제거
  }
};