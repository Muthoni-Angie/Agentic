"use client";

import { useState } from "react";
import { FileText } from "lucide-react";

import type { ArtifactFile } from "@/lib/pipeline";
import { AGENT_BY_KEY } from "./agents";
import { Markdown } from "./Markdown";

export function ArtifactExplorer({ artifacts }: { artifacts: ArtifactFile[] }) {
  const [active, setActive] = useState(artifacts[0]?.filename ?? "");

  if (artifacts.length === 0) {
    return (
      <div className="rounded-[var(--radius)] border border-dashed border-[var(--color-border)] p-10 text-center text-sm text-[var(--color-muted)]">
        No artifacts produced yet for this run.
      </div>
    );
  }

  const current = artifacts.find((a) => a.filename === active) ?? artifacts[0];

  return (
    <div className="grid gap-4 lg:grid-cols-[260px_1fr]">
      {/* Artifact navigator */}
      <aside className="lg:sticky lg:top-20 lg:self-start">
        <div className="rounded-[var(--radius)] border border-[var(--color-border)] bg-[var(--color-surface)] p-2">
          <div className="px-2 py-1.5 text-[11px] font-semibold uppercase tracking-wide text-[var(--color-faint)]">
            Artifacts
          </div>
          <ul className="flex flex-col gap-0.5">
            {artifacts.map((a) => {
              const meta = AGENT_BY_KEY[a.agent];
              const isActive = a.filename === current.filename;
              return (
                <li key={a.filename}>
                  <button
                    onClick={() => setActive(a.filename)}
                    className="flex w-full items-center gap-2.5 rounded-lg px-2.5 py-2 text-left text-sm transition-colors"
                    style={{
                      backgroundColor: isActive
                        ? "var(--color-surface-2)"
                        : "transparent",
                    }}
                  >
                    <span
                      className="h-2 w-2 shrink-0 rounded-full"
                      style={{
                        backgroundColor: meta?.color ?? "var(--color-faint)",
                      }}
                    />
                    <span className="flex-1 truncate">
                      <span
                        className={
                          isActive
                            ? "font-medium text-[var(--color-text)]"
                            : "text-[var(--color-muted)]"
                        }
                      >
                        {a.kind}
                      </span>
                      <span className="block text-[10px] text-[var(--color-faint)]">
                        {a.filename}
                      </span>
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
        </div>
      </aside>

      {/* Rendered artifact */}
      <section className="min-w-0 rounded-[var(--radius)] border border-[var(--color-border)] bg-[var(--color-surface)]">
        <div className="flex items-center gap-2 border-b border-[var(--color-border)] px-5 py-3">
          <FileText size={15} className="text-[var(--color-faint)]" />
          <span className="font-mono text-xs text-[var(--color-muted)]">
            {current.filename}
          </span>
          <span
            className="ml-auto rounded-full px-2 py-0.5 text-[10px] font-medium"
            style={{
              backgroundColor: `${AGENT_BY_KEY[current.agent]?.color ?? "#888"}22`,
              color: AGENT_BY_KEY[current.agent]?.color ?? "#888",
            }}
          >
            {AGENT_BY_KEY[current.agent]?.label ?? "system"}
          </span>
        </div>
        <div className="px-5 py-4 sm:px-7 sm:py-6">
          <Markdown content={current.content} />
        </div>
      </section>
    </div>
  );
}
