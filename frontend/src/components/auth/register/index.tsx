/**
 * 회원가입 폼 컴포넌트 - 모듈화 버전
 * 다단계 폼으로 계정 정보, 개인 정보, 관심사를 수집
 */

"use client";

import Link from "next/link";
import { Toast } from "@/components/ui/toast";
import { StepIndicator } from "../step-indicator";
import { useRegisterForm } from "./use-register-form";
import { Step1Account } from "./step1-account";
import { Step2Profile } from "./step2-profile";
import { Step3Interests } from "./step3-interests";

export function RegisterForm() {
  const {
    step,
    formData,
    setFormData,
    topicInput,
    setTopicInput,
    error,
    setError,
    success,
    setSuccess,
    isLoading,
    idChecked,
    setIdChecked,
    idAvailable,
    setIdAvailable,
    checkingId,
    handleCheckId,
    handleAddTopic,
    handleRemoveTopic,
    goToStep,
    validateStep1,
    validateStep2,
    handleSubmit,
  } = useRegisterForm();

  // Step 1 다음 버튼 핸들러
  const handleStep1Next = () => {
    if (validateStep1()) {
      goToStep(2);
    }
  };

  // Step 2 다음 버튼 핸들러
  const handleStep2Next = () => {
    if (validateStep2()) {
      goToStep(3);
    }
  };

  // 스텝 전환 애니메이션 클래스
  const getStepClass = (stepNumber: number) => {
    const isActive = step === stepNumber;
    const isPast = step > stepNumber;

    return `transition-all duration-400 ease-out
            ${isActive ? "opacity-100 translate-x-0" : "opacity-0 absolute inset-0 pointer-events-none"}
            ${isPast ? "-translate-x-full" : !isActive ? "translate-x-full" : ""}`;
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
          <div className={getStepClass(1)}>
            {step === 1 && (
              <Step1Account
                formData={formData}
                setFormData={setFormData}
                error={error}
                setError={setError}
                onNext={handleStep1Next}
                idChecked={idChecked}
                idAvailable={idAvailable}
                checkingId={checkingId}
                onCheckId={handleCheckId}
                setIdChecked={setIdChecked}
                setIdAvailable={setIdAvailable}
              />
            )}
          </div>

          {/* Step 2: 개인 정보 */}
          <div className={getStepClass(2)}>
            {step === 2 && (
              <Step2Profile
                formData={formData}
                setFormData={setFormData}
                error={error}
                setError={setError}
                onNext={handleStep2Next}
                onPrev={() => goToStep(1)}
              />
            )}
          </div>

          {/* Step 3: 관심사 */}
          <div className={getStepClass(3)}>
            {step === 3 && (
              <Step3Interests
                formData={formData}
                setFormData={setFormData}
                error={error}
                setError={setError}
                topicInput={topicInput}
                setTopicInput={setTopicInput}
                isLoading={isLoading}
                onNext={() => {}}
                onPrev={() => goToStep(2)}
                onAddTopic={handleAddTopic}
                onRemoveTopic={handleRemoveTopic}
                onSubmit={handleSubmit}
              />
            )}
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
    </>
  );
}

export { useRegisterForm } from "./use-register-form";
export type { RegisterFormData } from "./types";
