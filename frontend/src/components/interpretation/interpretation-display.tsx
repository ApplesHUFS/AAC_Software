/**
 * 해석 결과 표시 컴포넌트
 */

"use client";

import { useState } from "react";
import { Interpretation } from "@/types/card";
import { Button, Textarea } from "@/components/ui";
import { cn } from "@/lib/utils";

interface InterpretationDisplayProps {
  interpretations: Interpretation[];
  onSelectInterpretation: (index: number) => void;
  onDirectFeedback: (feedback: string) => void;
  isLoading: boolean;
}

export function InterpretationDisplay({
  interpretations,
  onSelectInterpretation,
  onDirectFeedback,
  isLoading,
}: InterpretationDisplayProps) {
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [showDirectInput, setShowDirectInput] = useState(false);
  const [directFeedback, setDirectFeedback] = useState("");

  const handleSelect = (index: number) => {
    setSelectedIndex(index);
    setShowDirectInput(false);
  };

  const handleSubmit = () => {
    if (showDirectInput && directFeedback.trim()) {
      onDirectFeedback(directFeedback.trim());
    } else if (selectedIndex !== null) {
      onSelectInterpretation(selectedIndex);
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-xl font-bold text-gray-900">
          소통이가 말하고 싶은 것은?
        </h2>
        <p className="text-gray-600 mt-1">
          가장 적절한 해석을 선택해주세요
        </p>
      </div>

      {/* 해석 옵션 */}
      <div className="space-y-3">
        {interpretations.map((interpretation, index) => (
          <button
            key={index}
            type="button"
            onClick={() => handleSelect(index)}
            disabled={isLoading}
            className={cn(
              "w-full p-4 rounded-xl border-2 text-left transition-all",
              "hover:shadow-md focus:outline-none focus:ring-2 focus:ring-partner-500",
              selectedIndex === index
                ? "border-partner-500 bg-partner-50"
                : "border-gray-200 bg-white hover:border-gray-300"
            )}
          >
            <div className="flex items-start gap-3">
              <div
                className={cn(
                  "w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 mt-0.5",
                  selectedIndex === index
                    ? "border-partner-500 bg-partner-500"
                    : "border-gray-300"
                )}
              >
                {selectedIndex === index && (
                  <svg
                    className="w-4 h-4 text-white"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                )}
              </div>
              <span className="text-gray-800">{interpretation.text}</span>
            </div>
          </button>
        ))}
      </div>

      {/* 직접 입력 옵션 */}
      <div className="border-t pt-4">
        <button
          type="button"
          onClick={() => {
            setShowDirectInput(!showDirectInput);
            setSelectedIndex(null);
          }}
          className="text-partner-600 hover:underline text-sm"
        >
          {showDirectInput ? "해석 선택으로 돌아가기" : "직접 입력하기"}
        </button>

        {showDirectInput && (
          <div className="mt-3">
            <Textarea
              value={directFeedback}
              onChange={(e) => setDirectFeedback(e.target.value)}
              placeholder="소통이가 말하고 싶은 것을 직접 입력해주세요"
              rows={3}
            />
          </div>
        )}
      </div>

      {/* 제출 버튼 */}
      <Button
        onClick={handleSubmit}
        className="w-full"
        disabled={
          isLoading ||
          (selectedIndex === null && !directFeedback.trim())
        }
      >
        {isLoading ? "제출 중..." : "확인"}
      </Button>
    </div>
  );
}
