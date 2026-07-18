import { getApiUrl } from "@/lib/utils";
import type { ApiError } from "@/lib/types";

export interface FetchOptions extends Omit<RequestInit, "body"> {
  token?: string;
  body?: BodyInit | object | null;
}

export async function apiFetch<T>(
  path: string,
  options: FetchOptions = {},
): Promise<T> {
  const { token, body, headers: customHeaders, ...rest } = options;

  const headers = new Headers(customHeaders);

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  let requestBody: BodyInit | undefined;
  if (body instanceof FormData || typeof body === "string") {
    requestBody = body;
  } else if (body != null) {
    headers.set("Content-Type", "application/json");
    requestBody = JSON.stringify(body);
  }

  const response = await fetch(`${getApiUrl()}${path}`, {
    ...rest,
    headers,
    body: requestBody,
  });

  if (!response.ok) {
    let message = response.statusText;
    try {
      const data = await response.json();
      if (typeof data.detail === "string") {
        message = data.detail;
      } else if (Array.isArray(data.detail)) {
        message = data.detail.map((d: { msg?: string }) => d.msg ?? String(d)).join(", ");
      }
    } catch {
      // ignore parse errors
    }
    const error: ApiError = { message, status: response.status };
    throw error;
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}
