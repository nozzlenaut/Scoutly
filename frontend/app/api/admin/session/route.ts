import { NextRequest, NextResponse } from "next/server";
import {
  ADMIN_COOKIE_NAME,
  ADMIN_SESSION_SECONDS,
} from "@/lib/adminSessionShared";

function backendBaseUrl(): string {
  return (
    process.env.API_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    "http://localhost:8000"
  ).replace(/\/+$/, "");
}

function safeNext(value: FormDataEntryValue | null): string {
  const candidate = typeof value === "string" ? value.trim() : "";
  if (!candidate.startsWith("/admin") || candidate.startsWith("//")) return "/admin";
  return candidate;
}

function redirectWithInvalid(request: NextRequest, destination: string): NextResponse {
  const url = new URL(destination, request.url);
  url.searchParams.set("invalid", "1");
  return NextResponse.redirect(url, 303);
}

export async function POST(request: NextRequest): Promise<NextResponse> {
  const form = await request.formData();
  const token = String(form.get("token") || "").trim();
  const destination = safeNext(form.get("next"));

  if (!token) return redirectWithInvalid(request, destination);

  let validation: Response;
  try {
    validation = await fetch(`${backendBaseUrl()}/api/analytics/summary`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    });
  } catch {
    return redirectWithInvalid(request, destination);
  }

  if (!validation.ok) return redirectWithInvalid(request, destination);

  const response = NextResponse.redirect(new URL(destination, request.url), 303);
  response.cookies.set({
    name: ADMIN_COOKIE_NAME,
    value: token,
    httpOnly: true,
    secure: request.nextUrl.protocol === "https:",
    sameSite: "strict",
    path: "/",
    maxAge: ADMIN_SESSION_SECONDS,
    priority: "high",
  });
  return response;
}
