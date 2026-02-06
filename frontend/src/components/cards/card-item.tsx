/**
 * AAC 카드 아이템 컴포넌트
 */

"use client";

import Image from "next/image";
import { Card as CardType } from "@/types/card";
import { cn, getImageUrl } from "@/lib/utils";
import { IMAGES } from "@/lib/images";

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
        "relative p-3 rounded-2xl bg-white transition-all duration-200",
        "shadow-app-card hover:shadow-app-md",
        "focus:outline-none focus:ring-2 focus:ring-communicator-500",
        "active:scale-[0.97]",
        isSelected && "ring-2 ring-communicator-500 bg-communicator-50 shadow-none",
        disabled && "opacity-50 pointer-events-none"
      )}
    >
      {/* 선택 체크 표시 */}
      {isSelected && (
        <div className="absolute top-2 right-2 w-6 h-6 z-10 animate-scale-in">
          <Image
            src={IMAGES.selectedCard}
            alt="선택됨"
            width={24}
            height={24}
          />
        </div>
      )}

      {/* 카드 이미지 */}
      <div className="aspect-square relative bg-gray-50 rounded-xl overflow-hidden mb-2">
        <Image
          src={getImageUrl(card.filename)}
          alt={card.name}
          fill
          className="object-contain p-2"
          sizes="(max-width: 768px) 50vw, 25vw"
        />
      </div>

      {/* 카드 이름 */}
      <p className={cn(
        "text-sm font-medium text-center truncate",
        isSelected ? "text-communicator-700" : "text-gray-700"
      )}>
        {card.name}
      </p>
    </button>
  );
}
