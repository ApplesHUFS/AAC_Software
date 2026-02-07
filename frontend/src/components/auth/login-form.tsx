/**
 * 로그인 폼 컴포넌트 - 접근성 준수 (WCAG 2.1 AA)
 */

"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/hooks/use-auth";
import { UserIcon, LockIcon } from "@/components/ui/icons";
import { Toast } from "@/components/ui/toast";

export function LoginForm() {
  const { login, isLoading } = useAuth();
  const [formData, setFormData] = useState({
    userId: "",
    password: "",
  });
  const [error, setError] = useState("");
  const [isFocused, setIsFocused] = useState<string | null>(null);

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
    } catch {
      setError("로그인 중 오류가 발생했습니다.");
    }
  };

  return (
    <>
      <form onSubmit={handleSubmit} className="space-y-6" noValidate>
        {/* 헤더 */}
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900">로그인</h2>
          <p className="text-gray-500 mt-2 text-sm">
            AAC 카드 해석 서비스에 오신 것을 환영합니다
          </p>
        </div>

        {/* 입력 필드 */}
        <div className="space-y-4">
          {/* 아이디 입력 */}
          <div className="relative">
            <label htmlFor="login-userId" className="sr-only">
              아이디
            </label>
            <div
              className={`absolute left-4 top-1/2 -translate-y-1/2 transition-colors duration-200
                         ${isFocused === "userId" ? "text-violet-600" : "text-gray-400"}`}
              aria-hidden="true"
            >
              <UserIcon className="w-5 h-5" />
            </div>
            <input
              id="login-userId"
              name="userId"
              type="text"
              autoComplete="username"
              value={formData.userId}
              onChange={(e) =>
                setFormData({ ...formData, userId: e.target.value })
              }
              onFocus={() => setIsFocused("userId")}
              onBlur={() => setIsFocused(null)}
              placeholder="아이디"
              disabled={isLoading}
              aria-label="아이디"
              aria-required="true"
              aria-describedby={error ? "login-error" : undefined}
              className={`w-full pl-12 pr-4 py-4 bg-gray-50/50 border-2 rounded-2xl text-gray-900
                         placeholder:text-gray-400 transition-all duration-200 outline-none
                         ${
                           isFocused === "userId"
                             ? "border-violet-500 ring-4 ring-violet-500/20 bg-white"
                             : "border-gray-200 hover:border-gray-300"
                         }
                         disabled:opacity-50 disabled:cursor-not-allowed`}
            />
          </div>

          {/* 비밀번호 입력 */}
          <div className="relative">
            <label htmlFor="login-password" className="sr-only">
              비밀번호
            </label>
            <div
              className={`absolute left-4 top-1/2 -translate-y-1/2 transition-colors duration-200
                         ${isFocused === "password" ? "text-violet-600" : "text-gray-400"}`}
              aria-hidden="true"
            >
              <LockIcon className="w-5 h-5" />
            </div>
            <input
              id="login-password"
              name="password"
              type="password"
              autoComplete="current-password"
              value={formData.password}
              onChange={(e) =>
                setFormData({ ...formData, password: e.target.value })
              }
              onFocus={() => setIsFocused("password")}
              onBlur={() => setIsFocused(null)}
              placeholder="비밀번호"
              disabled={isLoading}
              aria-label="비밀번호"
              aria-required="true"
              aria-describedby={error ? "login-error" : undefined}
              className={`w-full pl-12 pr-4 py-4 bg-gray-50/50 border-2 rounded-2xl text-gray-900
                         placeholder:text-gray-400 transition-all duration-200 outline-none
                         ${
                           isFocused === "password"
                             ? "border-violet-500 ring-4 ring-violet-500/20 bg-white"
                             : "border-gray-200 hover:border-gray-300"
                         }
                         disabled:opacity-50 disabled:cursor-not-allowed`}
            />
          </div>
        </div>

        {/* 로그인 버튼 */}
        <button
          type="submit"
          disabled={isLoading}
          aria-busy={isLoading}
          className="w-full py-4 bg-violet-600 hover:bg-violet-700 text-white
                     font-semibold rounded-2xl shadow-lg shadow-violet-500/20
                     hover:shadow-xl hover:shadow-violet-500/30 hover:scale-[1.02]
                     active:scale-[0.98] transition-all duration-200
                     disabled:opacity-70 disabled:cursor-not-allowed disabled:hover:scale-100"
        >
          <span className="flex items-center justify-center gap-2">
            {isLoading ? (
              <>
                <svg
                  className="w-5 h-5 animate-spin"
                  fill="none"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                  />
                </svg>
                <span>로그인 중...</span>
              </>
            ) : (
              "로그인"
            )}
          </span>
        </button>

        {/* 구분선 */}
        <div className="relative my-6" role="separator" aria-hidden="true">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-200" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-4 bg-white/70 text-gray-400">또는</span>
          </div>
        </div>

        {/* 소셜 로그인 (향후 확장용) */}
        <div className="grid grid-cols-3 gap-3" role="group" aria-label="소셜 로그인">
          <button
            type="button"
            className="flex items-center justify-center py-3 px-4 bg-gray-50 hover:bg-gray-100
                       rounded-xl border border-gray-200 transition-colors duration-200"
            disabled
            aria-label="Google 로그인 (준비 중)"
          >
            <svg
              className="w-5 h-5 text-gray-400"
              viewBox="0 0 24 24"
              fill="currentColor"
              aria-hidden="true"
            >
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
            </svg>
          </button>
          <button
            type="button"
            className="flex items-center justify-center py-3 px-4 bg-gray-50 hover:bg-gray-100
                       rounded-xl border border-gray-200 transition-colors duration-200"
            disabled
            aria-label="GitHub 로그인 (준비 중)"
          >
            <svg
              className="w-5 h-5 text-gray-400"
              fill="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.009-.866-.013-1.7-2.782.603-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.463-1.11-1.463-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.268 2.75 1.026A9.578 9.578 0 0112 6.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.026 2.747-1.026.546 1.377.202 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.163 22 16.418 22 12c0-5.523-4.477-10-10-10z" />
            </svg>
          </button>
          <button
            type="button"
            className="flex items-center justify-center py-3 px-4 bg-gray-50 hover:bg-gray-100
                       rounded-xl border border-gray-200 transition-colors duration-200"
            disabled
            aria-label="Apple 로그인 (준비 중)"
          >
            <svg
              className="w-5 h-5 text-gray-400"
              fill="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z" />
            </svg>
          </button>
        </div>

        {/* 회원가입 링크 */}
        <p className="text-center text-sm text-gray-500 mt-6">
          계정이 없으신가요?{" "}
          <Link
            href="/auth/register"
            className="font-semibold text-violet-600 hover:text-violet-700 transition-colors"
          >
            회원가입
          </Link>
        </p>
      </form>

      {/* Toast 에러 메시지 */}
      {error && (
        <Toast
          message={error}
          type="error"
          onClose={() => setError("")}
        />
      )}
    </>
  );
}
