import type { Stage } from "@/lib/pipeline";

const STYLES: Record<Stage, { bg: string; fg: string; label: string }> = {
  PLANNING: { bg: "#1d1d3a", fg: "#a9a9ff", label: "Planning" },
  CODING: { bg: "#0f2b22", fg: "#4dd0a7", label: "Coding" },
  TESTING: { bg: "#2e2410", fg: "#f0b35a", label: "Testing" },
  REVIEWING: { bg: "#2e1626", fg: "#e06b9c", label: "Reviewing" },
  DONE: { bg: "#0f2b1a", fg: "#46c98b", label: "Done" },
};

export function StageBadge({ stage }: { stage: Stage }) {
  const s = STYLES[stage];
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium"
      style={{ backgroundColor: s.bg, color: s.fg }}
    >
      <span
        className="h-1.5 w-1.5 rounded-full"
        style={{ backgroundColor: s.fg }}
      />
      {s.label}
    </span>
  );
}
