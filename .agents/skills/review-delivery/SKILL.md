---
name: review-delivery
description: Review scoped changes and evidence before commits and PR publication.
---

Read AGENTS.md, the task, its criteria and the bounded diff. Do not delegate.
Owner decision 2026-10-22: primary-agent review only; never claim independence.
Inspect all commits included in the PR to catch accidental previous work.
Check requirement sources, actual evidence, regressions, removals and preserved local
changes. Check proposed files for accidental secrets/personal material without reading
sensitive files to prove their absence. Do not reproduce sensitive content in findings.
Check that skills, profiles and documentation do not promise nonexistent enforcement.
Return Blocked / Verify / Confirmed with file:line, impact and a concrete action,
within 300 words. Blocked findings prevent commits; substantive questions go to the primary.
In a second pass focus on corrections/regressions. After two failed rounds, report the blocker.
