import api from './api';

export const authService = {
  async register(userData) {
    const payload = {
      userId: userData.userId,
      name: userData.name,
      age: parseInt(userData.age),
      gender: userData.gender,
      disabilityType: userData.disabilityType,
      communicationCharacteristics: userData.communicationCharacteristics,
      interestingTopics: userData.interestingTopics,
      password: userData.password
    };
    
    return await api.post('/api/auth/register', payload);
  },

  async login(userId, password) {
    return await api.post('/api/auth/login', { userId, password });
  },

  async getProfile(userId) {
    return await api.get(`/api/auth/profile/${userId}`);
  },

  async updateProfile(userId, updateData) {
    const payload = {
      name: updateData.name,
      age: updateData.age ? parseInt(updateData.age) : undefined,
      gender: updateData.gender,
      disabilityType: updateData.disabilityType,
      communicationCharacteristics: updateData.communicationCharacteristics,
      interestingTopics: updateData.interestingTopics
    };
    
    // undefined 값들 제거
    Object.keys(payload).forEach(key => payload[key] === undefined && delete payload[key]);
    
    return await api.put(`/api/auth/profile/${userId}`, payload);
  }
};
