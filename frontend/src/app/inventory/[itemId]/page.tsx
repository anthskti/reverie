"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useApiClient } from "@/lib/auth/use-api-client";
import { getItem } from "@/lib/api/inventory";
import { getProjects } from "@/lib/api/projects";
import type { ApiError, Item, Project } from "@/lib/types";
import { resolveMediaUrl } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";

export default function InventoryItemPage() {
  const params = useParams<{ itemId: string }>();
  const { getToken, isAuthenticated } = useApiClient();
  const [item, setItem] = useState<Item | null>(null);
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) return;
    async function load() {
      try {
        const token = await getToken();
        const [itemData, projectsData] = await Promise.all([
          getItem(token, params.itemId),
          getProjects(token),
        ]);
        setItem(itemData);
        setProject(
          projectsData.projects.find((p) => p.item_id === params.itemId) ?? null,
        );
      } catch (error) {
        toast.error((error as ApiError).message ?? "Failed to load item");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [getToken, isAuthenticated, params.itemId]);

  if (loading) {
    return (
      <div className="mx-auto max-w-4xl space-y-4 px-4 py-8">
        <Skeleton className="aspect-square w-full max-w-md" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }

  if (!item) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-8 text-center">
        <p>Item not found.</p>
        <Button asChild className="mt-4">
          <Link href="/profile">Back to profile</Link>
        </Button>
      </div>
    );
  }

  const imageUrl = resolveMediaUrl(item.original_image_url);

  return (
    <div className="mx-auto max-w-4xl space-y-6 px-4 py-8">
      <Button asChild variant="ghost" size="sm">
        <Link href="/profile">← Profile</Link>
      </Button>

      <div className="grid gap-8 md:grid-cols-2">
        <div className="relative aspect-square overflow-hidden rounded-xl bg-muted">
          {imageUrl ? (
            <Image
              src={imageUrl}
              alt={item.style ?? "Garment"}
              fill
              className="object-cover"
              unoptimized
            />
          ) : (
            <div className="flex h-full items-center justify-center text-muted-foreground">
              No image
            </div>
          )}
        </div>

        <div className="space-y-4">
          <div>
            <h1 className="text-3xl font-black text-primary">{item.style ?? "Garment"}</h1>
            <p className="text-muted-foreground capitalize">
              {item.difficulty ?? "unknown difficulty"} · {item.fabric_type ?? "unknown fabric"}
            </p>
          </div>
          {item.is_market_eligible && (
            <Badge variant="success">Marketplace eligible</Badge>
          )}
          <div className="flex flex-wrap gap-3">
            <Button asChild>
              <Link href="/upcycle">New upcycle</Link>
            </Button>
            <Button asChild variant="outline">
              <Link href={`/marketplace/sell?itemId=${item.id}`}>List for sale</Link>
            </Button>
          </div>
        </div>
      </div>

      {project && (
        <Card>
          <CardHeader>
            <CardTitle>{project.selected_concept?.title ?? "Linked project"}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm text-muted-foreground line-clamp-3">
              {project.environmental_impact}
            </p>
            <Button asChild variant="outline" size="sm">
              <Link href={`/projects/${project.id}`}>View sewing guide</Link>
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
