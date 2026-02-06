/**
 * 카드 선택 페이지
 */

"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { useContextStore } from "@/stores/context-store";
import { useCards } from "@/hooks/use-cards";
import { Button, Spinner } from "@/components/ui";
import { CardGrid } from "@/components/cards/card-grid";
import { IMAGES } from "@/lib/images";
import { getImageUrl } from "@/lib/utils";

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

  // 중복 호출 방지 플래그
  const isFetching = useRef(false);

  // 초기 카드 로드
  useEffect(() => {
    if (!context) {
      router.push("/main/dashboard");
      return;
    }

    // 이미 카드가 있거나 로딩 중이면 스킵
    if (recommendedCards.length > 0 || isFetching.current) {
      return;
    }

    isFetching.current = true;
    fetchRecommendations().finally(() => {
      isFetching.current = false;
    });
  }, [context, recommendedCards.length, fetchRecommendations, router]);

  // 카드 재추천
  const handleReroll = async () => {
    await fetchRecommendations();
  };

  // 카드 제거
  const handleRemoveCard = (card: (typeof selectedCards)[0]) => {
    setSelectedCards(selectedCards.filter((c) => c.filename !== card.filename));
  };

  if (!context) {
    return null;
  }

  // 로딩 화면
  if (isLoading && recommendedCards.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
        <div className="text-center">
          <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-communicator-100 flex items-center justify-center animate-pulse-soft shadow-app-sm">
            <Image src={IMAGES.message} alt="" width={40} height={40} />
          </div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">
            소통이를 위한 카드를 준비하고 있어요!
          </h2>
          <p className="text-gray-500 mb-6 text-sm">
            소통이의 관심사와 현재 상황을 분석해서
            <br />
            딱 맞는 카드들을 골라드릴게요
          </p>
          <Spinner size="lg" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-36">
      {/* 헤더 */}
      <header className="app-header">
        <div className="max-w-7xl mx-auto px-4 py-3">
          {/* 상단 네비게이션 */}
          <div className="flex justify-between items-center">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.push("/main/dashboard")}
            >
              ← 뒤로
            </Button>
            <div className="text-center">
              <h1 className="font-semibold text-gray-900">카드 선택</h1>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleReroll}
              disabled={isLoading}
            >
              {isLoading ? "로딩..." : "새로고침"}
            </Button>
          </div>

          {/* 상황 정보 태그 */}
          <div className="flex gap-2 mt-3 overflow-x-auto pb-1">
            <div className="tag tag-communicator flex-shrink-0">
              <Image src={IMAGES.place} alt="" width={14} height={14} />
              <span>{context.place}</span>
            </div>
            <div className="tag tag-partner flex-shrink-0">
              <Image src={IMAGES.interactionPartner} alt="" width={14} height={14} />
              <span>{context.interactionPartner}</span>
            </div>
            {context.currentActivity && (
              <div className="tag tag-gray flex-shrink-0">
                <Image src={IMAGES.currentActivity} alt="" width={14} height={14} />
                <span>{context.currentActivity}</span>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* 메인 카드 그리드 */}
      <main className="max-w-7xl mx-auto px-4 py-4">
        {error && (
          <div className="message-error mb-4">
            <Image src={IMAGES.error} alt="" width={18} height={18} />
            <span>{error}</span>
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
          <p className="text-center text-sm text-gray-500 mt-4">
            지금까지 <span className="font-semibold text-communicator-600">{allRecommendedCards.length}개</span>의 카드가 추천되었어요
          </p>
        )}
      </main>

      {/* 하단 고정 선택 바 */}
      <div className="bottom-bar p-4">
        <div className="max-w-lg mx-auto">
          {/* 선택된 카드 미니 프리뷰 */}
          <div className="flex items-center gap-2 mb-3 overflow-x-auto">
            {selectedCards.length > 0 ? (
              selectedCards.map((card) => (
                <div key={card.filename} className="relative flex-shrink-0">
                  <div className="w-12 h-12 rounded-xl bg-gray-100 overflow-hidden shadow-app-sm">
                    <Image
                      src={getImageUrl(card.filename)}
                      alt={card.name}
                      width={48}
                      height={48}
                      className="object-contain p-1"
                    />
                  </div>
                  <button
                    onClick={() => handleRemoveCard(card)}
                    className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full text-white text-xs flex items-center justify-center shadow-app-sm"
                  >
                    ×
                  </button>
                </div>
              ))
            ) : (
              <span className="text-gray-400 text-sm">카드를 선택해주세요</span>
            )}
          </div>

          {/* 소통하기 버튼 */}
          <Button
            fullWidth
            size="lg"
            className="bg-communicator-600 hover:bg-communicator-700"
            disabled={selectedCards.length === 0 || isLoading}
            onClick={proceedToInterpretation}
          >
            이 카드로 소통하기 ({selectedCards.length}개)
          </Button>
        </div>
      </div>
    </div>
  );
}
