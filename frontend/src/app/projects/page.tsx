"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useApiClient } from "@/lib/auth/use-api-client";
import { getProjects } from "@/lib/api/projects";
import type { ApiError, Project } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";

export default function ProjectsPage() {
  const { getToken, isAuthenticated } = useApiClient();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) return;
    async function load() {
      try {
        const token = await getToken();
        const data = await getProjects(token);
        setProjects(data.projects);
      } catch (error) {
        toast.error((error as ApiError).message ?? "Failed to load projects");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [getToken, isAuthenticated]);

  if (loading) {
    return (
      <div className="mx-auto max-w-6xl space-y-4 px-4 py-8">
        <Skeleton className="h-10 w-48" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <h1 className="text-3xl font-bold">Your projects</h1>
      <p className="mt-2 text-muted-foreground">
        Active and completed upcycle journeys with sewing guides.
      </p>

      {projects.length === 0 ? (
        <div className="mt-8 rounded-xl border border-dashed p-12 text-center">
          <p className="text-muted-foreground">No projects yet.</p>
          <Link href="/upcycle" className="mt-4 inline-block text-primary hover:underline">
            Start upcycling →
          </Link>
        </div>
      ) : (
        <div className="mt-8 grid gap-4">
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
    </div>
  );
}
