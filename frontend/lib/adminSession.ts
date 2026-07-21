import "server-only";

import { cookies } from "next/headers";
import {
  ADMIN_BROWSER_SESSION,
  ADMIN_COOKIE_NAME,
  ADMIN_SESSION_SECONDS,
} from "@/lib/adminSessionShared";

export { ADMIN_BROWSER_SESSION, ADMIN_COOKIE_NAME, ADMIN_SESSION_SECONDS };

export async function getAdminToken(): Promise<string | null> {
  const value = (await cookies()).get(ADMIN_COOKIE_NAME)?.value?.trim();
  return value || null;
}
