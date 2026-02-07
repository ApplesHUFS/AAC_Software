"use client";

/**
 * 인증 페이지 레이아웃 - 미니멀 디자인
 */

import Image from "next/image";
import { IMAGES } from "@/lib/images";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen relative overflow-hidden flex items-center justify-center p-4">
      {/* 배경 - 미세한 그라데이션 */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-50 to-violet-50/30" />

      {/* 메인 컨테이너 */}
      <div className="relative z-10 w-full max-w-md animate-fade-in-up">
        {/* 로고 영역 */}
        <div className="text-center mb-8">
          <div
            className="w-28 h-28 mx-auto mb-4 relative bg-white rounded-3xl p-4 shadow-lg
                       ring-1 ring-slate-200/50 animate-float"
          >
            <Image
              src={IMAGES.logo}
              alt="소통, 이룸"
              fill
              className="object-contain p-2"
              priority
            />
          </div>
          <h1 className="text-3xl font-bold text-slate-800">
            소통, 이룸
          </h1>
          <p className="text-slate-500 mt-2 text-sm font-medium">
            AAC 카드 해석 서비스
          </p>
        </div>

        {/* 카드 컨테이너 */}
        <div
          className="bg-white rounded-3xl shadow-xl p-8
                     ring-1 ring-slate-200/50 animate-scale-in"
        >
          {children}
        </div>

        {/* 하단 저작권 */}
        <p className="text-center text-slate-400 text-xs mt-6">
          Copyright 2024. All rights reserved.
        </p>
      </div>

      {/* CSS 키프레임 애니메이션 */}
      <style jsx global>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-8px); }
        }
        .animate-float {
          animation: float 3s ease-in-out infinite;
        }
        @keyframes fade-in-up {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fade-in-up {
          animation: fade-in-up 0.6s ease-out forwards;
        }
        @keyframes scale-in {
          from {
            opacity: 0;
            transform: scale(0.95);
          }
          to {
            opacity: 1;
            transform: scale(1);
          }
        }
        .animate-scale-in {
          animation: scale-in 0.4s ease-out 0.2s forwards;
          opacity: 0;
        }
      `}</style>
    </div>
  );
}
