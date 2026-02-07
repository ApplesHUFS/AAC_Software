/**
 * 선택된 카드 하단 바 컴포넌트
 * - 선택된 카드 미니 프리뷰
 * - 소통하기 버튼
 */

import Image from "next/image";
import { Card } from "@/types/card";
import { getImageUrl, cn } from "@/lib/utils";
import { XIcon, BoxIcon } from "@/components/ui/icons";

interface SelectedCardsBarProps {
  selectedCards: Card[];
  isLoading: boolean;
  onRemoveCard: (card: Card) => void;
  onProceed: () => void;
}

export function SelectedCardsBar({
  selectedCards,
  isLoading,
  onRemoveCard,
  onProceed,
}: SelectedCardsBarProps) {
  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-white/90 backdrop-blur-xl border-t border-gray-200 shadow-2xl">
      <div className="max-w-lg mx-auto p-4">
        {/* 선택된 카드 미니 프리뷰 */}
        <div className="flex items-center gap-3 mb-4 overflow-x-auto pb-1 scrollbar-hide">
          {selectedCards.length > 0 ? (
            selectedCards.map((card, index) => (
              <div
                key={card.filename}
                className="relative flex-shrink-0 animate-scale-in"
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <div className="w-14 h-14 rounded-2xl bg-violet-50 overflow-hidden shadow-lg border-2 border-white">
                  <Image
                    src={getImageUrl(card.filename)}
                    alt={card.name}
                    width={56}
                    height={56}
                    className="object-contain p-1.5"
                  />
                </div>
                {/* X 버튼 */}
                <button
                  onClick={() => onRemoveCard(card)}
                  className="absolute -top-1.5 -right-1.5 w-6 h-6 bg-red-500 hover:bg-red-600 rounded-full text-white text-xs flex items-center justify-center shadow-lg hover:scale-110 transition-transform"
                  aria-label={`${card.name} 제거`}
                >
                  <XIcon className="w-3 h-3" />
                </button>
              </div>
            ))
          ) : (
            <div className="flex items-center gap-2 text-gray-400 py-2">
              <BoxIcon className="w-5 h-5" />
              <span className="text-sm">카드를 선택해주세요</span>
            </div>
          )}
        </div>

        {/* 소통하기 버튼 */}
        <button
          onClick={onProceed}
          disabled={selectedCards.length === 0 || isLoading}
          className={cn(
            "w-full py-4 rounded-2xl font-bold text-white text-lg transition-all",
            "bg-violet-600 hover:bg-violet-700",
            "shadow-lg shadow-violet-500/25",
            "hover:shadow-xl hover:shadow-violet-500/30 hover:scale-[1.02]",
            "active:scale-[0.98]",
            "disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 disabled:shadow-none"
          )}
        >
          <span className="flex items-center justify-center gap-2">
            이 카드로 소통하기
            {selectedCards.length > 0 && (
              <span className="px-2.5 py-0.5 bg-white/20 rounded-full text-sm">
                {selectedCards.length}개
              </span>
            )}
          </span>
        </button>
      </div>
    </div>
  );
}
