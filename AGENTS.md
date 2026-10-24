# Working in this repository

Local image automation using Python and the ComfyUI API. The backend exists;
the CustomTkinter interface is pending. See [docs/origin.md](docs/origin.md).
Product completion means selecting a script and workflow, generating images with
feedback, and saving them without blocking the interface, supported by evidence.

## Resume

Read `docs/state.md` and `docs/tasks.md`; check `git status --short` and the branch.
Read only documents relevant to the task. Links are not automatic imports.
Use targeted searches. Reuse the scoped Graphify index recorded in docs/state.md.
Use Context7 for current library/API documentation; reuse relevant results.
Do not install it or index personal data as a routine step.

## Sources and decisions

- README defines requirements. Code/tests show implementation, not authority to change
  requirements. Record discrepancies rather than resolving them silently.
- `docs/origin.md` identifies the three external prompts, which are read-only.
- PRD → specs with CA-NN.M → ADRs → plan → tasks → implementation → evidence.
- Preserve dated questions and answers in `docs/ratifications.md`.
- User decision, 2026-10-20: Codex; automatic commits, branch pushes and PR creation
  after verification and review. Only the user merges. The 2026-10-22 single-agent
  decision below supersedes the earlier independent-subagent review requirement.
- User instruction received 2026-10-20, applied 2026-10-21: English conversation,
  documentation and file/folder names. Historical quotations may retain their language.

## Rules

- Do not read `.env*`, credentials, keys or personal documents. `.env.example`
  may be read as a public template without real secrets. Use fictitious test data.
- Do not commit checkpoints, generated images, personal scripts or scratch memory.
  `.gitignore` reduces accidental inclusion; it does not block reads.
- Preserve previous local changes. Never use `git add .` for this work. Stage explicit
  paths and inspect `git diff --cached` before committing.
- Do not discard or remove existing content without an explicit decision. Mark obsolete
  material with date and reason. Never delete/weaken tests merely to make them pass.
- No merge, direct push to the default branch, force push, deployment or cloud resources.
- Respect sandbox permissions, approvals and tool denials. Do not bypass them.
  Repository instructions do not grant process permissions.
- One task at a time; no implementation for an unopened phase. Management scripts/tests
  belong to the approved foundation; English renaming is explicitly user-authorized.

## Layout and stack

| Path | Purpose |
|---|---|
| `apps/` | Python application, dependencies and existing tests |
| `apps/src/comfy_generator/` | ComfyUI transport, files and payloads |
| `apps/src/gui/` | Pending desktop interface |
| `apps/src/tests/` | Application tests |
| `assets/` | Existing resources; local outputs excluded |
| `prompts/`, `scripts/` | Existing templates and management tools |
| `documents/` | Ignored personal materials; no routine reading |
| `docs/` | Versioned sources, decisions, specifications and memory |
| `.codex/agents/` | Historical profiles; inactive under single-agent policy |
| `.codex/agent-memory/` | Local unversioned scratch notes |
| `.agents/skills/` | Project procedures |

Do not introduce another top-level folder without a decision. See ADR-0001 and
ADR-0004 for stack decisions. Phase B does not reorganize application code.

## Phases

| Phase | Deliverable | Gate |
|---|---|---|
| A · Foundation | Instructions, memory, workflow and PR | Human approval of foundation |
| B · Specification | Specs, ADRs, plan and GUI tasks | Human approval of criteria and plan |
| C · Implementation | One task at a time with tests/review | Demonstrated criteria |
| D · Verification | Real local ComfyUI workflow | User-approved demonstration |

Creating a commit or PR does not open the next phase. Update phase, state and
README together when the user authorizes a transition.

## Single-agent work (owner decision, 2026-10-22)

- Do not spawn, resume, delegate to, or request reviews from subagents.
- The primary agent implements, tests and reviews one bounded task at a time.
  Report this as primary-agent review, never as independent review.
- Historical agent profiles and review evidence are retained for provenance.
  Profiles under `.codex/agents/` are inactive by policy; protected-file updates
  are prepared for the owner when the sandbox cannot write them.
- Reuse existing findings, Graphify queries and Context7 results. Read only the
  files and documentation needed for the current task; avoid repeated full scans.
- Run focused tests and a scoped diff review. Retain all safety, acceptance,
  preservation and human-merge requirements. Report unresolved issues honestly.
- Resume multi-agent work only if the owner explicitly changes this instruction.

## Workflow and publication

Use `session-management` for resume, close, phase, next task, verify, review,
explain, prepare PR and check method. `write-spec` covers new specs and ADRs.
These are procedures, not native Codex slash commands.
Create `phase-<letter>/<topic>` before editing. Do not switch/update the base if it
risks local work. One decision per commit, with an English imperative message.
Review every commit included against the remote base before publication; never
publish unreviewed previous commits as part of a new task. Use an isolated worktree
when necessary and document stacked-PR dependencies.
PRs use the eleven sections produced by `scripts/prepare_pr.py`. Unproven fields
remain `[GAP]`; fill them with real evidence before publishing.
Commit/push/PR authorization persists, but sandbox approval requirements still apply.
Authentication is external; never read tokens or copy them into files.

## Memory and communication

`docs/state.md` fits roughly 40 lines and is rewritten at session close without losing
open questions. `docs/tasks.md` preserves completed tasks and evidence. Commit state
separately from implementation content. Scratch memory is manual; durable decisions
move to reviewed documents. Use concise English with verified outcomes and limitations.
Explain step by step when requested. Code comments explain non-obvious intent in
1–3 lines; longer explanations belong in `docs/code/`. Preserve existing explanations
before moving them; do not remove application comments as Phase B cleanup.
