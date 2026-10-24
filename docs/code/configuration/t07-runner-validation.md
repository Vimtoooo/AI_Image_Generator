# T07 - Serial runner validation

Date: 2026-10-23. Phase C. Primary-agent implementation and review; no subagents.
Sources: implementation-plan T07; CA-01.16, CA-02.1, CA-02.9-11,
CA-02.15 and CA-02.18. T08 has not started.

## Implementation and handoff contract

- `runner.run(config, emit, stop_control)` validates all scenes and prepares isolated
  payloads before allocating/probing the batch directory and before any POST.
- Fixed seeds repeat; -1 draws a catalog-valid nonnegative seed per scene. Effective
  seeds appear in payloads and scene_started events. Checkpoint selection comes
  from the immutable workflow snapshot's mapped loader.
- One `StopControl` per run. `request_stop()` and `authorize_submission()` share
  a lock, released before network I/O. The existing client's hook runs after WS
  connection. Once authorized, the scene finishes saving; Stop prevents the next.
- All downloads share the scene deadline. Saved-file counts advance per published
  file; saved-scene counts advance only after the complete download operation.
  The first error ends the run without retry and retains completed files.
- Events carry one run_id and correlated scene/prompt identifiers. The terminal
  event contains the same RunResult returned by run. A future worker must not emit
  it again. Supply a non-raising queue event sink; Tk calls do not belong here.
- Optional client, clock, randint and run_id injection supports offline verification.
  Injected clients are caller-owned; the default Requests session is closed by run.
  The existing client supports HTTP host/port endpoints only; unsupported URL forms
  fail explicitly. TLS and reverse-proxy paths were not added to this task.

## Executed evidence

Python 3.14.3 / pytest 9.1.1 from `apps/.venv/Scripts/python.exe`.
The historical temporary T01 interpreter is no longer runnable at its recorded path.
Used the process-local fresh-directory wrapper from T02, from `apps/`, passing:

```text
src/tests/test_scene_parsing.py src/tests/test_workflow_mapping.py
src/tests/test_catalog_validation.py src/tests/test_transport_protocol.py
src/tests/test_output_storage.py src/tests/test_runner.py
-p no:cacheprovider --basetemp <fresh temporary directory>
```

Result: **174 passed in 3.36s**, including **28 runner tests**. No real ComfyUI
generation, model, personal script or .env file was used. Existing transport/storage
suites include loopback HTTP/WS and truncated-download evidence.

Runner evidence includes invalid later scenes preventing all POSTs, fixed/random
seeds, payload isolation, failed output probe, partial second-scene retention,
unknown submission/timeout/execution failures without retry, default session cleanup,
and one terminal result. Event barriers exercise both sides of submission
authorization with a concurrent Stop request; Stop acknowledges while simulated
I/O is held. An integration test runs the actual client and atomic storage with
fictional HTTP/WS responses and confirms two serial scenes and all four local files.

## Primary-agent review

Confirmed: assigned T07 behavior at the offline runner boundary. No blocking code
findings after scoped review. `git diff --check` passed (line-ending warnings only).
Earlier application files and test deletions were preserved. No GUI behavior or
live ComfyUI acceptance is claimed; these remain T08-T12 and Phase D work.

Context7 `/python/cpython` supplied lock context-manager semantics from
https://github.com/python/cpython/blob/main/Doc/library/threading.rst.
The existing scoped Graphify index located build_scene_payload, apply_parameters,
generate_images and download_images. It does not yet contain the new runner;
refresh its backend-only scope before using it for runner relationships.

Publication must exclude unreviewed earlier work. This task depends on currently
uncommitted T02-T06 modules/tests; a standalone remote T07 commit would not be
runnable. Prior Phase B/C publication must be resolved before publishing T07.
The owner instruction is one completed task per chat, followed by handoff and stop.
