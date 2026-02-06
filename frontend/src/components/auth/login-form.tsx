/**
 * 로그인 폼 컴포넌트
 */

"use client";

import { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { useAuth } from "@/hooks/use-auth";
import { Button, Input } from "@/components/ui";
import { IMAGES } from "@/lib/images";

export function LoginForm() {
  const { login, isLoading } = useAuth();
  const [formData, setFormData] = useState({
    userId: "",
    password: "",
  });
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!formData.userId || !formData.password) {
      setError("아이디와 비밀번호를 입력해주세요.");
      return;
    }

    try {
      const response = await login(formData);
      if (!response?.success) {
        setError(response?.error || "로그인에 실패했습니다.");
      }
    } catch (err) {
      setError("로그인 중 오류가 발생했습니다.");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* 헤더 */}
      <div className="text-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">로그인</h1>
        <p className="text-gray-500 mt-1 text-sm">
          AAC 카드 해석 서비스에 오신 것을 환영합니다
        </p>
      </div>

      {/* 입력 필드 */}
      <div className="space-y-4">
        <Input
          label="아이디"
          type="text"
          leftIcon={IMAGES.accountInfo}
          value={formData.userId}
          onChange={(e) => setFormData({ ...formData, userId: e.target.value })}
          placeholder="아이디를 입력하세요"
          disabled={isLoading}
        />

        <Input
          label="비밀번호"
          type="password"
          leftIcon={IMAGES.eye}
          value={formData.password}
          onChange={(e) => setFormData({ ...formData, password: e.target.value })}
          placeholder="비밀번호를 입력하세요"
          disabled={isLoading}
        />
      </div>

      {/* 에러 메시지 */}
      {error && (
        <div className="message-error">
          <Image src={IMAGES.error} alt="" width={18} height={18} />
          <span>{error}</span>
        </div>
      )}

      {/* 로그인 버튼 */}
      <Button
        type="submit"
        fullWidth
        size="lg"
        isLoading={isLoading}
      >
        로그인
      </Button>

      {/* 회원가입 링크 */}
      <p className="text-center text-sm text-gray-500">
        계정이 없으신가요?{" "}
        <Link
          href="/auth/register"
          className="text-partner-600 font-medium hover:text-partner-700 transition-colors"
        >
          회원가입
        </Link>
      </p>
    </form>
  );
}
