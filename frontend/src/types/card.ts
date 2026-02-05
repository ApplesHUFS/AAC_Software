/**
 * 카드 관련 타입 정의
 */

import { PaginationInfo } from "./api";

export interface Card {
  id: string;
  name: string;
  filename: string;
  imagePath: string;
  index: number;
  selected: boolean;
}

export interface CardRecommendRequest {
  userId: string;
  contextId: string;
}

export interface SelectionRules {
  minCards: number;
  maxCards: number;
  totalOptions: number;
}

export interface ContextInfo {
  time: string;
  place: string;
  interactionPartner: string;
  currentActivity: string;
}

export interface CardRecommendResponse {
  cards: Card[];
  totalCards: number;
  contextInfo: ContextInfo;
  selectionRules: SelectionRules;
  pagination: PaginationInfo;
}

export interface CardValidateRequest {
  selectedCards: string[];
  allRecommendedCards: string[];
}

export interface CardValidateResponse {
  valid: boolean;
  selectedCount: number;
}

export interface CardInterpretRequest {
  userId: string;
  contextId: string;
  selectedCards: string[];
}

export interface Interpretation {
  index: number;
  text: string;
  selected: boolean;
}

export interface SelectedCardInfo {
  filename: string;
  name: string;
  imagePath: string;
}

export interface CardInterpretResponse {
  interpretations: Interpretation[];
  feedbackId: number;
  method: string;
  selectedCards: SelectedCardInfo[];
}

export interface HistorySummaryItem {
  pageNumber: number;
  cardCount: number;
  timestamp: string;
}

export interface CardHistoryResponse {
  contextId: string;
  totalPages: number;
  latestPage: number;
  historySummary: HistorySummaryItem[];
}

export interface CardHistoryPageResponse {
  cards: Card[];
  pagination: PaginationInfo;
  timestamp: string;
  contextId: string;
}
