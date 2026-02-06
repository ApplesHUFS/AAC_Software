/**
 * 상황 설정 폼 컴포넌트
 */

"use client";

import { useState } from "react";
import Image from "next/image";
import { useContext } from "@/hooks/use-context";
import { Button, Input, Textarea } from "@/components/ui";
import { IMAGES } from "@/lib/images";

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
      {/* 헤더 */}
      <div className="text-center">
        <div className="icon-container icon-container-lg icon-container-partner mx-auto mb-4">
          <Image
            src={IMAGES.communicationSituation}
            alt=""
            width={32}
            height={32}
          />
        </div>
        <h2 className="text-xl font-bold text-gray-900">대화 상황 설정</h2>
        <p className="text-gray-500 mt-1 text-sm">
          소통이가 어디서 누구와 대화하고 있나요?
        </p>
      </div>

      {/* 입력 필드 */}
      <div className="space-y-4">
        <Input
          label="장소"
          leftIcon={IMAGES.place}
          value={formData.place}
          onChange={(e) => setFormData({ ...formData, place: e.target.value })}
          placeholder="예: 집, 학교, 병원, 놀이터"
          required
        />

        <Input
          label="대화 상대"
          leftIcon={IMAGES.interactionPartner}
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
      </div>

      {/* 에러 메시지 */}
      {error && (
        <div className="message-error">
          <Image src={IMAGES.error} alt="" width={18} height={18} />
          <span>{error}</span>
        </div>
      )}

      {/* 버튼 */}
      <div className="flex gap-3 pt-2">
        {onCancel && (
          <Button
            type="button"
            variant="secondary"
            onClick={onCancel}
            className="flex-shrink-0 min-w-[60px]"
          >
            취소
          </Button>
        )}
        <Button type="submit" fullWidth isLoading={isLoading}>
          카드 추천 받기
        </Button>
      </div>
    </form>
  );
}
