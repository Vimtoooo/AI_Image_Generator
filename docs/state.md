Phase: C - Implementation
Updated: 2026-10-24. Sources and prompt hashes: docs/origin.md.

## Current position
- Phase B package approved; Phase C authorized by owner on 2026-10-21.
- Local branch: phase-c/commit-pending-work; owner-authorized pending work committed.
- T01-T02 complete with historical independent review; T03-T08 primary-agent review passed.
- Offline evidence: 206 application tests and 7 management tests passed; includes 27 panel tests.
- Session stopped after T08. T09 workers starts in a NEW chat; one completed task per chat.

## Next-session handoff
- Start with AGENTS.md, this file and docs/tasks.md; check Git status before T09.
- T09 has not started. Read its plan entry, SPEC-02/03 and T08 evidence; use build-interface skill.
- Implement thread_worker.py/test_gui_worker.py; queues, coalescing, finite shutdown and async catalog adapter.
- Panel boundary: request_catalog(id, url, deliver); return promptly, deliver(id, catalog, error) on Tk thread.
- Runner API: run(config, emit, StopControl(), run_id=...). Use a non-raising sink; runner alone emits terminal.
- Later: T09 workers; T10 logs/progress; T11 window/CLI; T12 integration/GUI; T13 delivery; Phase D needs authorization.
- T08 evidence: docs/code/configuration/t08-panel-validation.md; T07 evidence retains runner contracts/races.

## Working policy
- No subagents: owner instruction 2026-10-22. Primary agent implements, tests and reviews.
- Five .codex/agents profiles archived as .toml.disabled by owner; two skills updated and verified.
- English names, documentation, conversation, branches and new commit messages.
- Reuse scoped Graphify index and Context7 documentation; avoid repeated broad reads.
- Pending-work commits: ecbc631 (docs/policy), 994ebe8 (environment), 90147e4 (backend), add474b (earlier work).
- PR #1 merged; PR #2 was last known open. Recheck before publication.
- Dependencies are committed locally. No push/PR; review remote ancestry and exclude 620feea before publication.

## Runtime and evidence
- Desktop: Python 3.14.3, CustomTkinter 6.0.0, Tk 8.6.15; uv sync --frozen restored missing GUI dependency.
- Test interpreter: apps/.venv/Scripts/python.exe (Python 3.14.3/pytest 9.1.1); old temporary interpreter no longer runs.
- Tests use fresh temporary-directory permissions wrapper documented in T02 evidence.
- ComfyUI 0.24.0 compatibility was verified read-only on 2026-10-21.
- Endpoint: http://127.0.0.1:8188/. Startup: C:\AI\ComfyUI_windows_portable\run_nvidia_gpu.bat.
- Launch from portable directory, hidden. 2026-10-22 launch requested; endpoint still refused connection.
- No image generation performed; live T04 catalog check remains unverified.
- Graphify: %TEMP%\comfy-code-map\graphify-out\graph.json; reused backend map, new runner not indexed yet.

## Preserved work and remaining limitations
- Owner's client/CLI/GUI edits, manual client tests and SVG are committed; no live CLI acceptance claimed.
- Filesystem test rename retained all five scenarios; corrected platform patch target, all five pass.
- Local pre-policy skill backups remain on disk, ignored; see pending-work-validation.md for scope and limits.
- Evidence: docs/code/configuration/t01-environment-validation.md through t08-panel-validation.md.
- SVG structure inspected; rendered visual acceptance and Phase D demonstration remain pending.
