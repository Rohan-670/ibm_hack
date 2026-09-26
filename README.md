# RepoPilot

A shared repo-intelligence engine, built for IBM Bob 2.0, that powers two
developer workflows from one set of subagents:

- **PR / Release mode** — a scored Release Readiness Report: breaking
  changes, test coverage gaps, doc drift, and checklist compliance.
- **Onboarding mode** — an Onboarding Brief: architecture map, "where
  things live," domain glossary, Day-0 setup checklist, safest-first-task
  ranking, and a self-check quiz.

The two modes share intelligence: onboarding-agent reuses compliance-agent's
parsed checklist and diff-analyst's file-churn risk scan instead of
recomputing them. See `demo/baseline-timing.md` for measured before/after
numbers.

## Problem this solves

Reviewers spend 25-40 minutes per PR manually checking for breaking
changes, missing tests, and doc drift — and things still slip through. New
contributors take 3-5 days to make a first meaningful commit because
there's no fast way to absorb a codebase's structure and conventions. Both
problems come from the same missing capability: fast, synthesized repo
understanding.

## Status of this repo

Everything in `orchestrator/agents/*.py` is a **working rule-based
reference implementation** — it runs right now, with no Bob access or
Bobcoins required, against the real sample project and a real planted-bug
PR in this repo. This exists so the whole pipeline (parallel execution,
shared state between agents, report generation) is provably correct before
spending hackathon time/Bobcoins wiring up live Bob calls.

`bob-agents/*.md` are the exact role-definition prompts to paste into Bob
IDE's Custom Modes during the hackathon. `orchestrator/bob_backend.py`
shows the swap point: replace a rule-based agent call in
`orchestrator/run.py` with `bob_backend.run_bob_agent(...)` and the rest of
the pipeline (scoring, report building, onboarding brief) doesn't change,
because both backends return the same JSON shape defined in
`bob-agents/output-schema.md`.

**To make this a genuine Bob 2.0 submission:**
1. Run `/init` in Bob IDE on `sample-project/` → let it regenerate
   `sample-project/AGENTS.md` for real (this repo ships a hand-written
   placeholder so the pipeline works before you do this).
2. Create the 5 custom modes in Bob IDE using the files in `bob-agents/`.
3. Swap the agent calls in `orchestrator/run.py` to use
   `bob_backend.run_bob_agent()` instead of the rule-based modules.
4. Run both modes for real, export the Bob task sessions into
   `bob_sessions/` (see that folder's README for the exact steps).

## Repo layout

```
sample-project/         The demo app (Flask "Tasks API")
  app/                  routes.py, db.py, __init__.py
  tests/                unittest suite
  AGENTS.md             Repo context (placeholder — replace with real /init output)
bob-agents/              Role-definition prompts for Bob's 5 custom modes
checklist.md             Mock release/onboarding compliance checklist
orchestrator/            Orchestration + rule-based reference agents
  agents/                diff_analyst.py, test_gap.py, doc_sync.py, compliance.py, onboarding.py
  bob_backend.py         Swap-in wrapper for real Bob Shell calls
  report_builder.py      Scoring + report generation
  run.py                 CLI entrypoint
demo/                    Planted-bug diff + before/after timing writeup
bob_sessions/            Bob task session exports go here (required for judging)
```

## Running it

```bash
cd sample-project && pip install -r requirements.txt && cd ..

# See the app work + baseline tests pass on master
cd sample-project && python -m unittest discover tests && cd ..

# PR mode: analyze the planted-bug branch
python -m orchestrator.run --mode=pr --base=master --branch=feature/bulk-update
cat release-report.md

# Onboarding mode (run PR mode first so setup-checklist.json exists to reuse)
python -m orchestrator.run --mode=onboard
cat onboarding-brief.md
```

## The planted PR (`feature/bulk-update`)

Four issues were deliberately introduced so the demo has ground truth to
check the agents against:
1. **Breaking change**: `completed` renamed to `is_done` in the task
   response — with no version bump, no CHANGELOG entry, and it actually
   breaks the existing test suite (verified — see `demo/baseline-timing.md`).
2. **Untested endpoint**: `POST /tasks/bulk_update` added with zero test
   coverage.
3. **Undocumented env var**: `TASKS_MAX_LIMIT` read from the environment
   but missing from `.env.example`.
4. **Missing CHANGELOG entry** for a PR that changes API behavior.

All four are caught by the reference agents (see `release-report.md` after
running PR mode) with file/line evidence and suggested fixes — this is the
project's core proof point.

## IBM Bob 2.0 features used / to be used live

- **Agent mode + custom modes as subagents** — 5 scoped roles
  (`bob-agents/*.md`), each with its own tool-access constraints.
- **Parallel tasks** — the 4 PR-mode agents run concurrently
  (`orchestrator/run.py` uses a thread pool; timings are logged in
  `release-report.md` as proof).
- **Document understanding** — `compliance-agent` is fed `checklist.md`
  as context rather than having the rules hardcoded.
- **`/init`** — generates `AGENTS.md`, the shared context source every
  other agent (especially `onboarding-agent`) builds on.
- **Bob Shell (non-interactive)** — `orchestrator/bob_backend.py` is the
  intended production path for running agents headlessly/in CI.

## Optional IBM watsonx.ai integration

`release-report.md` and `onboarding-brief.md` are plain Markdown — pipe
either through watsonx.ai's Granite model (see the project write-up for a
ready-to-use `summarize()` function) to generate audience-tailored versions:
an engineer-facing, manager-facing, and auditor-facing summary of the same
report; or a junior-vs-senior-dev version of the onboarding brief.
