/**
 * 컨텍스트 관련 커스텀 훅
 */

"use client";

import { useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth-store";
import { useContextStore } from "@/stores/context-store";
import { useCardStore } from "@/stores/card-store";
import { contextApi } from "@/lib/api/context";

interface CreateContextParams {
  place: string;
  interactionPartner: string;
  currentActivity?: string;
}

export function useContext() {
  const router = useRouter();
  const { user } = useAuthStore();
  const { context, setContext, clearContext } = useContextStore();
  const { clearCards } = useCardStore();

  /**
   * 컨텍스트 생성
   */
  const createContext = useCallback(
    async (params: CreateContextParams) => {
      if (!user) {
        throw new Error("로그인이 필요합니다.");
      }

      const response = await contextApi.create({
        userId: user.userId,
        place: params.place,
        interactionPartner: params.interactionPartner,
        currentActivity: params.currentActivity,
      });

      if (response.success && response.data) {
        setContext(response.data);
        router.push("/main/cards");
      }

      return response;
    },
    [user, setContext, router]
  );

  /**
   * 세션 시작 (새 컨텍스트)
   */
  const startNewSession = useCallback(() => {
    clearContext();
    clearCards();
  }, [clearContext, clearCards]);

  /**
   * 현재 세션 이어하기
   */
  const continueSession = useCallback(() => {
    if (context) {
      router.push("/main/cards");
    }
  }, [context, router]);

  return {
    context,
    createContext,
    startNewSession,
    continueSession,
    clearContext,
  };
}
