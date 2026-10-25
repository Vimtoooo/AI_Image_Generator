Phase: C - Implementation
Updated: 2026-10-25. Sources and prompt hashes: docs/origin.md.

## Current position
- Phase B approved; Phase C authorized 2026-10-21. Phase D remains closed.
- T01-T11 complete. T11 primary-agent review passed; no subagents.
- Branch: phase-c/window-launch; T11 3782269 on reviewed T10 6f0c6bd.
- T09 e070fba verified in main via PR #10; older merge-target warnings resolved.
- T11 evidence: docs/code/configuration/t11-window-validation.md.
- T12 automated work committed at a120472; visible checks still pending.
- Final T12 verification: 287 application tests and 7 management tests passed.
- Each module ran in isolation with no stderr; full-window heartbeat max 0.102s.
- Owner authorized T11-T13 in this chat; update state after each task.

## Next-session handoff
- PR #11 (T10) remains a dependency; main is 604a426. Owner merges only.
- Read T12 plan entry and specs; T08-T11 evidence records integration contracts.
- T12 next: visible layout, scrolling, native dialogs, Reset/Stop/close checks.
- Desktop helper native pipe unavailable after retry/reset; owner checking setup.
- Evidence/matrix: docs/code/configuration/t12-integration-validation.md (53 criteria).
- Window assembled; launch via python src/main.py --gui; no args retains CLI.
- After controller.start(config) returns ID, call panel.start_run(id, scene count).
- Route on_event to panel.on_event; on_error to panel.show_error.
- Call panel.show_stopping on first acknowledged Stop; host owns window states.
- Feedback stage is not execution-control state. Last summary survives new runs.
- Worker busy clears after terminal delivery AND observed exit; wait before restart.
- Bind request_catalog(id, url, deliver); monotonic IDs, Tk-thread delivery.
- close(on_closed) keeps draining; destroy Tk only in on_closed. No UI-thread join.
- Queue defaults: 256 envelopes, 64 events/tick, 20ms poll; overflow gets a notice.
- Do not mark T12 complete yet. After visual checks, update state then T13 delivery.

## Publication and working policy
- Automatic reviewed commits, feature-branch pushes and PR creation authorized.
- Owner merges only; no default-branch push or force push. Preserve local work.
- Review every included commit against remote base; state committed separately.
- English names/docs/conversation; primary-agent review only since 2026-10-22.
- Historical profiles remain archived; ignored skill backups retained.

## Runtime and remaining limits
- Python 3.14.3 / pytest 9.1.1: apps/.venv/Scripts/python.exe; CTk 6.0.0 / Tk 8.6.15.
- Use T02 fresh-test-directory wrapper. Management temp-repo tests needed elevation.
- Graphify: %TEMP%/comfy-code-map/graphify-out/graph.json; reuse T08 findings.
- Runner/workers not indexed. Context7 Tk timers/HTTP server docs fetched for T12.
- ComfyUI 0.24.0 read-only compatibility checked 2026-10-21; no generation demo.
- Endpoint http://127.0.0.1:8188/; C:\AI\ComfyUI_windows_portable\run_nvidia_gpu.bat.
- Last 2026-10-22 startup met connection refusal; live T04 catalog unverified.
- Shutdown is cooperative with finite transport waits, not hard I/O cancellation.
- CLI MediaUtils binding fixed; manual server tests are not acceptance evidence.
- Visible layout/dialogs/SVG and real generation unverified. Phase D remains closed.
- Offline preview PID 16900 was launched; its title ends OFFLINE TEST.
- Preview fixtures: %TEMP%/comfy-t12-visible-6a3f0da8e1d840a7b98644d79a1a5dab.
- Preview uses fictional catalog/runner, not real ComfyUI. Close it after visual checks.
