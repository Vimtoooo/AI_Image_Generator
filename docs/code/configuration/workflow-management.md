# Workflow management configuration

This page describes the Phase A artifacts and their use. Decisions are in [ADR-0002](../../adr/0002-codex-workflow.md); historical sources are in [origin](../../origin.md).

Translation and naming update, 2026-10-21: the user requested English documentation and filenames. Active paths, profile names and procedures below reflect that authorization.

## Resources and memory

`AGENTS.md` guides the principal and requires explicitly reading `docs/state.md` and `docs/tasks.md` when resuming. State summarizes the phase, sources, stopping point, next task and blockers in approximately 40 lines. The task board preserves completion history and evidence.

Owner decision, 2026-10-22: no subagents. The primary agent performs implementation, focused tests and review. The five historical profiles are inactive by policy. Earlier delegation instructions are superseded; permissions remain enforced by the environment.

Auxiliary notes live in `.codex/agent-memory/`, ignored by Git. They are drafts, not the source of truth. Decisions that must survive a session belong in reviewed documents. Do not put secrets or personal content in this memory.

## Skills and procedures

Skills live in `.agents/skills/`: `session-management`, `write-spec`, `integrate-comfyui`, `build-interface` and `review-delivery`. Procedure names below are working conventions, not claims that native Codex interface commands exist.

| Procedure | Expected behavior |
|---|---|
| resume | Read state and tasks, check Git and sources, summarize the phase and next authorized task |
| close | Update tasks and state, record evidence and blockers, publish only after review |
| phase | Show the current phase, deliverable, exit condition and missing approval |
| next-task | Select work from the open phase, define scope, execute and submit for verification and review |
| new-spec | In Phase B, describe behavior and criteria with explicit sources and gaps |
| new-adr | Record a decision; if open, propose alternatives and ratifications before finalizing it |
| verify | Run appropriate checks, distinguish infrastructure failures, record actual commands and results |
| review | Perform primary-agent review of the diff and report findings without softening them |
| explain | Explain a topic and its evidence without changing code |
| prepare-pr | Generate a description, fill gaps with evidence, and publish after verification and review |
| check-method | Compare hashes of the three authorized files, analyze changes and record local impact |

The `scripts/prepare_pr.py` generator produces a description with eleven sections in order: 🧭 What changes; ❓ Why; ⚙️ How it works; 🧾 Commits; ✅ Acceptance criteria; 📁 Files; 🗑️ Removals; 🔎 Verification; 🛡️ Scope and data checks; ⏳ Limitations and questions; 🙋 What needs your action. Running it does not publish anything. Unsupported fields remain `[GAP]`; Git history cannot establish that a test or review passed. Run `python scripts/prepare_pr.py --help` for the implemented options (`--repo`, `--base`, `--title`, `--summary`, `--output`).

## Git and review routine

Open a working branch before the first edit. Inventory local changes and stage explicit paths rather than adding everything. Do not discard earlier changes to clean the tree. After verification, an agent other than the author reviews the publication diff. The principal confirms findings and allows at most two correction rounds; remaining blockers return to the owner.

The plan authorizes commits, branch pushes and PR creation. Merging belongs exclusively to the user; agents do not push directly to `main` or force push. Permission changes do not follow automatically from this authorization. If a tool denies an action, record the reason and respect the restriction.

## Boundaries and maintenance

Keep `documents/` untouched. New examples use fictional data. Do not read secrets or environment files, except the public `.env.example` template; do not publish checkpoints or generated images. `.gitignore` does not untrack existing files or control reads: staged-file review remains necessary.

This configuration does not activate any Claude hook. Graphify is optional and was not installed by the foundation; if future use is proposed, review exclusions before indexing and never bypass boundaries to build a map.

Long implementation explanations belong in `docs/code/<area>/`; code comments explain only intent that is not evident from the code. Do not remove existing documentation to meet this convention without preserving its content and justifying the change. The README receives targeted corrections and remains in English.
