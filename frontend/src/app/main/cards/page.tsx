/**
 * 카드 선택 페이지
 */

"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useContextStore } from "@/stores/context-store";
import { useCards } from "@/hooks/use-cards";
import { Button, Spinner } from "@/components/ui";
import { CardGrid } from "@/components/cards/card-grid";
import { SelectedCardsDisplay } from "@/components/cards/selected-cards-display";

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
    setError,
  } = useCards();

  // 초기 카드 로드
  useEffect(() => {
    if (!context) {
      router.push("/main/dashboard");
      return;
    }

    if (recommendedCards.length === 0) {
      fetchRecommendations();
    }
  }, [context, recommendedCards.length, fetchRecommendations, router]);

  // 카드 재추천
  const handleReroll = async () => {
    await fetchRecommendations();
  };

  // 카드 제거
  const handleRemoveCard = (card: typeof selectedCards[0]) => {
    setSelectedCards(selectedCards.filter((c) => c.filename !== card.filename));
  };

  if (!context) {
    return null;
  }

  if (isLoading && recommendedCards.length === 0) {
    return (
      <div className="min-h-screen bg-communicator-50 flex flex-col items-center justify-center p-4">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          소통이를 위한 카드를 준비하고 있어요!
        </h2>
        <p className="text-gray-600 mb-6 text-center">
          소통이의 관심사와 현재 상황을 분석해서
          <br />
          딱 맞는 카드들을 골라드릴게요
        </p>
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-communicator-50">
      {/* 헤더 */}
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div>
              <span className="text-communicator-600 font-medium text-sm">
                카드 선택
              </span>
              <h1 className="text-lg font-semibold text-gray-900">
                어떤 카드로 소통할까요?
              </h1>
            </div>
            <Button
              variant="outline"
              onClick={() => router.push("/main/dashboard")}
            >
              대시보드로
            </Button>
          </div>
          {/* 상황 정보 */}
          <div className="flex gap-4 mt-2 text-sm text-gray-600">
            <span>장소: {context.place}</span>
            <span>대화상대: {context.interactionPartner}</span>
            {context.currentActivity && (
              <span>활동: {context.currentActivity}</span>
            )}
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6 flex gap-6">
        {/* 사이드바 */}
        <aside className="w-64 flex-shrink-0 space-y-4">
          <SelectedCardsDisplay
            selectedCards={selectedCards}
            onRemoveCard={handleRemoveCard}
            maxCards={4}
          />

          <div className="space-y-2">
            <Button
              variant="outline"
              className="w-full"
              onClick={handleReroll}
              disabled={isLoading}
            >
              {isLoading ? "새 카드 찾는 중..." : "다른 카드 보기"}
            </Button>

            <Button
              className="w-full bg-communicator-600 hover:bg-communicator-700"
              onClick={proceedToInterpretation}
              disabled={selectedCards.length === 0 || isLoading}
            >
              이 카드로 소통하기 ({selectedCards.length}개)
            </Button>
          </div>

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          {allRecommendedCards.length > 0 && (
            <div className="p-3 bg-communicator-50 border border-communicator-200 rounded-lg text-sm text-communicator-700">
              지금까지 <strong>{allRecommendedCards.length}개</strong>의 카드가
              추천되었어요!
            </div>
          )}
        </aside>

        {/* 메인 영역 */}
        <main className="flex-1">
          <CardGrid
            cards={recommendedCards}
            selectedCards={selectedCards}
            onCardSelect={handleCardSelect}
            maxSelection={4}
            disabled={isLoading}
          />
        </main>
      </div>
    </div>
  );
}
