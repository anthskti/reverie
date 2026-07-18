import { apiFetch } from "./client";
import type {
  CheckoutResponse,
  ListItemRequest,
  Listing,
} from "@/lib/types";

export function browseListings(params?: {
  category?: string;
  q?: string;
}): Promise<Listing[]> {
  const search = new URLSearchParams();
  if (params?.category) search.set("category", params.category);
  if (params?.q) search.set("q", params.q);
  const query = search.toString();
  return apiFetch<Listing[]>(
    `/api/marketplace${query ? `?${query}` : ""}`,
  );
}

export function getListing(listingId: string): Promise<Listing> {
  return apiFetch<Listing>(`/api/marketplace/${listingId}`);
}

export function createListing(
  token: string,
  body: ListItemRequest,
): Promise<{ listing_id: string }> {
  return apiFetch<{ listing_id: string }>("/api/marketplace/list", {
    method: "POST",
    token,
    body,
  });
}

export function updateListing(
  token: string,
  listingId: string,
  body: Partial<{
    title: string;
    price_usdc: number;
    description: string;
    status: string;
  }>,
): Promise<Listing> {
  return apiFetch<Listing>(`/api/marketplace/${listingId}`, {
    method: "PATCH",
    token,
    body,
  });
}

export function checkout(
  token: string,
  listingId: string,
): Promise<CheckoutResponse> {
  return apiFetch<CheckoutResponse>(
    `/api/marketplace/checkout/${listingId}`,
    { method: "POST", token },
  );
}

export function settle(
  token: string,
  listingId: string,
): Promise<{ listing_id: string; status: string; message: string }> {
  return apiFetch(`/api/marketplace/settle/${listingId}`, {
    method: "POST",
    token,
  });
}
