import { Suspense } from "react";
import ListingDetailPage from "./listing-detail-client";

export default function Page() {
  return (
    <Suspense fallback={<div className="p-8">Loading listing…</div>}>
      <ListingDetailPage />
    </Suspense>
  );
}
