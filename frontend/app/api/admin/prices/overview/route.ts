import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

function backendUrl(): string | null {
  const value = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || "";
  return value.trim().replace(/\/$/, "") || null;
}

export async function GET(request: NextRequest) {
  const backend = backendUrl();
  if (!backend) {
    return NextResponse.json(
      { detail: "Vercel is missing API_URL or NEXT_PUBLIC_API_URL." },
      { status: 503 },
    );
  }

  const target = new URL(`${backend}/api/prices/overview`);
  request.nextUrl.searchParams.forEach((value, key) => target.searchParams.set(key, value));

  try {
    const response = await fetch(target, { cache: "no-store" });
    const body = await response.text();
    return new NextResponse(body, {
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
