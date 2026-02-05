/**
 * 인증 관련 커스텀 훅
 */

"use client";

import { useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth-store";
import { useContextStore } from "@/stores/context-store";
import { useCardStore } from "@/stores/card-store";
import { authApi } from "@/lib/api/auth";
import { RegisterRequest, LoginRequest, ProfileUpdateRequest } from "@/types/auth";

export function useAuth() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading, setUser, clearUser, setLoading, updateUser } =
    useAuthStore();
  const { clearContext } = useContextStore();
  const { clearCards } = useCardStore();

  /**
   * 회원가입
   */
  const register = useCallback(
    async (data: RegisterRequest) => {
      setLoading(true);
      try {
        const response = await authApi.register(data);
        return response;
      } finally {
        setLoading(false);
      }
    },
    [setLoading]
  );

  /**
   * 로그인
   */
  const login = useCallback(
    async (data: LoginRequest) => {
      setLoading(true);
      try {
        const response = await authApi.login(data);
        if (response.success && response.data) {
          setUser({
            userId: response.data.userId,
            ...response.data.user,
          });
          router.push("/main/dashboard");
        }
        return response;
      } finally {
        setLoading(false);
      }
    },
    [setUser, setLoading, router]
  );

  /**
   * 로그아웃
   */
  const logout = useCallback(() => {
    clearUser();
    clearContext();
    clearCards();
    router.push("/auth/login");
  }, [clearUser, clearContext, clearCards, router]);

  /**
   * 프로필 업데이트
   */
  const updateProfile = useCallback(
    async (data: ProfileUpdateRequest) => {
      if (!user) return null;

      setLoading(true);
      try {
        const response = await authApi.updateProfile(user.userId, data);
        if (response.success) {
          const profileResponse = await authApi.getProfile(user.userId);
          if (profileResponse.success && profileResponse.data) {
            updateUser(profileResponse.data);
          }
        }
        return response;
      } finally {
        setLoading(false);
      }
    },
    [user, setLoading, updateUser]
  );

  return {
    user,
    isAuthenticated,
    isLoading,
    register,
    login,
    logout,
    updateProfile,
  };
}
