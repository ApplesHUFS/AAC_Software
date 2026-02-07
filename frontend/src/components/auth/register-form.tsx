/**
 * 회원가입 폼 컴포넌트 - 다단계 글래스모피즘 디자인
 */

"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";
import { DISABILITY_TYPES, GENDER_OPTIONS, TOPIC_SUGGESTIONS } from "@/lib/constants";

// 아이콘 SVG 컴포넌트
const UserIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
      d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
  </svg>
);

const LockIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
      d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
  </svg>
);

const PersonIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
      d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const HeartIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
      d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
  </svg>
);

const CheckIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
  </svg>
);

// Toast 메시지 컴포넌트
interface ToastProps {
  message: string;
  type: "error" | "success";
  onClose: () => void;
}

function Toast({ message, type, onClose }: ToastProps) {
  useEffect(() => {
    const timer = setTimeout(onClose, 4000);
    return () => clearTimeout(timer);
  }, [onClose]);

  const bgColor = type === "error" ? "bg-red-500/90" : "bg-green-500/90";
  const ringColor = type === "error" ? "ring-red-400/50" : "ring-green-400/50";

  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 animate-slide-up">
      <div className={`flex items-center gap-3 px-5 py-3 ${bgColor} backdrop-blur-lg text-white
                       rounded-2xl shadow-2xl ring-1 ${ringColor}`}>
        <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          {type === "error" ? (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          ) : (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          )}
        </svg>
        <span className="font-medium text-sm">{message}</span>
        <button onClick={onClose} className="ml-2 hover:bg-white/20 rounded-full p-1 transition-colors">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  );
}

// 스텝 표시 컴포넌트
interface StepIndicatorProps {
  currentStep: number;
  totalSteps: number;
}

