"use client";

import { useState } from "react";
import { MessagesSquare, Files } from "lucide-react";

import type { ArtifactFile, HandoffMessage } from "@/lib/pipeline";
import { Conversation } from "./Conversation";
import { ArtifactExplorer } from "./ArtifactExplorer";

type Tab = "conversation" | "artifacts";

export function RunViews({
  conversation,
  artifacts,
}: {
  conversation: HandoffMessage[];
  artifacts: ArtifactFile[];
}) {
  const [tab, setTab] = useState<Tab>("conversation");

  const tabs: { key: Tab; label: string; icon: React.ReactNode; count: number }[] =
    [
      {
        key: "conversation",
        label: "Conversation",
        icon: <MessagesSquare size={15} />,
        count: conversation.length,
      },
      {
        key: "artifacts",
        label: "Artifacts",
        icon: <Files size={15} />,
        count: artifacts.length,
      },
    ];

  return (
    <div className="flex flex-col gap-4">
      <div className="flex w-fit items-center gap-1 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-1">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className="inline-flex items-center gap-2 rounded-lg px-3.5 py-1.5 text-sm font-medium transition-colors"
            style={{
              backgroundColor:
                tab === t.key ? "var(--color-surface-2)" : "transparent",
              color:
                tab === t.key
                  ? "var(--color-text)"
                  : "var(--color-muted)",
            }}
          >
            {t.icon}
            {t.label}
            <span className="rounded-full bg-[var(--color-bg)] px-1.5 text-[10px] text-[var(--color-faint)]">
              {t.count}
            </span>
          </button>
        ))}
      </div>

      {tab === "conversation" ? (
        <Conversation messages={conversation} />
      ) : (
        <ArtifactExplorer artifacts={artifacts} />
      )}
    </div>
  );
}
