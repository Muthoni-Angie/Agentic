import { Check, ArrowRight, RotateCcw } from "lucide-react";

import type { RunStatus } from "@/lib/pipeline";
import { AGENTS, STAGE_INDEX } from "./agents";

function completeFlag(status: RunStatus | null, key: string): boolean {
  if (!status) return false;
  return Boolean(
    (status as unknown as Record<string, boolean>)[`${key}_complete`],
  );
}

/**
 * Horizontal visualization of the agent workflow:
 * Planner → Coder → Tester → Reviewer → Done, with live state.
 */
export function PipelineFlow({ status }: { status: RunStatus | null }) {
  const currentIndex = status ? STAGE_INDEX[status.stage] : -1;
  const looped = (status?.iteration ?? 0) > 0;

  return (
    <div className="rounded-[var(--radius)] border border-[var(--color-border)] bg-[var(--color-surface)] p-5">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-[var(--color-muted)]">
          Pipeline
        </h2>
        {looped && (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-[#2e2410] px-2.5 py-1 text-xs font-medium text-[var(--color-warn)]">
            <RotateCcw size={12} />
            {status?.iteration} rejection loop
            {(status?.iteration ?? 0) > 1 ? "s" : ""}
          </span>
        )}
      </div>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-stretch">
        {AGENTS.map((agent, i) => {
          const done = completeFlag(status, agent.key);
          const active = currentIndex === STAGE_INDEX[agent.stage];
          const approved =
            agent.key === "tester"
              ? status?.tester_approved
              : agent.key === "reviewer"
                ? status?.reviewer_approved
                : undefined;

          return (
            <div key={agent.key} className="flex flex-1 items-stretch gap-3">
              <div
                className="relative flex flex-1 flex-col rounded-xl border bg-[var(--color-surface-2)] p-3.5 transition-all"
                style={{
                  borderColor: active ? agent.color : "var(--color-border)",
                  boxShadow: active ? `0 0 0 1px ${agent.color}` : "none",
                }}
              >
                <div className="mb-2 flex items-center justify-between">
                  <span
                    className="inline-flex h-7 w-7 items-center justify-center rounded-lg text-xs font-bold"
                    style={{
                      backgroundColor: `${agent.color}22`,
                      color: agent.color,
                    }}
                  >
                    {done ? <Check size={15} /> : i + 1}
                  </span>
                  {active && (
                    <span
                      className="h-2 w-2 animate-pulse rounded-full"
                      style={{ backgroundColor: agent.color }}
                    />
                  )}
                </div>
                <div className="text-sm font-semibold">{agent.label}</div>
                <div className="text-[11px] text-[var(--color-faint)]">
                  {agent.role}
                </div>
                {approved !== undefined && (
                  <div
                    className="mt-2 text-[11px] font-medium"
                    style={{
                      color: approved
                        ? "var(--color-ok)"
                        : "var(--color-faint)",
                    }}
                  >
                    {approved ? "✓ approved" : "awaiting approval"}
                  </div>
                )}
              </div>

              {i < AGENTS.length - 1 && (
                <div className="hidden items-center text-[var(--color-faint)] sm:flex">
                  <ArrowRight size={16} />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
