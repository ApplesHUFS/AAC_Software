/**
 * 회원가입 스텝 표시 컴포넌트
 * - 진행 단계를 시각적으로 표시
 * - 완료/현재/미완료 상태 구분
 */

import { LockIcon, PersonIcon, HeartIcon, CheckIcon } from "@/components/ui/icons";

interface StepIndicatorProps {
  currentStep: number;
  totalSteps: number;
}

const STEPS = [
  { icon: LockIcon, label: "계정 정보" },
  { icon: PersonIcon, label: "개인 정보" },
  { icon: HeartIcon, label: "관심사" },
];

export function StepIndicator({ currentStep, totalSteps }: StepIndicatorProps) {
  return (
    <nav className="mb-8" aria-label="회원가입 진행 단계">
      <ol className="flex items-center justify-between">
        {STEPS.map((step, index) => {
          const stepNum = index + 1;
          const isCompleted = stepNum < currentStep;
          const isCurrent = stepNum === currentStep;

          return (
            <li key={index} className="flex flex-col items-center flex-1">
              <div className="relative flex items-center justify-center w-full">
                {/* 연결선 (오른쪽) */}
                {index < totalSteps - 1 && (
                  <div
                    className="absolute left-1/2 right-0 top-1/2 -translate-y-1/2 h-1 w-full"
                    aria-hidden="true"
                  >
                    <div
                      className={`h-full transition-all duration-500 ${
                        isCompleted ? "bg-violet-500" : "bg-gray-200"
                      }`}
                    />
                  </div>
                )}
                {/* 연결선 (왼쪽) */}
                {index > 0 && (
                  <div
                    className="absolute right-1/2 left-0 top-1/2 -translate-y-1/2 h-1 w-full"
                    aria-hidden="true"
                  >
                    <div
                      className={`h-full transition-all duration-500 ${
                        isCompleted || isCurrent ? "bg-violet-500" : "bg-gray-200"
                      }`}
                    />
                  </div>
                )}

                {/* 스텝 원 */}
                <div
                  className={`relative z-10 w-12 h-12 rounded-full flex items-center justify-center
                              transition-all duration-300 shadow-lg
                              ${
                                isCompleted
                                  ? "bg-violet-500 text-white scale-100"
                                  : isCurrent
                                    ? "bg-violet-600 text-white scale-110 ring-4 ring-violet-500/30"
                                    : "bg-gray-100 text-gray-400 scale-90"
                              }`}
                  aria-current={isCurrent ? "step" : undefined}
                  aria-label={`${step.label} ${isCompleted ? "(완료)" : isCurrent ? "(현재)" : ""}`}
                >
                  {isCompleted ? (
                    <CheckIcon className="w-4 h-4" aria-hidden="true" />
                  ) : (
                    <step.icon className="w-5 h-5" aria-hidden="true" />
                  )}
                </div>
              </div>

              {/* 라벨 */}
              <span
                className={`mt-2 text-xs font-medium transition-colors duration-300 ${
                  isCurrent ? "text-violet-600" : isCompleted ? "text-violet-500" : "text-gray-400"
                }`}
              >
                {step.label}
              </span>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
