/**
 * 에러 박스 컴포넌트
 * - 일관된 에러 메시지 표시
 * - AlertCircle 아이콘 포함
 */

import { cn } from "@/lib/utils";
import { AlertCircleIcon } from "./icons";

interface ErrorBoxProps {
  message: string;
  className?: string;
}

export function ErrorBox({ message, className }: ErrorBoxProps) {
  return (
    <div
      className={cn(
        "flex items-center gap-3 p-4 bg-red-50/80 backdrop-blur-sm border border-red-100 rounded-2xl",
        className
      )}
    >
      <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0 text-red-600">
        <AlertCircleIcon className="w-[18px] h-[18px]" />
      </div>
      <span className="text-red-700 text-sm font-medium">{message}</span>
    </div>
  );
}
