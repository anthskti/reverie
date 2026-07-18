import { apiFetch } from "./client";
import type { GlobalStats } from "@/lib/types";

export function getGlobalStats(): Promise<GlobalStats> {
  return apiFetch<GlobalStats>("/api/stats/global");
}
