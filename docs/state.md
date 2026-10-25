Phase: C - Implementation
Updated: 2026-10-24. Sources and prompt hashes: docs/origin.md.

## Current position
- Phase B approved; Phase C authorized by owner on 2026-10-21. Phase D remains closed.
- T01-T09 complete. T09 primary-agent review passed; no subagents.
- Handoff branch: phase-c/t09-handoff; T09 implementation e070fba, previous handoff 83f3578.
- Evidence: 226 offline application tests (20 T09) and 7 management tests passed.
- Real withdrawn Tk heartbeat: 50 samples / 5s, max 0.103s with simulated batch/catalog I/O.
- Stop after T09; T10 starts in a NEW chat under one-completed-task-per-chat policy.

## Next-session handoff
- First check git status/branch, fetch origin, and verify T09 reached main before choosing the T10 base; preserve local changes.
- Read AGENTS.md, state/tasks, T10 plan entry, SPEC-03 and T09 worker evidence; use build-interface/session-management skills.
- T10 owns apps/src/gui/log_panel.py and apps/src/tests/test_log_panel.py: read-only logs, 2,000-line limit, preserved summaries and real progress.
- WorkerController(root, on_event, on_error=...); start(config) returns ID or None when busy/closing.
- busy clears only after terminal delivery AND observed exit; runner alone emits terminal.
- Bind request_catalog(id, url, deliver) to panel; monotonic IDs per controller, delivery on Tk thread.
- stop() acknowledges once. close(on_closed) keeps draining; destroy Tk only in on_closed.
- Queue defaults: 256 envelopes, 64 events/tick, 20ms poll; overflow log/progress gets a notice.
- Later: T11 window/CLI; T12 integration/GUI; T13 delivery; Phase D requires authorization.
- Contracts/limits: docs/code/configuration/t09-worker-validation.md; T07 retains runner races.

## Publication and working policy
- Verified: PR #8 merged into main at 8f90ae3; T01-T08 and preserved earlier work now reached main.
- PR #9 is merged into phase-c/configuration-publication, NOT main; T09 commits e070fba/83f3578 are still absent from main.
- Owner must merge the phase-c/t09-handoff PR targeting main to deliver T09 and this correction; verify ancestry, not just the merged badge.
- Owner merges only. No force-push/default-branch push; original local branches remain intact.
- Prior PRs: https://github.com/Vimtoooo/AI_Image_Generator/pull/8 and /pull/9. Older open/merge-order notes in tasks/evidence are historical.
- Automatic reviewed commits/pushes/PRs authorized; sandbox approvals still apply.
- English names/docs/conversation; primary-agent review only (owner decision 2026-10-22).
- Five .codex/agents profiles archived as .toml.disabled; ignored skill backups retained.

## Runtime and remaining limits
- Python 3.14.3 / pytest 9.1.1: apps/.venv/Scripts/python.exe; CustomTkinter 6.0.0 / Tk 8.6.15.
- Use T02 fresh-test-directory wrapper. Management temp-repo tests required approved elevation.
- Graphify: %TEMP%/comfy-code-map/graphify-out/graph.json; reuse T08 findings, runner/workers not indexed.
- ComfyUI 0.24.0 read-only compatibility checked 2026-10-21; no image generation demonstrated.
- Endpoint http://127.0.0.1:8188/; C:\AI\ComfyUI_windows_portable\run_nvidia_gpu.bat (hidden, portable cwd).
- Last 2026-10-22 startup request still met connection refusal; live T04 catalog check unverified.
- Cooperative shutdown uses finite transport limits/deadlines, not hard cancellation of stuck external I/O.
- CLI MediaUtils binding remains T11; manual server tests preserved, not acceptance evidence.
- Visible layout/native dialogs/SVG rendering and real generation remain unverified; no Phase D approval.
