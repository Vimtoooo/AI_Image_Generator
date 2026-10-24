# Phase C entry check

Date: 2026-10-21. Owner approved Phase B and authorized Phase C.

## Local server

- Endpoint: `http://127.0.0.1:8188/`, confirmed by the owner.
- Startup: `C:\AI\ComfyUI_windows_portable\run_nvidia_gpu.bat`, with
  `C:\AI\ComfyUI_windows_portable` as working directory. Check availability first;
  start hidden if needed. The owner already started it for this check.
- GET `/system_stats` reports ComfyUI **0.24.0**.
- GET `/object_info/{node_class}` confirms expected inputs/outputs for KSampler,
  CheckpointLoaderSimple, EmptyLatentImage, CLIPTextEncode, VAEDecode and SaveImage.
- Read-only source review confirms WS query `clientId`, POST `client_id`, correlated
  execution events, node-keyed history outputs and successful-history checking.
  The initial reconnect event can lack `prompt_id` and must be ignored as uncorrelated.
  Success events can precede history availability, requiring bounded history polling.
- No generation, queue mutation, history-content read or image download was performed.
- Independent source review completed with no blocking contract mismatch:
  `server.py:261,958` specifies client identifiers; `execution.py:793-815` handles
  success/history ordering; `nodes.py:1669-1677` constructs image descriptors;
  `main.py:327-339` stores history status and then emits `executing` with node null.
  Failed history may have `completed=false`; T05 must detect `status_str=error` or
  correlated error/interruption messages immediately. A null-node event is not
  sufficient proof of success. These checks are static/read-only compatibility
  evidence, not the real generation demonstration required in Phase D.

## T01 preparation and blockers

The candidate manifest is prepared outside the repository at
`%TEMP%\comfy-phase-c-t01\pyproject.toml`: Python `>=3.14,<3.15`,
CustomTkinter `==6.0.0`, pytest moved to the development group.

Validation used Python 3.14.3. The shared uv cache denied access, so a permitted
temporary cache was selected. Offline resolution failed because CustomTkinter was
not cached. Online resolution failed to connect to PyPI through the configured
network connection. No newly resolved lock or environment smoke is claimed.
The copied lock in that temporary directory is the original baseline, not a
validated candidate lock. Application manifests remain unchanged.

Git metadata remains read-only, preventing the required Phase C branch. T01 is
prepared but not implemented or complete; publication is also pending permissions.
