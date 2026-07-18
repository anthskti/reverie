import { Suspense } from "react";
import MarketplacePage from "./marketplace-client";

export default function Page() {
  return (
    <Suspense fallback={<div className="p-8">Loading marketplace…</div>}>
      <MarketplacePage />
    </Suspense>
  );
}