function StepIndicator({ currentStep, totalSteps }: StepIndicatorProps) {
  const steps = [
    { icon: LockIcon, label: "계정 정보" },
    { icon: PersonIcon, label: "개인 정보" },
    { icon: HeartIcon, label: "관심사" },
  ];

  return (
    <div className="mb-8">
      <div className="flex items-center justify-between">
        {steps.map((step, index) => {
          const stepNum = index + 1;
          const isCompleted = stepNum < currentStep;
          const isCurrent = stepNum === currentStep;

          return (
            <div key={index} className="flex flex-col items-center flex-1">
              <div className="relative flex items-center justify-center w-full">
                {/* 연결선 */}
                {index < totalSteps - 1 && (
                  <div className="absolute left-1/2 right-0 top-1/2 -translate-y-1/2 h-1 w-full">
                    <div
                      className={`h-full transition-all duration-500 ${
                        isCompleted ? "bg-violet-500" : "bg-gray-200"
                      }`}
                    />
                  </div>
                )}
                {index > 0 && (
                  <div className="absolute right-1/2 left-0 top-1/2 -translate-y-1/2 h-1 w-full">
                    <div
                      className={`h-full transition-all duration-500 ${
                        isCompleted || isCurrent ? "bg-violet-500" : "bg-gray-200"
                      }`}
                    />
                  </div>
                )}

                {/* 스텝 원 */}
                <div
                  className={`relative z-10 w-12 h-12 rounded-full flex items-center justify-center
                              transition-all duration-300 shadow-lg
                              ${isCompleted
                                ? "bg-violet-500 text-white scale-100"
                                : isCurrent
                                  ? "bg-violet-600 text-white scale-110 ring-4 ring-violet-500/30"
                                  : "bg-gray-100 text-gray-400 scale-90"
                              }`}
                >
                  {isCompleted ? <CheckIcon /> : <step.icon />}
                </div>
              </div>

              {/* 라벨 */}
              <span
                className={`mt-2 text-xs font-medium transition-colors duration-300 ${
                  isCurrent ? "text-violet-600" : isCompleted ? "text-violet-500" : "text-gray-400"
                }`}
              >
                {step.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// 입력 필드 컴포넌트
interface InputFieldProps {
  type: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder: string;
  icon: React.ReactNode;
  disabled?: boolean;
}

function InputField({ type, value, onChange, placeholder, icon, disabled }: InputFieldProps) {
  const [isFocused, setIsFocused] = useState(false);

  return (
    <div className="relative">
      <div className={`absolute left-4 top-1/2 -translate-y-1/2 transition-colors duration-200
                      ${isFocused ? "text-violet-600" : "text-gray-400"}`}>
        {icon}
      </div>
      <input
        type={type}
        value={value}
        onChange={onChange}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        placeholder={placeholder}
        disabled={disabled}
        className={`w-full pl-12 pr-4 py-4 bg-gray-50/50 border-2 rounded-2xl text-gray-900
                   placeholder:text-gray-400 transition-all duration-200 outline-none
                   ${isFocused
                     ? "border-violet-500 ring-4 ring-violet-500/20 bg-white"
                     : "border-gray-200 hover:border-gray-300"
                   }
                   disabled:opacity-50 disabled:cursor-not-allowed`}
      />
    </div>
  );
}

// 선택 필드 컴포넌트
interface SelectFieldProps {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  options: readonly { value: string; label: string }[];
  placeholder: string;
  icon: React.ReactNode;
}

function SelectField({ value, onChange, options, placeholder, icon }: SelectFieldProps) {
  const [isFocused, setIsFocused] = useState(false);

  return (
    <div className="relative">
      <div className={`absolute left-4 top-1/2 -translate-y-1/2 transition-colors duration-200 pointer-events-none
                      ${isFocused ? "text-violet-600" : "text-gray-400"}`}>
        {icon}
      </div>
      <select
        value={value}
        onChange={onChange}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        className={`w-full pl-12 pr-4 py-4 bg-gray-50/50 border-2 rounded-2xl text-gray-900
                   transition-all duration-200 outline-none appearance-none cursor-pointer
                   ${!value ? "text-gray-400" : ""}
                   ${isFocused
                     ? "border-violet-500 ring-4 ring-violet-500/20 bg-white"
                     : "border-gray-200 hover:border-gray-300"
                   }`}
      >
        <option value="" disabled>{placeholder}</option>
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>
      <div className={`absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none transition-colors
                      ${isFocused ? "text-violet-600" : "text-gray-400"}`}>
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
  );
}

export function RegisterForm() {
  const router = useRouter();
  const { register, isLoading } = useAuth();
  const [step, setStep] = useState(1);
  const [direction, setDirection] = useState<"forward" | "backward">("forward");
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
    setDirection(newStep > step ? "forward" : "backward");
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
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* 헤더 */}
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900">
            회원가입
          </h2>
          <p className="text-gray-500 mt-2 text-sm">소통이의 정보를 입력해주세요</p>
        </div>

        {/* 스텝 표시 */}
        <StepIndicator currentStep={step} totalSteps={3} />

        {/* 스텝 콘텐츠 */}
        <div className="relative overflow-hidden">
          {/* Step 1: 계정 정보 */}
          <div
            className={`space-y-4 transition-all duration-400 ease-out
                       ${step === 1 ? "opacity-100 translate-x-0" : "opacity-0 absolute inset-0 pointer-events-none"}
                       ${step > 1 ? "-translate-x-full" : step < 1 ? "translate-x-full" : ""}`}
          >
            <InputField
              type="text"
              value={formData.userId}
              onChange={(e) => setFormData({ ...formData, userId: e.target.value })}
              placeholder="아이디"
              icon={<UserIcon />}
            />
            <InputField
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              placeholder="비밀번호"
              icon={<LockIcon />}
            />
            <InputField
              type="password"
              value={formData.passwordConfirm}
              onChange={(e) => setFormData({ ...formData, passwordConfirm: e.target.value })}
              placeholder="비밀번호 확인"
              icon={<LockIcon />}
            />

            <button
              type="button"
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
                goToStep(2);
              }}
              className="w-full py-4 bg-violet-600 text-white font-semibold rounded-2xl
                         shadow-lg shadow-violet-500/30 hover:bg-violet-700
                         hover:shadow-xl hover:shadow-violet-500/40 hover:scale-[1.02]
                         active:scale-[0.98] transition-all duration-200"
            >
              다음
            </button>
          </div>

          {/* Step 2: 개인 정보 */}
          <div
            className={`space-y-4 transition-all duration-400 ease-out
                       ${step === 2 ? "opacity-100 translate-x-0" : "opacity-0 absolute inset-0 pointer-events-none"}
                       ${step > 2 ? "-translate-x-full" : step < 2 ? "translate-x-full" : ""}`}
          >
            <InputField
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="이름"
              icon={<PersonIcon />}
            />
            <InputField
              type="number"
              value={formData.age}
              onChange={(e) => setFormData({ ...formData, age: e.target.value })}
              placeholder="나이"
              icon={
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              }
            />
            <SelectField
              value={formData.gender}
              onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
              options={GENDER_OPTIONS}
              placeholder="성별 선택"
              icon={
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              }
            />
            <SelectField
              value={formData.disabilityType}
              onChange={(e) => setFormData({ ...formData, disabilityType: e.target.value })}
              options={DISABILITY_TYPES}
              placeholder="장애 유형 선택"
              icon={
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              }
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
          </div>

          {/* Step 3: 관심사 */}
          <div
            className={`space-y-4 transition-all duration-400 ease-out
                       ${step === 3 ? "opacity-100 translate-x-0" : "opacity-0 absolute inset-0 pointer-events-none"}
                       ${step > 3 ? "-translate-x-full" : step < 3 ? "translate-x-full" : ""}`}
          >
            {/* 의사소통 특성 */}
            <div className="relative">
              <textarea
                value={formData.communicationCharacteristics}
                onChange={(e) => setFormData({ ...formData, communicationCharacteristics: e.target.value })}
                placeholder="의사소통 특성을 설명해주세요"
                rows={3}
                className="w-full px-4 py-4 bg-gray-50/50 border-2 rounded-2xl text-gray-900
                          placeholder:text-gray-400 transition-all duration-200 outline-none resize-none
                          focus:border-violet-500 focus:ring-4 focus:ring-violet-500/20 focus:bg-white
                          border-gray-200 hover:border-gray-300"
              />
            </div>

            {/* 관심 주제 입력 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">관심 주제</label>
              <div className="flex gap-2">
                <div className="flex-1 relative">
                  <input
                    type="text"
                    value={topicInput}
                    onChange={(e) => setTopicInput(e.target.value)}
                    onKeyPress={(e) => e.key === "Enter" && (e.preventDefault(), handleAddTopic())}
                    placeholder="관심 주제 입력"
                    className="w-full px-4 py-3 bg-gray-50/50 border-2 rounded-xl text-gray-900
                              placeholder:text-gray-400 transition-all duration-200 outline-none
                              focus:border-violet-500 focus:ring-4 focus:ring-violet-500/20 focus:bg-white
                              border-gray-200 hover:border-gray-300"
                  />
                </div>
                <button
                  type="button"
                  onClick={handleAddTopic}
                  className="px-6 py-3 bg-violet-500 text-white font-medium rounded-xl
                             hover:bg-violet-600 active:scale-95 transition-all duration-200"
                >
                  추가
                </button>
              </div>

              {/* 추천 주제 칩 */}
              <div className="flex flex-wrap gap-2 mt-3">
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
                    className={`px-3 py-1.5 text-sm rounded-full transition-all duration-200
                               ${formData.interestingTopics.includes(topic)
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
                <div className="flex flex-wrap gap-2 mt-4">
                  {formData.interestingTopics.map((topic) => (
                    <span
                      key={topic}
                      className="inline-flex items-center gap-1.5 px-4 py-2 bg-violet-500
                                text-white text-sm font-medium rounded-full shadow-md animate-pop-in"
                    >
                      {topic}
                      <button
                        type="button"
                        onClick={() => handleRemoveTopic(topic)}
                        className="hover:bg-white/20 rounded-full p-0.5 transition-colors"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
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
                className="flex-[2] py-4 bg-violet-600 text-white font-semibold rounded-2xl
                           shadow-lg shadow-violet-500/30 hover:bg-violet-700
                           hover:shadow-xl hover:shadow-violet-500/40 hover:scale-[1.02]
                           active:scale-[0.98] transition-all duration-200
                           disabled:opacity-70 disabled:cursor-not-allowed disabled:hover:scale-100
                           relative overflow-hidden"
              >
                {isLoading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    가입 중...
                  </span>
                ) : (
                  "회원가입 완료"
                )}
              </button>
            </div>
          </div>
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

      {/* 애니메이션 스타일 */}
      <style jsx global>{`
        @keyframes slide-up {
          from { opacity: 0; transform: translate(-50%, 20px); }
          to { opacity: 1; transform: translate(-50%, 0); }
        }
        .animate-slide-up {
          animation: slide-up 0.3s ease-out forwards;
        }
        @keyframes pop-in {
          from { opacity: 0; transform: scale(0.8); }
          to { opacity: 1; transform: scale(1); }
        }
        .animate-pop-in {
          animation: pop-in 0.2s ease-out forwards;
        }
      `}</style>
    </>
  );
}
