import { apiFetch } from "./client";
import type { Item, UserStats } from "@/lib/types";

export function getMyStats(token: string): Promise<UserStats> {
  return apiFetch<UserStats>("/api/inventory/me/stats", { token });
}

export function getMyItems(token: string): Promise<Item[]> {
  return apiFetch<Item[]>("/api/inventory/me", { token });
}

export function getItem(token: string, itemId: string): Promise<Item> {
  return apiFetch<Item>(`/api/inventory/${itemId}`, { token });
}
