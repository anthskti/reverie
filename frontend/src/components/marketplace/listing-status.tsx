import type { Listing } from "@/lib/types";

const statusSteps = [
  { key: "active", label: "Listed" },
  { key: "pending_payment", label: "Payment pending" },
  { key: "locked_in_escrow", label: "In escrow" },
  { key: "sold", label: "Sold" },
];

export function ListingStatusTimeline({ status }: { status: string }) {
  const currentIndex = statusSteps.findIndex((s) => s.key === status);

  return (
    <div className="flex flex-wrap gap-2">
      {statusSteps.map((step, index) => {
        const isActive = index <= currentIndex && currentIndex >= 0;
        const isCurrent = step.key === status;
        return (
          <div
            key={step.key}
            className={`rounded-full px-3 py-1 text-xs font-bold ${
              isCurrent
                ? "bg-primary text-primary-foreground shadow-sm shadow-primary/25"
                : isActive
                  ? "bg-accent text-accent-foreground"
                  : "bg-muted text-muted-foreground"
            }`}
          >
            {step.label}
          </div>
        );
      })}
    </div>
  );
}

export function getListingStatusMessage(listing: Listing, isBuyer: boolean): string | null {
  if (listing.status === "pending_payment" && isBuyer) {
    return "Finish the Unifold sandbox checkout to move this listing into escrow. No real payment is charged.";
  }
  if (listing.status === "locked_in_escrow" && isBuyer) {
    return "Payment is in escrow. Mark as received once your item arrives to release funds to the seller.";
  }
  if (listing.status === "sold") {
    return "This listing has been sold.";
  }
  return null;
}
