/**
 * 대시보드 페이지 - 서브컴포넌트 활용
 */

"use client";

import { useState } from "react";
import { useAuth } from "@/hooks/use-auth";
import { useContext } from "@/hooks/use-context";
import { ContextForm } from "@/components/context/context-form";
import { ChatPlusIcon, MessageIcon } from "@/components/ui/icons";
import {
  DashboardHeader,
  WelcomeCard,
  ActionCard,
  InfoCard,
} from "@/components/dashboard";

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
          <div className="bg-white/70 backdrop-blur-xl rounded-3xl shadow-xl border border-white/50 overflow-hidden animate-fade-in-up">
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
      <DashboardHeader onLogout={logout} />

      <main className="max-w-lg mx-auto px-4 py-6 space-y-5">
        <WelcomeCard userName={user?.name || ""} />

        {/* 액션 카드들 */}
        <div className="space-y-3">
          <ActionCard
            onClick={handleNewSession}
            icon={<ChatPlusIcon className="w-6 h-6 text-white" />}
            iconBgColor="bg-violet-500"
            title="새 대화 시작"
            description="새로운 상황에서 대화하기"
            arrowBgColor="bg-violet-100 group-hover:bg-violet-200"
            arrowColor="text-violet-600"
            animationDelay="0.1s"
          />

          {context && (
            <ActionCard
              onClick={continueSession}
              icon={<MessageIcon className="w-6 h-6 text-white" />}
              iconBgColor="bg-rose-500"
              title="대화 이어하기"
              description={`${context.place}에서 ${context.interactionPartner}와 대화 중`}
              arrowBgColor="bg-pink-100 group-hover:bg-pink-200"
              arrowColor="text-pink-600"
              animationDelay="0.2s"
            />
          )}
        </div>

        <InfoCard
          age={user?.age}
          gender={user?.gender}
          disabilityType={user?.disabilityType}
          interestingTopics={user?.interestingTopics}
        />
      </main>

    </div>
  );
}
