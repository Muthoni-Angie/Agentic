"use client";

import { ArrowRight, CheckCircle2, XCircle, FileText, Flag } from "lucide-react";

import type { HandoffMessage } from "@/lib/pipeline";
import { AGENT_BY_KEY } from "./agents";

function agentColor(key: string): string {
  return AGENT_BY_KEY[key]?.color ?? "var(--color-faint)";
}

function agentLabel(key: string | null): string {
  if (!key) return "Done";
  return AGENT_BY_KEY[key]?.label ?? key;
}

export function Conversation({ messages }: { messages: HandoffMessage[] }) {
  if (messages.length === 0) {
    return (
      <div className="rounded-[var(--radius)] border border-dashed border-[var(--color-border)] p-10 text-center text-sm text-[var(--color-muted)]">
        No handoffs recorded yet for this run.
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      <p className="text-xs text-[var(--color-muted)]">
        Agents never call each other. Each message below is an artifact one agent
        wrote for the next — this is the entire inter-agent conversation,
        reconstructed from <code className="text-[var(--color-brand)]">status.json</code>{" "}
        and the produced artifacts.
      </p>

      {messages.map((m) => {
        const color = agentColor(m.fromAgent);
        const meta = AGENT_BY_KEY[m.fromAgent];
        return (
          <div
            key={m.index}
            className="rounded-[var(--radius)] border border-[var(--color-border)] bg-[var(--color-surface)] p-4 sm:p-5"
            style={{ borderLeft: `3px solid ${color}` }}
          >
            {/* Header: from → to */}
            <div className="mb-3 flex flex-wrap items-center gap-2">
              <span
                className="inline-flex h-7 w-7 items-center justify-center rounded-lg text-xs font-bold"
                style={{ backgroundColor: `${color}22`, color }}
              >
                {agentLabel(m.fromAgent).charAt(0)}
              </span>
              <span className="text-sm font-semibold">
                {agentLabel(m.fromAgent)}
              </span>
              <span className="text-[var(--color-faint)]">
                <ArrowRight size={14} />
              </span>
              <span className="text-sm font-medium text-[var(--color-muted)]">
                {agentLabel(m.toAgent)}
              </span>

              {m.iteration > 0 && (
                <span className="rounded-full bg-[#2e2410] px-2 py-0.5 text-[10px] font-medium text-[var(--color-warn)]">
                  iteration {m.iteration}
                </span>
              )}

              {m.verdict && (
                <span
                  className="ml-auto inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium"
                  style={{
                    backgroundColor:
                      m.verdict === "approved" ? "#0f2b1a" : "#2e1620",
                    color:
                      m.verdict === "approved"
                        ? "var(--color-ok)"
                        : "var(--color-danger)",
                  }}
                >
                  {m.verdict === "approved" ? (
                    <CheckCircle2 size={12} />
                  ) : (
                    <XCircle size={12} />
                  )}
                  {m.verdict}
                </span>
              )}
            </div>

            {/* The message */}
            <p className="text-sm leading-relaxed text-[var(--color-text)]">
              “{m.headline}”
            </p>

            {m.bullets.length > 0 && (
              <ul className="mt-2.5 flex flex-col gap-1">
                {m.bullets.map((b, i) => (
                  <li
                    key={i}
                    className="flex gap-2 text-xs leading-relaxed text-[var(--color-muted)]"
                  >
                    <span style={{ color }}>•</span>
                    <span>{b}</span>
                  </li>
                ))}
              </ul>
            )}

            {/* Footer: role + produced artifacts */}
            <div className="mt-3 flex flex-wrap items-center gap-2 border-t border-[var(--color-border-soft)] pt-3">
              {meta && (
                <span className="text-[11px] text-[var(--color-faint)]">
                  acting as {meta.role}
                </span>
              )}
              <span className="ml-auto flex flex-wrap items-center gap-1.5">
                {m.toAgent === null && (
                  <span className="inline-flex items-center gap-1 text-[11px] font-medium text-[var(--color-ok)]">
                    <Flag size={11} /> pipeline complete
                  </span>
                )}
                {m.produced.map((f) => (
                  <span
                    key={f}
                    className="inline-flex items-center gap-1 rounded-md bg-[var(--color-surface-2)] px-2 py-0.5 font-mono text-[10px] text-[var(--color-muted)]"
                  >
                    <FileText size={10} />
                    {f}
                  </span>
                ))}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
