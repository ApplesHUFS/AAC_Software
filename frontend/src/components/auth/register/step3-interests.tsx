/**
 * 회원가입 Step 3: 관심사 (의사소통 특성, 관심 주제)
 */

"use client";

import { XIcon } from "@/components/ui/icons";
import { Spinner } from "@/components/ui/spinner";
import { TOPIC_SUGGESTIONS } from "@/lib/constants";
import { Step3Props } from "./types";

export function Step3Interests({
  formData,
  setFormData,
  topicInput,
  setTopicInput,
  isLoading,
  onPrev,
  onAddTopic,
  onRemoveTopic,
  onSubmit,
}: Step3Props) {
  return (
    <fieldset className="space-y-4">
      <legend className="sr-only">관심사 및 의사소통 특성</legend>

      {/* 의사소통 특성 */}
      <div className="relative">
        <label htmlFor="register-communication" className="sr-only">
          의사소통 특성
        </label>
        <textarea
          id="register-communication"
          name="communicationCharacteristics"
          value={formData.communicationCharacteristics}
          onChange={(e) =>
            setFormData({ ...formData, communicationCharacteristics: e.target.value })
          }
          placeholder="의사소통 특성을 설명해주세요"
          rows={3}
          aria-label="의사소통 특성"
          className="w-full px-4 py-4 bg-gray-50/50 border-2 rounded-2xl text-gray-900
                    placeholder:text-gray-400 transition-all duration-200 outline-none resize-none
                    focus:border-violet-500 focus:ring-4 focus:ring-violet-500/20 focus:bg-white
                    border-gray-200 hover:border-gray-300"
        />
      </div>

      {/* 관심 주제 입력 */}
      <div>
        <label
          htmlFor="register-topic-input"
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          관심 주제
        </label>
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <input
              id="register-topic-input"
              type="text"
              value={topicInput}
              onChange={(e) => setTopicInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  onAddTopic();
                }
              }}
              placeholder="관심 주제 입력"
              aria-label="관심 주제 입력"
              aria-describedby="topic-hint"
              className="w-full px-4 py-3 bg-gray-50/50 border-2 rounded-xl text-gray-900
                        placeholder:text-gray-400 transition-all duration-200 outline-none
                        focus:border-violet-500 focus:ring-4 focus:ring-violet-500/20 focus:bg-white
                        border-gray-200 hover:border-gray-300"
            />
          </div>
          <button
            type="button"
            onClick={onAddTopic}
            aria-label="관심 주제 추가"
            className="px-6 py-3 bg-violet-500 text-white font-medium rounded-xl
                       hover:bg-violet-600 active:scale-95 transition-all duration-200"
          >
            추가
          </button>
        </div>
        <p id="topic-hint" className="sr-only">
          Enter 키를 눌러 주제를 추가할 수 있습니다
        </p>

        {/* 추천 주제 칩 */}
        <div className="flex flex-wrap gap-2 mt-3" role="group" aria-label="추천 관심 주제">
          {TOPIC_SUGGESTIONS.map((topic) => (
            <button
              key={topic}
              type="button"
              onClick={() => {
                if (!formData.interestingTopics.includes(topic)) {
                  setFormData({
                    ...formData,
                    interestingTopics: [...formData.interestingTopics, topic],
                  });
                }
              }}
              disabled={formData.interestingTopics.includes(topic)}
              aria-pressed={formData.interestingTopics.includes(topic)}
              className={`px-3 py-1.5 text-sm rounded-full transition-all duration-200
                         ${
                           formData.interestingTopics.includes(topic)
                             ? "bg-violet-100 text-violet-400 cursor-not-allowed"
                             : "bg-gray-100 text-gray-600 hover:bg-violet-100 hover:text-violet-600"
                         }`}
            >
              + {topic}
            </button>
          ))}
        </div>

        {/* 선택된 주제 */}
        {formData.interestingTopics.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-4" role="list" aria-label="선택된 관심 주제">
            {formData.interestingTopics.map((topic) => (
              <span
                key={topic}
                role="listitem"
                className="inline-flex items-center gap-1.5 px-4 py-2 bg-violet-500
                          text-white text-sm font-medium rounded-full shadow-md animate-pop-in"
              >
                {topic}
                <button
                  type="button"
                  onClick={() => onRemoveTopic(topic)}
                  aria-label={`${topic} 삭제`}
                  className="hover:bg-white/20 rounded-full p-0.5 transition-colors"
                >
                  <XIcon className="w-4 h-4" aria-hidden="true" />
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* 버튼 */}
      <div className="flex gap-3 pt-2">
        <button
          type="button"
          onClick={onPrev}
          className="flex-1 py-4 bg-gray-100 text-gray-700 font-semibold rounded-2xl
                     hover:bg-gray-200 active:scale-[0.98] transition-all duration-200"
        >
          이전
        </button>
        <button
          type="submit"
          onClick={onSubmit}
          disabled={isLoading}
          aria-busy={isLoading}
          className="flex-[2] py-4 bg-violet-600 text-white font-semibold rounded-2xl
                     shadow-lg shadow-violet-500/30 hover:bg-violet-700
                     hover:shadow-xl hover:shadow-violet-500/40 hover:scale-[1.02]
                     active:scale-[0.98] transition-all duration-200
                     disabled:opacity-70 disabled:cursor-not-allowed disabled:hover:scale-100
                     relative overflow-hidden"
        >
          {isLoading ? (
            <span className="flex items-center justify-center gap-2">
              <Spinner size="sm" />
              <span>가입 중...</span>
            </span>
          ) : (
            "회원가입 완료"
          )}
        </button>
      </div>
    </fieldset>
  );
}
