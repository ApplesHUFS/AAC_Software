/**
 * 해석 페이지 - AI 카드 해석 결과 표시
 */

"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { useContextStore } from "@/stores/context-store";
import { useCards } from "@/hooks/use-cards";
import { useFeedback } from "@/hooks/use-feedback";
import { Button } from "@/components/ui";
import { InterpretationDisplay } from "@/components/interpretation/interpretation-display";
import { getImageUrl } from "@/lib/utils";
import { SparklesIcon, CardsIcon, AlertCircleIcon } from "@/components/ui/icons";

export default function InterpretationPage() {
  const router = useRouter();
  const { context } = useContextStore();
  const { selectedCards, interpretations, interpretCards } = useCards();
  const { requestFeedback, submitWithSelection, submitWithDirectFeedback, isLoading } =
    useFeedback();

  const [isInterpreting, setIsInterpreting] = useState(false);
  const [error, setError] = useState("");

  // 중복 호출 방지 플래그
  const isInterpreted = useRef(false);

  // 초기 해석 요청
  useEffect(() => {
    if (!context || selectedCards.length === 0) {
      router.push("/main/dashboard");
      return;
    }

    // 이미 해석이 있거나 호출 중이면 스킵
    if (interpretations.length > 0 || isInterpreted.current) {
      return;
    }

    isInterpreted.current = true;
    setIsInterpreting(true);
    interpretCards().finally(() => setIsInterpreting(false));
  }, [context, selectedCards, interpretations.length, interpretCards, router]);

  // 해석 선택 핸들러
  const handleSelectInterpretation = async (index: number) => {
    setError("");

    const feedbackRequest = await requestFeedback(context?.interactionPartner || "");

    if (feedbackRequest) {
      const result = await submitWithSelection(index, feedbackRequest.confirmationId);
      if (!result?.success) {
        setError("피드백 제출에 실패했습니다.");
      }
    }
  };

  // 직접 입력 핸들러
  const handleDirectFeedback = async (feedback: string) => {
    setError("");

    const feedbackRequest = await requestFeedback(context?.interactionPartner || "");

    if (feedbackRequest) {
      const result = await submitWithDirectFeedback(feedback, feedbackRequest.confirmationId);
      if (!result?.success) {
        setError("피드백 제출에 실패했습니다.");
      }
    }
  };

  if (!context || selectedCards.length === 0) {
    return null;
  }

  // 로딩 화면 - AI 분석 중
  if (isInterpreting) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
        <div className="relative text-center">
          {/* 아이콘 컨테이너 */}
          <div className="relative w-24 h-24 mx-auto mb-8">
            <div className="absolute inset-0 rounded-3xl bg-violet-500 animate-ping opacity-20" />
            <div className="absolute inset-0 rounded-3xl bg-violet-500 animate-pulse opacity-40" />
            <div className="relative w-full h-full rounded-3xl bg-violet-600 flex items-center justify-center shadow-lg">
              <SparklesIcon className="w-12 h-12 text-white" />
            </div>
          </div>

          <h2 className="text-2xl font-bold text-gray-800 mb-3">
            카드를 분석하고 있어요
          </h2>
          <p className="text-gray-600 mb-8 leading-relaxed">
            소통이가 선택한 카드들의 의미를
            <br />
            AI가 정성껏 해석하고 있어요
          </p>

          {/* 커스텀 스피너 */}
          <div className="flex justify-center gap-2">
            <div className="w-3 h-3 rounded-full bg-violet-500 animate-bounce" style={{ animationDelay: "0ms" }} />
            <div className="w-3 h-3 rounded-full bg-violet-500 animate-bounce" style={{ animationDelay: "150ms" }} />
            <div className="w-3 h-3 rounded-full bg-violet-500 animate-bounce" style={{ animationDelay: "300ms" }} />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-8">

      {/* 헤더 */}
      <header className="sticky top-0 z-50 bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-lg mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-xs text-violet-600 font-semibold tracking-wide uppercase">
                카드 해석
              </p>
              <h1 className="text-lg font-bold text-gray-900 mt-0.5">
                소통이가 말하고 싶은 것은?
              </h1>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.push("/main/cards")}
              className="text-violet-600 hover:text-violet-700 hover:bg-violet-50"
            >
              다시 선택
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-lg mx-auto px-4 py-6 space-y-5">
        {/* 선택한 카드 미리보기 */}
        <div className="bg-white rounded-2xl border border-gray-200 p-4 shadow-sm animate-fade-in">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-lg bg-violet-600 flex items-center justify-center">
              <CardsIcon className="w-[18px] h-[18px] text-white" />
            </div>
            <h3 className="font-semibold text-gray-900">선택한 카드</h3>
            <span className="ml-auto text-xs text-violet-600 font-medium bg-violet-50 px-2 py-1 rounded-full">
              {selectedCards.length}개
            </span>
          </div>

          {/* 가로 스크롤 카드 목록 */}
          <div className="flex gap-3 overflow-x-auto pb-2 -mx-1 px-1 scrollbar-hide">
            {selectedCards.map((card, index) => (
              <div
                key={card.filename}
                className="flex-shrink-0 w-20 text-center group"
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <div className="w-20 h-20 bg-white rounded-2xl overflow-hidden shadow-md group-hover:shadow-lg transition-shadow duration-300 border border-gray-100">
                  <Image
                    src={getImageUrl(card.filename)}
                    alt={card.name}
                    width={80}
                    height={80}
                    className="object-contain p-2"
                  />
                </div>
                <p className="text-xs text-gray-700 mt-2 font-medium truncate px-1">
                  {card.name}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* AI 해석 결과 카드 */}
        <div className="bg-white rounded-2xl border border-gray-200 p-5 shadow-sm animate-fade-in-up">
          <div className="flex items-center gap-3 mb-5">
            <div className="w-10 h-10 rounded-xl bg-violet-600 flex items-center justify-center shadow-sm">
              <SparklesIcon className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="font-bold text-gray-900">AI 해석 결과</h2>
              <p className="text-xs text-gray-500">가장 적절한 해석을 선택해주세요</p>
            </div>
          </div>

          <InterpretationDisplay
            interpretations={interpretations}
            onSelectInterpretation={handleSelectInterpretation}
            onDirectFeedback={handleDirectFeedback}
            isLoading={isLoading}
          />

          {error && (
            <div className="mt-4 flex items-center gap-2 p-3 rounded-xl bg-red-50 border border-red-100 text-red-600 text-sm">
              <AlertCircleIcon className="w-[18px] h-[18px]" />
              <span>{error}</span>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
