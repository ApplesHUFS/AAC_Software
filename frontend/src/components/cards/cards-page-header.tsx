/**
 * 카드 페이지 헤더 컴포넌트
 * - 뒤로가기, 제목, 새로고침 버튼
 * - 상황 정보 태그 표시
 */

import { cn } from "@/lib/utils";
import { MapPinIcon, UsersIcon, ActivityIcon, ChevronLeftIcon, RefreshIcon } from "@/components/ui/icons";

interface Context {
  place: string;
  interactionPartner: string;
  currentActivity?: string;
}

interface CardsPageHeaderProps {
  context: Context;
  isLoading: boolean;
  onBack: () => void;
  onRefresh: () => void;
}

export function CardsPageHeader({
  context,
  isLoading,
  onBack,
  onRefresh,
}: CardsPageHeaderProps) {
  return (
    <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-xl border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 py-4">
        {/* 상단 네비게이션 */}
        <div className="flex justify-between items-center">
          <button
            onClick={onBack}
            aria-label="이전 페이지로 돌아가기"
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors px-3 py-2 rounded-xl hover:bg-gray-100"
          >
            <ChevronLeftIcon className="w-5 h-5" />
            <span className="font-medium">뒤로</span>
          </button>

          <div className="text-center">
            <h1 className="text-lg font-bold text-gray-900">카드 선택</h1>
          </div>

          <button
            onClick={onRefresh}
            disabled={isLoading}
            aria-label={isLoading ? "카드 목록 로딩 중" : "카드 목록 새로고침"}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-xl transition-all",
              "bg-violet-50 hover:bg-violet-100",
              "text-violet-700 font-medium border border-violet-200",
              isLoading && "opacity-50 cursor-not-allowed"
            )}
          >
            <RefreshIcon className={cn("w-4 h-4", isLoading && "animate-spin")} />
            <span>{isLoading ? "로딩..." : "새로고침"}</span>
          </button>
        </div>

        {/* 상황 정보 태그 */}
        <div className="flex gap-3 mt-4 overflow-x-auto pb-1 scrollbar-hide">
          <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-full border border-violet-200 shadow-sm flex-shrink-0">
            <div className="w-6 h-6 bg-violet-100 rounded-full flex items-center justify-center text-violet-600">
              <MapPinIcon className="w-3.5 h-3.5" />
            </div>
            <span className="text-sm font-medium text-violet-700">{context.place}</span>
          </div>

          <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-full border border-pink-200 shadow-sm flex-shrink-0">
            <div className="w-6 h-6 bg-pink-100 rounded-full flex items-center justify-center text-pink-600">
              <UsersIcon className="w-3.5 h-3.5" />
            </div>
            <span className="text-sm font-medium text-pink-700">{context.interactionPartner}</span>
          </div>

          {context.currentActivity && (
            <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-full border border-gray-200 shadow-sm flex-shrink-0">
              <div className="w-6 h-6 bg-gray-100 rounded-full flex items-center justify-center text-gray-600">
                <ActivityIcon className="w-3.5 h-3.5" />
              </div>
              <span className="text-sm font-medium text-gray-700">{context.currentActivity}</span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
