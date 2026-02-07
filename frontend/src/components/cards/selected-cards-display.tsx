/**
 * 선택된 카드 표시 컴포넌트 - 글래스모피즘 스타일
 */

"use client";

import Image from "next/image";
import { Card as CardType } from "@/types/card";
import { cn, getImageUrl } from "@/lib/utils";

interface SelectedCardsDisplayProps {
  selectedCards: CardType[];
  onRemoveCard: (card: CardType) => void;
  maxCards: number;
}

export function SelectedCardsDisplay({
  selectedCards,
  onRemoveCard,
  maxCards,
}: SelectedCardsDisplayProps) {
  return (
    <div className="bg-white/70 backdrop-blur-xl rounded-2xl border border-white/60 p-5 shadow-lg">
      {/* 헤더 */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-bold text-gray-900">선택한 카드</h3>
        <div className="flex items-center gap-1.5">
          {Array.from({ length: maxCards }).map((_, i) => (
            <div
              key={i}
              className={cn(
                "w-2.5 h-2.5 rounded-full transition-all",
                i < selectedCards.length
                  ? "bg-gradient-to-r from-violet-500 to-pink-500"
                  : "bg-gray-200"
              )}
            />
          ))}
          <span className="ml-2 text-sm font-medium text-gray-500">
            {selectedCards.length} / {maxCards}
          </span>
        </div>
      </div>

      {selectedCards.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-8 text-gray-400">
          <svg className="w-12 h-12 mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
          <p className="text-sm">카드를 선택해주세요</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-3">
          {selectedCards.map((card, index) => (
            <div
              key={card.filename}
              className={cn(
                "relative group",
                "bg-gradient-to-br from-violet-50/80 to-pink-50/80",
                "rounded-xl p-2 border border-violet-100/50",
                "shadow-sm hover:shadow-md transition-all",
                "animate-scale-in"
              )}
              style={{ animationDelay: `${index * 50}ms` }}
            >
              {/* 제거 버튼 */}
              <button
                onClick={() => onRemoveCard(card)}
                className={cn(
                  "absolute -top-2 -right-2 z-10",
                  "w-6 h-6 bg-gradient-to-br from-red-500 to-red-600",
                  "rounded-full text-white",
                  "flex items-center justify-center",
                  "shadow-lg shadow-red-500/30",
                  "opacity-0 group-hover:opacity-100",
                  "hover:scale-110 transition-all"
                )}
                aria-label={`${card.name} 제거`}
              >
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>

              {/* 카드 이미지 */}
              <div className="aspect-square relative rounded-lg overflow-hidden bg-white/50 shadow-inner">
                <Image
                  src={getImageUrl(card.filename)}
                  alt={card.name}
                  fill
                  className="object-contain p-2"
                  sizes="100px"
                />
              </div>

              {/* 카드 이름 */}
              <p className="text-xs font-medium text-center text-gray-700 truncate mt-2 px-1">
                {card.name}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
