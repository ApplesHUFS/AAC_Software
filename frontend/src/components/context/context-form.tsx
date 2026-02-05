/**
 * 상황 설정 폼 컴포넌트
 */

"use client";

import { useState } from "react";
import { useContext } from "@/hooks/use-context";
import { Button, Input, Textarea } from "@/components/ui";

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
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="text-center mb-6">
        <h2 className="text-xl font-bold text-gray-900">대화 상황 설정</h2>
        <p className="text-gray-600 mt-1">
          소통이가 어디서 누구와 대화하고 있나요?
        </p>
      </div>

      <Input
        label="장소"
        value={formData.place}
        onChange={(e) => setFormData({ ...formData, place: e.target.value })}
        placeholder="예: 집, 학교, 병원, 놀이터"
        required
      />

      <Input
        label="대화 상대"
        value={formData.interactionPartner}
        onChange={(e) =>
          setFormData({ ...formData, interactionPartner: e.target.value })
        }
        placeholder="예: 엄마, 선생님, 친구"
        required
      />

      <Textarea
        label="현재 활동 (선택)"
        value={formData.currentActivity}
        onChange={(e) =>
          setFormData({ ...formData, currentActivity: e.target.value })
        }
        placeholder="예: 밥 먹기, 놀이하기, 수업 듣기"
        rows={2}
      />

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      <div className="flex gap-3">
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel}>
            취소
          </Button>
        )}
        <Button type="submit" className="flex-1" disabled={isLoading}>
          {isLoading ? "설정 중..." : "카드 추천 받기"}
        </Button>
      </div>
    </form>
  );
}
