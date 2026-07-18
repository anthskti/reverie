"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useAuth0 } from "@auth0/auth0-react";
import {
  getListing,
  checkout,
  confirmPayment,
  settle,
  updateListing,
} from "@/lib/api/marketplace";
import { useApiClient } from "@/lib/auth/use-api-client";
import type { ApiError, DepositSession, Listing } from "@/lib/types";
import { formatUsdc, resolveMediaUrl, truncateId } from "@/lib/utils";
import {
  getListingStatusMessage,
  ListingStatusTimeline,
} from "@/components/marketplace/listing-status";
import { UnifoldSandboxCheckout } from "@/components/marketplace/unifold-sandbox-checkout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";

function decodeSub(token: string): string | null {
  try {
    const payload = token.split(".")[1];
    if (!payload) return null;
    const json = JSON.parse(atob(payload.replace(/-/g, "+").replace(/_/g, "/")));
    return json.sub ?? null;
  } catch {
    return null;
  }
}

export default function ListingDetailPage() {
  const params = useParams<{ listingId: string }>();
  const { isAuthenticated } = useAuth0();
  const { getToken } = useApiClient();
  const [listing, setListing] = useState<Listing | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [userSub, setUserSub] = useState<string | null>(null);
  const [sandboxOpen, setSandboxOpen] = useState(false);
  const [deposit, setDeposit] = useState<DepositSession | null>(null);
  const [confirming, setConfirming] = useState(false);

  const loadListing = async () => {
    try {
      const data = await getListing(params.listingId);
      setListing(data);
    } catch (error) {
      toast.error((error as ApiError).message ?? "Listing not found");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadListing();
  }, [params.listingId]);

  useEffect(() => {
    if (!isAuthenticated) return;
    getToken().then((token) => setUserSub(decodeSub(token)));
  }, [getToken, isAuthenticated]);

  const handleCheckout = async () => {
    if (!listing) return;
    setActionLoading(true);
    try {
      const token = await getToken();
      const result = await checkout(token, listing.listing_id);
      setDeposit(result.deposit);
      setSandboxOpen(true);
      await loadListing();
    } catch (error) {
      toast.error((error as ApiError).message ?? "Checkout failed");
    } finally {
      setActionLoading(false);
    }
  };

  const handleConfirmSandboxPayment = async () => {
    if (!listing) return;
    setConfirming(true);
    try {
      const token = await getToken();
      const result = await confirmPayment(token, listing.listing_id);
      toast.success(result.message);
      setSandboxOpen(false);
      setDeposit(null);
      await loadListing();
    } catch (error) {
      toast.error((error as ApiError).message ?? "Sandbox payment failed");
    } finally {
      setConfirming(false);
    }
  };

  const handleSettle = async () => {
    if (!listing) return;
    setActionLoading(true);
    try {
      const token = await getToken();
      await settle(token, listing.listing_id);
      toast.success("Purchase settled. Sandbox payout recorded for seller.");
      await loadListing();
    } catch (error) {
      toast.error((error as ApiError).message ?? "Settlement failed");
    } finally {
      setActionLoading(false);
    }
  };

  const handleCancel = async () => {
    if (!listing) return;
    setActionLoading(true);
    try {
      const token = await getToken();
      await updateListing(token, listing.listing_id, { status: "cancelled" });
      toast.success("Listing cancelled");
      await loadListing();
    } catch (error) {
      toast.error((error as ApiError).message ?? "Could not cancel listing");
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="mx-auto max-w-4xl space-y-4 px-4 py-8">
        <Skeleton className="aspect-[4/3] w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }

  if (!listing) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-8 text-center">
        <p>Listing not found.</p>
        <Button asChild className="mt-4">
          <Link href="/marketplace">Back to marketplace</Link>
        </Button>
      </div>
    );
  }

  const imageUrl = resolveMediaUrl(listing.item_image_url);
  const isSeller = userSub === listing.seller_id;
  const isBuyer = userSub === listing.buyer_id;
  const statusMessage = getListingStatusMessage(listing, isBuyer);

  return (
    <div className="mx-auto max-w-4xl space-y-6 px-4 py-8">
      <Button asChild variant="ghost" size="sm">
        <Link href="/marketplace">← Marketplace</Link>
      </Button>

      <div className="grid gap-8 md:grid-cols-2">
        <div className="relative aspect-square overflow-hidden rounded-xl bg-muted">
          {imageUrl ? (
            <Image
              src={imageUrl}
              alt={listing.title}
              fill
              className="object-cover"
              unoptimized
            />
          ) : (
            <div className="flex h-full items-center justify-center text-4xl text-muted-foreground">
              {listing.title.charAt(0)}
            </div>
          )}
        </div>

        <div className="space-y-4">
          <div>
            <Badge variant="outline" className="mb-2 capitalize">
              {listing.category.replace("_", " ")}
            </Badge>
            <h1 className="text-3xl font-black text-primary">{listing.title}</h1>
            <p className="mt-2 text-2xl font-bold text-primary">
              {formatUsdc(listing.price_usdc)}
            </p>
          </div>

          {listing.description && (
            <p className="text-muted-foreground">{listing.description}</p>
          )}

          <p className="text-sm text-muted-foreground">
            Seller: {truncateId(listing.seller_id)}
          </p>

          <ListingStatusTimeline status={listing.status} />

          {statusMessage && (
            <Card className="border-primary/20 bg-accent/15">
              <CardContent className="p-4 text-sm">{statusMessage}</CardContent>
            </Card>
          )}

          <div className="flex flex-wrap gap-3">
            {listing.status === "active" && !isSeller && (
              <Button onClick={handleCheckout} disabled={actionLoading || !isAuthenticated}>
                {actionLoading && <Loader2 className="animate-spin" />}
                {isAuthenticated ? "Buy now" : "Log in to buy"}
              </Button>
            )}
            {listing.status === "pending_payment" && isBuyer && (
              <Button
                onClick={() => {
                  setDeposit({
                    mode: "sandbox",
                    session_id: `uf_resume_${listing.listing_id.slice(0, 8)}`,
                    external_user_id: listing.buyer_id ?? "",
                    recipient_address: "0x606C49ca2Fa4982F07016265040F777eD3DA3160",
                    destination_chain_type: "ethereum",
                    destination_chain_id: "8453",
                    destination_token_address:
                      "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
                    destination_token_symbol: "USDC",
                    amount_usdc: listing.price_usdc,
                    listing_id: listing.listing_id,
                    seller_id: listing.seller_id,
                  });
                  setSandboxOpen(true);
                }}
                disabled={actionLoading}
              >
                Complete sandbox payment
              </Button>
            )}
            {listing.status === "locked_in_escrow" && isBuyer && (
              <Button onClick={handleSettle} disabled={actionLoading}>
                {actionLoading && <Loader2 className="animate-spin" />}
                Mark as received
              </Button>
            )}
            {isSeller && listing.status === "active" && (
              <Button
                variant="destructive"
                onClick={handleCancel}
                disabled={actionLoading}
              >
                Cancel listing
              </Button>
            )}
          </div>
        </div>
      </div>

      <UnifoldSandboxCheckout
        open={sandboxOpen}
        deposit={deposit}
        listingTitle={listing.title}
        confirming={confirming}
        onConfirm={handleConfirmSandboxPayment}
        onCancel={() => {
          if (confirming) return;
          setSandboxOpen(false);
        }}
      />
    </div>
  );
}
