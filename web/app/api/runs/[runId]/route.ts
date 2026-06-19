import { NextResponse } from "next/server";

import { getRunDetail } from "@/lib/pipeline";

export const dynamic = "force-dynamic";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ runId: string }> },
) {
  const { runId } = await params;
  const detail = await getRunDetail(runId);
  if (!detail.status && detail.artifacts.length === 0) {
    return NextResponse.json({ error: "run not found" }, { status: 404 });
  }
  return NextResponse.json(detail);
}
