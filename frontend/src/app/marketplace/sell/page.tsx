import { Suspense } from "react";
import SellPage from "./sell-client";

export default function Page() {
  return (
    <Suspense fallback={<div className="p-8">Loading…</div>}>
      <SellPage />
    </Suspense>
  );
}
