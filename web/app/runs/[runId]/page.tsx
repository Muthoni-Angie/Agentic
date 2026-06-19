import Link from "next/link";
import { notFound } from "next/navigation";
import { ChevronLeft, CheckCircle2, Clock } from "lucide-react";

import { getRunDetail, getConversation } from "@/lib/pipeline";
import { PipelineFlow } from "@/components/PipelineFlow";
import { StageBadge } from "@/components/StageBadge";
import { RunViews } from "@/components/RunViews";

export const dynamic = "force-dynamic";

export default async function RunPage({
  params,
}: {
  params: Promise<{ runId: string }>;
}) {
  const { runId } = await params;
  const [detail, conversation] = await Promise.all([
    getRunDetail(runId),
    getConversation(runId),
  ]);

  if (!detail.status && detail.artifacts.length === 0) notFound();

  const status = detail.status;
  const complete =
    status?.tester_approved && status?.reviewer_approved;

  return (
    <div className="flex flex-col gap-6">
      {/* Breadcrumb + title */}
      <div className="flex flex-col gap-3">
        <Link
          href="/"
          className="inline-flex w-fit items-center gap-1 text-sm text-[var(--color-muted)] transition-colors hover:text-[var(--color-text)]"
        >
          <ChevronLeft size={15} />
          All runs
        </Link>
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="font-mono text-2xl font-bold tracking-tight">
            run #{runId}
          </h1>
          {status && <StageBadge stage={status.stage} />}
          {complete && (
            <span className="inline-flex items-center gap-1.5 rounded-full bg-[#0f2b1a] px-2.5 py-1 text-xs font-medium text-[var(--color-ok)]">
              <CheckCircle2 size={13} />
              Tester + Reviewer approved
            </span>
          )}
        </div>
      </div>

      {/* Pipeline visualization */}
      <PipelineFlow status={status} />

      {/* History + artifacts */}
      <div className="grid gap-6 lg:grid-cols-[1fr_320px] lg:items-start">
        <div className="order-2 min-w-0 lg:order-1">
          <RunViews
            conversation={conversation}
            artifacts={detail.artifacts}
          />
        </div>

        {/* Transition timeline */}
        <aside className="order-1 lg:order-2 lg:sticky lg:top-20">
          <div className="rounded-[var(--radius)] border border-[var(--color-border)] bg-[var(--color-surface)] p-5">
            <h2 className="mb-4 text-sm font-semibold text-[var(--color-muted)]">
              State history
            </h2>
            {status && status.history.length > 0 ? (
              <ol className="relative flex flex-col gap-4 border-l border-[var(--color-border)] pl-5">
                {status.history.map((h, i) => (
                  <li key={i} className="relative">
                    <span className="absolute -left-[1.46rem] top-1 h-2.5 w-2.5 rounded-full border-2 border-[var(--color-surface)] bg-[var(--color-brand)]" />
                    <div className="text-sm font-medium">
                      {h.from_stage} → {h.to_stage}
                    </div>
                    <div className="text-xs text-[var(--color-faint)]">
                      by {h.agent}
                      {h.iteration > 0 && ` · iteration ${h.iteration}`}
                    </div>
                    {h.note && (
                      <div className="mt-0.5 text-xs italic text-[var(--color-muted)]">
                        “{h.note}”
                      </div>
                    )}
                  </li>
                ))}
              </ol>
            ) : (
              <div className="flex items-center gap-2 text-sm text-[var(--color-muted)]">
                <Clock size={14} /> No transitions recorded.
              </div>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
}
