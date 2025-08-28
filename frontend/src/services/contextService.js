import api from './api';

// 대화 컨텍스트 관리 서비스
// app.py의 컨텍스트 관련 API와 통신하여 대화 상황 관리
export const contextService = {
  // 새로운 대화 컨텍스트 생성
  // 흐름명세서 4.1단계: partner한테 context 입력 요청
  // app.py의 /api/context POST 엔드포인트와 통신
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

  // 기존 컨텍스트 조회
  // app.py의 /api/context/{contextId} GET 엔드포인트와 통신
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

  // 컨텍스트 데이터 검증
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

  // 컨텍스트 요약 정보 생성
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

  // 컨텍스트 ID 유효성 검증
  isValidContextId(contextId) {
    if (!contextId || typeof contextId !== 'string') {
      return false;
    }

    const trimmedId = contextId.trim();
    
    // 기본적인 ID 형식 검증 (UUID 또는 영숫자 조합)
    const idPattern = /^[a-zA-Z0-9-_]{8,}$/;
    
    return idPattern.test(trimmedId);
  },

  // 컨텍스트 시간 포맷팅
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