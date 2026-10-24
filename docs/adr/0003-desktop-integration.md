# ADR-0003 · Desktop interface and correlated execution

Date: 2026-10-20. Translated and updated: 2026-10-21. Status: architecture proposed
for Phase B approval. R-B.1–R-B.8 and choices R-A3.1/R-A3.2 were confirmed on
2026-10-20; those choices do not automatically approve the entire architecture.

## Context

README requires CustomTkinter, logs and a worker. The UI is empty; the backend
uses fixed IDs and has implementation issues, including writing sampler to the
checkpoint node. Previous local main changes must be preserved. Identify the
selected chain without interpreting prompt text; a node output alone does not
confirm completion.

Local sources: README **Current Tasks**, `PayloadManager`, `main.py` and
[ratifications](../ratifications.md). Check HTTP/WS contracts against the intended
local ComfyUI version before Phase C; this proposal does not prove compatibility.

Primary sources checked on 2026-10-20:
[ComfyUI messages](https://docs.comfy.org/development/comfyui-server/comms_messages),
[official WebSocket client example](https://github.com/comfyanonymous/ComfyUI/blob/master/script_examples/websockets_api_example.py)
and [Tkinter threading model](https://docs.python.org/3/library/tkinter.html#threading-model).
The official example establishes WebSocket-before-submission and history after
completion; timeouts, fallback and interface behavior are project decisions.

## Proposed architecture

- `main.py --gui` opens the GUI; no arguments preserve the CLI path. Separate
  reusable orchestration from widget callbacks without another application or
  silently changing CLI defaults. Preserve legacy method signatures through
  explicit adapters as detailed in the implementation plan.
- The main thread owns widgets. A worker receives a validated snapshot and emits
  through `queue.Queue`; `after` drains events. Catalog threads also emit events
  without calling Tk. Coalesce repeated progress to prevent unbounded queues;
  terminal events must not be discarded.
- Minimum internal contracts: configuration with paths, ID mapping, parameters
  and timeout; scene with index, timestamp and description; event with type,
  batch/scene, prompt_id when available and progress/result data. Use explicit
  Python types and propagate errors rather than silently returning success.
- Resolve a connected standard chain including VAEDecode and batch_size=1;
  require mapping for ambiguity. Validate classes and connections and extract
  only the selected subgraph. Positive/negative roles follow KSampler inputs.
- Validate against workflow and `/object_info`, with scheduler separate from
  sampler. No model downloads, checkpoint manipulation or embedded LLM.
- Open WebSocket before POST using the matching client_id. Correlate owned events;
  confirm completion and success with `/history/{prompt_id}`, including cache.
  After WS loss with known prompt_id, recover through history within deadline,
  without resubmission. Missing confirmation becomes failure/unknown result.
  Never attribute events without reliable prompt correlation by assumption.
- Retrieve all images from mapped SaveImage, passing type, subfolder and filename
  to `/view`. Generate local paths independently. Use temporary files and atomic
  publication without overwriting. A scene completes only after all downloads.
  Stop is cooperative, never `/interrupt`; closing waits for scene completion or
  a finite failure/deadline.

## Ratified technical choices

**R-A3.1 · Presentation and parameters [CONFIRMED 2026-10-20, option a].** English
and dark theme follow the local reference. Use scrollable/resizable layout with
no GPU telemetry, preview or preference persistence in this release. Exact
presets 1024×576, 576×1024 and 512×512 avoid silent ratio rounding; custom accepts
multiples of 8 within server limits. Initial values remain workflow-derived until
a preset is chosen. Terminal buffer: 2,000 lines. An architectural alternative
considered here is user-defined presets with more editing/persistence; it was not
an option presented to the owner. The confirmed presentation uses fixed presets.

**R-A3.2 · Deadlines [CONFIRMED 2026-10-20, option a].** HTTP connection/read limits:
10/60 seconds; WS receive timeout: 1 second for signal checks. Scene deadline:
30 minutes including queue and downloads, editable as positive minutes before a
batch. Query history every 2 seconds after WS loss or while terminal history is
not yet visible, until deadline. Reconnection never resubmits POST. Unlimited
waiting was the alternative; finite waiting permits eventual cooperative closure.
Each connection/read is also capped by remaining scene time. Deadline ends local
tracking rather than server execution; warn that work may continue, without resubmitting.

Prompts, destination and errors follow R-B.4–R-B.6; seeds and script format follow
R-B.7/R-B.8, all confirmed 2026-10-20. Python and packaging follow ADR-0004.

## Alternatives, consequences and validation

Networking in Tk callbacks blocks responsiveness. Rewriting with asyncio adds
loop integration without demonstrated need. Global interruption contradicts
R-B.3; arbitrary graphs exceed R-B.2. Threads plus queues follow README and
separate UI testing from protocol testing, requiring coordinated shutdown and
rejection of stale events by batch ID.

Specs [01](../specs/01-configuration.md), [02](../specs/02-execution.md) and
[03](../specs/03-interface-feedback.md) define acceptance criteria. Use simulated
servers and temporary files for cache, partial downloads, unrelated events and
Stop/submission races. Phase D demonstrates a real standard workflow with fictional
data; this ADR supplies no such evidence.

Revisit for new graph types, parallelism, persistent resume, protocol changes or
a user decision changing visual scope.
