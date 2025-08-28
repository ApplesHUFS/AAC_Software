import api from './api';

/**
 * 대화 컨텍스트 관리 서비스
 * app.py의 컨텍스트 관련 API와 통신하여 대화 상황 관리
 */
export const contextService = {
  /**
   * 새로운 대화 컨텍스트 생성
   * app.py의 /api/context POST 엔드포인트와 통신
   * @param {Object} contextData - 컨텍스트 생성 데이터
   * @param {string} contextData.userId - 사용자 ID
   * @param {string} contextData.place - 대화 장소
   * @param {string} contextData.interactionPartner - 대화 상대
   * @param {string} [contextData.currentActivity] - 현재 활동 (선택사항)
   * @returns {Promise<Object>} 생성된 컨텍스트 정보
   */
  async createContext(contextData) {
    try {
      // 입력 검증
      if (!contextData || typeof contextData !== 'object') {
        throw new Error('컨텍스트 데이터가 필요합니다.');
      }

      const { userId, place, interactionPartner, currentActivity } = contextData;

      if (!userId || !userId.trim()) {
        throw new Error('사용자 ID가 필요합니다.');
      }

      if (!place || !place.trim()) {
        throw new Error('대화 장소를 입력해주세요.');
      }

      if (!interactionPartner || !interactionPartner.trim()) {
        throw new Error('대화 상대를 입력해주세요.');
      }

      // 입력값 정제
      const payload = {
        userId: userId.trim(),
        place: place.trim(),
        interactionPartner: interactionPartner.trim(),
        currentActivity: currentActivity ? currentActivity.trim() : ''
      };

      // 추가 검증
      if (payload.place.length > 100) {
        throw new Error('장소명은 100자를 초과할 수 없습니다.');
      }

      if (payload.interactionPartner.length > 50) {
        throw new Error('대화 상대명은 50자를 초과할 수 없습니다.');
      }

      if (payload.currentActivity && payload.currentActivity.length > 100) {
        throw new Error('현재 활동은 100자를 초과할 수 없습니다.');
      }

      const response = await api.post('/api/context', payload);

      if (response.success && response.data) {
        // app.py 응답 구조 검증
        if (!response.data.contextId) {
          throw new Error('컨텍스트 ID가 생성되지 않았습니다.');
        }

        return response;
      } else {
        throw new Error(response.error || '컨텍스트 생성에 실패했습니다.');
      }
    } catch (error) {
      console.error('컨텍스트 생성 실패:', error);
      
      // 특정 에러 처리
      if (error.message.includes('400')) {
        throw new Error('입력 정보가 올바르지 않습니다. 모든 필수 항목을 확인해주세요.');
      } else if (error.message.includes('404')) {
        throw new Error('사용자를 찾을 수 없습니다.');
      }
      
      throw error;
    }
  },

  /**
   * 기존 컨텍스트 조회
   * app.py의 /api/context/{contextId} GET 엔드포인트와 통신
   * @param {string} contextId - 조회할 컨텍스트 ID
   * @returns {Promise<Object>} 컨텍스트 정보
   */
  async getContext(contextId) {
    try {
      if (!contextId || !contextId.trim()) {
        throw new Error('컨텍스트 ID가 필요합니다.');
      }

      const response = await api.get(`/api/context/${contextId.trim()}`);

      if (response.success && response.data) {
        // 응답 구조 검증
        const requiredFields = ['contextId', 'place', 'interactionPartner'];
        for (const field of requiredFields) {
          if (!response.data[field]) {
            throw new Error(`컨텍스트 응답에 필수 필드가 누락되었습니다: ${field}`);
          }
        }

        return response;
      } else {
        throw new Error(response.error || '컨텍스트 정보를 불러올 수 없습니다.');
      }
    } catch (error) {
      console.error('컨텍스트 조회 실패:', error);
      
      if (error.message.includes('404')) {
        throw new Error('해당 컨텍스트를 찾을 수 없습니다.');
      }
      
      throw error;
    }
  },

  /**
   * 컨텍스트 업데이트
   * TODO: app.py에 해당 엔드포인트 구현 필요
   * @param {string} contextId - 업데이트할 컨텍스트 ID
   * @param {Object} updateData - 업데이트할 데이터
   * @returns {Promise<Object>} 업데이트 결과
   */
  async updateContext(contextId, updateData) {
    try {
      if (!contextId || !contextId.trim()) {
        throw new Error('컨텍스트 ID가 필요합니다.');
      }

      if (!updateData || typeof updateData !== 'object') {
        throw new Error('업데이트할 데이터가 필요합니다.');
      }

      // 현재 app.py에 해당 엔드포인트가 없으므로 임시로 에러 반환
      throw new Error('컨텍스트 업데이트 기능은 아직 구현되지 않았습니다.');

      // TODO: app.py에 PUT /api/context/{contextId} 구현 후 주석 해제
      // const payload = {
      //   place: updateData.place?.trim(),
      //   interactionPartner: updateData.interactionPartner?.trim(),
      //   currentActivity: updateData.currentActivity?.trim() || ''
      // };
      // 
      // // undefined 값들 제거
      // Object.keys(payload).forEach(key => {
      //   if (payload[key] === undefined) {
      //     delete payload[key];
      //   }
      // });
      // 
      // const response = await api.put(`/api/context/${contextId.trim()}`, payload);
      // 
      // if (response.success) {
      //   return response;
      // } else {
      //   throw new Error(response.error || '컨텍스트 업데이트에 실패했습니다.');
      // }
    } catch (error) {
      console.error('컨텍스트 업데이트 실패:', error);
      throw error;
    }
  },

  /**
   * 컨텍스트 삭제
   * TODO: app.py에 해당 엔드포인트 구현 필요
   * @param {string} contextId - 삭제할 컨텍스트 ID
   * @returns {Promise<Object>} 삭제 결과
   */
  async deleteContext(contextId) {
    try {
      if (!contextId || !contextId.trim()) {
        throw new Error('컨텍스트 ID가 필요합니다.');
      }

      // 현재 app.py에 해당 엔드포인트가 없으므로 임시로 에러 반환
      throw new Error('컨텍스트 삭제 기능은 아직 구현되지 않았습니다.');

      // TODO: app.py에 DELETE /api/context/{contextId} 구현 후 주석 해제
      // const response = await api.delete(`/api/context/${contextId.trim()}`);
      // 
      // if (response.success) {
      //   return response;
      // } else {
      //   throw new Error(response.error || '컨텍스트 삭제에 실패했습니다.');
      // }
    } catch (error) {
      console.error('컨텍스트 삭제 실패:', error);
      throw error;
    }
  },

  /**
   * 사용자의 모든 컨텍스트 조회
   * TODO: app.py에 해당 엔드포인트 구현 필요
   * @param {string} userId - 사용자 ID
   * @param {Object} [options] - 조회 옵션
   * @param {number} [options.page=1] - 페이지 번호
   * @param {number} [options.limit=10] - 페이지당 항목 수
   * @returns {Promise<Object>} 컨텍스트 목록
   */
  async getUserContexts(userId, options = {}) {
    try {
      if (!userId || !userId.trim()) {
        throw new Error('사용자 ID가 필요합니다.');
      }

      const { page = 1, limit = 10 } = options;

      if (page < 1) {
        throw new Error('페이지 번호는 1 이상이어야 합니다.');
      }

      if (limit < 1 || limit > 100) {
        throw new Error('페이지당 항목 수는 1-100 범위여야 합니다.');
      }

      // 현재 app.py에 해당 엔드포인트가 없으므로 임시로 에러 반환
      throw new Error('사용자 컨텍스트 목록 조회 기능은 아직 구현되지 않았습니다.');

      // TODO: app.py에 GET /api/context/user/{userId} 구현 후 주석 해제
      // const response = await api.get(`/api/context/user/${userId.trim()}`, {
      //   params: { page, limit }
      // });
      // 
      // if (response.success && response.data) {
      //   return response;
      // } else {
      //   throw new Error(response.error || '컨텍스트 목록을 불러올 수 없습니다.');
      // }
    } catch (error) {
      console.error('사용자 컨텍스트 조회 실패:', error);
      throw error;
    }
  },

  /**
   * 컨텍스트 데이터 검증
   * @param {Object} contextData - 검증할 컨텍스트 데이터
   * @returns {Object} 검증 결과 { valid: boolean, errors: string[] }
   */
  validateContextData(contextData) {
    const errors = [];

    if (!contextData || typeof contextData !== 'object') {
      return { valid: false, errors: ['컨텍스트 데이터가 올바르지 않습니다.'] };
    }

    const { userId, place, interactionPartner, currentActivity } = contextData;

    // 필수 필드 검증
    if (!userId || !userId.trim()) {
      errors.push('사용자 ID가 필요합니다.');
    }

    if (!place || !place.trim()) {
      errors.push('대화 장소가 필요합니다.');
    } else if (place.trim().length > 100) {
      errors.push('장소명은 100자를 초과할 수 없습니다.');
    }

    if (!interactionPartner || !interactionPartner.trim()) {
      errors.push('대화 상대가 필요합니다.');
    } else if (interactionPartner.trim().length > 50) {
      errors.push('대화 상대명은 50자를 초과할 수 없습니다.');
    }

    // 선택적 필드 검증
    if (currentActivity && typeof currentActivity === 'string' && currentActivity.trim().length > 100) {
      errors.push('현재 활동은 100자를 초과할 수 없습니다.');
    }

    return {
      valid: errors.length === 0,
      errors
    };
  },

  /**
   * 컨텍스트 요약 정보 생성
   * @param {Object} contextData - 컨텍스트 데이터
   * @returns {string} 컨텍스트 요약 문자열
   */
  generateContextSummary(contextData) {
    if (!contextData || typeof contextData !== 'object') {
      return '알 수 없는 상황';
    }

    const { place, interactionPartner, currentActivity } = contextData;

    let summary = '';

    if (place) {
      summary += place;
    }

    if (interactionPartner) {
      summary += summary ? `에서 ${interactionPartner}와` : `${interactionPartner}와`;
    }

    if (currentActivity) {
      summary += ` ${currentActivity} 중`;
    }

    return summary || '대화 상황';
  },

  /**
   * 컨텍스트 ID 유효성 검증
   * @param {string} contextId - 검증할 컨텍스트 ID
   * @returns {boolean} 유효성 여부
   */
  isValidContextId(contextId) {
    if (!contextId || typeof contextId !== 'string') {
      return false;
    }

    const trimmedId = contextId.trim();
    
    // 기본적인 ID 형식 검증 (UUID 또는 영숫자 조합)
    const idPattern = /^[a-zA-Z0-9-_]{8,}$/;
    
    return idPattern.test(trimmedId);
  },

  /**
   * 컨텍스트 시간 포맷팅
   * @param {string|Date} timestamp - 타임스탬프
   * @param {string} [format='relative'] - 포맷 타입 ('relative', 'absolute', 'time')
   * @returns {string} 포맷된 시간 문자열
   */
  formatContextTime(timestamp, format = 'relative') {
    if (!timestamp) return '';

    const date = new Date(timestamp);
    
    if (isNaN(date.getTime())) {
      return '';
    }

    switch (format) {
      case 'relative':
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        
        if (diffMins < 1) return '방금 전';
        if (diffMins < 60) return `${diffMins}분 전`;
        if (diffHours < 24) return `${diffHours}시간 전`;
        
        const diffDays = Math.floor(diffHours / 24);
        if (diffDays < 7) return `${diffDays}일 전`;
        
        return date.toLocaleDateString('ko-KR');

      case 'absolute':
        return date.toLocaleString('ko-KR');

      case 'time':
        return date.toLocaleTimeString('ko-KR', { 
          hour: '2-digit', 
          minute: '2-digit' 
        });

      default:
        return date.toLocaleString('ko-KR');
    }
  }
};