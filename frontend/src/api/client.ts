import { clearToken, getToken } from "../auth/token";

const API_BASE = "/api";

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function getMessage(detail: unknown): string {
  if (typeof detail === "string") {
    return detail;
  }
  if (isRecord(detail) && typeof detail.detail === "string") {
    return detail.detail;
  }
  if (isRecord(detail) && typeof detail.message === "string") {
    return detail.message;
  }
  return "Request failed";
}

export class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(status: number, detail: unknown) {
    super(getMessage(detail));
    this.status = status;
    this.detail = detail;
  }
}

interface RequestOptions extends Omit<RequestInit, "body"> {
  body?:
    | BodyInit
    | Record<string, unknown>
    | Array<unknown>
    | null;
  auth?: boolean;
  handleUnauthorized?: boolean;
}

export async function apiFetch<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const {
    auth = true,
    handleUnauthorized = true,
    headers,
    body,
    ...rest
  } = options;

  const finalHeaders = new Headers(headers ?? {});
  const token = getToken();

  if (auth && token) {
    finalHeaders.set("Authorization", `Bearer ${token}`);
  }

  let requestBody: BodyInit | undefined;

  if (
    body !== undefined &&
    body !== null &&
    !(body instanceof FormData) &&
    !(body instanceof URLSearchParams) &&
    typeof body !== "string" &&
    !(body instanceof Blob)
  ) {
    finalHeaders.set("Content-Type", "application/json");
    requestBody = JSON.stringify(body);
  } else {
    requestBody = body as BodyInit | undefined;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...rest,
    headers: finalHeaders,
    body: requestBody,
  });

  let payload: unknown = null;
  if (response.status !== 204) {
    const contentType = response.headers.get("content-type") ?? "";
    if (contentType.includes("application/json")) {
      payload = await response.json();
    } else {
      payload = await response.text();
    }
  }

  if (!response.ok) {
    if (response.status === 401 && handleUnauthorized) {
      clearToken();
      window.location.assign("/login");
    }
    throw new ApiError(response.status, payload);
  }

  return payload as T;
}

export function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "Request failed";
}
