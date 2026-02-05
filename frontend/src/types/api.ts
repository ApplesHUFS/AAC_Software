/**
 * API 공통 타입 정의
 */

export interface ApiResponse<T = unknown> {
  success: boolean;
  timestamp: string;
  data: T | null;
  message?: string;
  error?: string;
}

export interface PaginationInfo {
  currentPage: number;
  totalPages: number;
}
