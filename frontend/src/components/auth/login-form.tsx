/**
 * 로그인 폼 컴포넌트
 */

"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/hooks/use-auth";
import { Button, Input } from "@/components/ui";

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
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold text-gray-900">로그인</h1>
        <p className="text-gray-600 mt-2">AAC 카드 해석 서비스에 오신 것을 환영합니다</p>
      </div>

      <Input
        label="아이디"
        type="text"
        value={formData.userId}
        onChange={(e) => setFormData({ ...formData, userId: e.target.value })}
        placeholder="아이디를 입력하세요"
        disabled={isLoading}
      />

      <Input
        label="비밀번호"
        type="password"
        value={formData.password}
        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
        placeholder="비밀번호를 입력하세요"
        disabled={isLoading}
      />

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      <Button type="submit" className="w-full" disabled={isLoading}>
        {isLoading ? "로그인 중..." : "로그인"}
      </Button>

      <p className="text-center text-sm text-gray-600">
        계정이 없으신가요?{" "}
        <Link href="/auth/register" className="text-partner-600 hover:underline">
          회원가입
        </Link>
      </p>
    </form>
  );
}
