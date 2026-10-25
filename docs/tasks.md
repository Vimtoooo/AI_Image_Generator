# Task board

Update, 2026-10-24 (T09): worker lifecycle is complete; 20 focused worker tests
and 226 combined offline application tests passed. Seven management tests passed.
See [T09 evidence](code/configuration/t09-worker-validation.md). T10 is next in a
new chat. Earlier T09-not-started and PR-open statements below are historical.
PRs #3-#7 are merged, but #4-#7 targeted feature branches, so main lacks T01-T08.
[Recovery PR #8](https://github.com/Vimtoooo/AI_Image_Generator/pull/8) targets main;
merge it first, then retarget the T09 PR to main before merging. Owner merges only.

Current update, 2026-10-24: the owner authorized committing all pending repository
work. Phase B and T01-T08 files are recorded in scoped local commits;
older statements below about read-only Git and uncommitted dependencies are
historical. Publication review completed; PRs #3-#7 are open in order. See
[publication and merge order](code/configuration/publication-validation.md).
Review evidence: [pending-work validation](code/configuration/pending-work-validation.md).
T09 remains next in a new chat; no new implementation task was opened.

Updated 2026-10-21. Status values: `todo`, `in progress`, `done · evidence`.
Keep completed tasks. Product criteria use stable CA-NN.M IDs; a planned test is not evidence.

| ID | Phase | Task | Acceptance / evidence required | Status |
|---|---|---|---|---|
| A01 | A | Record origin, PRD and decisions | Reviewed sources, hashes, scope and adaptations | done · independent review 2026-10-20 |
| A02 | A | Configure instructions, profiles and skills | Five profiles, five skills and eleven procedures | done · TOML and skill validation; new-session discovery not demonstrated |
| A03 | A | Organize memory and publication boundaries | Concise state, task board, exclusions and preserved local work | done · hashes/exclusions checked |
| A04 | A | Create PR description generator | Eleven ordered sections, isolated Git/error/gap tests | done · seven tests passed |
| A05 | A | Correct README status | UI pending and existing tests described accurately | done · scoped diff reviewed |
| A06 | A | Validate and review foundation | Evidence and independent review without blockers | done · foundation-validation.md |
| A07 | A | Publish foundation | Scoped commits, branch push and PR | done · [PR #1](https://github.com/Vimtoooo/AI_Image_Generator/pull/1) |
| A08 | A | Approve foundation | Human approval and merge | done · owner merged #1 at 8e6115b on 2026-10-20 |
| B01 | B | Specify files, models and inputs | SPEC-01 and ratified product decisions | done - 18 criteria reviewed; package approved 2026-10-21 |
| B02 | B | Specify execution, feedback and window | SPEC-02/03 with observable criteria | done - 19 execution and 16 UI criteria reviewed; package approved |
| B03 | B | Assess runtime and client limitations | ADR-0003/0004 and sourced assessment | done - runtime evidence and ComfyUI 0.24.0 read-only compatibility recorded |
| B04 | B | Prepare technical plan and task breakdown | All 53 criteria mapped to T01–T13 | done - all 53 criteria mapped to approved T01-T13 |
| B05 | B | Approve Phase B package | Owner approves specs, ADRs and plan | done · owner approved 2026-10-21 and authorized Phase C subject to entry checks |
| B06 | B | Standardize English names and documentation | Updated references, helper tests and profile/skill validation | done - English migration independently reviewed; publication pending |
| C01 | C | Implement approved tasks in small units | Historical umbrella task, expanded below without reusing its ID | todo · Phase C closed |
| D01 | D | Demonstrate full local generation | Real ComfyUI evidence per criterion and human acceptance | todo · Phase D closed |

## Implementation breakdown

The [implementation plan](implementation-plan.md) defines exact file ownership, dependencies,
contracts and acceptance mapping. Phase B approval and Phase C authorization were recorded on 2026-10-21.
The status table below distinguishes completed implementation from planned work.

| ID | Depends on | Deliverable | Status |
|---|---|---|---|
| T01 | Phase B gate | Reproducible Python/CustomTkinter environment | done - [T01 evidence](code/configuration/t01-environment-validation.md); independent review passed |
| T02 | T01 | Immutable contracts and timestamped-script parser | done - [T02 evidence](code/configuration/t02-script-validation.md); 32 tests, independent review |
| T03 | T02 | Connected workflow mapping and isolated payloads | done - [T03 evidence](code/configuration/t03-workflow-validation.md); primary-agent review passed |
| T04 | T03 | Server catalog and parameter validation | done - [T04 evidence](code/configuration/t04-catalog-validation.md); 101 combined tests passed |
| T05 | T04 | Correlated transport, history/cache and finite waits | done - [T05 evidence](code/configuration/t05-transport-validation.md); primary-agent review passed |
| T06 | T05 | Safe batch directories and atomic image storage | done - [T06 evidence](code/configuration/t06-output-validation.md); 146 combined tests, primary-agent review passed |
| T07 | T06 | Serial runner, per-scene seeds and cooperative Stop | done - [T07 evidence](code/configuration/t07-runner-validation.md); 174 combined tests, primary-agent review passed |
| T08 | T07 | Configuration panel and testable catalog boundary | done - [T08 evidence](code/configuration/t08-panel-validation.md); 201 combined tests, primary-agent review passed |
| T09 | T08 | Workers, queues, stale-event control and shutdown | done - [T09 evidence](code/configuration/t09-worker-validation.md); 20 worker / 226 combined tests, primary-agent review passed |
| T10 | T09 | Read-only logs, real progress and summaries | todo |
| T11 | T10 | Main window, catalog wiring and CLI-compatible launch | todo |
| T12 | T11 | Offline integration, races and real GUI interaction checks | todo |
| T13 | T12 | Evidence review, documentation and delivery PR | todo |

The owner approved Phase B and authorized Phase C on 2026-10-21, then created
`phase-c/environment` and validated the prepared environment.
T01-T08 are complete; T09 is next, in a new chat. ComfyUI 0.24.0 passed read-only compatibility checks. See
[entry check](code/configuration/phase-c-entry-check.md). Git publication remains
blocked for this agent; implementation can proceed using the validated environment.
2026-10-23 update: one completed task per chat, then handoff and stop. T07 was
implemented on `phase-c/runner`; earlier uncommitted dependencies still prevent
standalone publication. The earlier read-only Git status is historical: branch
creation succeeded this session. See T07 evidence for the current test interpreter.

T08 session, 2026-10-23: configuration panel completed on `phase-c/configuration-panel`.
27 focused tests and 201 combined tests passed. Real withdrawn widgets were tested;
visible layout/native-dialog acceptance remains pending. T09 must dispatch catalog
I/O asynchronously and deliver results on the Tk thread using the T08 callback
contract. Earlier uncommitted dependencies still prevent standalone publication.

Independent specification and migration reviews completed on 2026-10-21 with no
blocking findings; minor corrections received a focused follow-up review. See
[Phase B validation](code/configuration/phase-b-validation.md). Publication remains
blocked by this session's read-only Git metadata permissions; no Phase B commit or
PR has been created. Draft statuses above remain pending final package delivery.
Foundation closure PR #2 remains separate; the Phase B PR will be stacked on that
reviewed branch while it is open, excluding the owner's previous application commit.

Owner instruction, 2026-10-22: no more subagents. Future task reviews are performed
by the primary agent and must not be described as independent. Prior independent
review evidence remains historical. Protected profile/skill changes are prepared
in `%TEMP%\comfy-single-agent-update\apply.ps1`; owner applied the script successfully and the archive/skill changes were verified.
