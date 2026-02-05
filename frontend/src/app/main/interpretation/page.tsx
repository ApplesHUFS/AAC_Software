/**
 * 해석 페이지
 */

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { useContextStore } from "@/stores/context-store";
import { useCards } from "@/hooks/use-cards";
import { useFeedback } from "@/hooks/use-feedback";
import { Button, Spinner, Card, CardContent } from "@/components/ui";
import { InterpretationDisplay } from "@/components/interpretation/interpretation-display";
import { getImageUrl } from "@/lib/utils";

export default function InterpretationPage() {
  const router = useRouter();
  const { context } = useContextStore();
  const { selectedCards, interpretations, interpretCards, setConfirmationId } =
    useCards();
  const { requestFeedback, submitWithSelection, submitWithDirectFeedback, isLoading } =
    useFeedback();

  const [isInterpreting, setIsInterpreting] = useState(false);
  const [error, setError] = useState("");

  // 초기 해석 요청
  useEffect(() => {
    if (!context || selectedCards.length === 0) {
      router.push("/main/dashboard");
      return;
    }

    if (interpretations.length === 0) {
      setIsInterpreting(true);
      interpretCards().finally(() => setIsInterpreting(false));
    }
  }, [context, selectedCards, interpretations.length, interpretCards, router]);

  // 해석 선택 핸들러
  const handleSelectInterpretation = async (index: number) => {
    setError("");

    // 먼저 피드백 요청 생성
    const feedbackRequest = await requestFeedback(context?.interactionPartner || "");

    if (feedbackRequest) {
      setConfirmationId(feedbackRequest.confirmationId);
      const result = await submitWithSelection(index);
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
      setConfirmationId(feedbackRequest.confirmationId);
      const result = await submitWithDirectFeedback(feedback);
      if (!result?.success) {
        setError("피드백 제출에 실패했습니다.");
      }
    }
  };

  if (!context || selectedCards.length === 0) {
    return null;
  }

  if (isInterpreting) {
    return (
      <div className="min-h-screen bg-partner-50 flex flex-col items-center justify-center p-4">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          카드를 분석하고 있어요!
        </h2>
        <p className="text-gray-600 mb-6 text-center">
          소통이가 선택한 카드들의 의미를
          <br />
          AI가 해석하고 있어요
        </p>
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-partner-50">
      {/* 헤더 */}
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div>
              <span className="text-partner-600 font-medium text-sm">
                카드 해석
              </span>
              <h1 className="text-lg font-semibold text-gray-900">
                소통이가 말하고 싶은 것은?
              </h1>
            </div>
            <Button variant="outline" onClick={() => router.push("/main/cards")}>
              카드 다시 선택
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-6 space-y-6">
        {/* 선택한 카드 표시 */}
        <Card>
          <CardContent className="p-4">
            <h3 className="font-medium text-gray-700 mb-3">선택한 카드</h3>
            <div className="flex gap-3 overflow-x-auto pb-2">
              {selectedCards.map((card) => (
                <div
                  key={card.filename}
                  className="flex-shrink-0 w-20 text-center"
                >
                  <div className="w-20 h-20 relative bg-gray-50 rounded-lg overflow-hidden">
                    <Image
                      src={getImageUrl(card.filename)}
                      alt={card.name}
                      fill
                      className="object-contain p-1"
                    />
                  </div>
                  <p className="text-xs text-gray-600 mt-1 truncate">
                    {card.name}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* 해석 결과 */}
        <Card>
          <CardContent className="p-6">
            <InterpretationDisplay
              interpretations={interpretations}
              onSelectInterpretation={handleSelectInterpretation}
              onDirectFeedback={handleDirectFeedback}
              isLoading={isLoading}
            />

            {error && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                {error}
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
