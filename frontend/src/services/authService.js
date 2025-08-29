// authService.js - 백엔드 검증 의존
import api from './api';

export const authService = {
  // 사용자 회원가입 (백엔드 검증에 의존)
  async register(userData) {
    try {
      const response = await api.post('/api/auth/register', userData);
      return response;
    } catch (error) {
      console.error('회원가입 요청 실패:', error);
      throw error;
    }
  },

  // 사용자 로그인 (백엔드 검증에 의존)
  async login(userId, password) {
    try {
      const payload = {
        userId: userId.trim(),
        password: password
      };

      const response = await api.post('/api/auth/login', payload);
      return response;
    } catch (error) {
      console.error('로그인 요청 실패:', error);
      throw error;
    }
  },

  // 사용자 프로필 조회
  async getProfile(userId) {
    try {
      const response = await api.get(`/api/auth/profile/${userId.trim()}`);
      return response;
    } catch (error) {
      console.error('프로필 조회 실패:', error);
      throw error;
    }
  },

  // 사용자 프로필 업데이트 (백엔드 검증에 의존)
  async updateProfile(userId, updateData) {
    try {
      const response = await api.put(`/api/auth/profile/${userId.trim()}`, updateData);
      return response;
    } catch (error) {
      console.error('프로필 업데이트 실패:', error);
      throw error;
    }
  },

  // 로그아웃 처리
  async logout() {
    try {
      localStorage.removeItem('aac_user');
      localStorage.removeItem('aac_context');
      localStorage.removeItem('aac_selected_cards');
      localStorage.removeItem('aac_current_step');
      console.log('로그아웃 완료');
    } catch (error) {
      console.error('로그아웃 처리 중 오류:', error);
    }
  },

  // 현재 로그인 상태 확인
  getCurrentUser() {
    try {
      const savedUser = localStorage.getItem('aac_user');
      if (savedUser) {
        const userData = JSON.parse(savedUser);
        if (userData.userId && userData.authenticated) {
          return userData;
        }
      }
      return null;
    } catch (error) {
      console.error('사용자 정보 파싱 실패:', error);
      localStorage.removeItem('aac_user');
      return null;
    }
  }
};