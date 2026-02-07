/**
 * 카드 관련 커스텀 훅
 */

"use client";

import { useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth-store";
import { useContextStore } from "@/stores/context-store";
import { useCardStore } from "@/stores/card-store";
import { cardApi } from "@/lib/api/cards";
import { Card } from "@/types/card";
import { CARD_LIMITS } from "@/lib/constants";

export function useCards() {
  const router = useRouter();
  const { user } = useAuthStore();
  const { context } = useContextStore();
  const {
    recommendedCards,
    allRecommendedCards,
    selectedCards,
    interpretations,
    feedbackId,
    isLoading,
    error,
    setRecommendedCards,
    addToAllRecommended,
    setSelectedCards,
    toggleCardSelection,
    setInterpretations,
    setFeedbackId,
    setConfirmationId,
    setLoading,
    setError,
    clearSelection,
    clearInterpretations,
  } = useCardStore();

  /**
   * 카드 추천 요청
   */
  const fetchRecommendations = useCallback(async () => {
    if (!user || !context) {
      setError("사용자 또는 컨텍스트 정보가 없습니다.");
      return null;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await cardApi.getRecommendations(
        user.userId,
        context.contextId
      );

      if (response.success && response.data) {
        const cards = cardApi.normalizeCardData(response.data.cards);
        setRecommendedCards(cards);
        addToAllRecommended(cards);
        return response.data;
      }

      return null;
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "카드 추천 중 오류가 발생했습니다."
      );
      return null;
    } finally {
      setLoading(false);
    }
  }, [
    user,
    context,
    setRecommendedCards,
    addToAllRecommended,
    setLoading,
    setError,
  ]);

  /**
   * 카드 선택 토글
   */
  const handleCardSelect = useCallback(
    (card: Card) => {
      toggleCardSelection(card);
      setError(null);
    },
    [toggleCardSelection, setError]
  );

  /**
   * 카드 선택 검증 및 해석 페이지로 이동
   */
  const proceedToInterpretation = useCallback(async () => {
    if (selectedCards.length === 0) {
      setError(`최소 ${CARD_LIMITS.MIN_SELECTION}개의 카드를 선택해주세요.`);
      return false;
    }

    setLoading(true);
    setError(null);

    try {
      const validation = await cardApi.validateSelection(
        selectedCards,
        allRecommendedCards
      );

      if (validation.success && validation.data?.valid) {
        clearInterpretations();
        router.push("/main/interpretation");
        return true;
      }

      setError("선택한 카드가 유효하지 않습니다.");
      return false;
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "카드 검증 중 오류가 발생했습니다."
      );
      return false;
    } finally {
      setLoading(false);
    }
  }, [
    selectedCards,
    allRecommendedCards,
    router,
    clearInterpretations,
    setLoading,
    setError,
  ]);

  /**
   * 카드 해석 요청
   */
  const interpretCards = useCallback(async () => {
    if (!user || !context || selectedCards.length === 0) {
      setError("해석할 카드가 없습니다.");
      return null;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await cardApi.interpretCards(
        user.userId,
        context.contextId,
        selectedCards.map((c) => c.filename)
      );

      if (response.success && response.data) {
        setInterpretations(response.data.interpretations);
        setFeedbackId(response.data.feedbackId);
        return response.data;
      }

      return null;
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "카드 해석 중 오류가 발생했습니다."
      );
      return null;
    } finally {
      setLoading(false);
    }
  }, [
    user,
    context,
    selectedCards,
    setInterpretations,
    setFeedbackId,
    setLoading,
    setError,
  ]);

  return {
    recommendedCards,
    allRecommendedCards,
    selectedCards,
    interpretations,
    feedbackId,
    isLoading,
    error,
    fetchRecommendations,
    handleCardSelect,
    proceedToInterpretation,
    interpretCards,
    setSelectedCards,
    clearSelection,
    clearInterpretations,
    setError,
    setConfirmationId,
  };
}
