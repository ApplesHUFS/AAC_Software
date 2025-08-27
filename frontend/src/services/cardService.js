import api from './api';

export const cardService = {
  async getRecommendations(userId, contextId) {
    return await api.post('/api/cards/recommend', { userId, contextId });
  },

  async validateSelection(selectedCards, availableOptions) {
    return await api.post('/api/cards/validate', { selectedCards, availableOptions });
  },

  async interpretCards(userId, selectedCards, contextId) {
    return await api.post('/api/cards/interpret', { 
      userId, 
      selectedCards, 
      contextId 
    });
  },

  async getHistorySummary(contextId) {
    return await api.get(`/api/cards/history/${contextId}`);
  },

  async getHistoryPage(contextId, pageNumber) {
    return await api.get(`/api/cards/history/${contextId}/page/${pageNumber}`);
  }
};
