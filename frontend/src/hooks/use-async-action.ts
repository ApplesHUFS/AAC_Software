/**
 * 비동기 액션 공통 훅
 * 로딩/에러 상태 관리를 통합 제공
 */

import { useState, useCallback } from "react";

interface AsyncActionState<T> {
  isLoading: boolean;
  error: string | null;
  data: T | null;
}

interface AsyncActionReturn<T> extends AsyncActionState<T> {
  execute: (action: () => Promise<T>) => Promise<T | null>;
  clearError: () => void;
  reset: () => void;
}

/**
 * 비동기 작업의 로딩/에러 상태를 관리하는 훅
 * @returns 로딩 상태, 에러, 실행 함수, 초기화 함수
 */
export function useAsyncAction<T = unknown>(): AsyncActionReturn<T> {
  const [state, setState] = useState<AsyncActionState<T>>({
    isLoading: false,
    error: null,
    data: null,
  });

  const execute = useCallback(
    async (action: () => Promise<T>): Promise<T | null> => {
      setState((prev) => ({ ...prev, isLoading: true, error: null }));
      try {
        const result = await action();
        setState({ isLoading: false, error: null, data: result });
        return result;
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "오류가 발생했습니다.";
        setState((prev) => ({ ...prev, isLoading: false, error: errorMessage }));
        return null;
      }
    },
    []
  );

  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }));
  }, []);

  const reset = useCallback(() => {
    setState({ isLoading: false, error: null, data: null });
  }, []);

  return {
    isLoading: state.isLoading,
    error: state.error,
    data: state.data,
    execute,
    clearError,
    reset,
  };
}
