/**
 * 카드 선택 페이지 - 미니멀 UI
 */

"use client";

import { useCallback, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useContextStore } from "@/stores/context-store";
import { useCards } from "@/hooks/use-cards";
import { CardGrid } from "@/components/cards/card-grid";
import { CardsPageHeader } from "@/components/cards/cards-page-header";
import { CardsLoadingScreen } from "@/components/cards/cards-loading-screen";
import { SelectedCardsBar } from "@/components/cards/selected-cards-bar";
import { ErrorBox } from "@/components/ui/error-box";

export default function CardsPage() {
  const router = useRouter();
  const { context } = useContextStore();
  const {
    recommendedCards,
    allRecommendedCards,
    selectedCards,
    isLoading,
    error,
    fetchRecommendations,
    handleCardSelect,
    proceedToInterpretation,
    setSelectedCards,
  } = useCards();

  const isFetching = useRef(false);

  useEffect(() => {
    if (!context) {
      router.push("/main/dashboard");
      return;
    }

    if (recommendedCards.length > 0 || isFetching.current) {
      return;
    }

    isFetching.current = true;
    fetchRecommendations().finally(() => {
      isFetching.current = false;
    });
  }, [context, recommendedCards.length, fetchRecommendations, router]);

  const handleReroll = useCallback(async () => {
    await fetchRecommendations();
  }, [fetchRecommendations]);

  const handleRemoveCard = useCallback(
    (card: (typeof selectedCards)[0]) => {
      setSelectedCards(selectedCards.filter((c) => c.filename !== card.filename));
    },
    [selectedCards, setSelectedCards]
  );

  if (!context) {
    return null;
  }

  // 로딩 화면
  if (isLoading && recommendedCards.length === 0) {
    return <CardsLoadingScreen />;
  }

  return (
    <div className="min-h-screen bg-slate-50 pb-44">
      {/* 헤더 */}
      <CardsPageHeader
        context={context}
        isLoading={isLoading}
        onBack={() => router.push("/main/dashboard")}
        onRefresh={handleReroll}
      />

      {/* 메인 카드 그리드 */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {error && <ErrorBox message={error} className="mb-6" />}

        <CardGrid
          cards={recommendedCards}
          selectedCards={selectedCards}
          onCardSelect={handleCardSelect}
          maxSelection={4}
          disabled={isLoading}
        />

        {allRecommendedCards.length > 0 && (
          <p className="text-center text-sm text-gray-500 mt-6">
            지금까지 <span className="font-semibold text-violet-600">{allRecommendedCards.length}개</span>의 카드가 추천되었어요
          </p>
        )}
      </main>

      {/* 하단 고정 선택 바 */}
      <SelectedCardsBar
        selectedCards={selectedCards}
        isLoading={isLoading}
        onRemoveCard={handleRemoveCard}
        onProceed={proceedToInterpretation}
      />
    </div>
  );
}
