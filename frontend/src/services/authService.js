import api from './api';

/**
 * 인증 관련 서비스
 * app.py의 인증 API와 통신하여 사용자 관리 기능 제공
 */
export const authService = {
  /**
   * 사용자 회원가입
   * app.py의 /api/auth/register 엔드포인트와 통신
   * @param {Object} userData - 사용자 등록 정보
   * @returns {Promise<Object>} 등록 결과
   */
  async register(userData) {
    try {
      // app.py 요구사항에 맞게 데이터 구조화
      const payload = {
        userId: userData.userId,
        name: userData.name,
        age: parseInt(userData.age),
        gender: userData.gender,
        disabilityType: userData.disabilityType,
        communicationCharacteristics: userData.communicationCharacteristics,
        interestingTopics: Array.isArray(userData.interestingTopics) ? userData.interestingTopics : [],
        password: userData.password
      };

      // 데이터 유효성 검증
      if (!payload.userId || payload.userId.length < 3) {
        throw new Error('사용자 ID는 3글자 이상이어야 합니다.');
      }

      if (!payload.name || payload.name.length < 1) {
        throw new Error('이름을 입력해주세요.');
      }

      if (!payload.age || payload.age < 1 || payload.age > 100) {
        throw new Error('유효한 나이를 입력해주세요.');
      }

      if (!payload.gender) {
        throw new Error('성별을 선택해주세요.');
      }

      if (!payload.disabilityType) {
        throw new Error('장애 유형을 선택해주세요.');
      }

      if (!payload.communicationCharacteristics || payload.communicationCharacteristics.length < 5) {
        throw new Error('의사소통 특징을 5글자 이상 입력해주세요.');
      }

      if (!payload.interestingTopics || payload.interestingTopics.length === 0) {
        throw new Error('관심 주제를 최소 1개 이상 입력해주세요.');
      }

      if (!payload.password || payload.password.length < 4) {
        throw new Error('비밀번호는 4글자 이상이어야 합니다.');
      }

      const response = await api.post('/api/auth/register', payload);

      if (response.success) {
        return response;
      } else {
        throw new Error(response.error || '회원가입에 실패했습니다.');
      }
    } catch (error) {
      console.error('회원가입 요청 실패:', error);
      throw error;
    }
  },

  /**
   * 사용자 로그인
   * app.py의 /api/auth/login 엔드포인트와 통신
   * @param {string} userId - 사용자 ID
   * @param {string} password - 비밀번호
   * @returns {Promise<Object>} 로그인 결과 (사용자 정보 포함)
   */
  async login(userId, password) {
    try {
      // 입력 검증
      if (!userId || !userId.trim()) {
        throw new Error('사용자 ID를 입력해주세요.');
      }

      if (!password) {
        throw new Error('비밀번호를 입력해주세요.');
      }

      const payload = {
        userId: userId.trim(),
        password: password
      };

      const response = await api.post('/api/auth/login', payload);

      if (response.success && response.data) {
        // app.py 응답 구조: { success: true, data: { userId, authenticated, user: {...} } }
        if (response.data.authenticated) {
          return response;
        } else {
          throw new Error('인증에 실패했습니다.');
        }
      } else {
        throw new Error(response.error || '로그인에 실패했습니다.');
      }
    } catch (error) {
      console.error('로그인 요청 실패:', error);
      
      // 특정 에러 메시지 처리
      if (error.message.includes('401') || error.message.includes('인증')) {
        throw new Error('사용자 ID 또는 비밀번호가 올바르지 않습니다.');
      } else if (error.message.includes('404')) {
        throw new Error('존재하지 않는 사용자입니다.');
      } else if (error.message.includes('429')) {
        throw new Error('로그인 시도가 너무 많습니다. 잠시 후 다시 시도해주세요.');
      }
      
      throw error;
    }
  },

  /**
   * 사용자 프로필 조회
   * app.py의 /api/auth/profile/{userId} 엔드포인트와 통신
   * @param {string} userId - 사용자 ID
   * @returns {Promise<Object>} 사용자 프로필 정보
   */
  async getProfile(userId) {
    try {
      if (!userId || !userId.trim()) {
        throw new Error('사용자 ID가 필요합니다.');
      }

      const response = await api.get(`/api/auth/profile/${userId.trim()}`);

      if (response.success && response.data) {
        return response;
      } else {
        throw new Error(response.error || '프로필 조회에 실패했습니다.');
      }
    } catch (error) {
      console.error('프로필 조회 실패:', error);
      
      if (error.message.includes('404')) {
        throw new Error('사용자를 찾을 수 없습니다.');
      } else if (error.message.includes('403')) {
        throw new Error('프로필에 접근할 권한이 없습니다.');
      }
      
      throw error;
    }
  },

  /**
   * 사용자 프로필 업데이트
   * app.py의 /api/auth/profile/{userId} PUT 엔드포인트와 통신
   * @param {string} userId - 사용자 ID
   * @param {Object} updateData - 업데이트할 데이터
   * @returns {Promise<Object>} 업데이트 결과
   */
  async updateProfile(userId, updateData) {
    try {
      if (!userId || !userId.trim()) {
        throw new Error('사용자 ID가 필요합니다.');
      }

      if (!updateData || Object.keys(updateData).length === 0) {
        throw new Error('업데이트할 데이터가 없습니다.');
      }

      // app.py 요구사항에 맞게 camelCase를 snake_case로 변환하지 않음
      // app.py에서 변환 처리함
      const payload = {
        name: updateData.name,
        age: updateData.age ? parseInt(updateData.age) : undefined,
        gender: updateData.gender,
        disabilityType: updateData.disabilityType,
        communicationCharacteristics: updateData.communicationCharacteristics,
        interestingTopics: updateData.interestingTopics
      };

      // undefined 값들 제거
      Object.keys(payload).forEach(key => {
        if (payload[key] === undefined) {
          delete payload[key];
        }
      });

      const response = await api.put(`/api/auth/profile/${userId.trim()}`, payload);

      if (response.success) {
        return response;
      } else {
        throw new Error(response.error || '프로필 업데이트에 실패했습니다.');
      }
    } catch (error) {
      console.error('프로필 업데이트 실패:', error);
      
      if (error.message.includes('404')) {
        throw new Error('사용자를 찾을 수 없습니다.');
      } else if (error.message.includes('403')) {
        throw new Error('프로필을 수정할 권한이 없습니다.');
      } else if (error.message.includes('400')) {
        throw new Error('입력 데이터가 올바르지 않습니다.');
      }
      
      throw error;
    }
  },

  /**
   * 비밀번호 변경
   * TODO: app.py에 해당 엔드포인트 구현 필요
   * @param {string} userId - 사용자 ID
   * @param {string} currentPassword - 현재 비밀번호
   * @param {string} newPassword - 새 비밀번호
   * @returns {Promise<Object>} 비밀번호 변경 결과
   */
  async changePassword(userId, currentPassword, newPassword) {
    try {
      // 입력 검증
      if (!userId || !userId.trim()) {
        throw new Error('사용자 ID가 필요합니다.');
      }

      if (!currentPassword) {
        throw new Error('현재 비밀번호를 입력해주세요.');
      }

      if (!newPassword) {
        throw new Error('새 비밀번호를 입력해주세요.');
      }

      if (newPassword.length < 4) {
        throw new Error('새 비밀번호는 4글자 이상이어야 합니다.');
      }

      if (currentPassword === newPassword) {
        throw new Error('현재 비밀번호와 새 비밀번호가 같습니다.');
      }

      const payload = {
        currentPassword,
        newPassword
      };

      // 현재 app.py에 해당 엔드포인트가 없으므로 임시로 에러 반환
      throw new Error('비밀번호 변경 기능은 아직 구현되지 않았습니다.');

      // TODO: app.py에 구현 후 주석 해제
      // const response = await api.post(`/api/auth/change-password/${userId.trim()}`, payload);
      // 
      // if (response.success) {
      //   return response;
      // } else {
      //   throw new Error(response.error || '비밀번호 변경에 실패했습니다.');
      // }
    } catch (error) {
      console.error('비밀번호 변경 실패:', error);
      throw error;
    }
  },

  /**
   * 로그아웃 처리
   * 클라이언트 사이드 로그아웃 (토큰 삭제 등)
   * @returns {Promise<void>}
   */
  async logout() {
    try {
      // 로컬 스토리지에서 사용자 정보 제거
      localStorage.removeItem('aac_user');
      localStorage.removeItem('aac_context');
      localStorage.removeItem('aac_selected_cards');
      localStorage.removeItem('aac_current_step');

      // 세션 스토리지도 정리 (있다면)
      sessionStorage.clear();

      console.log('로그아웃 완료');
    } catch (error) {
      console.error('로그아웃 처리 중 오류:', error);
      // 로그아웃은 실패해도 크리티컬하지 않으므로 에러를 던지지 않음
    }
  },

  /**
   * 현재 로그인 상태 확인
   * @returns {Object|null} 저장된 사용자 정보 또는 null
   */
  getCurrentUser() {
    try {
      const savedUser = localStorage.getItem('aac_user');
      if (savedUser) {
        const userData = JSON.parse(savedUser);
        // 기본적인 구조 검증
        if (userData.userId && userData.authenticated) {
          return userData;
        }
      }
      return null;
    } catch (error) {
      console.error('사용자 정보 파싱 실패:', error);
      // 손상된 데이터 제거
      localStorage.removeItem('aac_user');
      return null;
    }
  },

  /**
   * 사용자 세션 유효성 검증
   * @param {Object} userData - 검증할 사용자 데이터
   * @returns {boolean} 세션 유효성
   */
  validateUserSession(userData) {
    if (!userData) return false;

    // 필수 필드 검증
    const requiredFields = ['userId', 'name', 'authenticated'];
    for (const field of requiredFields) {
      if (!userData[field]) {
        return false;
      }
    }

    // 인증 상태 검증
    if (userData.authenticated !== true) {
      return false;
    }

    return true;
  }
};