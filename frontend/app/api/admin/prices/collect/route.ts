import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

function backendUrl(): string | null {
  const value = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || "";
  return value.trim().replace(/\/$/, "") || null;
}

export async function POST(request: NextRequest) {
  const backend = backendUrl();
  if (!backend) {
    return NextResponse.json(
      { detail: "Vercel is missing API_URL or NEXT_PUBLIC_API_URL." },
      { status: 503 },
    );
  }

  const target = new URL(`${backend}/api/prices/collect/qa`);
  request.nextUrl.searchParams.forEach((value, key) => target.searchParams.set(key, value));

  try {
    const body = await request.text();
    const response = await fetch(target, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body,
      cache: "no-store",
    });
    const responseBody = await response.text();
    return new NextResponse(responseBody, {
      status: response.status,
      headers: { "content-type": response.headers.get("content-type") || "application/json" },
    });
  } catch (error) {
    return NextResponse.json(
      { detail: error instanceof Error ? error.message : "Could not reach the Railway API." },
      { status: 502 },
    );
  }
}
