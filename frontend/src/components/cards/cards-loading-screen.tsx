/**
 * 카드 로딩 화면 컴포넌트
 * - 카드 추천 중 표시
 * - 애니메이션 로딩 표시
 */

import { LayoutGridIcon } from "@/components/ui/icons";

export function CardsLoadingScreen() {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-4">
      <div className="text-center">
        {/* 아이콘 */}
        <div className="relative w-24 h-24 mx-auto mb-8">
          <div className="absolute inset-0 bg-violet-200 rounded-3xl animate-pulse opacity-40" />
          <div className="absolute inset-2 bg-violet-100 rounded-2xl flex items-center justify-center shadow-lg">
            <div className="animate-bounce text-violet-600">
              <LayoutGridIcon className="w-10 h-10" />
            </div>
          </div>
        </div>

        {/* 텍스트 */}
        <h2 className="text-2xl font-bold text-gray-900 mb-3 animate-fade-in">
          소통이를 위한 카드를 준비하고 있어요
        </h2>
        <p className="text-gray-500 mb-8 text-sm leading-relaxed animate-fade-in animation-delay-100">
          소통이의 관심사와 현재 상황을 분석해서
          <br />
          딱 맞는 카드들을 골라드릴게요
        </p>

        {/* 로딩 도트 */}
        <div className="flex justify-center gap-2">
          <div className="w-3 h-3 bg-violet-600 rounded-full animate-bounce [animation-delay:-0.3s]" />
          <div className="w-3 h-3 bg-violet-500 rounded-full animate-bounce [animation-delay:-0.15s]" />
          <div className="w-3 h-3 bg-violet-400 rounded-full animate-bounce" />
        </div>
      </div>
    </div>
  );
}
