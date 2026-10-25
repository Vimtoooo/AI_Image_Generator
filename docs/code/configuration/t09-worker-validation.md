# T09 - Worker lifecycle validation

Date: 2026-10-24. Phase C. Primary-agent implementation and review; no subagents.
Scope: `gui/thread_worker.py`, `tests/test_gui_worker.py`, status/evidence documents.

## Contracts for T10/T11

Create `WorkerController(root, on_event, on_error=...)` on the Tk thread. It starts
one 20 ms polling callback, delivering at most 64 queued events per tick plus an
omission notice. `start(config)` returns a unique run ID, or None if busy/closing.
`busy` remains true until terminal delivery AND observed worker exit. UI controls
must use that lifecycle, not assume terminal delivery alone permits another run.
The runner alone emits the terminal RunResult; its return is not re-emitted.
Unexpected runner exceptions or missing terminal results call on_error; they do
not fabricate saved counts. View callback failures use Tk's exception reporter
and do not stop queue draining.

`stop()` returns true only on the first active request. T11 uses that return to
show Stopping once. `close(on_closed)` requests cooperative Stop, discards pending
catalog work and suppresses catalog deliveries. Keep Tk and feedback alive until
on_closed; only then destroy the window. No UI-thread join or global /interrupt.
Closing waits for observed exit of both workers, including terminal/exit lag.

Bind `controller.request_catalog` to T08's `(request_id, server_url, deliver)`
boundary. Use one panel's monotonically increasing IDs per controller. At most one
catalog thread runs; only the newest pending replacement survives. Obsolete results
are discarded. All deliveries, event handlers and public controller calls belong
to the creating Tk thread. T11 still owns initial refresh and window wiring.

The Queue holds at most 256 envelopes. Consecutive progress for the same run,
scene and prompt shares an envelope; structural events separate progress groups.
When full, new log/progress messages may be omitted with a counted notice.
Structural and terminal messages apply worker-side backpressure until Tk drains
space, preserving them and their order. The host must continue polling on close.

## Executed verification

Python 3.14.3 / pytest 9.1.1 / Tk 8.6.15, Windows. No GPU/server operations.
From apps/, use `.venv/Scripts/python.exe` and the T02 process-local fresh-directory
creation-mode wrapper, with a unique `comfy-t09-<uuid>` temporary test root:

```text
pytest src/tests/test_scene_parsing.py src/tests/test_workflow_mapping.py
  src/tests/test_catalog_validation.py src/tests/test_transport_protocol.py
  src/tests/test_output_storage.py src/tests/test_runner.py
  src/tests/test_config_panel.py src/tests/test_file_system.py
  src/tests/test_gui_worker.py -q -s -p no:cacheprovider --basetemp <fresh root>
```

Final result: **226 passed in 11.32s**, including **20 T09 tests**. A real withdrawn
Tk root in an isolated subprocess processed 50 heartbeat samples during five
seconds of simultaneous simulated batch/catalog I/O. Maximum interval: **0.103s**,
below the 0.500s criterion. Isolation avoids old CTk fixture timer warnings seen
in the initial combined run; final heartbeat stderr was empty. Original collision
test emits an expected download error while its preservation assertion passes.

`apps/.venv/Scripts/python.exe -m unittest discover -s scripts -p 'test_*.py'`:
**7 passed in 4.167s** under approved elevation. The initial sandbox run failed
creating/cleaning fresh temporary repositories; no tests or permissions were
weakened to obtain the successful rerun. Scoped `git diff --check` passed.

| Criterion | Evidence |
|---|---|
| CA-02.2 | Second start rejected while running, after terminal but before exit, and while closing |
| CA-03.4 | Real Tk heartbeat with worker I/O; bounded draining and queue-pressure tests |
| CA-03.5 | Async catalog delivery on owner thread; latest request wins, errors and close suppressions |
| CA-03.12 | Repeated Stop and close call the same StopControl only once |

Additional tests cover 10,000 coalesced progress updates, scene/stage boundaries,
overflow notices, preserved structural/terminal events, stale/duplicate terminal
events, callback errors, worker start errors, runner contract failures and actual
runner completed/stopped/failed results through a two-envelope queue.

## Primary-agent review and limits

Confirmed: bounded channels/thread counts, UI-thread callbacks, idempotent Stop,
terminal ownership, stale-event rejection and draining through observed exit.
Reviewed the new test file as well as the tracked diff; no blocking findings.
Context7 `/python/cpython` supplied official Tk threading/timer documentation.
Reused the T08 Graphify findings; no new indexing or personal-data scans.

Shutdown is cooperative: the existing catalog uses 10/60-second connection/read
limits, and the runner uses finite transport waits and scene deadlines. These
are not hard wall-clock cancellation of DNS, trickling responses, filesystem I/O
or an injected callable that violates its finite-wait contract. A host that stops
pumping Tk early can strand a producer under backpressure. No visible scrolling,
Loading label, full-window close dialog or live generation is demonstrated here;
T11/T12 and separately authorized Phase D retain those responsibilities.

## Publication dependency

Remote main is 5572042: only PR #3 reached main. GitHub confirms #4–#7 merged
into predecessor feature branches. T09 therefore starts at df0ed2d on
phase-c/configuration-publication, whose tree exactly matches the reviewed
da22035 publication tree. Prior review evidence is reused from publication-validation.md;
the additional merge introduces no tree changes. Original branches remain intact.

[Recovery PR #8](https://github.com/Vimtoooo/AI_Image_Generator/pull/8) delivers
the complete T01–T08 stack to main. Merge it first, then retarget the T09 PR to
main before merging. Only the owner merges. T10 begins in a new chat; stop after T09.
