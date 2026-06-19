import { NextResponse } from "next/server";

import { getRunSummaries } from "@/lib/pipeline";

export const dynamic = "force-dynamic";

export async function GET() {
  const runs = await getRunSummaries();
  return NextResponse.json({ runs });
}
