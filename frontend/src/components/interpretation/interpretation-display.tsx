/**
 * 해석 결과 표시 컴포넌트 - 미니멀 디자인
 */

"use client";

import { useState } from "react";
import { Interpretation } from "@/types/card";
import { Textarea } from "@/components/ui";
import { cn } from "@/lib/utils";

interface InterpretationDisplayProps {
  interpretations: Interpretation[];
  onSelectInterpretation: (index: number) => void;
  onDirectFeedback: (feedback: string) => void;
  isLoading: boolean;
}

// 체크 아이콘 컴포넌트
function CheckIcon({ className }: { className?: string }) {
  return (
    <svg
      className={cn("w-4 h-4", className)}
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2.5}
        d="M5 13l4 4L19 7"
      />
    </svg>
  );
}

// 스피너 컴포넌트
function LoadingSpinner() {
  return (
    <svg
      className="w-5 h-5 animate-spin"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
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

  const isSubmitDisabled = isLoading || (selectedIndex === null && !directFeedback.trim());

  return (
    <div className="space-y-5">
      {/* 해석 옵션 - 라디오 버튼 스타일 */}
      <div className="space-y-3">
        {interpretations.map((interpretation, index) => {
          const isSelected = selectedIndex === index;

          return (
            <button
              key={index}
              type="button"
              onClick={() => handleSelect(index)}
              disabled={isLoading}
              className={cn(
                "w-full p-4 rounded-2xl text-left transition-all duration-200",
                "backdrop-blur-md border-2",
                "hover:-translate-y-0.5 hover:shadow-lg",
                "focus:outline-none focus:ring-2 focus:ring-violet-500/50 focus:ring-offset-2",
                "disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0",
                isSelected
                  ? "border-violet-500 bg-violet-50/50 shadow-md shadow-violet-500/10"
                  : "border-transparent bg-white/50 hover:bg-white/70 hover:border-gray-200"
              )}
            >
              <div className="flex items-start gap-3">
                {/* 라디오 버튼 스타일 체크박스 */}
                <div
                  className={cn(
                    "w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 mt-0.5 transition-all duration-200",
                    isSelected
                      ? "border-violet-500 bg-violet-500 scale-110"
                      : "border-gray-300 bg-white"
                  )}
                >
                  {isSelected && <CheckIcon className="text-white" />}
                </div>

                <span
                  className={cn(
                    "text-gray-800 leading-relaxed transition-colors",
                    isSelected && "text-gray-900 font-medium"
                  )}
                >
                  {interpretation.text}
                </span>
              </div>
            </button>
          );
        })}
      </div>

      {/* 직접 입력 섹션 */}
      <div className="pt-3 border-t border-gray-200/50">
        <button
          type="button"
          onClick={() => {
            setShowDirectInput(!showDirectInput);
            if (!showDirectInput) {
              setSelectedIndex(null);
            }
          }}
          disabled={isLoading}
          className={cn(
            "text-violet-600 hover:text-violet-700 text-sm font-medium transition-colors",
            "focus:outline-none focus:underline",
            "disabled:opacity-50 disabled:cursor-not-allowed"
          )}
        >
          {showDirectInput ? "해석 선택으로 돌아가기" : "원하는 해석이 없나요? 직접 입력하기"}
        </button>

        {showDirectInput && (
          <div className="mt-4 animate-fade-in">
            <Textarea
              value={directFeedback}
              onChange={(e) => setDirectFeedback(e.target.value)}
              placeholder="소통이가 전하고 싶은 말을 직접 적어주세요..."
              rows={3}
              disabled={isLoading}
              className={cn(
                "w-full backdrop-blur-md bg-white/50 border-2 border-gray-200/50",
                "rounded-xl resize-none transition-all duration-200",
                "focus:border-violet-500 focus:bg-white/70 focus:ring-2 focus:ring-violet-500/20",
                "placeholder:text-gray-400"
              )}
            />
          </div>
        )}
      </div>

      {/* 확인 버튼 */}
      <button
        type="button"
        onClick={handleSubmit}
        disabled={isSubmitDisabled}
        className={cn(
          "w-full py-4 rounded-2xl font-semibold text-white transition-all duration-200",
          "flex items-center justify-center gap-2",
          "focus:outline-none focus:ring-2 focus:ring-offset-2",
          isSubmitDisabled
            ? "bg-gray-300 cursor-not-allowed"
            : "bg-violet-600 hover:bg-violet-700 hover:-translate-y-0.5 focus:ring-violet-500"
        )}
      >
        {isLoading ? (
          <>
            <LoadingSpinner />
            <span>제출 중...</span>
          </>
        ) : (
          <span>확인</span>
        )}
      </button>
    </div>
  );
}
