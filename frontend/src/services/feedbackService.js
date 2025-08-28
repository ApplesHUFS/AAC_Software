import api from './api';

// 피드백 관리 서비스
// app.py의 피드백 관련 API와 통신하여 Partner 피드백 처리
export const feedbackService = {
  // Partner 확인 요청
  // 흐름명세서 4.5단계: partner에게 해석 확인 요청
  // app.py의 /api/feedback/request 엔드포인트와 통신
  async requestPartnerConfirmation(requestData) {
    try {
      // 입력 검증
      if (!requestData || typeof requestData !== 'object') {
        throw new Error('피드백 요청 데이터가 필요합니다.');
      }

      const { userId, cards, context, interpretations, partnerInfo } = requestData;

      if (!userId || !userId.trim()) {
        throw new Error('사용자 ID가 필요합니다.');
      }

      if (!cards || !Array.isArray(cards) || cards.length === 0) {
        throw new Error('선택된 카드 정보가 필요합니다.');
      }

      if (!context || typeof context !== 'object') {
        throw new Error('대화 컨텍스트 정보가 필요합니다.');
      }

      if (!interpretations || !Array.isArray(interpretations) || interpretations.length === 0) {
        throw new Error('해석 정보가 필요합니다.');
      }

      // 카드 데이터 정규화
      const normalizedCards = cards.map(card => {
        if (typeof card === 'string') {
          return card;
        } else if (card && card.filename) {
          return card.filename;
        } else if (card && card.name) {
          return card.name.replace(/ /g, '_') + '.png';
        } else {
          throw new Error('올바르지 않은 카드 형식입니다.');
        }
      });

      // 해석 데이터 정규화
      const normalizedInterpretations = interpretations.map(interp => {
        if (typeof interp === 'string') {
          return interp;
        } else if (interp && interp.text) {
          return interp.text;
        } else {
          throw new Error('올바르지 않은 해석 형식입니다.');
        }
      });

      // 컨텍스트 데이터 검증
      if (!context.place || !context.interactionPartner) {
        throw new Error('컨텍스트에 필수 정보(장소, 대화상대)가 누락되었습니다.');
      }

      // API 요청 페이로드 구성
      const payload = {
        userId: userId.trim(),
        cards: normalizedCards,
        context: {
          time: context.time || new Date().toLocaleTimeString('ko-KR'),
          place: context.place,
          interaction_partner: context.interactionPartner,
          current_activity: context.currentActivity || null
        },
        interpretations: normalizedInterpretations,
        partnerInfo: partnerInfo || context.interactionPartner || 'Partner'
      };

      const response = await api.post('/api/feedback/request', payload);

      if (response.success && response.data) {
        // app.py 응답 구조 검증
        if (!response.data.confirmationId) {
          throw new Error('확인 요청 ID가 생성되지 않았습니다.');
        }

        return response;
      } else {
        throw new Error(response.error || 'Partner 확인 요청에 실패했습니다.');
      }
    } catch (error) {
      console.error('Partner 확인 요청 실패:', error);
      
      // 특정 에러 처리
      if (error.message.includes('400')) {
        throw new Error('요청 데이터가 올바르지 않습니다. 모든 필수 정보를 확인해주세요.');
      } else if (error.message.includes('404')) {
        throw new Error('사용자를 찾을 수 없습니다.');
      }
      
      throw error;
    }
  },

  // Partner 피드백 제출
  // 흐름명세서 마지막 단계: Partner가 선택한 해석 또는 직접 피드백 제출
  // app.py의 /api/feedback/submit 엔드포인트와 통신
  async submitPartnerFeedback(confirmationId, feedbackData) {
    try {
      // 입력 검증
      if (!confirmationId || !confirmationId.trim()) {
        throw new Error('확인 요청 ID가 필요합니다.');
      }

      if (!feedbackData || typeof feedbackData !== 'object') {
        throw new Error('피드백 데이터가 필요합니다.');
      }

      const { selectedInterpretationIndex, directFeedback } = feedbackData;

      // 피드백 타입 검증 (해석 선택 또는 직접 피드백 중 하나는 필수)
      const hasInterpretationSelection = selectedInterpretationIndex !== null && 
                                        selectedInterpretationIndex !== undefined && 
                                        Number.isInteger(selectedInterpretationIndex) &&
                                        selectedInterpretationIndex >= 0;

      const hasDirectFeedback = directFeedback && 
                               typeof directFeedback === 'string' && 
                               directFeedback.trim().length > 0;

      if (!hasInterpretationSelection && !hasDirectFeedback) {
        throw new Error('해석을 선택하거나 직접 피드백을 입력해주세요.');
      }

      if (hasInterpretationSelection && hasDirectFeedback) {
        throw new Error('해석 선택과 직접 피드백 중 하나만 선택해주세요.');
      }

      // 해석 인덱스 범위 검증
      if (hasInterpretationSelection && (selectedInterpretationIndex < 0 || selectedInterpretationIndex > 2)) {
        throw new Error('해석 인덱스는 0-2 범위여야 합니다.');
      }

      // 직접 피드백 길이 검증
      if (hasDirectFeedback && directFeedback.trim().length < 5) {
        throw new Error('직접 피드백은 5글자 이상이어야 합니다.');
      }

      if (hasDirectFeedback && directFeedback.trim().length > 500) {
        throw new Error('직접 피드백은 500글자를 초과할 수 없습니다.');
      }

      // API 요청 페이로드 구성
      const payload = {
        confirmationId: confirmationId.trim()
      };

      if (hasInterpretationSelection) {
        payload.selectedInterpretationIndex = selectedInterpretationIndex;
      }

      if (hasDirectFeedback) {
        payload.directFeedback = directFeedback.trim();
      }

      const response = await api.post('/api/feedback/submit', payload);

      if (response.success && response.data) {
        // 응답 구조 검증
        if (!response.data.feedbackResult) {
          throw new Error('피드백 처리 결과를 받을 수 없습니다.');
        }

        return response;
      } else {
        throw new Error(response.error || '피드백 제출에 실패했습니다.');
      }
    } catch (error) {
      console.error('피드백 제출 실패:', error);
      
      // 특정 에러 처리
      if (error.message.includes('404')) {
        throw new Error('확인 요청을 찾을 수 없습니다. 페이지를 새로고침해주세요.');
      } else if (error.message.includes('400')) {
        throw new Error('피드백 데이터가 올바르지 않습니다.');
      } else if (error.message.includes('409')) {
        throw new Error('이미 처리된 피드백입니다.');
      }
      
      throw error;
    }
  },

  // 피드백 요청 데이터 검증
  validateFeedbackRequest(requestData) {
    const errors = [];

    if (!requestData || typeof requestData !== 'object') {
      return { valid: false, errors: ['피드백 요청 데이터가 올바르지 않습니다.'] };
    }

    const { userId, cards, context, interpretations } = requestData;

    // 필수 필드 검증
    if (!userId || !userId.trim()) {
      errors.push('사용자 ID가 필요합니다.');
    }

    if (!cards || !Array.isArray(cards) || cards.length === 0) {
      errors.push('선택된 카드가 필요합니다.');
    } else if (cards.length > 4) {
      errors.push('카드는 최대 4개까지만 선택할 수 있습니다.');
    }

    if (!context || typeof context !== 'object') {
      errors.push('대화 컨텍스트가 필요합니다.');
    } else {
      if (!context.place) {
        errors.push('대화 장소가 필요합니다.');
      }
      if (!context.interactionPartner) {
        errors.push('대화 상대가 필요합니다.');
      }
    }

    if (!interpretations || !Array.isArray(interpretations) || interpretations.length === 0) {
      errors.push('해석 정보가 필요합니다.');
    } else if (interpretations.length > 5) {
      errors.push('해석은 최대 5개까지만 가능합니다.');
    }

    return {
      valid: errors.length === 0,
      errors
    };
  },

  // 피드백 데이터 검증
  validateFeedbackData(feedbackData) {
    const errors = [];
    let type = null;

    if (!feedbackData || typeof feedbackData !== 'object') {
      return { valid: false, errors: ['피드백 데이터가 올바르지 않습니다.'], type: null };
    }

    const { selectedInterpretationIndex, directFeedback } = feedbackData;

    const hasInterpretationSelection = selectedInterpretationIndex !== null && 
                                      selectedInterpretationIndex !== undefined;
    const hasDirectFeedback = directFeedback && typeof directFeedback === 'string' && directFeedback.trim();

    // 피드백 타입 결정
    if (hasInterpretationSelection && hasDirectFeedback) {
      errors.push('해석 선택과 직접 피드백 중 하나만 선택해주세요.');
    } else if (!hasInterpretationSelection && !hasDirectFeedback) {
      errors.push('해석을 선택하거나 직접 피드백을 입력해주세요.');
    } else if (hasInterpretationSelection) {
      type = 'interpretation_selected';
      
      // 해석 인덱스 검증
      if (!Number.isInteger(selectedInterpretationIndex) || 
          selectedInterpretationIndex < 0 || 
          selectedInterpretationIndex > 2) {
        errors.push('해석 인덱스는 0-2 범위의 정수여야 합니다.');
      }
    } else if (hasDirectFeedback) {
      type = 'direct_feedback';
      
      // 직접 피드백 검증
      const trimmedFeedback = directFeedback.trim();
      if (trimmedFeedback.length < 5) {
        errors.push('직접 피드백은 5글자 이상이어야 합니다.');
      } else if (trimmedFeedback.length > 500) {
        errors.push('직접 피드백은 500글자를 초과할 수 없습니다.');
      }
    }

    return {
      valid: errors.length === 0,
      errors,
      type
    };
  },

  // 확인 요청 ID 유효성 검증
  isValidConfirmationId(confirmationId) {
    if (!confirmationId || typeof confirmationId !== 'string') {
      return false;
    }

    const trimmedId = confirmationId.trim();
    
    // 기본적인 ID 형식 검증
    const idPattern = /^[a-zA-Z0-9-_]{8,}$/;
    
    return idPattern.test(trimmedId);
  },

  // 피드백 결과 요약 생성
  generateFeedbackSummary(feedbackResult) {
    if (!feedbackResult || typeof feedbackResult !== 'object') {
      return '피드백 결과 없음';
    }

    const finalInterpretation = feedbackResult.selected_interpretation || 
                               feedbackResult.direct_feedback || 
                               feedbackResult.selectedInterpretation ||
                               feedbackResult.directFeedback ||
                               '해석 없음';

    const feedbackType = feedbackResult.feedback_type === 'interpretation_selected' ? 
                        '제시된 해석 선택' : '직접 피드백';

    return `${feedbackType}: "${finalInterpretation}"`;
  }
};