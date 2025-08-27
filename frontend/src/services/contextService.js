import api from './api';

export const contextService = {
  async createContext(contextData) {
    const payload = {
      userId: contextData.userId,
      place: contextData.place,
      interactionPartner: contextData.interactionPartner,
      currentActivity: contextData.currentActivity || ''
    };
    
    return await api.post('/api/context', payload);
  },

  async getContext(contextId) {
    return await api.get(`/api/context/${contextId}`);
  }
};
