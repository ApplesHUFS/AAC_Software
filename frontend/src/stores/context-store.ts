/**
 * 컨텍스트 상태 관리 (Zustand)
 */

import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { Context } from "@/types/context";

interface ContextState {
  context: Context | null;

  // Actions
  setContext: (context: Context) => void;
  clearContext: () => void;
}

export const useContextStore = create<ContextState>()(
  persist(
    (set) => ({
      context: null,

      setContext: (context) => set({ context }),
      clearContext: () => set({ context: null }),
    }),
    {
      name: "aac-context-storage",
      storage: createJSONStorage(() => sessionStorage),
    }
  )
);
