# Technical implementation plan · ComfyUI desktop interface

Date: 2026-10-20. Translated and updated: 2026-10-21. Status: approved by the owner
on 2026-10-21; Phase C authorized subject to entry checks. Sources: [SPEC-01](specs/01-configuration.md),
[SPEC-02](specs/02-execution.md), [SPEC-03](specs/03-interface-feedback.md),
[ADR-0003](adr/0003-desktop-integration.md), [ADR-0004](adr/0004-python-environment.md)
and [ratifications](ratifications.md).

## Entry gate and boundaries

Execute T01–T13 in order, one task at a time, only after human approval of the
criteria, ADRs and this plan. R-B.1–R-B.8, R-A3.1, R-A3.2 and R-A4.1 follow the
owner's confirmed choices of 2026-10-20. Phase B delivers documentation; this plan
does not itself authorize dependency or application changes.

Before each task, check the diff and inventory in `state.md`. Earlier local edits,
including new or deleted tests, require separate provenance review: neither absorb
them into task commits nor discard them. Record the actual test baseline and
compare the complete PR commit set against origin/main.

## Proposed internal contracts

`apps/src/comfy_generator/models.py` holds dataclasses without Tk imports:

- `Scene(index, timestamp, timestamp_seconds, description)`, with 1-based index.
- `NodeMapping(sampler, checkpoint, latent, positive, negative, decode, save)`:
  string IDs validated against classes, connections and output slots from SPEC-01.
- `GenerationConfig`: frozen snapshot of scenes, copied workflow, node mapping,
  server URL, destination, global prompts, width/height, steps, cfg, sampler,
  scheduler, seed and scene deadline. No references to Tk variables or widgets.
  Its graph is a private copy, never reused as a mutable submission payload.
- `GenerationEvent(run_id, kind, scene_index, prompt_id, data)`: kinds `state`,
  `scene_started`, `submitted`, `progress`, `saving`, `scene_saved`, `log`, `terminal`.
  Progress has value/max only with reliable correlation; otherwise indicate
  indeterminate activity. A terminal event contains exactly one `RunResult`.
- `RunResult(status, total, saved_scenes, saved_files, output_dir, error)`:
  status is `completed`, `stopped` or `failed`. Structured errors identify scene,
  stage, reason, suggested action and whether submission has an unknown result.

`runner.py` exposes `run(config, emit, stop_control) -> RunResult`, without GUI
imports. Prevalidate every scene before the first POST and prepare a clean copy
of the selected subgraph per scene. Draw a seed per scene only for -1, recording
the actual seed in payload and event. Count completion only after all scene files
are published. One final block emits exactly one terminal event, including on
exception or Stop. Its return is the same result; the worker does not emit another
terminal notification from that return.

`StopControl` combines Event and Lock. Stop and authorization of the next POST
share the lock. Connect WS first; under the lock check Stop and mark submission
as started before POST. If Stop wins, prevent submission; if submission wins,
that scene is already current. Never hold the lock during I/O: acknowledging Stop
must not wait for an HTTP response.

`client.py` accepts injectable transport, monotonic clock and callbacks. A new
tracking method returns every mapped SaveImage descriptor after successful
history. Preserve legacy `track_generation_progress` through an explicit adapter:
retain its first-image-dictionary return and compatible public errors; the runner
uses the new list-returning method. Never silently turn a legacy return into a
list. Record any further adapters needed before changing existing signatures.

Open WS with client_id before POST; correlate prompt_id and require terminal,
successful history. `executed` alone is insufficient. Cache uses the same contract.
After WS loss with a known prompt_id, poll history every 2 seconds until deadline;
never repeat POST. HTTP connection/read limits are 10/60 seconds and WS polling
is 1 second, all capped by remaining scene time. The ratified 30-minute default
includes queueing and downloads. Inject clock and sleep for tests. Close sockets
and sessions in finally. Deadline causes local failure with a warning that server
work may remain active; never call /interrupt.

