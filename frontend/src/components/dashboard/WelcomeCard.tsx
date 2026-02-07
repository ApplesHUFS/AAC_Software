/**
 * 환영 카드 컴포넌트
 */

import { HeartIcon } from "@/components/ui/icons";

interface WelcomeCardProps {
  userName: string;
}

export function WelcomeCard({ userName }: WelcomeCardProps) {
  return (
    <div className="relative overflow-hidden rounded-3xl p-6 shadow-xl bg-violet-600 animate-fade-in-up">
      <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2" />
      <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/10 rounded-full translate-y-1/2 -translate-x-1/2" />
      <div className="relative flex items-center gap-4">
        <div className="w-14 h-14 rounded-2xl bg-white/20 backdrop-blur flex items-center justify-center">
          <HeartIcon className="w-8 h-8 text-white" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-white">
            안녕하세요, {userName}님!
          </h1>
          <p className="text-white/80 text-sm mt-0.5">
            오늘도 즐거운 대화를 나눠보세요
          </p>
        </div>
      </div>
    </div>
  );
}
