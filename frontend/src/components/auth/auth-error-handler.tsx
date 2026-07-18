"use client";

import { useAuth0 } from "@auth0/auth0-react";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

/** Wipe all Auth0 PKCE transaction entries from both storages. */
function clearAuth0State() {
  try {
    [sessionStorage, localStorage].forEach((storage) => {
      Object.keys(storage)
        .filter((k) => k.startsWith("a0.spajs"))
        .forEach((k) => storage.removeItem(k));
    });
  } catch {
    // storage may be unavailable in some browser contexts — ignore
  }
}

export function AuthErrorHandler() {
  const { error } = useAuth0();
  const router = useRouter();

  useEffect(() => {
    if (!error) return;

    // "Invalid state" = stale PKCE state (sessionStorage) doesn't match the
    // ?code=&state= params Auth0 returned. Clear Auth0 storage entries and
    // redirect to home so the user gets a clean URL and can retry.
    if (error.message === "Invalid state") {
      clearAuth0State();
      router.replace("/");
      return;
    }

    console.error("Auth0 Error:", error);
    toast.error(`Auth error: ${error.message}`);
  }, [error, router]);

  return null;
}
