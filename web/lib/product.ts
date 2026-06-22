import fs from "node:fs/promises";
import fsSync from "node:fs";
import path from "node:path";

// Mirror of product/backlog.py (id + title + ordered files). Kept small and
// stable; the source of truth for *progress* is roadmap.json.
export const PRODUCT_NAME = "LedgerLoop";
export const PRODUCT_PITCH =
  "An automated reconciliation toolkit that matches transactions across sources and reports the result — built incrementally by the agent pipeline.";

export interface FeatureManifest {
  id: string;
  title: string;
  summary: string;
  files: string[]; // paths relative to src/
}

export const FEATURES: FeatureManifest[] = [
  {
    id: "F1",
    title: "Domain models",
    summary: "Transaction and Reconciliation data models (Python core).",
    files: ["ledgerloop/__init__.py", "ledgerloop/models.py"],
  },
  {
    id: "F2",
    title: "Matching engine",
    summary: "Reconcile transactions across two sources by amount and date.",
    files: ["ledgerloop/matcher.py"],
  },
  {
    id: "F3",
    title: "CSV import",
    summary: "Load transactions from CSV text into the domain model.",
    files: ["ledgerloop/csv_io.py"],
  },
  {
    id: "F4",
    title: "Reporting",
    summary: "Render a reconciliation result as a Markdown report.",
    files: ["ledgerloop/report.py"],
  },
  {
    id: "F5",
    title: "Web app shell",
    summary: "Responsive single-page UI with two CSV inputs and a toolbar.",
    files: ["webapp/index.html", "webapp/styles.css"],
  },
  {
    id: "F6",
    title: "CSV parser (web)",
    summary: "Parse pasted CSV text into transactions in the browser.",
    files: ["webapp/parse.js"],
  },
  {
    id: "F7",
    title: "Matching engine (web)",
    summary: "Reconcile two transaction lists in the browser.",
    files: ["webapp/engine.js"],
  },
  {
    id: "F8",
    title: "Summary & report",
    summary: "Summary stats and a downloadable Markdown report.",
    files: ["webapp/report.js"],
  },
  {
    id: "F9",
    title: "Interactive app + results",
    summary: "Wire inputs to the engine; render summary cards and tables.",
    files: ["webapp/app.js"],
  },
  {
    id: "F10",
    title: "Sample data & one-click demo",
    summary: "Bundled sample CSVs for a one-click reconciliation demo.",
    files: ["webapp/sample.js"],
  },
];

function productSrcRoot(): string {
  const bundled = path.join(process.cwd(), "product-src");
  if (fsSync.existsSync(bundled)) return bundled;
  return path.join(process.cwd(), "..", "src");
}

function roadmapPath(): string {
  const bundled = path.join(process.cwd(), "roadmap.json");
  if (fsSync.existsSync(bundled)) return bundled;
  return path.join(process.cwd(), "..", "roadmap.json");
}

export interface SourceFile {
  path: string;
  content: string;
}

export interface FeatureStatus extends FeatureManifest {
  done: boolean;
  building: boolean;
  sources: SourceFile[];
}

export interface ProductState {
  name: string;
  pitch: string;
  doneCount: number;
  total: number;
  features: FeatureStatus[];
}

async function readDone(): Promise<string[]> {
  try {
    const raw = await fs.readFile(roadmapPath(), "utf-8");
    return (JSON.parse(raw).done ?? []) as string[];
  } catch {
    return [];
  }
}

async function readSource(rel: string): Promise<SourceFile | null> {
  try {
    const content = await fs.readFile(path.join(productSrcRoot(), rel), "utf-8");
    return { path: `src/${rel}`, content };
  } catch {
    return null;
  }
}

export async function getProductState(): Promise<ProductState> {
  const done = new Set(await readDone());
  // The "building now" feature is the first not-done one.
  const buildingId = FEATURES.find((f) => !done.has(f.id))?.id;

  const features: FeatureStatus[] = await Promise.all(
    FEATURES.map(async (f) => {
      const sources = (
        await Promise.all(f.files.map((rel) => readSource(rel)))
      ).filter((s): s is SourceFile => s !== null);
      return {
        ...f,
        done: done.has(f.id),
        building: f.id === buildingId,
        sources,
      };
    }),
  );

  return {
    name: PRODUCT_NAME,
    pitch: PRODUCT_PITCH,
    doneCount: features.filter((f) => f.done).length,
    total: FEATURES.length,
    features,
  };
}
