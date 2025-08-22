import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const userAPI = {
  createUser: (userData) => api.post('/users', userData),
  getUser: (userId) => api.get(`/users/${userId}`),
  updatePersona: (userId, personaData) => api.put(`/users/${userId}/persona`, personaData),
};

export const contextAPI = {
  createContext: (contextData) => api.post('/contexts', contextData),
  getContext: (contextId) => api.get(`/contexts/${contextId}`),
};

export const cardAPI = {
  getRecommendations: (requestData) =>
    api.post('/cards/recommendations', requestData),
  interpretCards: (selectedCards, userId, contextId) =>
    api.post('/cards/interpret', { selectedCards, userId, contextId }),
  getRecommendationHistoryPage: (contextId, pageNumber) =>
    api.get(`/cards/recommendations/history/${contextId}/page/${pageNumber}`),
  getRecommendationHistorySummary: (contextId) =>
    api.get(`/cards/recommendations/history/${contextId}`),
};

export const feedbackAPI = {
  submitFeedback: (feedbackData) => api.post('/feedback', feedbackData),
  updateMemory: (memoryData) => api.post('/memory/update', memoryData),
};

export default api;
