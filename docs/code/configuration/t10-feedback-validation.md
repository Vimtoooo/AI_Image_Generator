# T10 - Feedback panel validation

Date: 2026-10-24. Phase C. Primary-agent implementation and review; no subagents.
Base: origin/main 604a426, with T09 e070fba verified as an ancestor after fetch.
Branch: phase-c/log-panel. Initial working tree was clean.

## T11 integration contract

Construct LogPanel on the Tk thread. After controller.start(config) returns a run
ID, call panel.start_run(id, len(config.scenes)) before the next Tk polling turn.
Deliver controller events to panel.on_event. Call panel.show_stopping only on the
first acknowledged Stop; use panel.show_error for worker faults. The host owns
window state and must still wait for controller.busy to clear before restarting.
The stage label describes feedback, not the window's execution-control state.
Destroy the panel only after worker shutdown has completed.

The feedback model keeps timestamp, scene index/script timestamp, effective seed,
stage and message. It never dumps event dictionaries or prompt content. Fractions
require the current submitted prompt and scene, finite numeric values and
0 <= value <= max with max > 0. Unknown activity is indeterminate. Queueing,
generation and downloading are distinct. Only scene_saved and terminal results
update saved-scene counts. Partial files remain represented in terminal totals.

The terminal reserves one of its 2,000 lines for a cumulative discard notice;
multiline messages count as physical lines. A separate read-only summary survives
log eviction and new starts until replaced by the next terminal result. Both
textboxes are scrollable. New messages follow the tail only if already at the
bottom. Logs stay in memory; no automatic export or persistence is introduced.

## Executed evidence

Python 3.14.3 / pytest 9.1.1 / CustomTkinter 6.0.0, Windows, no server or GPU.
Use the T02 process-local fresh-directory wrapper from apps/ and the existing
.venv/Scripts/python.exe interpreter. Commands use -p no:cacheprovider and a fresh
comfy-t10-<uuid> basetemp.

- Focused final suite: test_log_panel.py, **25 passed in 0.60s**; no Tk warnings.
- Combined suite: scene_parsing, workflow_mapping, catalog_validation,
  transport_protocol, output_storage, runner, config_panel, file_system,
  gui_worker and log_panel: **248 passed in 10.84s** before three additional
  runner-stream tests were added and passed in the final focused run.
- The combined run emitted Tk invalid-command timer warnings from sequential
  widget-suite roots. The fresh-process focused run is clean. This is recorded,
  not treated as visible GUI acceptance. The preserved download-collision test
  also printed its expected error while passing its preservation assertion.
- Existing worker heartbeat passed: 50 samples, maximum interval 0.103s. This
  measures T09 simulated I/O, not rendering throughput of the new panel.
- Scoped git diff --check passed. Management code was unchanged.

| Criterion | Evidence |
|---|---|
| CA-03.6 | Actual disabled textboxes reject insertion/deletion |
| CA-03.7 | Deterministic time, scene, timestamp, stage, seed and message checks |
| CA-03.8 | Correlated sampler fractions including 25% and 100% |
| CA-03.9 | Twelve malformed/uncorrelated cases; actual indeterminate widget mode |
| CA-03.10 | Sampler completion, downloading and individual file logs do not count scenes |
| CA-03.11 | Saved-scene event updates actual batch bar to 1/2 |
| CA-03.14 | Completed/stopped/failed summaries, partial files and absent destination |
| CA-03.16 | Multiline overflow, 2,000 displayed lines, notice and preserved summary |

Real runner streams with fictitious client/storage verify completed, stopped and
failed results; failure after one file leaves zero fully saved scenes and one
saved file. Stale/post-terminal events, repeated Stop, thread ownership, scrolling
and new-run correlation reset are also covered.

## Primary-agent review and limitations

Confirmed: bounded task scope, immutable event contract compatibility, explicit
correlation, accurate saved counts, read-only rendering, preservation and owner
thread checks. Reviewed implementation, tests, evidence and status diff; no
blocking findings. No previous unreviewed commits are included above origin/main.
Reused T08 Graphify findings; runner/worker gaps in that index remain documented.
Context7 /tomschimansky/customtkinter supplied CTkTextbox and CTkProgressBar docs.

Visible layout, full-window integration, feedback under sustained event floods
and real ComfyUI generation remain unverified. T11/T12 own window/integration
checks; Phase D remains closed. Stop after T10; T11 starts in a new chat.
