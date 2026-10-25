# SPEC-03 · Window, feedback and responsiveness

Date: 2026-10-20. Translated and updated: 2026-10-21. Status: proposed for Phase B approval; no implementation evidence.
Sources: README **Current Tasks / log_panel.py, thread_worker.py, main_window.py**;
[PRD](../prd.md); R-B.1 and R-B.3 in [ratifications](../ratifications.md).

## Interface and states

The CustomTkinter window combines configuration, execution controls, progress and
a read-only terminal. The local SVG guides organization: files, model, prompts,
resolution, seed, steps, CFG, sampler, Reset, Generate and logs. Its structure and
text were inspected, but rendering did not succeed. Do not claim demonstrated
visual fidelity or require detailed GPU telemetry.

**R-A3.1 [CONFIRMED 2026-10-20]:** English labels, initial dark theme and resizable
layout with scrollable configuration keep actions accessible. Sampler and scheduler
are separate even where the reference combines them. No workflow editor, live
image preview, preference persistence or theme switching in this first release.
The operator continues building and exporting graphs in ComfyUI.

Visible states: Ready, Validating, Running, Stopping, Completed, Stopped, Failed.
Catalog Loading/Unavailable is independent. Configuration and Reset are disabled
during Validating/Running/Stopping; logs, scrolling, window movement and Stop remain
usable. Repeated Stop does not create additional actions.

Batch progress is fully saved scenes / valid scenes. Scene progress is sampler
value/max only when reliably correlated to the owned prompt; otherwise display
indeterminate activity. Do not invent percentages from node stages. Distinguish
queueing, generation and downloading; sampler 100% does not mean the scene is saved.

Logs show time, scene index/timestamp, stage, effective seed and message. Do not
routinely print whole scripts, prompt content or raw HTTP responses. Record start,
submission, relevant progress, saving, stopping and failure. The final summary
shows saved and pending totals and destination. Logs are in memory without automatic
export. The confirmed 2,000-line buffer drops oldest lines with a notice while
preserving the terminal summary.

## Acceptance criteria

| ID | Given / When / Then |
|---|---|
| CA-03.1 | Given GUI initialization, when the window opens, then configuration, generation, progress and terminal are available in one window. |
| CA-03.2 | Given a resized window, when content exceeds available space, then configuration controls remain reachable by scrolling. |
| CA-03.3 | Given an active batch, when configuration editing is attempted, then fields stay disabled until a terminal state. |
| CA-03.4 | Given slow networking, when the interface receives interaction, then scrolling and window events continue to be processed. |
| CA-03.5 | Given catalog loading, when the server is slow, then Loading appears without blocking the event loop. |
| CA-03.6 | Given terminal content, when editing is attempted, then text remains read-only. |
| CA-03.7 | Given a batch-stage event, when received, then the terminal shows its time, scene and message. |
| CA-03.8 | Given correlated progress with a valid maximum, when received, then the scene bar shows the reported fraction. |
| CA-03.9 | Given progress without reliable correlation or a valid maximum, when displayed, then activity is indeterminate without invented percentages. |
| CA-03.10 | Given sampler 100% without complete downloads, when the interface updates, then the saved-scene counter does not increase. |
| CA-03.11 | Given a fully saved scene, when its result arrives, then the batch bar reflects saved scenes / total. |
| CA-03.12 | Given Stop already requested, when selected again, then the state remains Stopping without another request. |
| CA-03.13 | Given a terminal result, when received, then the window distinguishes Completed, Stopped and Failed. |
| CA-03.14 | Given a terminal batch, when its summary appears, then it reports saved and pending counts and final directory. |
| CA-03.15 | Given a field or server failure, when displayed, then the message identifies the problem and a possible action without a raw traceback. |
| CA-03.16 | Given a terminal exceeding 2,000 lines, when new lines arrive, then the buffer maintains its limit and indicates discarded lines. |

## Planned evidence

Simulated events verify states, counts and logs. Proposed responsiveness test:
Tk heartbeat every 100 ms during 5 seconds of simulated I/O, with no interval over
500 ms in a test environment without GPU load. Local manual testing confirms
scrolling and Stop during real generation without promising deadlines under system
saturation. Future visual capture checks composition against the reference;
behavioral criteria do not depend on pixel-perfect comparison.
