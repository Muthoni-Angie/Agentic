import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const REPO = process.env.GH_REPO ?? "Muthoni-Angie/Agentic";
const WORKFLOW = process.env.GH_WORKFLOW ?? "agentic-pipeline.yml";
const TOKEN = process.env.GH_DISPATCH_TOKEN;

/**
 * Trigger a pipeline run on demand.
 *
 * The Python pipeline can't run inside a Vercel function (it needs git + the
 * gh CLI), so the button fires the GitHub Actions workflow via workflow_dispatch
 * and the Action does the real work in the cloud — opening a PR for the next
 * roadmap feature.
 */
export async function POST() {
  if (!TOKEN) {
    return NextResponse.json(
      { ok: false, error: "Server is missing GH_DISPATCH_TOKEN env var." },
      { status: 500 },
    );
  }

  const res = await fetch(
    `https://api.github.com/repos/${REPO}/actions/workflows/${WORKFLOW}/dispatches`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${TOKEN}`,
        Accept: "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
      },
      body: JSON.stringify({ ref: "main" }),
    },
  );

  if (res.status === 204) {
    return NextResponse.json({
      ok: true,
      message: "Pipeline run triggered — a PR will open shortly.",
    });
  }

  let detail = await res.text();
  if (res.status === 404) {
    detail =
      "Workflow not found. Add .github/workflows/agentic-pipeline.yml to the repo first.";
  }
  return NextResponse.json(
    { ok: false, status: res.status, error: detail },
    { status: 502 },
  );
}
