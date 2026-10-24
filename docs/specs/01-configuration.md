# SPEC-01 · Generation configuration

Date: 2026-10-20. Translated and updated: 2026-10-21. Status: proposed for Phase B approval; no acceptance criterion demonstrated.
Sources: README **Current Tasks / config_panel.py** and **Execution Steps**;
[PRD](../prd.md), [ratifications](../ratifications.md), confirmed R-B.1 and R-B.2.
Technical design: [ADR-0003](../adr/0003-desktop-integration.md).

## Behavior and boundaries

Select a UTF-8 TXT script and API-format JSON workflow through native dialogs,
showing the selected paths. Canceling preserves the previous selection. Script
reading accepts BOM, ignores blank lines and preserves file order.
**R-B.8 [CONFIRMED 2026-10-20]:** each scene starts with `(MM:SS)` or `(HH:MM:SS)`
at the beginning of a line, followed by its description. Subsequent lines without
a timestamp continue that description. Seconds and minutes range from 00 to 59
(minutes are unrestricted in MM:SS). An empty final description, text before the
first scene or a malformed timestamp blocks the entire batch, identifying the
line and reason. Repeated timestamps are allowed; scene indices distinguish files.

Support only the standard chain identified by classes and connections. One
KSampler receives model from CheckpointLoaderSimple, latent_image from
EmptyLatentImage and positive/negative from two distinct CLIPTextEncode nodes
connected to that loader. VAEDecode connects sampler output to SaveImage using
that loader's VAE. Batch size must be 1. For multiple chains, the operator selects
IDs by role; validate connections rather than interpreting prompt text. Nodes
outside the selected chain are not submitted. Explain incompatible topology;
there is no generic support for custom nodes or specialized Flux/SDXL chains.

Checkpoint, sampler, scheduler and limit catalogs come from the local server and
refresh asynchronously. A model is the name returned by ComfyUI; do not open or
copy `.safetensors`. Initial field values come from the workflow. Never silently
replace a selection that is absent from the catalog.

## Confirmed choices

- **R-B.4 [CONFIRMED 2026-10-20]:** initialize global prompt fields from workflow
  text. Editing replaces the global text; clearing positive leaves only the scene
  description, and clearing negative produces an empty negative prompt. For a
  nonempty global positive, compose global + newline + `SCENE TO CREATE: ` +
  description. Loading TXT fills its field without modifying the source file;
  replacing edited field content requires confirmation. No LLM calls are included.
- **R-B.7 [CONFIRMED 2026-10-20]:** initial seed comes from the workflow. Seed `-1`
  draws a valid value for each scene; a fixed seed, including zero if accepted by
  the server, repeats across scenes. Different prompts need not produce visually
  identical results. Record the effective seed per scene.
- **R-A3.1 [CONFIRMED 2026-10-20]:** presets are 16:9 = 1024×576, 9:16 = 576×1024,
  1:1 = 512×512. Custom preserves entered dimensions. Width/height are positive
  integer multiples of 8 within metadata limits. Steps is a positive integer;
  CFG is finite and nonnegative; both respect server limits. Sampler and scheduler
  are separate controls.
- Reset restores generation fields and global text from the loaded workflow,
  preserving files and destination. Clearing or restoring never starts generation.

## Acceptance criteria

These confirmed choices inform the proposed criteria; Phase C still requires approval.

| ID | Given / When / Then |
|---|---|
| CA-01.1 | Given a selected file, when the next dialog is canceled, then the previous selection remains. |
| CA-01.2 | Given a valid script with multiline descriptions, when loaded, then scenes and continuations preserve file order under R-B.8. |
| CA-01.3 | Given an empty script or invalid line, when validated, then Generate is blocked with a reason and line where applicable. |
| CA-01.4 | Given invalid JSON or a Canvas export, when opened, then the interface requests an API-format workflow. |
| CA-01.5 | Given one standard chain with different IDs, when loaded, then roles are detected through connections. |
| CA-01.6 | Given multiple valid chains, when loaded, then generation waits for explicit mapping. |
| CA-01.7 | Given disconnected mapping or unsupported topology, when validated, then generation is blocked with the incompatible role identified. |
| CA-01.8 | Given an accessible server, when models are refreshed, then the list reflects its returned checkpoints. |
| CA-01.9 | Given an unavailable catalog or removed selection, when generation is attempted, then the interface requests refresh or a valid selection without choosing a substitute. |
| CA-01.10 | Given a valid workflow, when loaded, then generation controls show its values. |
| CA-01.11 | Given an invalid number or missing catalog option, when starting is attempted, then the responsible field is identified before any POST. |
| CA-01.12 | Given an aspect preset, when selected, then dimensions adopt the pair defined by R-A3.1. |
| CA-01.13 | Given a filled or empty positive override, when preparing a scene, then positive composition follows R-B.4. |
| CA-01.14 | Given a filled or empty negative override, when preparing a scene, then the negative follows R-B.4. |
| CA-01.15 | Given an edited prompt field, when Load would replace it, then confirmation is requested; cancel preserves the field and confirm loads TXT without editing the source file. |
| CA-01.16 | Given fixed seed and seed -1, when exercised separately, then effective seeds follow R-B.7 and are recorded per scene. |
| CA-01.17 | Given manual edits, when Reset is selected, then fields return to the defined state without starting execution. |
| CA-01.18 | Given a file reading or encoding error, when selected, then an error appears without replacing the last valid configuration. |

## Planned evidence

Fictional scripts and graphs cover changed IDs, two chains, invalid connections,
batch size above 1, Canvas, UTF-8/BOM and file errors. A simulated catalog proves
options and validation. Visual checks cover dialogs and Reset; local integration
confirms metadata. These tests have not been executed by this specification.
