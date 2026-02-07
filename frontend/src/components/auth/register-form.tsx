/**
 * 회원가입 폼 컴포넌트 - 접근성 준수 (WCAG 2.1 AA)
 * 다단계 폼으로 계정 정보, 개인 정보, 관심사를 수집
 */

"use client";

import { useState, useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";
import { authApi } from "@/lib/api/auth";
import { DISABILITY_TYPES, GENDER_OPTIONS, TOPIC_SUGGESTIONS } from "@/lib/constants";
import {
  UserIcon,
  LockIcon,
  PersonIcon,
  CalendarIcon,
  ShieldIcon,
  XIcon,
} from "@/components/ui/icons";
import { Toast } from "@/components/ui/toast";
import { Spinner } from "@/components/ui/spinner";
import { Input } from "@/components/ui/input";
import { StepIndicator } from "./step-indicator";
import { SelectField } from "./select-field";

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
  const [success, setSuccess] = useState("");
  const [idChecked, setIdChecked] = useState(false);
  const [idAvailable, setIdAvailable] = useState(false);
  const [checkingId, setCheckingId] = useState(false);

  // 아이디 중복 확인
  const handleCheckId = useCallback(async () => {
    if (!formData.userId.trim()) {
      setError("아이디를 입력해주세요.");
      return;
    }
    setCheckingId(true);
    setError("");
    try {
      const response = await authApi.checkId(formData.userId);
      if (response.data?.available) {
        setIdAvailable(true);
        setIdChecked(true);
        setSuccess("사용 가능한 아이디입니다.");
        setTimeout(() => setSuccess(""), 2000);
      } else {
        setIdAvailable(false);
        setIdChecked(true);
        setError("이미 사용 중인 아이디입니다.");
      }
    } catch {
      setError("중복 확인 중 오류가 발생했습니다.");
    } finally {
      setCheckingId(false);
    }
  }, [formData.userId]);

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

  const goToStep = (newStep: number) => {
    setStep(newStep);
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
        setSuccess("회원가입이 완료되었습니다!");
        setTimeout(() => router.push("/auth/login"), 1500);
      } else {
        setError(response?.error || "회원가입에 실패했습니다.");
      }
    } catch {
      setError("회원가입 중 오류가 발생했습니다.");
    }
  };

  return (
    <>
      <form onSubmit={handleSubmit} className="space-y-6" noValidate>
        {/* 헤더 */}
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900">회원가입</h2>
          <p className="text-gray-500 mt-2 text-sm">소통이의 정보를 입력해주세요</p>
        </div>

        {/* 스텝 표시 */}
        <StepIndicator currentStep={step} totalSteps={3} />

        {/* 스텝 콘텐츠 */}
        <div className="relative overflow-visible">
          {/* Step 1: 계정 정보 */}
          <fieldset
            className={`space-y-4 transition-all duration-400 ease-out
                       ${step === 1 ? "opacity-100 translate-x-0" : "opacity-0 absolute inset-0 pointer-events-none"}
                       ${step > 1 ? "-translate-x-full" : step < 1 ? "translate-x-full" : ""}`}
            disabled={step !== 1}
          >
            <legend className="sr-only">계정 정보</legend>
            {/* 아이디 + 중복확인 버튼 */}
            <div className="flex gap-2">
              <div className="flex-1">
                <Input
                  variant="minimal"
                  id="register-userId"
                  name="userId"
                  type="text"
                  value={formData.userId}
                  onChange={(e) => {
                    setFormData({ ...formData, userId: e.target.value });
                    setIdChecked(false);
                    setIdAvailable(false);
                  }}
                  placeholder="아이디"
                  label="아이디"
                  srOnlyLabel
                  leftIcon={<UserIcon className="w-5 h-5" />}
                  autoComplete="username"
                  aria-invalid={!!error && !idAvailable}
                  errorId={error ? "register-error" : undefined}
                />
              </div>
              <button
                type="button"
                onClick={handleCheckId}
                disabled={checkingId || !formData.userId.trim()}
                className={`px-4 py-4 font-medium rounded-2xl transition-all duration-200 whitespace-nowrap
                           ${idChecked && idAvailable
                             ? "bg-green-500 text-white"
                             : "bg-violet-100 text-violet-600 hover:bg-violet-200"
                           }
                           disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                {checkingId ? "확인중..." : idChecked && idAvailable ? "확인됨" : "중복확인"}
              </button>
            </div>
            <Input
              variant="minimal"
              id="register-password"
              name="password"
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              placeholder="비밀번호"
              label="비밀번호"
              srOnlyLabel
              leftIcon={<LockIcon className="w-5 h-5" />}
              autoComplete="new-password"
              aria-invalid={!!error}
              errorId={error ? "register-error" : undefined}
            />
            <Input
              variant="minimal"
              id="register-passwordConfirm"
              name="passwordConfirm"
              type="password"
              value={formData.passwordConfirm}
              onChange={(e) => setFormData({ ...formData, passwordConfirm: e.target.value })}
              placeholder="비밀번호 확인"
              label="비밀번호 확인"
              srOnlyLabel
              leftIcon={<LockIcon className="w-5 h-5" />}
              autoComplete="new-password"
              aria-invalid={!!error}
              errorId={error ? "register-error" : undefined}
            />

            <button
              type="button"
              onClick={() => {
                if (!formData.userId || !formData.password || !formData.passwordConfirm) {
                  setError("모든 필드를 입력해주세요.");
                  return;
                }
                if (!idChecked || !idAvailable) {
                  setError("아이디 중복 확인을 해주세요.");
                  return;
                }
                if (formData.password !== formData.passwordConfirm) {
                  setError("비밀번호가 일치하지 않습니다.");
                  return;
                }
                setError("");
                goToStep(2);
              }}
              className="w-full py-4 bg-violet-600 text-white font-semibold rounded-2xl
                         shadow-lg shadow-violet-500/30 hover:bg-violet-700
                         hover:shadow-xl hover:shadow-violet-500/40 hover:scale-[1.02]
                         active:scale-[0.98] transition-all duration-200"
            >
              다음
            </button>
          </fieldset>

          {/* Step 2: 개인 정보 */}
          <fieldset
            className={`space-y-4 transition-all duration-400 ease-out
                       ${step === 2 ? "opacity-100 translate-x-0" : "opacity-0 absolute inset-0 pointer-events-none"}
                       ${step > 2 ? "-translate-x-full" : step < 2 ? "translate-x-full" : ""}`}
            disabled={step !== 2}
          >
            <legend className="sr-only">개인 정보</legend>
            <Input
              variant="minimal"
              id="register-name"
              name="name"
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="이름"
              label="이름"
              srOnlyLabel
              leftIcon={<PersonIcon className="w-5 h-5" />}
              autoComplete="name"
              aria-invalid={!!error}
              errorId={error ? "register-error" : undefined}
            />
            <Input
              variant="minimal"
              id="register-age"
              name="age"
              type="number"
              value={formData.age}
              onChange={(e) => setFormData({ ...formData, age: e.target.value })}
              placeholder="나이"
              label="나이"
              srOnlyLabel
              leftIcon={<CalendarIcon className="w-5 h-5" />}
              aria-invalid={!!error}
              errorId={error ? "register-error" : undefined}
            />
            <SelectField
              id="register-gender"
              name="gender"
              value={formData.gender}
              onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
              options={GENDER_OPTIONS}
              placeholder="성별 선택"
              label="성별"
              icon={<UserIcon className="w-5 h-5" />}
              error={!!error}
              errorId={error ? "register-error" : undefined}
            />
            <SelectField
              id="register-disabilityType"
              name="disabilityType"
              value={formData.disabilityType}
              onChange={(e) => setFormData({ ...formData, disabilityType: e.target.value })}
              options={DISABILITY_TYPES}
              placeholder="장애 유형 선택"
              label="장애 유형"
              icon={<ShieldIcon className="w-5 h-5" />}
              error={!!error}
              errorId={error ? "register-error" : undefined}
            />

            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => goToStep(1)}
                className="flex-1 py-4 bg-gray-100 text-gray-700 font-semibold rounded-2xl
                           hover:bg-gray-200 active:scale-[0.98] transition-all duration-200"
              >
                이전
              </button>
              <button
                type="button"
                onClick={() => {
                  if (!formData.name || !formData.age || !formData.gender || !formData.disabilityType) {
                    setError("모든 필드를 입력해주세요.");
                    return;
                  }
                  setError("");
                  goToStep(3);
                }}
                className="flex-[2] py-4 bg-violet-600 text-white font-semibold rounded-2xl
                           shadow-lg shadow-violet-500/30 hover:bg-violet-700
                           hover:shadow-xl hover:shadow-violet-500/40 hover:scale-[1.02]
                           active:scale-[0.98] transition-all duration-200"
              >
                다음
              </button>
            </div>
          </fieldset>

          {/* Step 3: 관심사 */}
          <fieldset
            className={`space-y-4 transition-all duration-400 ease-out
                       ${step === 3 ? "opacity-100 translate-x-0" : "opacity-0 absolute inset-0 pointer-events-none"}
                       ${step > 3 ? "-translate-x-full" : step < 3 ? "translate-x-full" : ""}`}
            disabled={step !== 3}
          >
            <legend className="sr-only">관심사 및 의사소통 특성</legend>
            {/* 의사소통 특성 */}
            <div className="relative">
              <label htmlFor="register-communication" className="sr-only">
                의사소통 특성
              </label>
              <textarea
                id="register-communication"
                name="communicationCharacteristics"
                value={formData.communicationCharacteristics}
                onChange={(e) =>
                  setFormData({ ...formData, communicationCharacteristics: e.target.value })
                }
                placeholder="의사소통 특성을 설명해주세요"
                rows={3}
                aria-label="의사소통 특성"
                className="w-full px-4 py-4 bg-gray-50/50 border-2 rounded-2xl text-gray-900
                          placeholder:text-gray-400 transition-all duration-200 outline-none resize-none
                          focus:border-violet-500 focus:ring-4 focus:ring-violet-500/20 focus:bg-white
                          border-gray-200 hover:border-gray-300"
              />
            </div>

            {/* 관심 주제 입력 */}
            <div>
              <label
                htmlFor="register-topic-input"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                관심 주제
              </label>
              <div className="flex gap-2">
                <div className="flex-1 relative">
                  <input
                    id="register-topic-input"
                    type="text"
                    value={topicInput}
                    onChange={(e) => setTopicInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        e.preventDefault();
                        handleAddTopic();
                      }
                    }}
                    placeholder="관심 주제 입력"
                    aria-label="관심 주제 입력"
                    aria-describedby="topic-hint"
                    className="w-full px-4 py-3 bg-gray-50/50 border-2 rounded-xl text-gray-900
                              placeholder:text-gray-400 transition-all duration-200 outline-none
                              focus:border-violet-500 focus:ring-4 focus:ring-violet-500/20 focus:bg-white
                              border-gray-200 hover:border-gray-300"
                  />
                </div>
                <button
                  type="button"
                  onClick={handleAddTopic}
                  aria-label="관심 주제 추가"
                  className="px-6 py-3 bg-violet-500 text-white font-medium rounded-xl
                             hover:bg-violet-600 active:scale-95 transition-all duration-200"
                >
                  추가
                </button>
              </div>
              <p id="topic-hint" className="sr-only">
                Enter 키를 눌러 주제를 추가할 수 있습니다
              </p>

              {/* 추천 주제 칩 */}
              <div
                className="flex flex-wrap gap-2 mt-3"
                role="group"
                aria-label="추천 관심 주제"
              >
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
                    disabled={formData.interestingTopics.includes(topic)}
                    aria-pressed={formData.interestingTopics.includes(topic)}
                    className={`px-3 py-1.5 text-sm rounded-full transition-all duration-200
                               ${
                                 formData.interestingTopics.includes(topic)
                                   ? "bg-violet-100 text-violet-400 cursor-not-allowed"
                                   : "bg-gray-100 text-gray-600 hover:bg-violet-100 hover:text-violet-600"
                               }`}
                  >
                    + {topic}
                  </button>
                ))}
              </div>

              {/* 선택된 주제 */}
              {formData.interestingTopics.length > 0 && (
                <div
                  className="flex flex-wrap gap-2 mt-4"
                  role="list"
                  aria-label="선택된 관심 주제"
                >
                  {formData.interestingTopics.map((topic) => (
                    <span
                      key={topic}
                      role="listitem"
                      className="inline-flex items-center gap-1.5 px-4 py-2 bg-violet-500
                                text-white text-sm font-medium rounded-full shadow-md animate-pop-in"
                    >
                      {topic}
                      <button
                        type="button"
                        onClick={() => handleRemoveTopic(topic)}
                        aria-label={`${topic} 삭제`}
                        className="hover:bg-white/20 rounded-full p-0.5 transition-colors"
                      >
                        <XIcon className="w-4 h-4" aria-hidden="true" />
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* 버튼 */}
            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={() => goToStep(2)}
                className="flex-1 py-4 bg-gray-100 text-gray-700 font-semibold rounded-2xl
                           hover:bg-gray-200 active:scale-[0.98] transition-all duration-200"
              >
                이전
              </button>
              <button
                type="submit"
                disabled={isLoading}
                aria-busy={isLoading}
                className="flex-[2] py-4 bg-violet-600 text-white font-semibold rounded-2xl
                           shadow-lg shadow-violet-500/30 hover:bg-violet-700
                           hover:shadow-xl hover:shadow-violet-500/40 hover:scale-[1.02]
                           active:scale-[0.98] transition-all duration-200
                           disabled:opacity-70 disabled:cursor-not-allowed disabled:hover:scale-100
                           relative overflow-hidden"
              >
                {isLoading ? (
                  <span className="flex items-center justify-center gap-2">
                    <Spinner size="sm" />
                    <span>가입 중...</span>
                  </span>
                ) : (
                  "회원가입 완료"
                )}
              </button>
            </div>
          </fieldset>
        </div>

        {/* 로그인 링크 */}
        <p className="text-center text-sm text-gray-500">
          이미 계정이 있으신가요?{" "}
          <Link
            href="/auth/login"
            className="font-semibold text-violet-600 hover:text-violet-700 transition-colors"
          >
            로그인
          </Link>
        </p>
      </form>

      {/* Toast 메시지 */}
      {error && <Toast message={error} type="error" onClose={() => setError("")} />}
      {success && <Toast message={success} type="success" onClose={() => setSuccess("")} />}
    </>
  );
}
