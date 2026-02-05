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

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const { context, continueSession, startNewSession } = useContext();
  const [showContextForm, setShowContextForm] = useState(false);

  const handleNewSession = () => {
    startNewSession();
    setShowContextForm(true);
  };

  if (showContextForm) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-partner-50 to-partner-100 p-4">
        <div className="max-w-md mx-auto pt-8">
          <Card>
            <CardContent className="p-6">
              <ContextForm onCancel={() => setShowContextForm(false)} />
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-partner-50 to-partner-100">
      {/* 헤더 */}
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 relative">
              <Image
                src="/images/logo.png"
                alt="Logo"
                fill
                className="object-contain"
              />
            </div>
            <span className="font-bold text-partner-700">소통, 이룸</span>
          </div>
          <Button variant="ghost" onClick={logout}>
            로그아웃
          </Button>
        </div>
      </header>

      {/* 메인 콘텐츠 */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* 환영 메시지 */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              안녕하세요, {user?.name}님!
            </h1>
            <p className="text-gray-600">
              오늘도 소통이와 함께 즐거운 대화를 나눠보세요.
            </p>
          </CardContent>
        </Card>

        {/* 세션 관리 */}
        <div className="grid gap-4 md:grid-cols-2">
          {/* 새 세션 시작 */}
          <Card className="card-hover cursor-pointer" onClick={handleNewSession}>
            <CardContent className="p-6 text-center">
              <div className="w-16 h-16 mx-auto mb-4 bg-partner-100 rounded-full flex items-center justify-center">
                <svg
                  className="w-8 h-8 text-partner-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 4v16m8-8H4"
                  />
                </svg>
              </div>
              <h2 className="text-lg font-semibold text-gray-900 mb-2">
                새 대화 시작
              </h2>
              <p className="text-sm text-gray-600">
                새로운 상황에서 대화를 시작합니다
              </p>
            </CardContent>
          </Card>

          {/* 이어하기 */}
          {context && (
            <Card
              className="card-hover cursor-pointer"
              onClick={continueSession}
            >
              <CardContent className="p-6 text-center">
                <div className="w-16 h-16 mx-auto mb-4 bg-communicator-100 rounded-full flex items-center justify-center">
                  <svg
                    className="w-8 h-8 text-communicator-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                    />
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </div>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">
                  대화 이어하기
                </h2>
                <p className="text-sm text-gray-600">
                  {context.place}에서 {context.interactionPartner}와(과) 대화 중
                </p>
              </CardContent>
            </Card>
          )}
        </div>

        {/* 사용자 정보 */}
        <Card className="mt-6">
          <CardContent className="p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              소통이 정보
            </h2>
            <div className="grid gap-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">나이</span>
                <span className="text-gray-900">{user?.age}세</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">성별</span>
                <span className="text-gray-900">{user?.gender}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">장애 유형</span>
                <span className="text-gray-900">{user?.disabilityType}</span>
              </div>
              <div>
                <span className="text-gray-500 block mb-1">관심 주제</span>
                <div className="flex flex-wrap gap-1">
                  {user?.interestingTopics.map((topic) => (
                    <span
                      key={topic}
                      className="px-2 py-0.5 bg-partner-100 text-partner-700 rounded-full text-xs"
                    >
                      {topic}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
