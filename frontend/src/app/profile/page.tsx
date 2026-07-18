"use client";

import { useAuth0 } from "@auth0/auth0-react";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useApiClient } from "@/lib/auth/use-api-client";
import { getMyItems, getMyStats } from "@/lib/api/inventory";
import { getProjects } from "@/lib/api/projects";
import { buildGamificationProfile } from "@/lib/gamification";
import type { Item, UserStats, Project, ApiError } from "@/lib/types";
import {
  BadgeGrid,
  GamificationHeader,
  ImpactStats,
} from "@/components/gamification/impact-stats";
import { InventoryGrid } from "@/components/inventory/item-card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import { useAuthModal } from "@/components/providers/auth-modal-provider";

export default function ProfilePage() {
  const { user } = useAuth0();
  const { getToken, isAuthenticated, isLoading: authLoading } = useApiClient();
  const { openAuthModal } = useAuthModal();
  const [stats, setStats] = useState<UserStats | null>(null);
  const [items, setItems] = useState<Item[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading) return;
    if (!isAuthenticated) {
      openAuthModal();
      return;
    }

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
        setProjects(projectsData.projects);
      } catch (error) {
        const apiError = error as ApiError;
        toast.error(apiError.message ?? "Failed to load profile");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [getToken, isAuthenticated, openAuthModal, authLoading]);

  if (authLoading) {
    return (
      <div className="mx-auto max-w-6xl space-y-6 px-4 py-8">
        <Skeleton className="h-40 w-full" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="flex min-h-[50vh] flex-col items-center justify-center space-y-4 px-4 text-center">
        <h1 className="text-2xl font-bold">Please log in</h1>
        <p className="text-muted-foreground">You need to log in to view your profile.</p>
        <Button onClick={() => openAuthModal()}>Log In</Button>
      </div>
    );
  }

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

  const gamification = buildGamificationProfile(stats, projects.length, {
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
          <Link href="/marketplace/sell">Sell an item</Link>
        </Button>
      </div>

      <Tabs defaultValue="stats" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="stats">Impact & Stats</TabsTrigger>
          <TabsTrigger value="inventory">Inventory</TabsTrigger>
          <TabsTrigger value="projects">Projects</TabsTrigger>
        </TabsList>

        <TabsContent value="stats" className="mt-6 space-y-8">
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
        </TabsContent>

        <TabsContent value="inventory" className="mt-6">
          <h2 className="mb-4 text-xl font-semibold">Wardrobe inventory</h2>
          <InventoryGrid items={items} />
        </TabsContent>

        <TabsContent value="projects" className="mt-6">
          <h2 className="mb-4 text-xl font-semibold">Your projects</h2>
          {projects.length === 0 ? (
            <div className="mt-4 rounded-xl border border-dashed p-12 text-center">
              <p className="text-muted-foreground">No projects yet.</p>
              <Link href="/upcycle" className="mt-4 inline-block text-primary hover:underline">
                Start upcycling →
              </Link>
            </div>
          ) : (
            <div className="mt-4 grid gap-4">
              {projects.map((project) => (
                <Link key={project.id} href={`/projects/${project.id}`}>
                  <Card className="transition-shadow hover:shadow-md">
                    <CardHeader className="flex flex-row items-start justify-between">
                      <div>
                        <CardTitle className="text-lg">
                          {project.selected_concept?.title ?? "Upcycle project"}
                        </CardTitle>
                        <p className="text-sm text-muted-foreground">
                          {project.created_at
                            ? new Date(project.created_at).toLocaleDateString()
                            : "Unknown date"}
                        </p>
                      </div>
                      <Badge variant="outline" className="capitalize">
                        {project.selected_concept?.difficulty ?? "n/a"}
                      </Badge>
                    </CardHeader>
                    {project.environmental_impact && (
                      <CardContent>
                        <p className="line-clamp-2 text-sm text-muted-foreground">
                          {project.environmental_impact}
                        </p>
                      </CardContent>
                    )}
                  </Card>
                </Link>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
