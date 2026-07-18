"use client";

import { useAuth0 } from "@auth0/auth0-react";
import { useEffect } from "react";

export function AuthSessionSync() {
  const { isAuthenticated, isLoading } = useAuth0();

  useEffect(() => {
    if (isLoading) return;
    if (isAuthenticated) {
      document.cookie = "reverie_auth=1; path=/; max-age=86400; SameSite=Lax";
    } else {
      document.cookie = "reverie_auth=; path=/; max-age=0; SameSite=Lax";
    }
  }, [isAuthenticated, isLoading]);

  return null;
}