`formatting_utils.py` owns pure parsing and prompt composition. `file_system.py`
owns UTF-8/BOM reading and output storage. Validation never modifies source files
or creates a batch. Before POST, create an exclusive directory and test writing
with an owned temporary file. Client transport streams downloads into the storage
helper; the helper owns local names, temporary lifecycle and atomic publication
without replacement. On Windows, same-volume rename must fail if the target
exists; choose another exclusive name on collision. Never use overwriting replace.
Delete only attempt-owned temporary files; complete files survive failures.

`payload_mgr.py` detects chains, validates explicit mapping and extracts only the
seven selected roles. Update sampler/scheduler on KSampler and checkpoint on its
loader. Enforce finite numbers and catalog limits without rejecting valid integer
CFG input. Never infer architecture by reading a .safetensors file.

GUI ownership: `config_panel.py` controls and snapshot; `log_panel.py` terminal and
summary; `thread_worker.py` threads/channels; `main_window.py` state and Tk lifecycle.
Threads publish through `queue.Queue`, drained through `after` on the main thread.
Coalesce repetitive progress per run/scene and bound pending messages without
losing terminal events. Drain in batches to preserve responsiveness. Only Tk
mutates widgets. Reject stale run_id events; catalog uses increasing request_id
and ignores obsolete responses. Loading never silently replaces a valid model.

T08 defines the catalog request/result callback boundary and tests the panel with
a fake catalog service. T09 implements asynchronous execution behind that boundary;
T11 wires it into the window. Thus T08 does not depend on unfinished T09 code.
Closing requests Stop and keeps draining until terminal and observed worker exit;
poll rather than blocking Tk with join. Catalog operations also have timeouts and
a closing signal; no thread waits indefinitely.

`main.py --gui` selects GUI through a late import; no-argument invocation preserves
CLI behavior, defaults and public interfaces. Fix invalid bindings such as
MediaUtils through an explicit import/adapter and regression test; do not rewrite
the CLI or absorb earlier changes without separate review.

## Sequence, ownership and acceptance

T01 paths and documentation paths below are relative to the repository root.
Other module/test paths are relative to `apps/src/`. Each task owns only its listed
files and named new tests; no concurrent writers. Require primary-agent review before
each unit's commit (single-agent decision, 2026-10-22), with at most two correction rounds.

| Task | Dependency | Owned paths and deliverable | Assigned criteria |
|---|---|---|---|
| T01 · Environment | Phase B gate | Root paths `apps/pyproject.toml`, `apps/requirements.txt`, `apps/uv.lock`, `README.md`: Python >=3.14,<3.15, CustomTkinter 6.0.0, development pytest, reproducible install | ADR-0004 prerequisite; smoke without generation |
| T02 · Contracts and script | T01 | `comfy_generator/models.py`, `utils/formatting_utils.py`, reading in `comfy_generator/file_system.py`, `tests/test_scene_parsing.py`: immutable data, pure parser and line errors | CA-01.2, CA-01.3, CA-01.18 |
| T03 · Workflow and payload | T02 | `comfy_generator/payload_mgr.py`, `tests/test_workflow_mapping.py`: detection, mapping, subgraph, clean copies and composition | CA-01.4, CA-01.5, CA-01.6, CA-01.7, CA-01.13, CA-01.14, CA-02.3 |
| T04 · Catalog and parameters | T03 | `comfy_generator/client.py`, `comfy_generator/payload_mgr.py`, `tests/test_catalog_validation.py`: object_info, choices, limits and snapshot validation | CA-01.8, CA-01.9, CA-01.11 |
| T05 · Correlated transport | T04 | `comfy_generator/client.py`, `comfy_generator/exceptions.py`, `tests/test_transport_protocol.py`: WS/POST, history/cache, full descriptor list, legacy adapter and deadline | CA-02.4, CA-02.5, CA-02.6, CA-02.7, CA-02.8, CA-02.16, CA-02.17, CA-02.19 |
| T06 · Safe output | T05 | `comfy_generator/file_system.py` owns directories, temporary files and atomic publication; `comfy_generator/client.py` owns HTTP streaming into that helper; `tests/test_output_storage.py` covers both | CA-02.13, CA-02.14 |
| T07 · Runner | T06 | `comfy_generator/runner.py`, `tests/test_runner.py`: full prevalidation, seeds, serial execution, synchronized Stop and one result | CA-01.16, CA-02.1, CA-02.9, CA-02.10, CA-02.11, CA-02.15, CA-02.18 |
| T08 · Configuration panel | T07 | `gui/config_panel.py`, `tests/test_config_panel.py`: dialogs, mapping, catalog callback boundary with fake service, prompts, presets/Reset and snapshot | CA-01.1, CA-01.10, CA-01.12, CA-01.15, CA-01.17 |
| T09 · Worker lifecycle | T08 | `gui/thread_worker.py`, `tests/test_gui_worker.py`: queues, coalescing, asynchronous catalog adapter, run_id/request_id, idempotent Stop and finite shutdown | CA-02.2, CA-03.4, CA-03.5, CA-03.12 |
| T10 · Terminal and progress | T09 | `gui/log_panel.py`, `tests/test_log_panel.py`: log fields, 2,000-line limit, preserved summary and real fractions | CA-03.6, CA-03.7, CA-03.8, CA-03.9, CA-03.10, CA-03.11, CA-03.14, CA-03.16 |
| T11 · Window and launch | T10 | `gui/main_window.py`, `gui/__init__.py`, `main.py`, `tests/test_main_window.py`, `tests/test_entrypoints.py`: assembly, catalog wiring, states, closing, --gui and preserved CLI | CA-02.12, CA-03.1, CA-03.2, CA-03.3, CA-03.13, CA-03.15 |
| T12 · Offline integration | T11 | `tests/test_desktop_integration.py`, fictional local fixtures and root `docs/code/`: complete scenarios and races | Recheck all 53 criteria across the three specs; mocks cannot establish visual acceptance |
| T13 · Delivery review | T12 | Root `docs/code/`, `docs/tasks.md`, `docs/state.md`, `README.md`: evidence, gaps, primary-agent review and PR | Every CA traced; Phase D still required |

