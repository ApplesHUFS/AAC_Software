/**
 * 피드백 관련 타입 정의
 */

export interface ContextSummary {
  time: string;
  place: string;
  interactionPartner?: string;
  currentActivity: string;
}

export interface FeedbackRequestBody {
  userId: string;
  cards: string[];
  context: ContextSummary;
  interpretations: string[];
  partnerInfo: string;
}

export interface InterpretationOption {
  index: number;
  interpretation: string;
}

export interface ConfirmationRequest {
  confirmationId: string;
  userContext: ContextSummary;
  selectedCards: string[];
  interpretationOptions: InterpretationOption[];
  partner: string;
}

export interface FeedbackRequestResponse {
  confirmationId: string;
  confirmationRequest: ConfirmationRequest;
}

export interface FeedbackSubmitRequest {
  confirmationId: string;
  selectedInterpretationIndex?: number;
  directFeedback?: string;
}

export interface FeedbackResult {
  feedbackType: "interpretation_selected" | "direct_feedback";
  selectedIndex?: number;
  selectedInterpretation?: string;
  directFeedback?: string;
  confirmationId: string;
  userId: string;
  cards: string[];
  context: Record<string, string>;
  interpretations: string[];
  partnerInfo: string;
  confirmedAt: string;
}

export interface FeedbackSubmitResponse {
  feedbackResult: FeedbackResult;
}
