"use client";

import { useAuth0 } from "@auth0/auth0-react";
import { useCallback } from "react";
import type { ApiError } from "@/lib/types";
import { apiFetch, type FetchOptions } from "@/lib/api/client";

export function useApiClient() {
  const { getAccessTokenSilently, loginWithRedirect, isAuthenticated } =
    useAuth0();

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
          await loginWithRedirect({
            appState: { returnTo: window.location.pathname },
          });
        }
        throw error;
      }
    },
    [getToken, loginWithRedirect],
  );

  return { authFetch, getToken, isAuthenticated };
}
