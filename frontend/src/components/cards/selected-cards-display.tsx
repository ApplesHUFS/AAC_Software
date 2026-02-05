/**
 * 선택된 카드 표시 컴포넌트
 */

"use client";

import Image from "next/image";
import { Card as CardType } from "@/types/card";
import { getImageUrl } from "@/lib/utils";

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
    <div className="bg-white rounded-xl border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-medium text-gray-900">선택한 카드</h3>
        <span className="text-sm text-gray-500">
          {selectedCards.length} / {maxCards}
        </span>
      </div>

      {selectedCards.length === 0 ? (
        <p className="text-gray-400 text-sm text-center py-4">
          카드를 선택해주세요
        </p>
      ) : (
        <div className="grid grid-cols-2 gap-2">
          {selectedCards.map((card) => (
            <div
              key={card.filename}
              className="relative bg-gray-50 rounded-lg p-1"
            >
              <button
                onClick={() => onRemoveCard(card)}
                className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white rounded-full text-xs flex items-center justify-center hover:bg-red-600 z-10"
                aria-label={`${card.name} 제거`}
              >
                ×
              </button>
              <div className="aspect-square relative">
                <Image
                  src={getImageUrl(card.filename)}
                  alt={card.name}
                  fill
                  className="object-contain"
                  sizes="100px"
                />
              </div>
              <p className="text-xs text-center text-gray-600 truncate mt-1">
                {card.name}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
