/**
 * 인증 페이지 레이아웃
 */

import Image from "next/image";
import { IMAGES } from "@/lib/images";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* 로고 영역 */}
        <div className="text-center mb-8 animate-fade-in-up">
          <div className="w-24 h-24 mx-auto mb-4 relative">
            <Image
              src={IMAGES.logo}
              alt="소통, 이룸"
              fill
              className="object-contain drop-shadow-md"
              priority
            />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">소통, 이룸</h1>
          <p className="text-gray-500 mt-1 text-sm">AAC 카드 해석 서비스</p>
        </div>

        {/* 콘텐츠 카드 */}
        <div className="bg-white rounded-3xl shadow-app-lg p-8 animate-scale-in">
          {children}
        </div>
      </div>
    </div>
  );
}