## Validation and transition to Phase D

- T02: UTF-8/BOM, multiline descriptions, internal parentheses, text before the
  first scene, malformed timestamps, repeated times and read errors preserving
  the last valid selection.
- T03–T04: changed IDs, two chains, incorrect links/slots, Canvas, batch_size other
  than 1, absent/empty catalog, integer/fractional CFG, NaN/infinity, invalid
  dimensions and distinct sampler/scheduler options.
- T05–T07: local simulated HTTP/WS server with unrelated events, partial executed,
  cached execution without progress, delayed/empty/error history, WS loss, lost
  POST responses, multiple/truncated downloads, permission errors and collisions.
  Test deadlines with a fake clock, never by waiting 30 minutes.
- Stop: deterministic barriers before authorization and after submission starts;
  prove no submission in the first case and saving the current scene in the second.
  Prove exactly one terminal event for success/failure/Stop and no second worker.
- T08–T11: stale events, out-of-order catalogs, closing during catalog/batch work,
  delayed terminal events, overflowing logs, Reset/Load confirmation and canceled
  dialogs. Real GUI without GPU: heartbeat every 100 ms over 5 seconds of simulated
  I/O, maximum interval 500 ms in the test environment; record measured conditions.
- Test CLI with fictional inputs/transport while preserving public calls. Separate
  ComfyUI-dependent tests. Offline tests do not read .env, personal documents,
  real checkpoints or the user's scripts.
- Evidence per CA records command/scenario, outcome, environment and limitations.
  Mocks demonstrate internal contracts; real capture/interaction demonstrate layout.
  A planned test is not a passed criterion.
- D01 after authorization: record ComfyUI version and relevant metadata, use a
  standard workflow and fictional two-scene script; demonstrate files, seeds,
  progress, Stop, connection failure and no interruption of other jobs. Generated
  data stays local. The owner approves the final demonstration.

## Assessment and known risks

See [Phase B assessment](code/configuration/phase-b-assessment.md). Isolated
CustomTkinter startup does not demonstrate server support. Check the intended
Phase D installation's ComfyUI contracts before opening Phase C; material incompatibility
returns to ADR/spec review before implementation. Preference persistence, preview,
GPU telemetry, parallel scenes, automatic resume and server/model installation
remain outside this release.
