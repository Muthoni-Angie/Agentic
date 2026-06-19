import fs from "node:fs/promises";
import fsSync from "node:fs";
import path from "node:path";

// Resolve the pipeline root. On Vercel the project root is web/, where a
// build-time snapshot lives at ./.pipeline; in local dev we read the live
// repo-root ../.pipeline. PIPELINE_ROOT overrides both.
function resolvePipelineRoot(): string {
  if (process.env.PIPELINE_ROOT) return process.env.PIPELINE_ROOT;
  const bundled = path.join(process.cwd(), ".pipeline");
  if (fsSync.existsSync(bundled)) return bundled;
  return path.join(process.cwd(), "..", ".pipeline");
}

export const PIPELINE_ROOT = resolvePipelineRoot();

export const STAGES = [
  "PLANNING",
  "CODING",
  "TESTING",
  "REVIEWING",
  "DONE",
] as const;
export type Stage = (typeof STAGES)[number];

export interface TransitionRecord {
  iteration: number;
  from_stage: Stage;
  to_stage: Stage;
  agent: string;
  note: string;
  timestamp: string;
}

export interface RunStatus {
  run_id: string;
  stage: Stage;
  planner_complete: boolean;
  coder_complete: boolean;
  tester_complete: boolean;
  reviewer_complete: boolean;
  tester_approved: boolean;
  reviewer_approved: boolean;
  iteration: number;
  history: TransitionRecord[];
  created_at: string;
  updated_at: string;
}

export interface ArtifactFile {
  filename: string;
  content: string;
  agent: string;
  kind: string;
}

export interface RunSummary {
  runId: string;
  status: RunStatus | null;
  artifactCount: number;
}

export interface RunDetail {
  runId: string;
  status: RunStatus | null;
  artifacts: ArtifactFile[];
}

// Maps each artifact filename to the agent that authors it and a display kind.
const ARTIFACT_META: Record<string, { agent: string; kind: string }> = {
  "idea.md": { agent: "planner", kind: "Idea" },
  "spec.md": { agent: "planner", kind: "Specification" },
  "tasks.md": { agent: "planner", kind: "Tasks" },
  "implementation.md": { agent: "coder", kind: "Implementation" },
  "test-plan.md": { agent: "tester", kind: "Test Plan" },
  "defects.md": { agent: "tester", kind: "Defects" },
  "review.md": { agent: "reviewer", kind: "Review" },
  "feedback.md": { agent: "reviewer", kind: "Feedback" },
};

// Stable display order across the UI.
const ARTIFACT_ORDER = Object.keys(ARTIFACT_META);

async function exists(p: string): Promise<boolean> {
  try {
    await fs.access(p);
    return true;
  } catch {
    return false;
  }
}

export async function listRunIds(): Promise<string[]> {
  if (!(await exists(PIPELINE_ROOT))) return [];
  const entries = await fs.readdir(PIPELINE_ROOT, { withFileTypes: true });
  return entries
    .filter((e) => e.isDirectory())
    .map((e) => e.name)
    .sort()
    .reverse();
}

export async function readStatus(runId: string): Promise<RunStatus | null> {
  const file = path.join(PIPELINE_ROOT, runId, "status.json");
  if (!(await exists(file))) return null;
  try {
    return JSON.parse(await fs.readFile(file, "utf-8")) as RunStatus;
  } catch {
    return null;
  }
}

export async function readArtifacts(runId: string): Promise<ArtifactFile[]> {
  const dir = path.join(PIPELINE_ROOT, runId);
  if (!(await exists(dir))) return [];
  const files = (await fs.readdir(dir)).filter(
    (f) => f.endsWith(".md") && f !== "status.json",
  );
  const artifacts = await Promise.all(
    files.map(async (filename) => {
      const meta = ARTIFACT_META[filename] ?? { agent: "system", kind: "Note" };
      return {
        filename,
        content: await fs.readFile(path.join(dir, filename), "utf-8"),
        agent: meta.agent,
        kind: meta.kind,
      } satisfies ArtifactFile;
    }),
  );
  return artifacts.sort(
    (a, b) =>
      (ARTIFACT_ORDER.indexOf(a.filename) + 1 || 99) -
      (ARTIFACT_ORDER.indexOf(b.filename) + 1 || 99),
  );
}

export async function getRunSummaries(): Promise<RunSummary[]> {
  const ids = await listRunIds();
  return Promise.all(
    ids.map(async (runId) => {
      const status = await readStatus(runId);
      const artifacts = await readArtifacts(runId);
      return { runId, status, artifactCount: artifacts.length };
    }),
  );
}

export async function getRunDetail(runId: string): Promise<RunDetail> {
  const [status, artifacts] = await Promise.all([
    readStatus(runId),
    readArtifacts(runId),
  ]);
  return { runId, status, artifacts };
}

