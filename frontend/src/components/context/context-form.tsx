/**
 * 상황 설정 폼 - 미니멀 디자인
 */

"use client";

import { useState } from "react";
import { useContext } from "@/hooks/use-context";
import { Button, Input, Textarea } from "@/components/ui";
import { MessageIcon, MapPinIcon, UsersIcon, AlertCircleIcon } from "@/components/ui/icons";

interface ContextFormProps {
  onCancel?: () => void;
}

export function ContextForm({ onCancel }: ContextFormProps) {
  const { createContext } = useContext();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [formData, setFormData] = useState({
    place: "",
    interactionPartner: "",
    currentActivity: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!formData.place || !formData.interactionPartner) {
      setError("장소와 대화 상대는 필수입니다.");
      return;
    }

    setIsLoading(true);
    try {
      const response = await createContext(formData);
      if (!response?.success) {
        setError(response?.error || "상황 설정에 실패했습니다.");
      }
    } catch (err) {
      setError("상황 설정 중 오류가 발생했습니다.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      {/* 헤더 */}
      <div className="text-center">
        <div className="w-20 h-20 mx-auto mb-5 rounded-3xl flex items-center justify-center shadow-xl bg-violet-500">
          <MessageIcon className="w-10 h-10 text-white" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900">
          대화 상황 설정
        </h2>
        <p className="text-gray-500 mt-2">
          소통이가 어디서 누구와 대화하고 있나요?
        </p>
      </div>

      {/* 입력 필드 */}
      <div className="space-y-5">
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">
            장소 <span className="text-pink-500">*</span>
          </label>
          <div className="relative">
            <div className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 flex items-center justify-center text-gray-400">
              <MapPinIcon className="w-5 h-5" />
            </div>
            <input
              type="text"
              value={formData.place}
              onChange={(e) => setFormData({ ...formData, place: e.target.value })}
              placeholder="예: 집, 학교, 병원, 놀이터"
              className="w-full pl-12 pr-4 py-3.5 bg-white/50 border border-gray-200 rounded-2xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-500/30 focus:border-violet-400 transition-all"
              required
            />
          </div>
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">
            대화 상대 <span className="text-pink-500">*</span>
          </label>
          <div className="relative">
            <div className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 flex items-center justify-center text-gray-400">
              <UsersIcon className="w-5 h-5" />
            </div>
            <input
              type="text"
              value={formData.interactionPartner}
              onChange={(e) => setFormData({ ...formData, interactionPartner: e.target.value })}
              placeholder="예: 엄마, 선생님, 친구"
              className="w-full pl-12 pr-4 py-3.5 bg-white/50 border border-gray-200 rounded-2xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-500/30 focus:border-violet-400 transition-all"
              required
            />
          </div>
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">
            현재 활동 <span className="text-gray-400">(선택)</span>
          </label>
          <textarea
            value={formData.currentActivity}
            onChange={(e) => setFormData({ ...formData, currentActivity: e.target.value })}
            placeholder="예: 밥 먹기, 놀이하기, 수업 듣기"
            rows={2}
            className="w-full px-4 py-3.5 bg-white/50 border border-gray-200 rounded-2xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-500/30 focus:border-violet-400 transition-all resize-none"
          />
        </div>
      </div>

      {/* 에러 메시지 */}
      {error && (
        <div className="flex items-center gap-3 px-4 py-3 bg-red-50 border border-red-100 rounded-2xl text-red-600">
          <AlertCircleIcon className="w-5 h-5" />
          <span className="text-sm font-medium">{error}</span>
        </div>
      )}

      {/* 버튼 */}
      <div className="flex gap-3 pt-2">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="px-6 py-3.5 text-gray-600 font-medium rounded-2xl border border-gray-200 hover:bg-gray-50 transition-all"
          >
            취소
          </button>
        )}
        <button
          type="submit"
          disabled={isLoading}
          className="flex-1 py-3.5 rounded-2xl font-semibold text-white shadow-lg bg-violet-600 hover:bg-violet-700 disabled:opacity-60 disabled:cursor-not-allowed transition-all hover:shadow-xl hover:scale-[1.02] active:scale-[0.98]"
        >
          {isLoading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="w-5 h-5 animate-spin" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeOpacity="0.3" />
                <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
              </svg>
              처리 중...
            </span>
          ) : (
            <span className="flex items-center justify-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              카드 추천 받기
            </span>
          )}
        </button>
      </div>
    </form>
  );
}
