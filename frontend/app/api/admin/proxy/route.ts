import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";
import { ADMIN_COOKIE_NAME } from "@/lib/adminSessionShared";

const ALLOWED_TARGETS = [
  "/api/analytics/",
  "/api/qa/",
  "/api/prices/",
  "/api/keh/overview",
  "/api/keh/inventory",
  "/api/keh/lenses/builder",
  "/api/keh/sync",
  "/api/books/lab/",
];

function backendBaseUrl(): string {
  return (
    process.env.API_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    "http://localhost:8000"
  ).replace(/\/+$/, "");
}

function targetIsAllowed(target: string): boolean {
  if (!target.startsWith("/api/") || target.startsWith("//") || target.includes("\\")) {
    return false;
  }
  return ALLOWED_TARGETS.some((prefix) => target.startsWith(prefix));
}

async function proxy(request: NextRequest): Promise<NextResponse> {
  if (request.headers.get("x-pricesift-admin") !== "1") {
    return NextResponse.json({ detail: "Admin proxy request rejected." }, { status: 403 });
  }

  const origin = request.headers.get("origin");
  if (origin && origin !== request.nextUrl.origin) {
    return NextResponse.json({ detail: "Admin proxy origin rejected." }, { status: 403 });
  }

  const token = (await cookies()).get(ADMIN_COOKIE_NAME)?.value?.trim();
  if (!token) {
    return NextResponse.json({ detail: "Admin session required." }, { status: 401 });
  }

  const target = request.nextUrl.searchParams.get("target") || "";
  if (!targetIsAllowed(target)) {
    return NextResponse.json({ detail: "Admin proxy target rejected." }, { status: 400 });
  }

  const upstreamUrl = new URL(target, `${backendBaseUrl()}/`);
  const headers = new Headers({
    Authorization: `Bearer ${token}`,
    Accept: request.headers.get("accept") || "application/json",
  });
  const contentType = request.headers.get("content-type");
  if (contentType) headers.set("Content-Type", contentType);

  const method = request.method.toUpperCase();
  const body = method === "GET" || method === "HEAD" ? undefined : await request.arrayBuffer();

  let upstream: Response;
  try {
    upstream = await fetch(upstreamUrl, {
      method,
      headers,
      body,
      cache: "no-store",
      redirect: "manual",
    });
  } catch {
    return NextResponse.json({ detail: "Admin backend unavailable." }, { status: 502 });
  }

  const responseHeaders = new Headers({ "Cache-Control": "no-store" });
  const upstreamContentType = upstream.headers.get("content-type");
  if (upstreamContentType) responseHeaders.set("Content-Type", upstreamContentType);

  return new NextResponse(await upstream.arrayBuffer(), {
    status: upstream.status,
    headers: responseHeaders,
  });
}

export const GET = proxy;
export const POST = proxy;
export const DELETE = proxy;
