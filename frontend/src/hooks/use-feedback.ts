/**
 * 피드백 관련 커스텀 훅
 */

"use client";

import { useCallback, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth-store";
import { useContextStore } from "@/stores/context-store";
import { useCardStore } from "@/stores/card-store";
import { feedbackApi } from "@/lib/api/feedback";
import { ContextSummary } from "@/types/feedback";

export function useFeedback() {
  const router = useRouter();
  const { user } = useAuthStore();
  const { context, clearContext } = useContextStore();
  const { selectedCards, interpretations, confirmationId, setConfirmationId, clearCards } =
    useCardStore();

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * 피드백 요청
   */
  const requestFeedback = useCallback(
    async (partnerInfo: string) => {
      if (!user || !context || interpretations.length === 0) {
        setError("피드백 요청에 필요한 정보가 없습니다.");
        return null;
      }

      setIsLoading(true);
      setError(null);

      try {
        const contextSummary: ContextSummary = {
          time: context.time,
          place: context.place,
          interactionPartner: context.interactionPartner,
          currentActivity: context.currentActivity,
        };

        const response = await feedbackApi.requestFeedback(
          user.userId,
          selectedCards.map((c) => c.filename),
          contextSummary,
          interpretations.map((i) => i.text),
          partnerInfo
        );

        if (response.success && response.data) {
          setConfirmationId(response.data.confirmationId);
          return response.data;
        }

        return null;
      } catch (err) {
        setError(err instanceof Error ? err.message : "피드백 요청 중 오류가 발생했습니다.");
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    [user, context, selectedCards, interpretations, setConfirmationId]
  );

  /**
   * 해석 선택으로 피드백 제출
   */
  const submitWithSelection = useCallback(
    async (selectedIndex: number) => {
      if (!confirmationId) {
        setError("확인 ID가 없습니다.");
        return null;
      }

      setIsLoading(true);
      setError(null);

      try {
        const response = await feedbackApi.submitWithSelection(
          confirmationId,
          selectedIndex
        );

        if (response.success) {
          clearCards();
          clearContext();
          router.push("/main/dashboard");
        }

        return response;
      } catch (err) {
        setError(err instanceof Error ? err.message : "피드백 제출 중 오류가 발생했습니다.");
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    [confirmationId, clearCards, clearContext, router]
  );

  /**
   * 직접 입력으로 피드백 제출
   */
  const submitWithDirectFeedback = useCallback(
    async (directFeedback: string) => {
      if (!confirmationId) {
        setError("확인 ID가 없습니다.");
        return null;
      }

      setIsLoading(true);
      setError(null);

      try {
        const response = await feedbackApi.submitWithDirectFeedback(
          confirmationId,
          directFeedback
        );

        if (response.success) {
          clearCards();
          clearContext();
          router.push("/main/dashboard");
        }

        return response;
      } catch (err) {
        setError(err instanceof Error ? err.message : "피드백 제출 중 오류가 발생했습니다.");
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    [confirmationId, clearCards, clearContext, router]
  );

  return {
    confirmationId,
    isLoading,
    error,
    requestFeedback,
    submitWithSelection,
    submitWithDirectFeedback,
    setError,
  };
}
