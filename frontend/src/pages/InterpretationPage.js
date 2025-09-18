// src/pages/InterpretationPage.js
import React, { useState, useEffect, useCallback } from "react";
import { cardService } from "../services/cardService";
import { feedbackService } from "../services/feedbackService";
import InterpretationDisplay, {
  InterpretationResult,
} from "../components/interpretation/InterpretationDisplay";

// 해석 진행 단계
const INTERPRETATION_STEPS = {
  INTERPRETING: "interpreting",
  FEEDBACK: "feedback",
  COMPLETED: "completed",
};

// 동적 로딩 상태
const LOADING_STATES = [
  { key: "cards", label: "카드 분석", icon: "/images/card_analysis.png" },
  {
    key: "context",
    label: "상황 고려",
    icon: "/images/context_consideration.png",
  },
  {
    key: "interpretation",
    label: "해석 생성",
    icon: "/images/interpretation_generate.png",
  },
];

const InterpretationPage = ({
  user,
  contextData,
  selectedCards,
  onSessionComplete,
}) => {
  // 해석 관련 상태
  const [interpretations, setInterpretations] = useState([]);
  const [feedbackResult, setFeedbackResult] = useState(null);
  const [confirmationId, setConfirmationId] = useState(null);

  // UI 상태
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [currentStep, setCurrentStep] = useState(
    INTERPRETATION_STEPS.INTERPRETING
  );
  const [interpretationMethod, setInterpretationMethod] = useState("");

  // 동적 로딩 상태
  const [currentLoadingState, setCurrentLoadingState] = useState(0);

  // 로딩 상태 애니메이션
  useEffect(() => {
    let interval;
    if (loading && currentStep === INTERPRETATION_STEPS.INTERPRETING) {
      interval = setInterval(() => {
        setCurrentLoadingState((prev) => (prev + 1) % LOADING_STATES.length);
      }, 2000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [loading, currentStep]);

  // Partner 피드백 확인 요청
  const requestPartnerConfirmation = useCallback(
    async (interpretationData) => {
      try {
        const requestPayload = {
          userId: user.userId,
          cards: selectedCards.map(
            (card) => card.filename || card.name || card
          ),
          context: {
            time: contextData.time,
            place: contextData.place,
            interactionPartner: contextData.interactionPartner,
            currentActivity: contextData.currentActivity,
          },
          interpretations: interpretationData.map(
            (interp) => interp.text || interp
          ),
          partnerInfo: contextData.interactionPartner || "Partner",
        };

        const response = await feedbackService.requestPartnerConfirmation(
          requestPayload
        );

        if (response.success && response.data?.confirmationId) {
          setConfirmationId(response.data.confirmationId);
          setCurrentStep(INTERPRETATION_STEPS.FEEDBACK);
        } else {
          throw new Error(
            response.error || "Partner 확인 요청에 실패했습니다."
          );
        }
      } catch (error) {
        throw error;
      }
    },
    [user.userId, selectedCards, contextData]
  );

  // AI 카드 해석 생성
  const generateInterpretations = useCallback(async () => {
    if (!user?.userId || !selectedCards?.length || !contextData?.contextId) {
      throw new Error("필수 정보가 누락되었습니다.");
    }

    try {
      setLoading(true);
      setError("");

      const response = await cardService.interpretCards(
        user.userId,
        selectedCards,
        contextData.contextId
      );

      if (response.success && response.data) {
        const interpretationData = response.data.interpretations || [];
        const method = response.data.method || "ai";

        setInterpretations(interpretationData);
        setInterpretationMethod(method);

        // 해석 생성 후 즉시 Partner 피드백 요청
        await requestPartnerConfirmation(interpretationData);
      } else {
        throw new Error(response.error || "서버에서 해석 생성을 거부했습니다.");
      }
    } catch (error) {
      throw error;
    }
  }, [user, selectedCards, contextData, requestPartnerConfirmation]);

  // 컴포넌트 마운트 시 해석 생성 시작
  useEffect(() => {
    let isCancelled = false;

    const runInterpretation = async () => {
      try {
        if (!isCancelled) {
          await generateInterpretations();
        }
      } catch (error) {
        if (!isCancelled) {
          setError(error.message);
        }
      } finally {
        if (!isCancelled) {
          setLoading(false);
        }
      }
    };

    runInterpretation();

    return () => {
      isCancelled = true;
    };
  }, [generateInterpretations]);

  // Partner 피드백 제출 완료 처리
  const handleFeedbackSubmit = useCallback((feedbackResponse) => {
    if (feedbackResponse?.data?.feedbackResult) {
      setFeedbackResult(feedbackResponse.data.feedbackResult);
      setCurrentStep(INTERPRETATION_STEPS.COMPLETED);
    } else {
      setError("피드백 처리 중 오류가 발생했습니다.");
    }
  }, []);

  // 새 대화 세션 시작
  const handleStartNewSession = useCallback(() => {
    onSessionComplete();
  }, [onSessionComplete]);

  // 해석 재시도
  const handleRetry = useCallback(() => {
    setError("");
    setLoading(true);
    setCurrentStep(INTERPRETATION_STEPS.INTERPRETING);
    setInterpretations([]);
    setConfirmationId(null);
    setFeedbackResult(null);
    setCurrentLoadingState(0);

    generateInterpretations().catch((error) => {
      setError(error.message);
      setLoading(false);
    });
  }, [generateInterpretations]);

  // 로딩 상태 (AI 해석 생성 중)
  if (loading && currentStep === INTERPRETATION_STEPS.INTERPRETING) {
    return (
      <div className="interpretation-page partner-theme loading">
        <div className="loading-content partner-loading">
          <div className="loading-header">
            <h2>AI가 소통이의 카드를 분석하고 있어요</h2>
          </div>
          <div className="loading-details">
            <p>
              선택하신 <strong>{selectedCards.length}개</strong>의 카드를 꼼꼼히
              살펴보고 있어요.👀
            </p>
            <div className="selected-cards-preview">
              {selectedCards.slice(0, 3).map((card, index) => (
                <span key={index} className="card-preview-item">
                  {card.name}
                </span>
              ))}
              {selectedCards.length > 3 && (
                <span>외 {selectedCards.length - 3}개...</span>
              )}
            </div>
            <p style={{ whiteSpace: "pre-line" }}>
              <strong>{contextData.place}</strong>에서{" "}
              <strong>{contextData.interactionPartner}</strong>와(과)의 대화
              상황을 고려해서{"\n"}가장 적절한 해석 3가지를 만들어드릴게요!
            </p>
          </div>
          <div className="loading-spinner"></div>
          <div className="loading-progress">
            {LOADING_STATES.map((state, index) => (
              <div
                key={state.key}
                className={`progress-step ${
                  index === currentLoadingState
                    ? "active"
                    : index < currentLoadingState
                    ? "completed"
                    : ""
                }`}
              >
                <img src={state.icon} alt="로고" width="16" height="16" />
                {state.label}
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // 에러 상태
  if (error) {
    return (
      <div className="interpretation-page partner-theme error">
        <div className="error-content partner-error">
          <div className="error-header">
            <img
              src="/images/error.png"
              alt="로고"
              width="48"
              height="48"
              className="error-icon"
            />
            <h2>해석 생성에 문제가 발생했어요</h2>
          </div>
          <div className="error-message">{error}</div>

          <div className="error-actions">
            <button className="primary-button" onClick={handleRetry}>
              다시 시도하기
            </button>
            <button
              className="secondary-button"
              onClick={handleStartNewSession}
            >
              새로운 대화 시작
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="interpretation-page partner-theme">
      {/* 통합된 해석 표시 및 피드백 단계 */}
      {currentStep === INTERPRETATION_STEPS.FEEDBACK &&
        interpretations.length > 0 && (
          <InterpretationDisplay
            interpretations={interpretations}
            selectedCards={selectedCards}
            contextInfo={contextData}
            method={interpretationMethod}
            userId={user.userId}
            confirmationId={confirmationId}
            onFeedbackSubmit={handleFeedbackSubmit}
          />
        )}

      {/* 해석 완료 단계 */}
      {currentStep === INTERPRETATION_STEPS.COMPLETED && feedbackResult && (
        <InterpretationResult
          feedbackResult={feedbackResult}
          selectedCards={selectedCards}
          contextInfo={contextData}
          interpretations={interpretations}
          onStartNewSession={handleStartNewSession}
        />
      )}

      {/* 진행 상태 표시 */}
      <div className="interpretation-progress partner-progress">
        <div className="progress-steps">
          <div
            className={`progress-step ${
              currentStep === INTERPRETATION_STEPS.INTERPRETING
                ? "active"
                : "completed"
            }`}
          >
            <span>AI 해석 생성</span>
          </div>
          <div
            className={`progress-step ${
              currentStep === INTERPRETATION_STEPS.FEEDBACK
                ? "active"
                : currentStep === INTERPRETATION_STEPS.COMPLETED
                ? "completed"
                : ""
            }`}
          >
            <span>도움이 확인</span>
          </div>
          <div
            className={`progress-step ${
              currentStep === INTERPRETATION_STEPS.COMPLETED ? "active" : ""
            }`}
          >
            <span>소통 완료</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InterpretationPage;
