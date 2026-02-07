/**
 * 대시보드 헤더 컴포넌트
 */

import Image from "next/image";
import { Button } from "@/components/ui";
import { IMAGES } from "@/lib/images";

interface DashboardHeaderProps {
  onLogout: () => void;
}

export function DashboardHeader({ onLogout }: DashboardHeaderProps) {
  return (
    <header
      className="sticky top-0 z-50 backdrop-blur-xl border-b border-white/30"
      style={{
        background: "rgba(255, 255, 255, 0.7)",
        paddingTop: "env(safe-area-inset-top)",
      }}
    >
      <div className="max-w-lg mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl overflow-hidden shadow-lg shadow-violet-200">
            <Image
              src={IMAGES.logoBasic}
              alt="소통이룸"
              width={40}
              height={40}
              className="object-cover"
            />
          </div>
          <span className="font-bold text-lg text-violet-600">소통, 이룸</span>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={onLogout}
          className="text-gray-500 hover:text-gray-700 hover:bg-white/50"
        >
          로그아웃
        </Button>
      </div>
    </header>
  );
}
