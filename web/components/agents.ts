import type { Stage } from "@/lib/pipeline";

export interface AgentMeta {
  key: string;
  label: string;
  role: string;
  stage: Stage;
  color: string;
  produces: string[];
}

export const AGENTS: AgentMeta[] = [
  {
    key: "planner",
    label: "Planner",
    role: "PM + Architect",
    stage: "PLANNING",
    color: "var(--color-planner)",
    produces: ["idea.md", "spec.md", "tasks.md"],
  },
  {
    key: "coder",
    label: "Coder",
    role: "Senior Engineer",
    stage: "CODING",
    color: "var(--color-coder)",
    produces: ["implementation.md"],
  },
  {
    key: "tester",
    label: "Tester",
    role: "QA Engineer",
    stage: "TESTING",
    color: "var(--color-tester)",
    produces: ["test-plan.md", "defects.md"],
  },
  {
    key: "reviewer",
    label: "Reviewer",
    role: "Staff Engineer",
    stage: "REVIEWING",
    color: "var(--color-reviewer)",
    produces: ["review.md", "feedback.md"],
  },
];

export const AGENT_BY_KEY = Object.fromEntries(
  AGENTS.map((a) => [a.key, a]),
) as Record<string, AgentMeta>;

export const STAGE_INDEX: Record<Stage, number> = {
  PLANNING: 0,
  CODING: 1,
  TESTING: 2,
  REVIEWING: 3,
  DONE: 4,
};
