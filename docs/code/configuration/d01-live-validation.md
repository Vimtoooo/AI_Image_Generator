# D01 - Live local verification (in progress)

Date: 2026-10-26. Phase D authorized by the owner in this session.
Primary-agent verification and review; no subagents. Phase C merged at a34b0a6.

## Environment and method

ComfyUI 0.24.0, embedded Python 3.13.12, PyTorch 2.12.0+cu130,
frontend 1.44.19, NVIDIA GeForce RTX 3050 Laptop GPU (4 GiB VRAM).
Application interpreter: apps/.venv/Scripts/python.exe (recorded Python 3.14.3).
Endpoint: http://127.0.0.1:8188. Initial sandbox socket access was denied;
approved elevated checks confirmed connection refusal. Started the owner-approved
C:\AI\ComfyUI_windows_portable\run_nvidia_gpu.bat hidden, from its portable directory.
The server became available after startup; no configuration change was necessary.

GET /system_stats, /object_info and /queue supplied live metadata. The queue was
empty before each generation batch and after the checks. No /interrupt, queue
mutation, history deletion or server shutdown was performed. Empty-queue checks
are snapshots, not reservations against another user submitting concurrently.
Context7 /comfy-org/docs confirmed these read-only local routes:
https://github.com/comfy-org/docs/blob/main/development/comfyui-server/comms_routes.mdx.

Used the real application runner, parser, workflow mapping, catalog validation,
HTTP/WebSocket client and output storage. No mock transport or test client.
Generated a standard seven-node CheckpointLoaderSimple / EmptyLatentImage /
two CLIPTextEncode / KSampler / VAEDecode / SaveImage workflow.
Checkpoint: DreamShaper_8_pruned.safetensors, already installed and advertised by
the server; 512x512, batch size 1, 12 steps, CFG 7, euler/normal, denoise 1.
Fictional scenes: a red wooden toy boat on a pond and a blue ceramic teapot on a table.

Local harness, TXT, workflow, JSON results and images are under ignored
assets/generated_images/phase-d-validation/. Re-run only with an idle server:

```powershell
.\apps\.venv\Scripts\python.exe assets/generated_images/phase-d-validation/verify_live.py
```

The harness is a local verification artifact, not a versioned application command.
It asserts an empty queue, runs the scenarios below and decodes PNG metadata using
Pillow. Raw evidence is results.json in that directory; it and generated images
are intentionally excluded from publication. ComfyUI also retains its normal
SaveImage outputs with the phase_d_fictional prefix.

## Observed results

| Scenario | Observed result | Acceptance evidence |
|---|---|---|
| Complete two scenes, seed 42 | completed; 2 scenes, 2 saved PNGs; both decode as 512x512 and contain seed 42 in embedded prompt metadata | CA-01.16 fixed mode; CA-02.18 |
| Real progress | 23 progress events during the successful batch, 2 submissions and exactly 1 terminal event | Live runner/transport evidence; visible CA-03.8 remains pending |
| Stop after first submission, seed 43 | stopped; first PNG saved with seed 43; exactly 1 submission and no second scene start; 1 terminal event | CA-02.10; no server-wide interrupt |
| Connection failure | A reserved non-listening loopback port refused catalog access; failed at validation; 0 submissions, 0 files, 1 terminal event and corrective message | Backend failure evidence supporting CA-01.9; visible CA-03.15 pending |

Command exited 0 with all assertions passing. Primary agent visually inspected
the first complete-batch PNG: a red boat on a wooded pond, with no decoding defect.
The other PNGs were decoded and their dimensions/seed metadata checked, but not
visually assessed. This is backend verification, not evidence of GUI interaction.

## Remaining D01 work at initial backend handoff (historical)

1. Use the local TXT/workflow with the real desktop; refresh catalog, select the
   destination and generate. Observe visible progress, logs, saved files and responsiveness.
2. Demonstrate the desktop Stop action during live work and its terminal summary.
   Demonstrate connection-error presentation without stopping a shared server.
3. Exercise random-seed mode live and record effective seeds (offline coverage exists).
4. Present the complete demonstration for owner acceptance, then update the task/state.

The previous 287 offline tests and 13 owner-reported GUI checks remain historical
Phase C evidence; they were not rerun or relabeled as live Phase D GUI verification.
No application code changed. Primary-agent review checked scenario assertions,
source runner behavior, document consistency and ignored-output boundaries.
No completion or owner acceptance is claimed. The server remains running.


