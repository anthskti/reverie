import { Suspense } from "react";
import { LoginRedirect } from "@/components/auth/login-redirect";

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="p-8 text-center">Loading…</div>}>
      <LoginRedirect />
    </Suspense>
  );
}
