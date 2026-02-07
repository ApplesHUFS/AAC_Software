/**
 * 액션 카드 컴포넌트 - 새 대화 시작 / 이어하기 버튼
 */

import { ReactNode, CSSProperties } from "react";

interface ActionCardProps {
  onClick: () => void;
  icon: ReactNode;
  iconBgColor: string;
  title: string;
  description: string;
  arrowBgColor: string;
  arrowColor: string;
  animationDelay?: string;
}

export function ActionCard({
  onClick,
  icon,
  iconBgColor,
  title,
  description,
  arrowBgColor,
  arrowColor,
  animationDelay = "0s",
}: ActionCardProps) {
  const style: CSSProperties = {
    animationDelay,
    animationFillMode: "both",
  };

  return (
    <button
      onClick={onClick}
      className="w-full text-left bg-white/70 backdrop-blur-xl rounded-2xl p-5 shadow-lg border border-white/50 transition-all duration-300 hover:shadow-xl hover:-translate-y-1 hover:bg-white/80 group animate-fade-in-up"
      style={style}
    >
      <div className="flex items-center gap-4">
        <div
          className={`w-12 h-12 rounded-xl ${iconBgColor} flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform`}
        >
          {icon}
        </div>
        <div className="flex-1">
          <h2 className="font-semibold text-gray-900">{title}</h2>
          <p className="text-sm text-gray-500">{description}</p>
        </div>
        <div
          className={`w-8 h-8 rounded-full ${arrowBgColor} flex items-center justify-center transition-colors`}
        >
          <svg
            className={`w-4 h-4 ${arrowColor}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5l7 7-7 7"
            />
          </svg>
        </div>
      </div>
    </button>
  );
}
