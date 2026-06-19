# Agentic

A **GitHub-native autonomous software engineering framework** where specialized
agents collaborate through **filesystem artifacts** instead of direct
communication.

Each run flows `Planner → Coder → Tester → Reviewer`, loops back to the Coder on
rejection, and completes **only when both the Tester and Reviewer approve**.

> This is the **architecture & infrastructure** version. Agents are deterministic
> stubs — there is **no LLM integration yet**. Every contract (artifacts, state
> machine, rejection loop, context assembly, DI) is real and fully tested, so
> dropping an LLM into any agent's `execute()` later is a localized change.

---

## Architecture

```
Planner ──▶ Coder ──▶ Tester ──▶ Reviewer ──▶ DONE
              ▲                      │
              └──────── reject ──────┘   (Tester or Reviewer can send work back)
```

Agents **never talk to each other**. They communicate exclusively through files
under `.pipeline/<run_id>/`:

```
.pipeline/001/
├── idea.md / .json            (Planner)
├── spec.md / .json            (Planner)
├── tasks.md / .json           (Planner)
├── implementation.md / .json  (Coder)
├── test-plan.md / .json       (Tester)
├── defects.md / .json         (Tester)
├── review.md / .json          (Reviewer, read-only)
├── feedback.md / .json        (Reviewer, read-only)
└── status.json                (Orchestrator — the state machine)
```

Each artifact is written as **rendered Markdown** (for humans / the UI / git
history) plus a **typed JSON sidecar** (so downstream agents re-hydrate a
strongly-typed Pydantic object instead of parsing prose).

### State machine

```
PLANNING → CODING → TESTING → REVIEWING → DONE
```

Persisted in `status.json`. The orchestrator is the **only** authority that
mutates state — agents just return an `AgentResult`.

### Layout

```
agents/        base/ + planner/ coder/ tester/ reviewer/ (agent.py + prompt.md)
models/        run_state.py, artifact.py, agent_result.py   (Pydantic)
services/      artifact_service, context_service, state_service
orchestrator/  orchestrator.py (loop) + run.py (CLI / composition root)
.pipeline/     per-run artifacts + status.json
src/           code the Coder writes
tests/         framework tests + tests the Tester writes
web/           production-grade Next.js UI
```

**Design principles:** file-based communication only · modular · dependency
injection · strong typing · no agent-to-agent calls · no shared global state ·
fully testable.

---

## Backend — quickstart (Python 3.13, runs on 3.11+)

```bash
cd Agentic
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"        # or: pip install pydantic pytest

# Run a full pipeline (creates .pipeline/001/, writes src/ + tests/)
python -m orchestrator.run

# Resume / replay a specific run
python -m orchestrator.run --run 001

# Tests
pytest -q
```

### Adding a new agent (e.g. Architect, Security Auditor)

1. Subclass `BaseAgent`, implement `execute(context) -> AgentResult`.
2. Add any new artifact models to `models/artifact.py`.
3. Inject it in the composition root (`orchestrator/run.py`) and slot a stage in.

The orchestrator is open for extension — agents stay decoupled because they only
`read_context()` and `write_artifact()`.

---

## UI — quickstart (Next.js App Router + Tailwind)

```bash
cd Agentic/web
npm install
npm run dev          # http://localhost:3000
```

The UI reads `../.pipeline` directly (override with `PIPELINE_ROOT`). It is a
**first-class product surface**, not a debug dashboard:

- Responsive across desktop / tablet / mobile.
- Live pipeline-stage visualization with rejection-loop indicators.
- Run navigation, state-history timeline, approval status.
- Human-friendly Markdown rendering of specs, tests, reviews, defects.
- Extensible for future Slack / GitHub / CI-CD integrations.

---

## Roadmap

- LLM integration per-agent (`prompt.md` files are already the prompt contracts).
- Additional agents: Architect, Security Auditor, Documentation Writer, DevOps,
  Product Analyst.
- Git-native audit trail: commit each artifact as the pipeline advances.
- Live UI updates (websocket/poll) while a run is executing.
```