## Live desktop verification and correction - 2026-10-26/27

Current status: all planned technical checks complete; owner acceptance remains
pending. This update supersedes the earlier GUI/random-seed pending statements.
The primary agent operated the real desktop through the computer-use skill,
selecting the fictional TXT and workflow with native dialogs. No subagents.

### Observed desktop scenarios

- Live catalog loaded. The two-scene run used seed -1, 512x512, 12 steps,
  CFG 7, euler/normal and the installed DreamShaper checkpoint. Visible sampler
  progress advanced; saved counts progressed from 0/2 through 1/2 to 2/2.
  Scrolling responded during generation; configuration controls were disabled
  while running and restored afterward. Responsiveness was observed, not timed.
- Completed summary: 2/2 scenes saved, 0 pending, 2 files saved, destination shown.
  Both PNGs decoded successfully. Embedded seeds were 7795494556777795134 and
  11123422455725577059, matching the two effective seeds observed in the logs.
  Local batch: batch_20261026_135351_2266e581f8284285bfa02d1fa42c8880.
- An 80-step run provided time to press the real Stop button during the first
  scene. The UI showed Stopping while sampling continued, then Stopped with
  1/2 scenes saved, 1 pending, 1 file saved. Exactly one PNG was present, with
  seed 1566243185716819391 and dimensions 512x512. Local batch:
  batch_20261026_135440_6ec3a867026a473585f854850f13039f.
- An isolated MainWindow instance pointed at a reserved non-listening loopback
  port displayed: "Catalog unavailable; check the server address and connection,
  then refresh." Refresh visibly entered loading and returned to that error.
  The instance was closed; the real ComfyUI server was not interrupted. This
  demonstrates catalog failure presentation, not a mid-generation disconnect.
- On resuming 2026-10-27, ComfyUI was stopped. Restarted the approved launcher;
  the fresh GUI initially showed the same error, then Refresh recovered to
  Catalog ready once the server was available. The queue was empty before the
  final run. No interrupt, queue deletion or server configuration change occurred.

### Display defect and fix

The live run exposed horizontal auto-scrolling when a long destination path was
appended. Tk Text.see("end") moved both axes, hiding the beginning of log lines.
LogPanel now follows the bottom with yview_moveto(1) and restores the previous
horizontal fraction. A reader's vertical position remains preserved when reading
older entries. Existing summary retention across runs remains unchanged.

Two regression cases (left edge and deliberately scrolled right) failed before
this fix, then passed. The full feedback module passed: **27 tests**. Desktop
integration passed: **14 tests in 25.65s**, with the existing no-stderr assertions.
The interrupted earlier integration run had no recoverable final result. A fresh
sandbox run failed on CTk font-loading warnings and restricted loopback traffic;
rerunning with approved system access passed without weakening any tests.
Commands: from apps/, use .venv/Scripts/python.exe -m pytest with each module in a
separate process, -p no:cacheprovider -q. The feedback run used the documented T02
fresh-directory wrapper; the successful integration run required no wrapper.

Context7 /tomschimansky/customtkinter documented CTkTextbox's Tk Text methods;
the installed wrapper source confirmed xview/yview delegation:
https://github.com/tomschimansky/customtkinter/wiki/CTkTextbox.

A fresh real GUI run after the fix completed two images on 2026-10-27. Log line
prefixes stayed visible after the long final path, and the summary showed 2/2,
0 pending, 2 files. Both PNGs decoded as 512x512 with seed 42. Local batch:
batch_20261027_122642_6b15ddfe0cac401082df0fe88f06075b.
The observed screenshot is stored locally as
assets/generated_images/phase-d-validation/gui-completed-2026-10-27.png.
The local gui-results.json records decoded PNG metadata. All outputs stay ignored.

### Review and acceptance boundary

Primary-agent review checked the five-line display change against CA-03.7 and
retained vertical scrolling, read-only controls, buffer limits and summary behavior.
Live evidence supports CA-01.16, CA-02.10/18 and CA-03.3/4/8/11/12/13/14/15
for the scenarios above; this is not a claim that every edge case was run live.
The prior Phase C matrix remains the source for offline and owner-reported checks.
No new blocking finding remains. The corrected GUI is left open at Completed and
ComfyUI is running. D01 closes only after the owner accepts the demonstration.
