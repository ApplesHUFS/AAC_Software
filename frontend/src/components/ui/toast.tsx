/**
 * Toast 알림 컴포넌트 - 접근성 준수 (WCAG 2.1 AA)
 * 에러/성공 메시지를 표시하는 재사용 가능한 컴포넌트
 */

"use client";

import { useEffect, useCallback } from "react";
import { XIcon, AlertCircleIcon, CheckIcon } from "./icons";

export type ToastType = "error" | "success" | "info";

export interface ToastProps {
  /** 표시할 메시지 */
  message: string;
  /** Toast 유형 (기본값: error) */
  type?: ToastType;
  /** 닫기 콜백 */
  onClose: () => void;
  /** 자동 닫힘 시간 (ms, 기본값: 4000) */
  duration?: number;
}

// 타입별 스타일 설정
const TOAST_STYLES: Record<ToastType, { bg: string; ring: string }> = {
  error: {
    bg: "bg-red-500/90",
    ring: "ring-red-400/50",
  },
  success: {
    bg: "bg-green-500/90",
    ring: "ring-green-400/50",
  },
  info: {
    bg: "bg-blue-500/90",
    ring: "ring-blue-400/50",
  },
};

export function Toast({
  message,
  type = "error",
  onClose,
  duration = 4000,
}: ToastProps) {
  const handleClose = useCallback(() => {
    onClose();
  }, [onClose]);

  useEffect(() => {
    const timer = setTimeout(handleClose, duration);
    return () => clearTimeout(timer);
  }, [handleClose, duration]);

  const styles = TOAST_STYLES[type];
  const IconComponent = type === "error" ? AlertCircleIcon : CheckIcon;

  return (
    <div
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
      className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 animate-slide-up"
    >
      <div
        className={`flex items-center gap-3 px-5 py-3 ${styles.bg} backdrop-blur-lg text-white
                    rounded-2xl shadow-2xl ring-1 ${styles.ring}`}
      >
        <IconComponent className="w-5 h-5 flex-shrink-0" aria-hidden="true" />
        <span className="font-medium text-sm">{message}</span>
        <button
          type="button"
          onClick={handleClose}
          className="ml-2 hover:bg-white/20 rounded-full p-1 transition-colors"
          aria-label="알림 닫기"
        >
          <XIcon className="w-4 h-4" aria-hidden="true" />
        </button>
      </div>
    </div>
  );
}
