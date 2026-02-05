/**
 * 카드 그리드 컴포넌트
 */

"use client";

import { Card as CardType } from "@/types/card";
import { CardItem } from "./card-item";

interface CardGridProps {
  cards: CardType[];
  selectedCards: CardType[];
  onCardSelect: (card: CardType) => void;
  maxSelection?: number;
  disabled?: boolean;
}

export function CardGrid({
  cards,
  selectedCards,
  onCardSelect,
  maxSelection = 4,
  disabled = false,
}: CardGridProps) {
  const isCardSelected = (card: CardType) =>
    selectedCards.some((c) => c.filename === card.filename);

  const isSelectionDisabled = (card: CardType) =>
    disabled ||
    (!isCardSelected(card) && selectedCards.length >= maxSelection);

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
      {cards.map((card) => (
        <CardItem
          key={card.filename}
          card={card}
          isSelected={isCardSelected(card)}
          onSelect={onCardSelect}
          disabled={isSelectionDisabled(card)}
        />
      ))}
    </div>
  );
}
