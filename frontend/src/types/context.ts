/**
 * 컨텍스트 관련 타입 정의
 */

export interface Context {
  contextId: string;
  userId: string;
  time: string;
  place: string;
  interactionPartner: string;
  currentActivity: string;
  createdAt?: string;
}

export interface CreateContextRequest {
  userId: string;
  place: string;
  interactionPartner: string;
  currentActivity?: string;
}
