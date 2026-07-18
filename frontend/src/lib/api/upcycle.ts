import { apiFetch } from "./client";
import type {
  ExecutionRequest,
  ExecutionResponse,
  IdeationResponse,
  VerificationResponse,
} from "@/lib/types";

export interface IdeateParams {
  image: File;
  style: string;
  difficulty: string;
  fabric_type?: string;
  weight_kg?: number;
  tools_available?: string[];
  generate_mockups?: boolean;
}

export function ideate(
  token: string,
  params: IdeateParams,
): Promise<IdeationResponse> {
  const form = new FormData();
  form.append("image", params.image);
  form.append("style", params.style);
  form.append("difficulty", params.difficulty);
  if (params.fabric_type) form.append("fabric_type", params.fabric_type);
  if (params.weight_kg != null) form.append("weight_kg", String(params.weight_kg));
  form.append(
    "tools_available",
    JSON.stringify(params.tools_available ?? ["scissors", "sewing machine"]),
  );
  form.append("generate_mockups", String(params.generate_mockups ?? true));

  return apiFetch<IdeationResponse>("/api/upcycle/ideate", {
    method: "POST",
    token,
    body: form,
  });
}

export function execute(
  token: string,
  body: ExecutionRequest,
): Promise<ExecutionResponse> {
  return apiFetch<ExecutionResponse>("/api/upcycle/execute", {
    method: "POST",
    token,
    body,
  });
}

export function verifyItem(
  token: string,
  itemId: string,
  image: File,
): Promise<VerificationResponse> {
  const form = new FormData();
  form.append("image", image);

  return apiFetch<VerificationResponse>(`/api/upcycle/${itemId}/verify`, {
    method: "POST",
    token,
    body: form,
  });
}
