/**
 * 회원가입 폼 컴포넌트
 */

"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";
import { Button, Input, Select, Textarea } from "@/components/ui";
import { DISABILITY_TYPES, GENDER_OPTIONS, TOPIC_SUGGESTIONS } from "@/lib/constants";

export function RegisterForm() {
  const router = useRouter();
  const { register, isLoading } = useAuth();
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    userId: "",
    password: "",
    passwordConfirm: "",
    name: "",
    age: "",
    gender: "",
    disabilityType: "",
    communicationCharacteristics: "",
    interestingTopics: [] as string[],
  });
  const [topicInput, setTopicInput] = useState("");
  const [error, setError] = useState("");

  const handleAddTopic = () => {
    const topic = topicInput.trim();
    if (topic && !formData.interestingTopics.includes(topic)) {
      setFormData({
        ...formData,
        interestingTopics: [...formData.interestingTopics, topic],
      });
      setTopicInput("");
    }
  };

  const handleRemoveTopic = (topic: string) => {
    setFormData({
      ...formData,
      interestingTopics: formData.interestingTopics.filter((t) => t !== topic),
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (formData.password !== formData.passwordConfirm) {
      setError("비밀번호가 일치하지 않습니다.");
      return;
    }

    if (formData.interestingTopics.length === 0) {
      setError("관심 주제를 최소 1개 이상 입력해주세요.");
      return;
    }

    try {
      const response = await register({
        userId: formData.userId,
        password: formData.password,
        name: formData.name,
        age: parseInt(formData.age),
        gender: formData.gender,
        disabilityType: formData.disabilityType,
        communicationCharacteristics: formData.communicationCharacteristics,
        interestingTopics: formData.interestingTopics,
      });

      if (response?.success) {
        alert("회원가입이 완료되었습니다. 로그인해주세요.");
        router.push("/auth/login");
      } else {
        setError(response?.error || "회원가입에 실패했습니다.");
      }
    } catch (err) {
      setError("회원가입 중 오류가 발생했습니다.");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold text-gray-900">회원가입</h1>
        <p className="text-gray-600 mt-2">소통이의 정보를 입력해주세요</p>
      </div>

      {step === 1 && (
        <>
          <Input
            label="아이디"
            type="text"
            value={formData.userId}
            onChange={(e) => setFormData({ ...formData, userId: e.target.value })}
            placeholder="사용할 아이디를 입력하세요"
            required
          />
          <Input
            label="비밀번호"
            type="password"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            placeholder="비밀번호를 입력하세요"
            required
          />
          <Input
            label="비밀번호 확인"
            type="password"
            value={formData.passwordConfirm}
            onChange={(e) =>
              setFormData({ ...formData, passwordConfirm: e.target.value })
            }
            placeholder="비밀번호를 다시 입력하세요"
            required
          />
          <Button
            type="button"
            className="w-full"
            onClick={() => {
              if (!formData.userId || !formData.password || !formData.passwordConfirm) {
                setError("모든 필드를 입력해주세요.");
                return;
              }
              if (formData.password !== formData.passwordConfirm) {
                setError("비밀번호가 일치하지 않습니다.");
                return;
              }
              setError("");
              setStep(2);
            }}
          >
            다음
          </Button>
        </>
      )}

      {step === 2 && (
        <>
          <Input
            label="이름"
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="이름을 입력하세요"
            required
          />
          <Input
            label="나이"
            type="number"
            value={formData.age}
            onChange={(e) => setFormData({ ...formData, age: e.target.value })}
            placeholder="나이를 입력하세요"
            min="1"
            max="100"
            required
          />
          <Select
            label="성별"
            value={formData.gender}
            onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
            options={[...GENDER_OPTIONS]}
            placeholder="성별을 선택하세요"
            required
          />
          <Select
            label="장애 유형"
            value={formData.disabilityType}
            onChange={(e) =>
              setFormData({ ...formData, disabilityType: e.target.value })
            }
            options={[...DISABILITY_TYPES]}
            placeholder="장애 유형을 선택하세요"
            required
          />
          <div className="flex gap-2">
            <Button type="button" variant="outline" onClick={() => setStep(1)}>
              이전
            </Button>
            <Button
              type="button"
              className="flex-1"
              onClick={() => {
                if (
                  !formData.name ||
                  !formData.age ||
                  !formData.gender ||
                  !formData.disabilityType
                ) {
                  setError("모든 필드를 입력해주세요.");
                  return;
                }
                setError("");
                setStep(3);
              }}
            >
              다음
            </Button>
          </div>
        </>
      )}

      {step === 3 && (
        <>
          <Textarea
            label="의사소통 특성"
            value={formData.communicationCharacteristics}
            onChange={(e) =>
              setFormData({ ...formData, communicationCharacteristics: e.target.value })
            }
            placeholder="의사소통 특성을 설명해주세요"
            rows={3}
            required
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              관심 주제
            </label>
            <div className="flex gap-2 mb-2">
              <Input
                value={topicInput}
                onChange={(e) => setTopicInput(e.target.value)}
                placeholder="관심 주제를 입력하세요"
                onKeyPress={(e) => e.key === "Enter" && (e.preventDefault(), handleAddTopic())}
              />
              <Button type="button" onClick={handleAddTopic}>
                추가
              </Button>
            </div>
            <div className="flex flex-wrap gap-2 mb-2">
              {TOPIC_SUGGESTIONS.map((topic) => (
                <button
                  key={topic}
                  type="button"
                  onClick={() => {
                    if (!formData.interestingTopics.includes(topic)) {
                      setFormData({
                        ...formData,
                        interestingTopics: [...formData.interestingTopics, topic],
                      });
                    }
                  }}
                  className="px-2 py-1 text-xs bg-gray-100 rounded hover:bg-gray-200"
                >
                  + {topic}
                </button>
              ))}
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.interestingTopics.map((topic) => (
                <span
                  key={topic}
                  className="px-3 py-1 bg-partner-100 text-partner-700 rounded-full text-sm flex items-center gap-1"
                >
                  {topic}
                  <button
                    type="button"
                    onClick={() => handleRemoveTopic(topic)}
                    className="hover:text-partner-900"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>

          <div className="flex gap-2">
            <Button type="button" variant="outline" onClick={() => setStep(2)}>
              이전
            </Button>
            <Button type="submit" className="flex-1" disabled={isLoading}>
              {isLoading ? "가입 중..." : "회원가입"}
            </Button>
          </div>
        </>
      )}

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      <p className="text-center text-sm text-gray-600">
        이미 계정이 있으신가요?{" "}
        <Link href="/auth/login" className="text-partner-600 hover:underline">
          로그인
        </Link>
      </p>
    </form>
  );
}
