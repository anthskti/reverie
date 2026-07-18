"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import ReactMarkdown from "react-markdown";
import { useApiClient } from "@/lib/auth/use-api-client";
import { getProjects } from "@/lib/api/projects";
import type { ApiError, Project } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";

export default function ProjectDetailPage() {
  const params = useParams<{ projectId: string }>();
  const { getToken, isAuthenticated } = useApiClient();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) return;
    async function load() {
      try {
        const token = await getToken();
        const data = await getProjects(token);
        const found = data.projects.find((p) => p.id === params.projectId);
        setProject(found ?? null);
      } catch (error) {
        toast.error((error as ApiError).message ?? "Failed to load project");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [getToken, isAuthenticated, params.projectId]);

  if (loading) {
    return (
      <div className="mx-auto max-w-4xl space-y-4 px-4 py-8">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (!project) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-8 text-center">
        <p>Project not found.</p>
        <Button asChild className="mt-4">
          <Link href="/projects">Back to projects</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6 px-4 py-8">
      <div>
        <Button asChild variant="ghost" size="sm">
          <Link href="/projects">← Projects</Link>
        </Button>
        <h1 className="mt-2 text-3xl font-bold">
          {project.selected_concept?.title ?? "Project"}
        </h1>
        <p className="text-muted-foreground capitalize">
          {project.selected_concept?.difficulty} ·{" "}
          {project.selected_concept?.techniques?.join(", ")}
        </p>
      </div>

      {project.sewing_guide && (
        <Card>
          <CardHeader>
            <CardTitle>Sewing guide</CardTitle>
          </CardHeader>
          <CardContent className="prose prose-sm max-w-none dark:prose-invert">
            <ReactMarkdown>{project.sewing_guide}</ReactMarkdown>
          </CardContent>
        </Card>
      )}

      {project.environmental_impact && (
        <Card>
          <CardHeader>
            <CardTitle>Environmental impact</CardTitle>
          </CardHeader>
          <CardContent>
            <p>{project.environmental_impact}</p>
          </CardContent>
        </Card>
      )}

      <div className="flex flex-wrap gap-3">
        {project.item_id && (
          <>
            <Button asChild>
              <Link href={`/inventory/${project.item_id}`}>View item</Link>
            </Button>
            <Button asChild variant="outline">
              <Link href={`/upcycle?itemId=${project.item_id}`}>Verify garment</Link>
            </Button>
            <Button asChild variant="outline">
              <Link href={`/marketplace/sell?itemId=${project.item_id}`}>
                Sell on marketplace
              </Link>
            </Button>
          </>
        )}
      </div>
    </div>
  );
}
