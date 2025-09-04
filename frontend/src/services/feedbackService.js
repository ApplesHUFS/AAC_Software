// src/services/feedbackService.js
import api from './api';

export const feedbackService = {
  // Partner 확인 요청
  async requestPartnerConfirmation(requestData) {
    try {
      const response = await api.post('/api/feedback/request', requestData);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Partner 피드백 제출
  async submitPartnerFeedback(confirmationId, feedbackData) {
    try {
      const payload = {
        confirmationId: confirmationId.trim(),
        ...feedbackData
      };

      const response = await api.post('/api/feedback/submit', payload);
      return response;
    } catch (error) {
      throw error;
    }
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