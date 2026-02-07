/**
 * 카드 선택 페이지 - 미니멀 UI
 */

"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { useContextStore } from "@/stores/context-store";
import { useCards } from "@/hooks/use-cards";
import { CardGrid } from "@/components/cards/card-grid";
import { getImageUrl, cn } from "@/lib/utils";
import { LayoutGridIcon, MapPinIcon, UsersIcon, ActivityIcon, AlertCircleIcon } from "@/components/ui/icons";

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

  const handleReroll = async () => {
    await fetchRecommendations();
  };

  const handleRemoveCard = (card: (typeof selectedCards)[0]) => {
    setSelectedCards(selectedCards.filter((c) => c.filename !== card.filename));
  };

  if (!context) {
    return null;
  }

  // 로딩 화면
  if (isLoading && recommendedCards.length === 0) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-4">
        <div className="text-center">
          {/* 아이콘 */}
          <div className="relative w-24 h-24 mx-auto mb-8">
            <div className="absolute inset-0 bg-violet-200 rounded-3xl animate-pulse opacity-40" />
            <div className="absolute inset-2 bg-violet-100 rounded-2xl flex items-center justify-center shadow-lg">
              <div className="animate-bounce text-violet-600">
                <LayoutGridIcon className="w-10 h-10" />
              </div>
            </div>
          </div>

          {/* 텍스트 */}
          <h2 className="text-2xl font-bold text-gray-900 mb-3 animate-fade-in">
            소통이를 위한 카드를 준비하고 있어요
          </h2>
          <p className="text-gray-500 mb-8 text-sm leading-relaxed animate-fade-in animation-delay-100">
            소통이의 관심사와 현재 상황을 분석해서
            <br />
            딱 맞는 카드들을 골라드릴게요
          </p>

          {/* 로딩 도트 */}
          <div className="flex justify-center gap-2">
            <div className="w-3 h-3 bg-violet-600 rounded-full animate-bounce [animation-delay:-0.3s]" />
            <div className="w-3 h-3 bg-violet-500 rounded-full animate-bounce [animation-delay:-0.15s]" />
            <div className="w-3 h-3 bg-violet-400 rounded-full animate-bounce" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 pb-44">
      {/* 헤더 */}
      <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-xl border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          {/* 상단 네비게이션 */}
          <div className="flex justify-between items-center">
            <button
              onClick={() => router.push("/main/dashboard")}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors px-3 py-2 rounded-xl hover:bg-gray-100"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <span className="font-medium">뒤로</span>
            </button>

            <div className="text-center">
              <h1 className="text-lg font-bold text-gray-900">
                카드 선택
              </h1>
            </div>

            <button
              onClick={handleReroll}
              disabled={isLoading}
              className={cn(
                "flex items-center gap-2 px-4 py-2 rounded-xl transition-all",
                "bg-violet-50 hover:bg-violet-100",
                "text-violet-700 font-medium border border-violet-200",
                isLoading && "opacity-50 cursor-not-allowed"
              )}
            >
              <svg className={cn("w-4 h-4", isLoading && "animate-spin")} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <span>{isLoading ? "로딩..." : "새로고침"}</span>
            </button>
          </div>

          {/* 상황 정보 태그 */}
          <div className="flex gap-3 mt-4 overflow-x-auto pb-1 scrollbar-hide">
            <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-full border border-violet-200 shadow-sm flex-shrink-0">
              <div className="w-6 h-6 bg-violet-100 rounded-full flex items-center justify-center text-violet-600">
                <MapPinIcon className="w-3.5 h-3.5" />
              </div>
              <span className="text-sm font-medium text-violet-700">{context.place}</span>
            </div>

            <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-full border border-pink-200 shadow-sm flex-shrink-0">
              <div className="w-6 h-6 bg-pink-100 rounded-full flex items-center justify-center text-pink-600">
                <UsersIcon className="w-3.5 h-3.5" />
              </div>
              <span className="text-sm font-medium text-pink-700">{context.interactionPartner}</span>
            </div>

            {context.currentActivity && (
              <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-full border border-gray-200 shadow-sm flex-shrink-0">
                <div className="w-6 h-6 bg-gray-100 rounded-full flex items-center justify-center text-gray-600">
                  <ActivityIcon className="w-3.5 h-3.5" />
                </div>
                <span className="text-sm font-medium text-gray-700">{context.currentActivity}</span>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* 메인 카드 그리드 */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {error && (
          <div className="flex items-center gap-3 p-4 mb-6 bg-red-50/80 backdrop-blur-sm border border-red-100 rounded-2xl">
            <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0 text-red-600">
              <AlertCircleIcon className="w-[18px] h-[18px]" />
            </div>
            <span className="text-red-700 text-sm font-medium">{error}</span>
          </div>
        )}

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
      <div className="fixed bottom-0 left-0 right-0 z-50 bg-white/90 backdrop-blur-xl border-t border-gray-200 shadow-2xl">
        <div className="max-w-lg mx-auto p-4">
          {/* 선택된 카드 미니 프리뷰 */}
          <div className="flex items-center gap-3 mb-4 overflow-x-auto pb-1 scrollbar-hide">
            {selectedCards.length > 0 ? (
              selectedCards.map((card, index) => (
                <div
                  key={card.filename}
                  className="relative flex-shrink-0 animate-scale-in"
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  <div className="w-14 h-14 rounded-2xl bg-violet-50 overflow-hidden shadow-lg border-2 border-white">
                    <Image
                      src={getImageUrl(card.filename)}
                      alt={card.name}
                      width={56}
                      height={56}
                      className="object-contain p-1.5"
                    />
                  </div>
                  {/* X 버튼 */}
                  <button
                    onClick={() => handleRemoveCard(card)}
                    className="absolute -top-1.5 -right-1.5 w-6 h-6 bg-red-500 hover:bg-red-600 rounded-full text-white text-xs flex items-center justify-center shadow-lg hover:scale-110 transition-transform"
                    aria-label={`${card.name} 제거`}
                  >
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              ))
            ) : (
              <div className="flex items-center gap-2 text-gray-400 py-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
                <span className="text-sm">카드를 선택해주세요</span>
              </div>
            )}
          </div>

          {/* 소통하기 버튼 */}
          <button
            onClick={proceedToInterpretation}
            disabled={selectedCards.length === 0 || isLoading}
            className={cn(
              "w-full py-4 rounded-2xl font-bold text-white text-lg transition-all",
              "bg-violet-600 hover:bg-violet-700",
              "shadow-lg shadow-violet-500/25",
              "hover:shadow-xl hover:shadow-violet-500/30 hover:scale-[1.02]",
              "active:scale-[0.98]",
              "disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 disabled:shadow-none"
            )}
          >
            <span className="flex items-center justify-center gap-2">
              이 카드로 소통하기
              {selectedCards.length > 0 && (
                <span className="px-2.5 py-0.5 bg-white/20 rounded-full text-sm">
                  {selectedCards.length}개
                </span>
              )}
            </span>
          </button>
        </div>
      </div>
    </div>
  );
}
