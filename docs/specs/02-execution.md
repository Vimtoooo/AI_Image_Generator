# SPEC-02 · Execution and storage

Date: 2026-10-20. Translated and updated: 2026-10-21. Status: proposed for Phase B approval; no implementation evidence.
Sources: README **Current Tasks / thread_worker.py**, **main.py**, **Future Roadmap**;
[PRD](../prd.md), [ratifications](../ratifications.md), confirmed R-B.3.

## Flow

Generate captures an immutable configuration and validates every scene before
submitting the first. Allow one batch per window and one scene at a time. The
worker prepares a clean workflow copy per scene, opens WebSocket before POST
/prompt and correlates events with the returned prompt_id. Other jobs do not
change this batch's state.

An isolated `executed` event does not prove prompt completion. Confirm the owned
prompt through successful history and output from the mapped SaveImage. Normal
and cached completion follow the same confirmation path. Download all images
listed by that node through /view with server filename, subfolder and type. A
scene counts as saved only after every file is complete. Missing images, server
errors or incomplete downloads are not success.

Stop is cooperative: prevent the next scene; if submission has started, finish
and save the current one. Never call global /interrupt. Stop before submission
prevents sending that scene. Synchronize submission authorization with Stop so
no new scene starts after the stop request has been acknowledged. Closing during
a batch offers returning or stopping after the current scene; the latter keeps
the window and feedback alive until that scene finishes or fails.

## Confirmed choices and deadlines

- **R-B.5 [CONFIRMED 2026-10-20]:** initial destination is `assets/generated_images`,
  with a folder picker. Create an exclusive batch subfolder. Image names combine
  scene index, sanitized timestamp, image index and returned file extension.
  Never use server paths as local destinations. Check destination writability
  before the first POST. Downloads use local temporary files and atomic publication
  without overwriting; failure removes only that attempt's temporary file,
  preserving complete files.
- **R-B.6 [CONFIRMED 2026-10-20]:** the first terminal error ends the batch, retains
  saved images and reports scene, stage and reason; no automatic resubmission.
  A dropped WebSocket with a known prompt_id is recoverable through history within
  the deadline. Confirmed execution, download, validation or timeout errors end
  the batch. A lost POST response means an unknown result: warn that the server
  may continue and do not duplicate it. Explicit Generate starts a new batch,
  without automatic resume.
- **R-A3.2 [CONFIRMED 2026-10-20]:** HTTP connection/read limits are 10/60 seconds;
  WebSocket checks signals every second. The total scene deadline defaults to
  30 minutes and is editable before the batch. It includes queueing, generation
  and downloads. Expiry is local failure, not global server cancellation. Check
  deadline between download chunks and events; each connection/read limit is
  capped by remaining scene time. Warn that server work may continue; never
  resubmit the scene.

## Acceptance criteria

| ID | Given / When / Then |
|---|---|
| CA-02.1 | Given invalid configuration in any scene, when Generate is selected, then no prompt from the batch is submitted. |
| CA-02.2 | Given an active batch, when Generate is activated again, then no second generation worker is created. |
| CA-02.3 | Given two scenes, when preparing the second, then edits from the first do not contaminate its base copy. |
| CA-02.4 | Given a ready scene, when submitted, then WebSocket is already open before POST. |
| CA-02.5 | Given an event from another prompt_id, when received, then the owned batch state remains unchanged. |
| CA-02.6 | Given a node executed event without prompt completion, when received, then the scene is not marked complete. |
| CA-02.7 | Given a completed prompt, including cache, when history confirms success, then all mapped SaveImage images are retrieved. |
| CA-02.8 | Given history without mapped-node images, when execution finishes, then the scene fails. |
| CA-02.9 | Given a scene with several files, when only some are saved, then the completed-scene counter does not advance. |
| CA-02.10 | Given Stop during generation, when the scene is saved, then no next scene is submitted. |
| CA-02.11 | Given Stop before scene submission, when acknowledged, then that scene is not submitted. |
| CA-02.12 | Given closing during execution, when the operator chooses to wait for stopping, then the window closes only after the current scene's terminal result. |
| CA-02.13 | Given repeated timestamps or existing folders, when preparing output, then no prior file is overwritten under R-B.5. |
| CA-02.14 | Given a download error, when the attempt ends, then no partial file remains under its final name under R-B.5. |
| CA-02.15 | Given a scene failure, when handled, then the batch stops while preserving complete images under R-B.6. |
| CA-02.16 | Given a lost POST response, when reporting failure, then the client does not automatically resubmit and communicates an unknown result. |
| CA-02.17 | Given an expired scene deadline, when checked, then the batch ends with local failure without interrupting other jobs. |
| CA-02.18 | Given every scene saved, when the batch ends, then the result reports success with totals and final directory. |
| CA-02.19 | Given WebSocket loss after receiving prompt_id, when history confirms success within the deadline, then the scene is saved without a new POST and the batch may continue. |

## Planned evidence

A simulated server covers interleaved events, cache, empty history, errors, missing
POST responses, truncated downloads and timeout. Temporary filesystem tests prove
preservation and exclusive names. A race test covers Stop at the submission
boundary. Phase D uses a local fictional batch to demonstrate files and no /interrupt.
