"use client";

import { useAuth0 } from "@auth0/auth0-react";
import { useEffect } from "react";
import { useSearchParams } from "next/navigation";

export function LoginRedirect() {
  const { loginWithRedirect, isAuthenticated, isLoading } = useAuth0();
  const searchParams = useSearchParams();
  const returnTo = searchParams.get("returnTo") ?? "/profile";

  useEffect(() => {
    if (isLoading) return;
    if (isAuthenticated) {
      window.location.href = returnTo;
      return;
    }
    loginWithRedirect({ appState: { returnTo } });
  }, [isAuthenticated, isLoading, loginWithRedirect, returnTo]);

  return (
    <div className="flex min-h-[50vh] items-center justify-center">
      <p className="text-muted-foreground">Redirecting to login…</p>
    </div>
  );
}
