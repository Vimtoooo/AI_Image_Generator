---
name: write-spec
description: Write traceable PRDs, specifications and ADRs for this ComfyUI generator.
---

Read the current phase and task in docs/state.md and docs/tasks.md.
Write only assigned docs/ files; do not rewrite docs/origin.md without a user request.
Do not write specs for an unopened phase. For a spec, cite the README requirement
or user decision; describe behavior, boundaries, failures and CA-NN.M criteria in
Given/When/Then form. Each criterion must be independently observable; never reuse IDs.
For an ADR, record context, options, consequences and when to reconsider it.
An open decision remains proposed until the user answers.
Record gaps and R-NN.M blocks in docs/ratifications.md, with a recommendation,
real alternatives and consequences. Route questions to the primary agent.
Keep the question, add dated answers below it, and propagate decisions to specs/ADRs.
If the meaning of a chosen option changes, obtain renewed ratification.
Report required changes outside docs/ to the primary agent rather than editing them.
