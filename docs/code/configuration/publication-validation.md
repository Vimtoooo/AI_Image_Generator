# Stacked publication review

Date: 2026-10-24. Owner requested a PR for every worked branch and selected
separate stacked PRs with documented merge order. Primary-agent review; no subagents.

## Publication branches and merge order

| Order | Publication branch | Base | Work represented |
|---|---|---|---|
| 1 | phase-b/specifications-publication | main | Phase B specifications, English migration and governance |
| 2 | phase-c/dependencies-publication | phase-b/specifications-publication | T01 environment and T02-T06 backend dependencies |
| 3 | phase-c/runner-publication | phase-c/dependencies-publication | T07 runner |
| 4 | phase-c/configuration-publication | phase-c/runner-publication | T08 configuration panel |
| 5 | phase-c/pending-work-publication | phase-c/configuration-publication | Preserved earlier work, cleanup and publication handoff |

Merge in order. Each PR targets the preceding branch so its diff stays scoped.
After merging a predecessor into main, confirm or change the next PR's base to
main before merging it. Keep predecessor branches until their dependent PRs
are retargeted; merging into a feature branch alone does not deliver to main.
Only the owner merges. No phase transition is implied.

Original local branches are preserved. `phase-b/specifications` and
`phase-b/gui-specifications` are superseded by publication item 1;
`phase-c/environment` by item 2; `phase-c/runner` by item 3;
`phase-c/configuration-panel` by item 4; `phase-c/commit-pending-work` by item 5.
These are publication replacements, not additional duplicate PRs. Foundation
PRs #1 and #2 are already merged. Historical foundation aliases need no new PR.

## Review and executed checks

Publication was rebuilt from origin/main at 1b324ab in an isolated worktree.
The original branches were not reset, rebased or force-pushed. Old commit 620feea
is absent from the publication ancestry. Its sampler functionality is preserved
in the reviewed current backend, with legacy sampler tests covering the corrected
KSampler target and returned catalog choices. No unreviewed commit is imported.

Before publication-only documentation was added, the final combined tree matched
the reviewed cb4b2fa tree with `git diff -w --exit-code cb4b2fa --`. Only three
trailing-whitespace lines in client.py/payload_mgr.py differed. Every branch's
staged scope and diff check were reviewed before committing.

Fresh verification in the isolated checkout:

- Specifications: seven management tests passed (2.853s). Initial sandbox run
  could not create accessible temporary repositories; approved escalation passed.
- Dependencies: 146 offline tests passed (3.67s).
- Runner: 28 focused tests passed (0.47s).
- Panel: 27 focused tests passed (2.26s), real withdrawn widgets/fake dialogs.
- Final stack: 206 offline application tests passed (4.93s), including the five
  preserved filesystem scenarios. Used the documented T02 directory wrapper and
  the validated Python 3.14.3/pytest 9.1.1 environment.

`scripts/prepare_pr.py --base origin/main` generated the publication scaffold.
All PR descriptions retain its eleven section headings and replace gaps with
scope, actual evidence, removals, limitations and the ordered dependency chain.

## Limits and future workflow

The manual server-dependent test_client.py was preserved but not executed.
Full CLI acceptance, visible GUI acceptance, T09-T13 and Phase D demonstration
remain pending. Historical evidence and task-board notes describe their original
session dates; this publication record supersedes older no-PR status statements.

Owner instruction: prepare and publish a reviewed PR for each substantive work
branch before session close, and report its URL. For a stack, document its base
and merge order. If publication is blocked, report the exact blocker rather than
presenting local commits as completed publication. Never merge on the owner's behalf.
