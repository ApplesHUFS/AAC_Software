"use client";

/**
 * 인증 페이지 레이아웃 - 글래스모피즘 디자인
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
      {/* 그라데이션 배경 */}
      <div className="absolute inset-0 bg-gradient-to-br from-violet-600 via-purple-600 to-pink-500" />

      {/* 장식용 원형 그라데이션 */}
      <div className="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] rounded-full bg-gradient-to-r from-blue-400/30 to-purple-400/30 blur-3xl" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[600px] h-[600px] rounded-full bg-gradient-to-r from-pink-400/30 to-orange-400/30 blur-3xl" />
      <div className="absolute top-[40%] right-[20%] w-[300px] h-[300px] rounded-full bg-gradient-to-r from-cyan-400/20 to-blue-400/20 blur-2xl" />

      {/* 메인 컨테이너 */}
      <div className="relative z-10 w-full max-w-md animate-fade-in-up">
        {/* 로고 영역 */}
        <div className="text-center mb-8">
          <div
            className="w-28 h-28 mx-auto mb-4 relative bg-white/20 backdrop-blur-xl rounded-3xl p-4 shadow-2xl
                       ring-1 ring-white/30 animate-float"
          >
            <Image
              src={IMAGES.logo}
              alt="소통, 이룸"
              fill
              className="object-contain p-2 drop-shadow-lg"
              priority
            />
          </div>
          <h1 className="text-3xl font-bold text-white drop-shadow-lg">
            소통, 이룸
          </h1>
          <p className="text-white/80 mt-2 text-sm font-medium">
            AAC 카드 해석 서비스
          </p>
        </div>

        {/* 글래스모피즘 카드 */}
        <div
          className="bg-white/70 backdrop-blur-2xl rounded-3xl shadow-2xl p-8
                     ring-1 ring-white/50 animate-scale-in"
        >
          {children}
        </div>

        {/* 하단 저작권 */}
        <p className="text-center text-white/60 text-xs mt-6">
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
