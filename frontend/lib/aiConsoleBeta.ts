import { adminFetch } from "@/lib/api";

const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type AIConsoleBetaStatus = {
  enabled: boolean;
  api_key_configured: boolean;
  ready: boolean;
  model: string;
  targets: string[];
};

function adminQuery(token?: string): string {
  return token ? `?token=${encodeURIComponent(token)}` : "";
}

export async function getAIConsoleBetaStatus(
  token?: string,
): Promise<AIConsoleBetaStatus> {
  const response = await adminFetch(
    `${baseUrl}/api/analytics/ai-console-beta${adminQuery(token)}`,
    { cache: "no-store" },
  );
  if (!response.ok) throw new Error("AI console beta status failed");
  return response.json();
}

export async function setAIConsoleBetaEnabled(
  enabled: boolean,
  token?: string,
): Promise<AIConsoleBetaStatus> {
  const response = await adminFetch(
    `${baseUrl}/api/analytics/ai-console-beta${adminQuery(token)}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ enabled }),
      cache: "no-store",
    },
  );
  if (!response.ok) throw new Error("Could not update AI console beta");
  return response.json();
}
