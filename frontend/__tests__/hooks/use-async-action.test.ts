import { renderHook, act, waitFor } from "@testing-library/react";
import { useAsyncAction } from "@/hooks/use-async-action";

describe("useAsyncAction", () => {
  it("초기 상태가 올바르게 설정됨", () => {
    const { result } = renderHook(() => useAsyncAction());

    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(result.current.data).toBeNull();
  });

  it("성공적인 비동기 작업 실행", async () => {
    const { result } = renderHook(() => useAsyncAction<string>());
    const mockData = "테스트 데이터";

    await act(async () => {
      const response = await result.current.execute(async () => mockData);
      expect(response).toBe(mockData);
    });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(result.current.data).toBe(mockData);
  });

  it("실패한 비동기 작업의 에러 처리", async () => {
    const { result } = renderHook(() => useAsyncAction());
    const errorMessage = "에러 발생";

    await act(async () => {
      await result.current.execute(async () => {
        throw new Error(errorMessage);
      });
    });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe(errorMessage);
    expect(result.current.data).toBeNull();
  });

  it("clearError가 에러 상태를 초기화함", async () => {
    const { result } = renderHook(() => useAsyncAction());

    await act(async () => {
      await result.current.execute(async () => {
        throw new Error("에러");
      });
    });

    expect(result.current.error).not.toBeNull();

    act(() => {
      result.current.clearError();
    });

    expect(result.current.error).toBeNull();
  });

  it("reset이 모든 상태를 초기화함", async () => {
    const { result } = renderHook(() => useAsyncAction<string>());

    await act(async () => {
      await result.current.execute(async () => "데이터");
    });

    expect(result.current.data).toBe("데이터");

    act(() => {
      result.current.reset();
    });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(result.current.data).toBeNull();
  });
});
