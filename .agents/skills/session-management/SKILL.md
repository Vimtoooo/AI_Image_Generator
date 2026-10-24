---
name: session-management
description: Resume, close, verify and publish reviewed work in this ComfyUI repository.
---

Read AGENTS.md, docs/state.md and docs/tasks.md from the repository root.
Use only the requested procedure; these names are not native slash commands.

- resume: inspect branch/status and summarize phase, stopping point, previous local
  changes, questions and next authorized task. Do not re-request existing authorization.
- close: update task evidence and state without losing open questions. Perform primary-agent
  review, commit state separately, and publish authorized branch/PR changes without merging.
- phase: show the exit criteria and remaining work; advance only on a human decision.
- next-task: choose the first released task of the open phase. Read its source and
  criteria; implement, test and review directly, at most two correction rounds.
- verify: run relevant checks. Management tests: python -m unittest discover -s scripts
  -p "test_*.py". Application tests that connect to ComfyUI are not offline tests.
  Record unrelated failures rather than hiding them.
- review: inspect the scoped diff against criteria directly; verify findings without delegating.
- explain: explain the topic without editing code unless separately requested.
- prepare-pr: inspect the base and every included commit; run python scripts/prepare_pr.py
  --base origin/main. Fill gaps with evidence, keeping all eleven headings.
  Write the exact body to a temporary file and use gh pr create --body-file.
  Commits, branch pushes and PR creation are authorized after verification/review; merge is not.
- check-method: read only the three external files named in docs/origin.md, compare
  hashes, document applicable changes, and review before updating the source record.

write-spec covers new specs and ADRs. Never invent phase approval or include unrelated
previous work. Scratch notes in .codex/agent-memory/ are optional and manual;
promote verified durable decisions to reviewed docs.
