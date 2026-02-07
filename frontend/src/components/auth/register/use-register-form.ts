/**
 * 회원가입 폼 로직 훅
 */

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";
import { authApi } from "@/lib/api/auth";
import { RegisterFormData } from "./types";

const initialFormData: RegisterFormData = {
  userId: "",
  password: "",
  passwordConfirm: "",
  name: "",
  age: "",
  gender: "",
  disabilityType: "",
  communicationCharacteristics: "",
  interestingTopics: [],
};

export function useRegisterForm() {
  const router = useRouter();
  const { register, isLoading } = useAuth();

  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState<RegisterFormData>(initialFormData);
  const [topicInput, setTopicInput] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // 아이디 중복 확인 상태
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

  // 관심 주제 추가
  const handleAddTopic = useCallback(() => {
    const topic = topicInput.trim();
    if (topic && !formData.interestingTopics.includes(topic)) {
      setFormData((prev) => ({
        ...prev,
        interestingTopics: [...prev.interestingTopics, topic],
      }));
      setTopicInput("");
    }
  }, [topicInput, formData.interestingTopics]);

  // 관심 주제 제거
  const handleRemoveTopic = useCallback((topic: string) => {
    setFormData((prev) => ({
      ...prev,
      interestingTopics: prev.interestingTopics.filter((t) => t !== topic),
    }));
  }, []);

  // 스텝 이동
  const goToStep = useCallback((newStep: number) => {
    setStep(newStep);
  }, []);

  // Step 1 유효성 검사
  const validateStep1 = useCallback((): boolean => {
    if (!formData.userId || !formData.password || !formData.passwordConfirm) {
      setError("모든 필드를 입력해주세요.");
      return false;
    }
    if (!idChecked || !idAvailable) {
      setError("아이디 중복 확인을 해주세요.");
      return false;
    }
    if (formData.password !== formData.passwordConfirm) {
      setError("비밀번호가 일치하지 않습니다.");
      return false;
    }
    setError("");
    return true;
  }, [formData, idChecked, idAvailable]);

  // Step 2 유효성 검사
  const validateStep2 = useCallback((): boolean => {
    if (!formData.name || !formData.age || !formData.gender || !formData.disabilityType) {
      setError("모든 필드를 입력해주세요.");
      return false;
    }
    setError("");
    return true;
  }, [formData]);

  // 폼 제출
  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
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
    },
    [formData, register, router]
  );

  return {
    // 상태
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

    // 아이디 확인 상태
    idChecked,
    setIdChecked,
    idAvailable,
    setIdAvailable,
    checkingId,

    // 핸들러
    handleCheckId,
    handleAddTopic,
    handleRemoveTopic,
    goToStep,
    validateStep1,
    validateStep2,
    handleSubmit,
  };
}
