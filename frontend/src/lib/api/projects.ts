import { apiFetch } from "./client";
import type { ProjectsResponse } from "@/lib/types";

export function getProjects(token: string): Promise<ProjectsResponse> {
  return apiFetch<ProjectsResponse>("/api/projects/", { token });
}
