/**
 * 대시보드 페이지
 */

"use client";

import { useState } from "react";
import Image from "next/image";
import { useAuth } from "@/hooks/use-auth";
import { useContext } from "@/hooks/use-context";
import { Button, Card, CardContent } from "@/components/ui";
import { ContextForm } from "@/components/context/context-form";
import { IMAGES } from "@/lib/images";

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
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-md mx-auto pt-8">
          <Card variant="elevated">
            <CardContent className="p-6">
              <ContextForm onCancel={() => setShowContextForm(false)} />
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-8">
      {/* 헤더 */}
      <header className="app-header">
        <div className="max-w-lg mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Image
              src={IMAGES.logo}
              alt="로고"
              width={36}
              height={36}
              className="object-contain"
            />
            <span className="font-bold text-gray-900">소통, 이룸</span>
          </div>
          <Button variant="ghost" size="sm" onClick={logout}>
            로그아웃
          </Button>
        </div>
      </header>

      {/* 메인 콘텐츠 */}
      <main className="max-w-lg mx-auto px-4 py-6 space-y-5">
        {/* 환영 카드 */}
        <div className="app-card p-5 animate-fade-in-up">
          <div className="flex items-center gap-4">
            <div className="icon-container icon-container-lg icon-container-partner">
              <Image src={IMAGES.heart} alt="" width={28} height={28} />
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900">
                안녕하세요, {user?.name}님!
              </h1>
              <p className="text-gray-500 text-sm">
                오늘도 즐거운 대화를 나눠보세요
              </p>
            </div>
          </div>
        </div>

        {/* 액션 카드들 */}
        <div className="space-y-3">
          {/* 새 대화 시작 */}
          <Card
            interactive
            onClick={handleNewSession}
            className="animate-fade-in-up delay-100"
          >
            <CardContent className="p-5 flex items-center gap-4">
              <div className="icon-container icon-container-lg icon-container-partner">
                <Image src={IMAGES.newChat} alt="" width={28} height={28} />
              </div>
              <div className="flex-1">
                <h2 className="font-semibold text-gray-900">새 대화 시작</h2>
                <p className="text-sm text-gray-500">새로운 상황에서 대화하기</p>
              </div>
              <svg
                className="w-5 h-5 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </CardContent>
          </Card>

          {/* 이어하기 */}
          {context && (
            <Card
              interactive
              onClick={continueSession}
              className="animate-fade-in-up delay-200"
            >
              <CardContent className="p-5 flex items-center gap-4">
                <div className="icon-container icon-container-lg icon-container-communicator">
                  <Image src={IMAGES.message} alt="" width={28} height={28} />
                </div>
                <div className="flex-1">
                  <h2 className="font-semibold text-gray-900">대화 이어하기</h2>
                  <p className="text-sm text-gray-500">
                    {context.place}에서 {context.interactionPartner}와 대화 중
                  </p>
                </div>
                <svg
                  className="w-5 h-5 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </CardContent>
            </Card>
          )}
        </div>

        {/* 사용자 정보 */}
        <div className="app-card overflow-hidden animate-fade-in-up delay-300">
          <div className="section-header">소통이 정보</div>
          <div className="divide-y divide-gray-100">
            {/* 나이 */}
            <div className="list-item">
              <Image src={IMAGES.basicInfo} alt="" width={20} height={20} className="opacity-60" />
              <span className="flex-1 text-gray-700">나이</span>
              <span className="text-gray-900 font-medium">{user?.age}세</span>
            </div>

            {/* 성별 */}
            <div className="list-item">
              <Image src={IMAGES.accountInfo2} alt="" width={20} height={20} className="opacity-60" />
              <span className="flex-1 text-gray-700">성별</span>
              <span className="text-gray-900 font-medium">{user?.gender}</span>
            </div>

            {/* 장애 유형 */}
            <div className="list-item">
              <Image src={IMAGES.type} alt="" width={20} height={20} className="opacity-60" />
              <span className="flex-1 text-gray-700">장애 유형</span>
              <span className="text-gray-900 font-medium">{user?.disabilityType}</span>
            </div>

            {/* 관심 주제 */}
            <div className="list-item flex-wrap">
              <Image src={IMAGES.interestTopic} alt="" width={20} height={20} className="opacity-60" />
              <span className="flex-1 text-gray-700">관심 주제</span>
              <div className="w-full mt-2 flex flex-wrap gap-1.5">
                {user?.interestingTopics.map((topic) => (
                  <span
                    key={topic}
                    className="tag tag-partner"
                  >
                    {topic}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
