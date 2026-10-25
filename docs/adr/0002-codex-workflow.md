# ADR-0002: adapt the management method to Codex

Date: 2026-10-20. Status: accepted by the owner through approval of the foundation plan. Sources and hashes: [origin record](../origin.md).

Translation and naming update, 2026-10-21: the user requested English documentation, identifiers and filenames. Active names below reflect that request. The original choice of Portuguese management documentation is superseded by this language decision; other historical decisions remain unchanged.

## Superseding decision - 2026-10-22

The owner disabled all subagent work to reduce token use. Historical team/profile
and independent-review decisions below are superseded: the primary agent now
implements, tests and reviews directly, without claiming review independence.
No agent delegation or reactivation is permitted without a new owner instruction.
Historical decisions and evidence remain intact.

## Context

The three prompts provide a method for specification, review, memory and publication. Their examples use Claude Code, another domain, and database and server phases that do not fit this local application. Literal copying would create nonexistent controls and work without a requirement.

## Decision

| Topic | Approved adaptation |
|---|---|
| Project instructions | `AGENTS.md`, at most 200 lines, explicitly requiring state and task reading |
| Profiles | Five `.codex/agents/*.toml` files: repository-explorer, spec-writer, implementer, tester and reviewer; models inherited from the session |
| Procedures | Five skills in `.agents/skills/`, covering the method's eleven procedures; these are not native slash commands |
| Memory | Versioned `docs/state.md` and `docs/tasks.md`; ignored auxiliary `.codex/agent-memory/` |
| Team | Principal coordinates at most three simultaneous subagents, without overlapping writes; subagents neither delegate nor publish |
| Review | Author and reviewer are different; at most two correction rounds before reporting a blocker |
| Git | Automatic commits, branch pushes and PRs after checks and review; human merge, no direct push to `main` or force push |
| Documents | Management in `docs/`, now English by the request received 2026-10-20 and applied 2026-10-21; `documents/` untouched; README remains English |
| Phases | A: foundation; B: specification; C: implementation; D: local verification |
| Tools | Python PR generator; Graphify optional and not installed by this delivery |

## Enforcement and limitations

Permissions and the sandbox are enforced by the environment. Markdown, TOML and written role boundaries guide agents but do not provide file isolation, shell blocking or guaranteed compliance. `.gitignore` reduces accidental inclusion; it neither protects tracked files nor prevents reading.

Do not copy `settings.json`, `PreToolUse` hooks, permission fields or Claude-only commands as if they were active Codex controls. Do not change global permissions or bypass a tool denial. If the session does not load local profiles automatically, the principal must explicitly include their role and boundaries in the delegation request; this remains an instruction, not a technical barrier.

The principal checks the diff and staged file list while preserving earlier changes. Secrets, personal documents, checkpoints and generated images must not be published. Authentication or permission blockers are recorded without claiming completed publication.

## Rejected alternatives

Copying `.claude/` literally would create false expectations. Installing Graphify would add optional work. Introducing database and login phases would divert from the product. Retaining an absolute push prohibition would contradict explicit plan approval and the autonomy update in the source norms.

## Consequences and review

The method preserves traceability and review through artifacts suited to this task. Literal equivalence with the original environment's hooks and menus is lost. The principal applies consequences outside `docs/` in `AGENTS.md`, profiles, skills, exclusions and the generator; all undergo independent review.

Revisit when Codex capabilities, permissions, team size or the need for additional executable controls changes. Accepting this ADR did not automatically approve final deliverables or open Phase B; the subsequent phase authorization is recorded separately.