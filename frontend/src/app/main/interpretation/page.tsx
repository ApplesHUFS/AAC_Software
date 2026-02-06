/**
 * 해석 페이지
 */

"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { useContextStore } from "@/stores/context-store";
import { useCards } from "@/hooks/use-cards";
import { useFeedback } from "@/hooks/use-feedback";
import { Button, Spinner, Card, CardContent } from "@/components/ui";
import { InterpretationDisplay } from "@/components/interpretation/interpretation-display";
import { getImageUrl } from "@/lib/utils";
import { IMAGES } from "@/lib/images";

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
      // confirmationId를 직접 전달하여 클로저 문제 방지
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
      // confirmationId를 직접 전달하여 클로저 문제 방지
      const result = await submitWithDirectFeedback(feedback, feedbackRequest.confirmationId);
      if (!result?.success) {
        setError("피드백 제출에 실패했습니다.");
      }
    }
  };

  if (!context || selectedCards.length === 0) {
    return null;
  }

  // 로딩 화면
  if (isInterpreting) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
        <div className="text-center">
          <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-partner-100 flex items-center justify-center animate-pulse-soft shadow-app-sm">
            <Image src={IMAGES.ai} alt="" width={40} height={40} />
          </div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">
            카드를 분석하고 있어요!
          </h2>
          <p className="text-gray-500 mb-6 text-sm">
            소통이가 선택한 카드들의 의미를
            <br />
            AI가 해석하고 있어요
          </p>
          <Spinner size="lg" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-8">
      {/* 헤더 */}
      <header className="app-header">
        <div className="max-w-lg mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-xs text-partner-600 font-medium">카드 해석</p>
              <h1 className="text-lg font-semibold text-gray-900">
                소통이가 말하고 싶은 것은?
              </h1>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.push("/main/cards")}
            >
              다시 선택
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-lg mx-auto px-4 py-6 space-y-5">
        {/* 선택한 카드 표시 */}
        <div className="app-card p-4 animate-fade-in">
          <div className="flex items-center gap-2 mb-3">
            <Image src={IMAGES.selectedCard} alt="" width={20} height={20} />
            <h3 className="font-medium text-gray-900">선택한 카드</h3>
          </div>
          <div className="flex gap-3 overflow-x-auto pb-1">
            {selectedCards.map((card) => (
              <div
                key={card.filename}
                className="flex-shrink-0 w-16 text-center"
              >
                <div className="w-16 h-16 bg-gray-50 rounded-xl overflow-hidden shadow-app-sm">
                  <Image
                    src={getImageUrl(card.filename)}
                    alt={card.name}
                    width={64}
                    height={64}
                    className="object-contain p-1"
                  />
                </div>
                <p className="text-xs text-gray-600 mt-1.5 truncate">
                  {card.name}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* 해석 결과 */}
        <Card variant="elevated" className="animate-fade-in-up delay-100">
          <CardContent className="p-5">
            <div className="flex items-center gap-2 mb-4">
              <Image src={IMAGES.ai} alt="" width={24} height={24} />
              <h2 className="font-semibold text-gray-900">AI 해석 결과</h2>
            </div>

            <InterpretationDisplay
              interpretations={interpretations}
              onSelectInterpretation={handleSelectInterpretation}
              onDirectFeedback={handleDirectFeedback}
              isLoading={isLoading}
            />

            {error && (
              <div className="message-error mt-4">
                <Image src={IMAGES.error} alt="" width={18} height={18} />
                <span>{error}</span>
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