/* ----------------------------------------------------------------------- */
/* Conversation / handoff derivation                                        */
/*                                                                          */
/* Agents never call each other — every "message" is an artifact written    */
/* for the next agent. We reconstruct the conversation from the transition   */
/* history (the true handoff order, including rejection loops) and enrich    */
/* each step with structured content read from the JSON sidecars.            */
/* ----------------------------------------------------------------------- */

export interface HandoffMessage {
  index: number;
  fromAgent: string;
  toStage: Stage;
  toAgent: string | null;
  iteration: number;
  note: string;
  timestamp: string;
  headline: string;
  bullets: string[];
  produced: string[];
  verdict: "approved" | "rejected" | null;
}

const STAGE_TO_AGENT: Record<Stage, string | null> = {
  PLANNING: "planner",
  CODING: "coder",
  TESTING: "tester",
  REVIEWING: "reviewer",
  DONE: null,
};

async function readSidecar<T = Record<string, unknown>>(
  runId: string,
  stem: string,
): Promise<T | null> {
  const file = path.join(PIPELINE_ROOT, runId, `${stem}.json`);
  if (!(await exists(file))) return null;
  try {
    return JSON.parse(await fs.readFile(file, "utf-8")) as T;
  } catch {
    return null;
  }
}

function str(value: unknown): string {
  return typeof value === "string" ? value : "";
}

function arr(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

async function summarize(
  runId: string,
  agent: string,
  toStage: Stage,
): Promise<Pick<HandoffMessage, "headline" | "bullets" | "produced" | "verdict">> {
  if (agent === "planner") {
    const idea = (await readSidecar(runId, "idea")) ?? {};
    const spec = (await readSidecar(runId, "spec")) ?? {};
    const tasks = (await readSidecar(runId, "tasks")) ?? {};
    const name = str(idea.name) || "a new product";
    return {
      headline: `I intend to build ${name} — ${str(idea.pitch)}`,
      bullets: [
        str(idea.problem) && `Problem: ${str(idea.problem)}`,
        str(idea.target_market) && `Target market: ${str(idea.target_market)}`,
        `${arr(spec.components).length} components and ${arr(tasks.tasks).length} tasks planned`,
        arr(idea.revenue_streams).length > 0 &&
          `Revenue: ${arr(idea.revenue_streams).join("; ")}`,
      ].filter(Boolean) as string[],
      produced: ["idea.md", "spec.md", "tasks.md"],
      verdict: null,
    };
  }

  if (agent === "coder") {
    const impl = (await readSidecar(runId, "implementation")) ?? {};
    return {
      headline: str(impl.summary) || "Implemented the requested features.",
      bullets: [
        arr(impl.files_changed).length > 0 &&
          `Wrote ${arr(impl.files_changed).join(", ")}`,
        ...arr(impl.decisions).slice(0, 3).map((d) => `Decision: ${str(d)}`),
      ].filter(Boolean) as string[],
      produced: ["implementation.md"],
      verdict: null,
    };
  }

  if (agent === "tester") {
    const plan = (await readSidecar(runId, "test-plan")) ?? {};
    const defects = (await readSidecar(runId, "defects")) ?? {};
    const cases = arr(plan.cases);
    const edge = cases.filter(
      (c) => (c as Record<string, unknown>).kind === "edge",
    ).length;
    const defectCount = arr(defects.defects).length;
    return {
      headline: `Authored ${cases.length} test cases (${edge} edge cases); found ${defectCount} defect${defectCount === 1 ? "" : "s"}.`,
      bullets: arr(defects.defects).map((d) => {
        const dd = d as Record<string, unknown>;
        return `[${str(dd.severity).toUpperCase()}] ${str(dd.summary)}`;
      }),
      produced: ["test-plan.md", "defects.md"],
      verdict: toStage === "CODING" ? "rejected" : "approved",
    };
  }

  if (agent === "reviewer") {
    const review = (await readSidecar(runId, "review")) ?? {};
    const feedback = (await readSidecar(runId, "feedback")) ?? {};
    return {
      headline: str(review.summary) || "Reviewed the architecture.",
      bullets: arr(feedback.items)
        .slice(0, 4)
        .map((it) => {
          const i = it as Record<string, unknown>;
          return `[${str(i.severity)}] ${str(i.message)}`;
        }),
      produced: ["review.md", "feedback.md"],
      verdict:
        feedback.approved === true || toStage === "DONE"
          ? "approved"
          : "rejected",
    };
  }

  return { headline: "", bullets: [], produced: [], verdict: null };
}

export async function getConversation(runId: string): Promise<HandoffMessage[]> {
  const status = await readStatus(runId);
  if (!status) return [];

  return Promise.all(
    status.history.map(async (h, index) => {
      const summary = await summarize(runId, h.agent, h.to_stage);
      return {
        index,
        fromAgent: h.agent,
        toStage: h.to_stage,
        toAgent: STAGE_TO_AGENT[h.to_stage],
        iteration: h.iteration,
        note: h.note,
        timestamp: h.timestamp,
        ...summary,
      } satisfies HandoffMessage;
    }),
  );
}
