import api from './api';

export const feedbackService = {
  async requestPartnerConfirmation(requestData) {
    const payload = {
      userId: requestData.userId,
      cards: requestData.cards,
      context: requestData.context,
      interpretations: requestData.interpretations,
      partnerInfo: requestData.partnerInfo || 'Partner'
    };
    
    return await api.post('/api/feedback/request', payload);
  },

  async submitPartnerFeedback(confirmationId, feedbackData) {
    const payload = {
      confirmationId,
      selectedInterpretationIndex: feedbackData.selectedInterpretationIndex,
      directFeedback: feedbackData.directFeedback
    };
    
    return await api.post('/api/feedback/submit', payload);
  }
};