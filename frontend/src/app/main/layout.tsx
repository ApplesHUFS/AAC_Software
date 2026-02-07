/**
 * 메인 페이지 레이아웃 - 글래스모피즘 헤더와 그라데이션 배경
 */

"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth-store";

export default function MainLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { isAuthenticated, isLoading, setLoading } = useAuthStore();

  useEffect(() => {
    setLoading(false);
  }, [setLoading]);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/auth/login");
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-indigo-50 to-pink-50 flex items-center justify-center">
        <div className="relative">
          <div className="w-16 h-16 rounded-full border-4 border-violet-200 border-t-violet-600 animate-spin" />
          <div className="absolute inset-0 w-16 h-16 rounded-full border-4 border-transparent border-b-pink-400 animate-spin animation-delay-150" />
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div
      className="min-h-screen"
      style={{
        background: "linear-gradient(135deg, #F8FAFC 0%, #EEF2FF 50%, #FCE7F3 100%)",
        paddingTop: "env(safe-area-inset-top)",
        paddingBottom: "env(safe-area-inset-bottom)",
        paddingLeft: "env(safe-area-inset-left)",
        paddingRight: "env(safe-area-inset-right)",
      }}
    >
      {children}
    </div>
  );
}
