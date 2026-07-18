"use client";

import { useAuth0 } from "@auth0/auth0-react";
import { useCallback } from "react";
import type { ApiError } from "@/lib/types";
import { apiFetch, type FetchOptions } from "@/lib/api/client";
import { useAuthModal } from "@/components/providers/auth-modal-provider";

export function useApiClient() {
  const { getAccessTokenSilently, isAuthenticated } = useAuth0();
  const { openAuthModal } = useAuthModal();

  const getToken = useCallback(async (): Promise<string> => {
    if (!isAuthenticated) {
      throw { message: "Not authenticated", status: 401 } satisfies ApiError;
    }
    return getAccessTokenSilently();
  }, [getAccessTokenSilently, isAuthenticated]);

  const authFetch = useCallback(
    async <T,>(path: string, options: Omit<FetchOptions, "token"> = {}) => {
      try {
        const token = await getToken();
        return await apiFetch<T>(path, { ...options, token });
      } catch (error) {
        const apiError = error as ApiError;
        if (apiError.status === 401) {
          openAuthModal();
        }
        throw error;
      }
    },
    [getToken, openAuthModal],
  );

  return { authFetch, getToken, isAuthenticated };
}
