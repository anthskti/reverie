"use client";

import { useAuth0 } from "@auth0/auth0-react";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useApiClient } from "@/lib/auth/use-api-client";
import { getMyItems, getMyStats } from "@/lib/api/inventory";
import { getProjects } from "@/lib/api/projects";
import { buildGamificationProfile } from "@/lib/gamification";
import type { Item, UserStats } from "@/lib/types";
import {
  BadgeGrid,
  GamificationHeader,
  ImpactStats,
} from "@/components/gamification/impact-stats";
import { InventoryGrid } from "@/components/inventory/item-card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import type { ApiError } from "@/lib/types";

export default function ProfilePage() {
  const { user } = useAuth0();
  const { getToken, isAuthenticated } = useApiClient();
  const [stats, setStats] = useState<UserStats | null>(null);
  const [items, setItems] = useState<Item[]>([]);
  const [projectsCount, setProjectsCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) return;

    async function load() {
      try {
        const token = await getToken();
        const [statsData, itemsData, projectsData] = await Promise.all([
          getMyStats(token),
          getMyItems(token),
          getProjects(token),
        ]);
        setStats(statsData);
        setItems(itemsData);
        setProjectsCount(projectsData.projects.length);
      } catch (error) {
        const apiError = error as ApiError;
        toast.error(apiError.message ?? "Failed to load profile");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [getToken, isAuthenticated]);

  if (loading) {
    return (
      <div className="mx-auto max-w-6xl space-y-6 px-4 py-8">
        <Skeleton className="h-40 w-full" />
        <div className="grid gap-4 sm:grid-cols-3">
          <Skeleton className="h-24" />
          <Skeleton className="h-24" />
          <Skeleton className="h-24" />
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="mx-auto max-w-6xl px-4 py-8 text-center">
        <p>Could not load profile data.</p>
      </div>
    );
  }

  const hasListed =
    typeof window !== "undefined" &&
    sessionStorage.getItem("reverie_has_listed") === "1";

  const gamification = buildGamificationProfile(stats, projectsCount, {
    hasListed,
    bestVerificationScore: Number(
      typeof window !== "undefined"
        ? sessionStorage.getItem("reverie_best_verification_score") ?? 0
        : 0,
    ),
  });

  return (
    <div className="mx-auto max-w-6xl space-y-8 px-4 py-8">
      <GamificationHeader
        profile={gamification}
        displayName={user?.name ?? user?.nickname ?? undefined}
      />

      <div className="flex flex-wrap gap-3">
        <Button asChild>
          <Link href="/upcycle">New upcycle</Link>
        </Button>
        <Button asChild variant="outline">
          <Link href="/projects">View projects</Link>
        </Button>
        <Button asChild variant="outline">
          <Link href="/marketplace/sell">Sell an item</Link>
        </Button>
      </div>

      <section>
        <h2 className="mb-4 text-xl font-semibold">Your impact</h2>
        <ImpactStats
          water={stats.water_saved_l}
          co2={stats.co2_offset_kg}
          landfill={stats.landfill_diverted_kg}
        />
      </section>

      <section>
        <h2 className="mb-4 text-xl font-semibold">Achievements</h2>
        <BadgeGrid badges={gamification.badges} />
      </section>

      <section>
        <h2 className="mb-4 text-xl font-semibold">Wardrobe inventory</h2>
        <InventoryGrid items={items} />
      </section>
    </div>
  );
}
