// src/services/contextService.js
import api from "./api";

export const contextService = {
  // 새로운 대화 컨텍스트 생성
  async createContext(contextData) {
    try {
      const response = await api.post("/api/context", contextData);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // 기존 컨텍스트 조회
  async getContext(contextId) {
    try {
      const response = await api.get(`/api/context/${contextId.trim()}`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // 컨텍스트 요약 정보 생성
  generateContextSummary(contextData) {
    if (!contextData || typeof contextData !== "object") {
      return "알 수 없는 상황";
    }

    const { place, interactionPartner, currentActivity } = contextData;
    let summary = "";

    if (place) {
      summary += place;
    }

    if (interactionPartner) {
      summary += summary
        ? `에서 ${interactionPartner}와`
        : `${interactionPartner}와`;
    }

    if (currentActivity) {
      summary += ` ${currentActivity} 중`;
    }

    return summary || "대화 상황";
  },
};
