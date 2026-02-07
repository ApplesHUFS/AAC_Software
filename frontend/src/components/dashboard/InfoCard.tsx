/**
 * 사용자 정보 카드 컴포넌트
 */

import { ReactNode, CSSProperties } from "react";
import {
  CalendarIcon,
  GenderIcon,
  TagIcon,
  StarIcon,
} from "@/components/ui/icons";

interface InfoRowProps {
  icon: ReactNode;
  iconBgColor: string;
  label: string;
  value: string;
}

function InfoRow({ icon, iconBgColor, label, value }: InfoRowProps) {
  return (
    <div className="flex items-center gap-3 px-5 py-4">
      <div
        className={`w-9 h-9 rounded-xl ${iconBgColor} flex items-center justify-center shadow-md`}
      >
        {icon}
      </div>
      <span className="flex-1 text-gray-600">{label}</span>
      <span className="text-gray-900 font-semibold">{value}</span>
    </div>
  );
}

interface InfoCardProps {
  age?: number;
  gender?: string;
  disabilityType?: string;
  interestingTopics?: string[];
}

export function InfoCard({
  age,
  gender,
  disabilityType,
  interestingTopics = [],
}: InfoCardProps) {
  const cardStyle: CSSProperties = {
    animationDelay: "0.3s",
    animationFillMode: "both",
  };

  return (
    <div
      className="bg-white/70 backdrop-blur-xl rounded-3xl shadow-xl border border-white/50 overflow-hidden animate-fade-in-up"
      style={cardStyle}
    >
      <div className="px-5 py-3 bg-violet-50 border-b border-violet-100">
        <span className="text-sm font-semibold text-violet-600">
          소통이 정보
        </span>
      </div>
      <div className="divide-y divide-gray-100/50">
        <InfoRow
          icon={<CalendarIcon className="w-[18px] h-[18px] text-white" />}
          iconBgColor="bg-blue-500"
          label="나이"
          value={`${age}세`}
        />
        <InfoRow
          icon={<GenderIcon className="w-[18px] h-[18px] text-white" />}
          iconBgColor="bg-emerald-500"
          label="성별"
          value={gender || ""}
        />
        <InfoRow
          icon={<TagIcon className="w-[18px] h-[18px] text-white" />}
          iconBgColor="bg-amber-500"
          label="장애 유형"
          value={disabilityType || ""}
        />
        <div className="px-5 py-4">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-9 h-9 rounded-xl bg-rose-500 flex items-center justify-center shadow-md">
              <StarIcon className="w-[18px] h-[18px] text-white" />
            </div>
            <span className="text-gray-600">관심 주제</span>
          </div>
          <div className="flex flex-wrap gap-2 ml-12">
            {interestingTopics.map((topic, index) => {
              const topicStyle: CSSProperties = {
                animationDelay: `${0.4 + index * 0.05}s`,
                animationFillMode: "both",
              };
              return (
                <span
                  key={topic}
                  className="px-3 py-1.5 rounded-full text-sm font-medium bg-violet-100 text-violet-700 animate-fade-in-up"
                  style={topicStyle}
                >
                  {topic}
                </span>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
