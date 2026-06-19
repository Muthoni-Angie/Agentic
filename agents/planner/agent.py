"""Planner — Product Manager + Software Architect.

Generates a high-potential, revenue-bearing product idea, a technical spec, and
a task breakdown. This stub produces deterministic artifacts (no LLM yet) but
respects the full artifact contract so the rest of the pipeline is exercisable.
"""

from __future__ import annotations

from models.agent_result import AgentResult
from models.artifact import (
    IdeaArtifact,
    SpecArtifact,
    Task,
    TaskArtifact,
)
from services.context_service import AgentContext

from agents.base.base_agent import BaseAgent


class PlannerAgent(BaseAgent):
    name = "planner"

    def execute(self, context: AgentContext) -> AgentResult:
        run_id = context.run_id

        idea = IdeaArtifact(
            run_id=run_id,
            created_by=self.name,
            name="LedgerLoop",
            pitch="An automated reconciliation platform that closes the books "
            "for SMBs in minutes instead of days.",
            problem="Finance teams waste hours manually matching transactions "
            "across banks, payment processors and accounting systems.",
            target_market="Small and mid-sized businesses with 10–500 employees "
            "running multiple payment rails.",
            revenue_streams=[
                "Per-seat SaaS subscription",
                "Usage-based fee per reconciled transaction batch",
                "Premium tier for multi-entity consolidation",
            ],
            scale_potential="Horizontally scalable SaaS; every business with a "
            "bank account is a potential customer.",
        )

        spec = SpecArtifact(
            run_id=run_id,
            created_by=self.name,
            overview="A service that ingests transactions from multiple sources "
            "and produces a reconciled ledger with an audit trail.",
            architecture="Modular Python core with a pure-function matching "
            "engine, a pluggable source adapter layer, and a thin API surface.",
            components=[
                "Matching engine (deterministic, pure functions)",
                "Source adapters (bank, processor, ledger)",
                "Reconciliation report builder",
            ],
            requirements=[
                "Match transactions across two sources by amount and date",
                "Flag unmatched transactions on both sides",
                "Produce a summary with matched/unmatched counts",
            ],
            non_functional=[
                "Deterministic and side-effect-free core",
                "100% unit-test coverage of the matching engine",
                "Strong typing throughout",
            ],
        )

        tasks = TaskArtifact(
            run_id=run_id,
            created_by=self.name,
            tasks=[
                Task(id="T1", title="Implement transaction model"),
                Task(id="T2", title="Implement matching engine"),
                Task(id="T3", title="Implement reconciliation summary"),
            ],
        )

        artifacts = [
            self.write_artifact(idea),
            self.write_artifact(spec),
            self.write_artifact(tasks),
        ]

        return AgentResult(
            agent=self.name,
            success=True,
            artifacts=artifacts,
            messages=[
                f"Generated idea '{idea.name}' with "
                f"{len(idea.revenue_streams)} revenue streams.",
                f"Specified {len(spec.components)} components and "
                f"{len(tasks.tasks)} tasks.",
            ],
        )
