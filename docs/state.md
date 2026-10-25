Phase: C - Implementation
Updated: 2026-10-24. Sources and prompt hashes: docs/origin.md.

## Current position
- Phase B approved; Phase C authorized 2026-10-21. Phase D remains closed.
- T01-T10 complete. T10 primary-agent review passed; no subagents.
- Branch: phase-c/log-panel, based on origin/main 604a426; clean initial tree.
- T09 e070fba verified in main via PR #10; older merge-target warnings resolved.
- T10 evidence: docs/code/configuration/t10-feedback-validation.md.
- Final focused suite: 25 passed; earlier combined suite: 248 passed.
- Combined Tk timer warnings recorded; focused fresh-process run clean.
- Stop after T10. T11 starts in a NEW chat, one completed task per chat.

## Next-session handoff
- Check status/branch and fetch origin; verify T10 ancestry before choosing a base.
- Read T11 plan entry, SPEC-03, T08/T09/T10 integration contracts and relevant skills.
- T11 owns main_window.py, gui/__init__.py, main.py and entrypoint/window tests.
- Assemble configuration, feedback, controls and catalog; preserve existing CLI.
- After controller.start(config) returns ID, call panel.start_run(id, scene count).
- Route on_event to panel.on_event; on_error to panel.show_error.
- Call panel.show_stopping on first acknowledged Stop; host owns window states.
- Feedback stage is not execution-control state. Last summary survives new runs.
- Worker busy clears after terminal delivery AND observed exit; wait before restart.
- Bind request_catalog(id, url, deliver); monotonic IDs, Tk-thread delivery.
- close(on_closed) keeps draining; destroy Tk only in on_closed. No UI-thread join.
- Queue defaults: 256 envelopes, 64 events/tick, 20ms poll; overflow gets a notice.
- Later: T12 integration/GUI, T13 delivery; Phase D requires authorization.

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
- Runner/workers not indexed. Context7 textbox/progress docs fetched for T10.
- ComfyUI 0.24.0 read-only compatibility checked 2026-10-21; no generation demo.
- Endpoint http://127.0.0.1:8188/; C:\AI\ComfyUI_windows_portable\run_nvidia_gpu.bat.
- Last 2026-10-22 startup met connection refusal; live T04 catalog unverified.
- Shutdown is cooperative with finite transport waits, not hard I/O cancellation.
- CLI MediaUtils binding remains T11; manual server tests are not acceptance evidence.
- Visible layout/dialogs/SVG, feedback flood throughput and real generation unverified.
