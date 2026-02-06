/**
 * 카드 상태 관리 (Zustand)
 */

import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { Card, Interpretation } from "@/types/card";

interface CardState {
  // 추천된 카드
  recommendedCards: Card[];
  // 모든 추천 카드 (히스토리 포함)
  allRecommendedCards: Card[];
  // 선택된 카드
  selectedCards: Card[];
  // 해석 결과
  interpretations: Interpretation[];
  // 피드백 ID
  feedbackId: number | null;
  // 확인 ID
  confirmationId: string | null;

  // Actions
  setRecommendedCards: (cards: Card[]) => void;
  addToAllRecommended: (cards: Card[]) => void;
  setSelectedCards: (cards: Card[]) => void;
  toggleCardSelection: (card: Card) => void;
  setInterpretations: (interpretations: Interpretation[]) => void;
  setFeedbackId: (id: number) => void;
  setConfirmationId: (id: string) => void;
  clearCards: () => void;
  clearSelection: () => void;
  clearInterpretations: () => void;
}

export const useCardStore = create<CardState>()(
  persist(
    (set, get) => ({
      recommendedCards: [],
      allRecommendedCards: [],
      selectedCards: [],
      interpretations: [],
      feedbackId: null,
      confirmationId: null,

      setRecommendedCards: (cards) => set({ recommendedCards: cards }),

      addToAllRecommended: (cards) =>
        set((state) => {
          const existingFilenames = new Set(
            state.allRecommendedCards.map((c) => c.filename)
          );
          const newCards = cards.filter(
            (c) => !existingFilenames.has(c.filename)
          );
          return {
            allRecommendedCards: [...state.allRecommendedCards, ...newCards],
          };
        }),

      setSelectedCards: (cards) => set({ selectedCards: cards }),

      toggleCardSelection: (card) =>
        set((state) => {
          const isSelected = state.selectedCards.some(
            (c) => c.filename === card.filename
          );

          if (isSelected) {
            return {
              selectedCards: state.selectedCards.filter(
                (c) => c.filename !== card.filename
              ),
            };
          }

          if (state.selectedCards.length >= 4) {
            return state;
          }

          return {
            selectedCards: [...state.selectedCards, card],
          };
        }),

      setInterpretations: (interpretations) => set({ interpretations }),

      setFeedbackId: (id) => set({ feedbackId: id }),

      setConfirmationId: (id) => set({ confirmationId: id }),

      clearCards: () =>
        set({
          recommendedCards: [],
          allRecommendedCards: [],
          selectedCards: [],
          interpretations: [],
          feedbackId: null,
          confirmationId: null,
        }),

      clearSelection: () => set({ selectedCards: [] }),

      clearInterpretations: () =>
        set({
          interpretations: [],
          feedbackId: null,
          confirmationId: null,
        }),
    }),
    {
      name: "aac-card-storage",
      storage: createJSONStorage(() => sessionStorage),
    }
  )
);
