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

## Remaining D01 work

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
