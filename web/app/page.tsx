import Link from "next/link";
import { ArrowUpRight, GitBranch, Layers, FileStack } from "lucide-react";

import { getRunSummaries } from "@/lib/pipeline";
import { StageBadge } from "@/components/StageBadge";
import { AGENTS } from "@/components/agents";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  const runs = await getRunSummaries();
  const done = runs.filter((r) => r.status?.stage === "DONE").length;

  return (
    <div className="flex flex-col gap-8">
      {/* Hero */}
      <section className="flex flex-col gap-3">
        <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
          Autonomous Engineering Pipeline
        </h1>
        <p className="max-w-2xl text-sm leading-relaxed text-[var(--color-muted)]">
          Specialized agents collaborate through filesystem artifacts — never
          directly. Each run flows Planner → Coder → Tester → Reviewer, looping
          on rejection, and completes only when both the Tester and Reviewer
          approve.
        </p>
      </section>

      {/* Stat cards */}
      <section className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Stat icon={<Layers size={16} />} label="Total runs" value={runs.length} />
        <Stat icon={<GitBranch size={16} />} label="Completed" value={done} />
        <Stat
          icon={<FileStack size={16} />}
          label="Artifacts"
          value={runs.reduce((n, r) => n + r.artifactCount, 0)}
        />
        <Stat icon={<Layers size={16} />} label="Agents" value={AGENTS.length} />
      </section>

      {/* Runs list */}
      <section className="flex flex-col gap-3">
        <h2 className="text-sm font-semibold text-[var(--color-muted)]">Runs</h2>
        {runs.length === 0 ? (
          <div className="rounded-[var(--radius)] border border-dashed border-[var(--color-border)] p-12 text-center">
            <p className="text-sm text-[var(--color-muted)]">
              No runs yet. Start one with{" "}
              <code className="rounded bg-[var(--color-surface-2)] px-1.5 py-0.5 font-mono text-xs text-[var(--color-brand)]">
                python -m orchestrator.run
              </code>
            </p>
          </div>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {runs.map((run) => (
              <Link
                key={run.runId}
                href={`/runs/${run.runId}`}
                className="group flex flex-col gap-3 rounded-[var(--radius)] border border-[var(--color-border)] bg-[var(--color-surface)] p-4 transition-all hover:border-[var(--color-brand)]/60 hover:bg-[var(--color-surface-2)]"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-sm font-semibold">
                    run #{run.runId}
                  </span>
                  <ArrowUpRight
                    size={16}
                    className="text-[var(--color-faint)] transition-transform group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-[var(--color-brand)]"
                  />
                </div>
                <div className="flex items-center gap-2">
                  {run.status ? (
                    <StageBadge stage={run.status.stage} />
                  ) : (
                    <span className="text-xs text-[var(--color-faint)]">
                      no status
                    </span>
                  )}
                </div>
                <div className="flex items-center justify-between border-t border-[var(--color-border-soft)] pt-3 text-xs text-[var(--color-faint)]">
                  <span>{run.artifactCount} artifacts</span>
                  {run.status && run.status.iteration > 0 && (
                    <span className="text-[var(--color-warn)]">
                      {run.status.iteration}× looped
                    </span>
                  )}
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function Stat({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: number;
}) {
  return (
    <div className="rounded-[var(--radius)] border border-[var(--color-border)] bg-[var(--color-surface)] p-4">
      <div className="mb-2 text-[var(--color-faint)]">{icon}</div>
      <div className="text-2xl font-bold tracking-tight">{value}</div>
      <div className="text-xs text-[var(--color-muted)]">{label}</div>
    </div>
  );
}
