/**
 * AAC 카드 아이템 컴포넌트
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
}

export function CardItem({ card, isSelected, onSelect, disabled }: CardItemProps) {
  return (
    <button
      type="button"
      onClick={() => !disabled && onSelect(card)}
      disabled={disabled}
      className={cn(
        "relative p-2 rounded-xl border-2 transition-all duration-200",
        "hover:shadow-md focus:outline-none focus:ring-2 focus:ring-partner-500",
        isSelected
          ? "border-communicator-500 bg-communicator-50 ring-2 ring-communicator-500"
          : "border-gray-200 bg-white hover:border-gray-300",
        disabled && "opacity-50 cursor-not-allowed"
      )}
    >
      {/* 선택 표시 */}
      {isSelected && (
        <div className="absolute top-1 right-1 w-6 h-6 bg-communicator-500 rounded-full flex items-center justify-center z-10">
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
        </div>
      )}

      {/* 카드 이미지 */}
      <div className="aspect-square relative bg-gray-50 rounded-lg overflow-hidden">
        <Image
          src={getImageUrl(card.filename)}
          alt={card.name}
          fill
          className="object-contain p-2"
          sizes="(max-width: 768px) 50vw, 25vw"
        />
      </div>

      {/* 카드 이름 */}
      <p className="mt-2 text-sm font-medium text-gray-700 text-center truncate">
        {card.name}
      </p>
    </button>
  );
}
