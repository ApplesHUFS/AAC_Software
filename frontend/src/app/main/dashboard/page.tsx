/**
 * 대시보드 페이지 - 글래스모피즘과 애니메이션 적용
 */

"use client";

import { useState } from "react";
import Image from "next/image";
import { useAuth } from "@/hooks/use-auth";
import { useContext } from "@/hooks/use-context";
import { Button } from "@/components/ui";
import { ContextForm } from "@/components/context/context-form";
import { IMAGES } from "@/lib/images";
import {
  HeartIcon,
  ChatPlusIcon,
  MessageIcon,
  CalendarIcon,
  GenderIcon,
  TagIcon,
  StarIcon,
} from "@/components/ui/icons";

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const { context, continueSession, startNewSession } = useContext();
  const [showContextForm, setShowContextForm] = useState(false);

  const handleNewSession = () => {
    startNewSession();
    setShowContextForm(true);
  };

  // 상황 설정 폼 화면
  if (showContextForm) {
    return (
      <div className="min-h-screen p-4">
        <div className="max-w-md mx-auto pt-8">
          <div
            className="bg-white/70 backdrop-blur-xl rounded-3xl shadow-xl border border-white/50 overflow-hidden"
            style={{
              animation: "fadeInUp 0.5s ease-out",
            }}
          >
            <div className="p-6 sm:p-8">
              <ContextForm onCancel={() => setShowContextForm(false)} />
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pb-8">
      {/* 글래스모피즘 헤더 */}
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
            <span className="font-bold text-lg bg-gradient-to-r from-violet-600 to-pink-600 bg-clip-text text-transparent">
              소통, 이룸
            </span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={logout}
            className="text-gray-500 hover:text-gray-700 hover:bg-white/50"
          >
            로그아웃
          </Button>
        </div>
      </header>

      {/* 메인 콘텐츠 */}
      <main className="max-w-lg mx-auto px-4 py-6 space-y-5">
        {/* 환영 카드 - 그라데이션 배경 */}
        <div
          className="relative overflow-hidden rounded-3xl p-6 shadow-xl"
          style={{
            background: "linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%)",
            animation: "fadeInUp 0.4s ease-out",
          }}
        >
          <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2" />
          <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/10 rounded-full translate-y-1/2 -translate-x-1/2" />
          <div className="relative flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-white/20 backdrop-blur flex items-center justify-center">
              <HeartIcon className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">
                안녕하세요, {user?.name}님!
              </h1>
              <p className="text-white/80 text-sm mt-0.5">
                오늘도 즐거운 대화를 나눠보세요
              </p>
            </div>
          </div>
        </div>

        {/* 액션 카드들 */}
        <div className="space-y-3">
          {/* 새 대화 시작 */}
          <button
            onClick={handleNewSession}
            className="w-full text-left bg-white/70 backdrop-blur-xl rounded-2xl p-5 shadow-lg border border-white/50 transition-all duration-300 hover:shadow-xl hover:-translate-y-1 hover:bg-white/80 group"
            style={{ animation: "fadeInUp 0.5s ease-out 0.1s both" }}
          >
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-500 to-violet-600 flex items-center justify-center shadow-lg shadow-violet-200 group-hover:scale-110 transition-transform">
                <ChatPlusIcon className="w-6 h-6 text-white" />
              </div>
              <div className="flex-1">
                <h2 className="font-semibold text-gray-900">새 대화 시작</h2>
                <p className="text-sm text-gray-500">새로운 상황에서 대화하기</p>
              </div>
              <div className="w-8 h-8 rounded-full bg-violet-100 flex items-center justify-center group-hover:bg-violet-200 transition-colors">
                <svg
                  className="w-4 h-4 text-violet-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </button>

          {/* 이어하기 */}
          {context && (
            <button
              onClick={continueSession}
              className="w-full text-left bg-white/70 backdrop-blur-xl rounded-2xl p-5 shadow-lg border border-white/50 transition-all duration-300 hover:shadow-xl hover:-translate-y-1 hover:bg-white/80 group"
              style={{ animation: "fadeInUp 0.5s ease-out 0.2s both" }}
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-pink-500 to-pink-600 flex items-center justify-center shadow-lg shadow-pink-200 group-hover:scale-110 transition-transform">
                  <MessageIcon className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1">
                  <h2 className="font-semibold text-gray-900">대화 이어하기</h2>
                  <p className="text-sm text-gray-500">
                    {context.place}에서 {context.interactionPartner}와 대화 중
                  </p>
                </div>
                <div className="w-8 h-8 rounded-full bg-pink-100 flex items-center justify-center group-hover:bg-pink-200 transition-colors">
                  <svg
                    className="w-4 h-4 text-pink-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            </button>
          )}
        </div>

        {/* 사용자 정보 카드 - 글래스모피즘 */}
        <div
          className="bg-white/70 backdrop-blur-xl rounded-3xl shadow-xl border border-white/50 overflow-hidden"
          style={{ animation: "fadeInUp 0.5s ease-out 0.3s both" }}
        >
          <div className="px-5 py-3 bg-gradient-to-r from-violet-500/10 to-pink-500/10 border-b border-white/30">
            <span className="text-sm font-semibold bg-gradient-to-r from-violet-600 to-pink-600 bg-clip-text text-transparent">
              소통이 정보
            </span>
          </div>
          <div className="divide-y divide-gray-100/50">
            {/* 나이 */}
            <div className="flex items-center gap-3 px-5 py-4">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-400 to-blue-500 flex items-center justify-center shadow-md">
                <CalendarIcon className="w-[18px] h-[18px] text-white" />
              </div>
              <span className="flex-1 text-gray-600">나이</span>
              <span className="text-gray-900 font-semibold">{user?.age}세</span>
            </div>

            {/* 성별 */}
            <div className="flex items-center gap-3 px-5 py-4">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-400 to-emerald-500 flex items-center justify-center shadow-md">
                <GenderIcon className="w-[18px] h-[18px] text-white" />
              </div>
              <span className="flex-1 text-gray-600">성별</span>
              <span className="text-gray-900 font-semibold">{user?.gender}</span>
            </div>

            {/* 장애 유형 */}
            <div className="flex items-center gap-3 px-5 py-4">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center shadow-md">
                <TagIcon className="w-[18px] h-[18px] text-white" />
              </div>
              <span className="flex-1 text-gray-600">장애 유형</span>
              <span className="text-gray-900 font-semibold">{user?.disabilityType}</span>
            </div>

            {/* 관심 주제 */}
            <div className="px-5 py-4">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-rose-400 to-pink-500 flex items-center justify-center shadow-md">
                  <StarIcon className="w-[18px] h-[18px] text-white" />
                </div>
                <span className="text-gray-600">관심 주제</span>
              </div>
              <div className="flex flex-wrap gap-2 ml-12">
                {user?.interestingTopics.map((topic, index) => (
                  <span
                    key={topic}
                    className="px-3 py-1.5 rounded-full text-sm font-medium text-violet-700 shadow-sm"
                    style={{
                      background: "linear-gradient(135deg, #EDE9FE 0%, #FCE7F3 100%)",
                      animation: `fadeInUp 0.3s ease-out ${0.4 + index * 0.05}s both`,
                    }}
                  >
                    {topic}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* 애니메이션 keyframes */}
      <style jsx>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
}
