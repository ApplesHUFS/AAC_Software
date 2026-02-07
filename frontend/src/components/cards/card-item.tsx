/**
 * AAC 카드 아이템 컴포넌트 - 글래스모피즘 스타일
 */

"use client";

import Image from "next/image";
import { Card as CardType } from "@/types/card";
import { cn, getImageUrl } from "@/lib/utils";

interface CardItemProps {
  card: CardType;
  isSelected: boolean;
  onSelect: (card: CardType) => void;
  disabled?: boolean;
  index?: number;
}

export function CardItem({ card, isSelected, onSelect, disabled, index = 0 }: CardItemProps) {
  return (
    <button
      type="button"
      onClick={() => !disabled && onSelect(card)}
      disabled={disabled}
      aria-pressed={isSelected}
      aria-label={`${card.name} 카드${isSelected ? " (선택됨)" : ""}`}
      className={cn(
        "relative p-3 rounded-2xl transition-all duration-300 ease-out",
        "bg-white/70 backdrop-blur-sm",
        "border border-white/60",
        "shadow-lg shadow-gray-200/50",
        "hover:shadow-xl hover:shadow-violet-200/40 hover:-translate-y-1",
        "focus:outline-none focus:ring-2 focus:ring-violet-400 focus:ring-offset-2",
        "active:scale-[0.97] active:shadow-md",
        "animate-fade-in-up",
        isSelected && "ring-2 ring-violet-500 bg-gradient-to-br from-violet-50/90 to-pink-50/90 border-violet-200 shadow-violet-200/60",
        disabled && !isSelected && "opacity-40 pointer-events-none grayscale"
      )}
      style={{ animationDelay: `${index * 30}ms` }}
    >
      {/* 선택 체크 뱃지 */}
      {isSelected && (
        <div className="absolute -top-2 -right-2 z-10 animate-scale-in">
          <div className="w-7 h-7 bg-gradient-to-br from-violet-500 to-pink-500 rounded-full flex items-center justify-center shadow-lg shadow-violet-500/30">
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        </div>
      )}

      {/* 호버 글로우 이펙트 */}
      <div className={cn(
        "absolute inset-0 rounded-2xl opacity-0 transition-opacity duration-300",
        "bg-gradient-to-br from-violet-400/10 to-pink-400/10",
        "group-hover:opacity-100"
      )} />

      {/* 카드 이미지 컨테이너 */}
      <div className={cn(
        "aspect-square relative rounded-xl overflow-hidden mb-2.5",
        "bg-gradient-to-br from-gray-50 to-gray-100",
        "shadow-inner",
        isSelected && "from-violet-50/50 to-pink-50/50"
      )}>
        <Image
          src={getImageUrl(card.filename)}
          alt={card.name}
          fill
          className="object-contain p-3 transition-transform duration-300 hover:scale-105"
          sizes="(max-width: 640px) 45vw, (max-width: 768px) 30vw, (max-width: 1024px) 22vw, 18vw"
        />
      </div>

      {/* 카드 이름 */}
      <p className={cn(
        "text-sm font-semibold text-center truncate transition-colors",
        isSelected
          ? "bg-gradient-to-r from-violet-700 to-pink-600 bg-clip-text text-transparent"
          : "text-gray-700"
      )}>
        {card.name}
      </p>
    </button>
  );
}
