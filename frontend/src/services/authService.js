// src/services/authService.js
import api from './api';

export const authService = {
  // 사용자 회원가입
  async register(userData) {
    try {
      const response = await api.post('/api/auth/register', userData);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // 사용자 로그인
  async login(userId, password) {
    try {
      const payload = {
        userId: userId.trim(),
        password: password
      };

      const response = await api.post('/api/auth/login', payload);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // 사용자 프로필 조회
  async getProfile(userId) {
    try {
      const response = await api.get(`/api/auth/profile/${userId.trim()}`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // 사용자 프로필 업데이트
  async updateProfile(userId, updateData) {
    try {
      const response = await api.put(`/api/auth/profile/${userId.trim()}`, updateData);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // 로그아웃 처리
  async logout() {
    try {
      sessionStorage.removeItem('aac_user');
      sessionStorage.removeItem('aac_context');
      sessionStorage.removeItem('aac_selected_cards');
      sessionStorage.removeItem('aac_current_step');
      console.log('로그아웃 완료');
    } catch (error) {
      console.error('로그아웃 처리 중 오류:', error);
    }
  },

  // 현재 로그인 상태 확인
  getCurrentUser() {
    try {
      const savedUser = sessionStorage.getItem('aac_user');
      if (savedUser) {
        const userData = JSON.parse(savedUser);
        if (userData.userId && userData.authenticated) {
          return userData;
        }
      }
      return null;
    } catch (error) {
      console.error('사용자 정보 파싱 실패:', error);
      sessionStorage.removeItem('aac_user');
      return null;
    }
  }
};