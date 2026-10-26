# Ratifications

0 open · 13 closed. Decisions received on 2026-10-20; final answers recorded and English translation applied on 2026-10-21.

The initial two questions were recorded retrospectively after the foundation was approved. Phase B proposals were written before the corresponding questions. Closed questions and answers remain part of the history; translations preserve their meaning.

## R-A2.1 · Agent platform

**Status:** closed; owner answered on 2026-10-20. **Recorded by:** primary agent.
**Reflected in:** ADR-0002. **Decision owner:** repository/product owner. **Basis:** explicit interactive response, except the free-text Git instruction shown verbatim.

**Context:** The source prompts target Claude Code while this session uses Codex.

a) Codex (recommended): adapt instructions and resources to this environment.

b) Codex and Claude Code: maintain shared guidance plus both configurations.

Other: write an alternative.

**Answer:** a) Codex; explicitly selected in the interactive question.

## R-A2.2 · Git autonomy

**Status:** closed; owner answered on 2026-10-20. **Recorded by:** primary agent.
**Reflected in:** ADR-0002. **Decision owner:** repository/product owner. **Basis:** explicit interactive response, except the free-text Git instruction shown verbatim.

**Context:** The source prompts differ on publication authority.

a) Approve each commit (recommendation presented): publication remains with the owner.

b) Automatic commits; owner handles push and PR.

c) Automatic commits, branch push and PR after review; owner handles merge and destructive operations.

Other: write an alternative.

**Answer:** Free text: “Eu quero que os comandos de git commit, push e PR sejam automáticos, mas deixa a merge para mim fazer.” This authorizes reviewed commits, branch pushes and PRs, not merges or force pushes.

## R-B.1 · Interface scope and visual reference

**Status:** closed; owner answered on 2026-10-20. **Recorded by:** primary agent.
**Reflected in:** SPEC-01, SPEC-03, ADR-0003. **Decision owner:** repository/product owner. **Basis:** explicit interactive response, except the free-text Git instruction shown verbatim.

**Context:** README covers configuration, logs and workers. The local SVG additionally depicts generation controls and GPU telemetry. Its structure/text was inspected; rendering did not produce an image.

a) README plus SVG generation controls (recommended): prompts, resolution, seed, steps, CFG, sampler and reset; no detailed GPU telemetry; proceed from the inspected structure.

b) README minimum only; defer additional controls.

c) Complete wireframe including extra indicators; visually validate the SVG before closing the ADR.

Other: write an alternative.

**Answer:** a) README plus generation controls, excluding detailed GPU telemetry.

## R-B.2 · Supported workflows

**Status:** closed; owner answered on 2026-10-20. **Recorded by:** primary agent.
**Reflected in:** SPEC-01, ADR-0003. **Decision owner:** repository/product owner. **Basis:** explicit interactive response, except the free-text Git instruction shown verbatim.

**Context:** The current payload manager hardcodes IDs 3/4/5/6/7/9.

a) Standard chain with configurable IDs (recommended): detect a unique connected chain, validate classes/links and offer mapping when ambiguous; no promise of arbitrary custom architectures.

b) Only today's fixed structure and IDs.

c) Arbitrary workflows with generic configuration and a broader compatibility scope.

Other: write an alternative.

**Answer:** a) Standard chain with automatic detection and explicit ID mapping when required.

## R-B.3 · Stopping a batch

**Status:** closed; owner answered on 2026-10-20. **Recorded by:** primary agent.
**Reflected in:** SPEC-02. **Decision owner:** repository/product owner. **Basis:** explicit interactive response, except the free-text Git instruction shown verbatim.

**Context:** Responsiveness is required but cancellation was unspecified; a global server interrupt may affect other clients.

a) Stop after saving the current scene (recommended); prevent subsequent scenes and let closing wait at this boundary with feedback.

b) No Stop button; protect window closing while the whole batch runs.

c) Cancel immediately on the server, requiring exclusivity and cross-client impact rules.

Other: write an alternative.

**Answer:** a) Stop after saving the current scene without interrupting other server jobs.

## R-B.4 · Prompt composition

**Status:** closed; owner answered on 2026-10-20. **Recorded by:** primary agent.
**Reflected in:** SPEC-01. **Decision owner:** repository/product owner. **Basis:** explicit interactive response, except the free-text Git instruction shown verbatim.

**Context:** A script provides scene descriptions and the interface provides global prompts; precedence needed clarification.

a) Global positive plus scene description (recommended); one global negative for the batch. Initialize fields from the workflow, edits replace the global, clearing removes it. Confirm Load when replacing edited text.

b) Use only the scene description as positive; retain a global negative.

c) Require complete positive and negative prompts per scene, changing the script format.

Other: write an alternative.

**Answer:** a) Combine global positive and scene description; use a global negative. The interactive question explicitly explained workflow initialization and clearing.

## R-B.5 · Output location

**Status:** closed; owner answered on 2026-10-20. **Recorded by:** primary agent.
**Reflected in:** SPEC-02. **Decision owner:** repository/product owner. **Basis:** explicit interactive response, except the free-text Git instruction shown verbatim.

**Context:** Existing code targets assets/generated_images and can overwrite files.

a) Chosen folder with an exclusive subfolder per batch (recommended), default assets/generated_images; scene index/timestamp filenames with no overwrite.

b) Always assets/generated_images, still with exclusive batch folders.

c) Chosen folder without subfolders; resolve repeated names using suffixes.

Other: write an alternative.

**Answer:** a) User-selected destination with an exclusive batch subfolder and no overwriting.

## R-B.6 · Scene failure

**Status:** closed; owner answered on 2026-10-20. **Recorded by:** primary agent.
**Reflected in:** SPEC-02. **Decision owner:** repository/product owner. **Basis:** explicit interactive response, except the free-text Git instruction shown verbatim.

**Context:** Automatic POST retry can duplicate generation; a lost response can leave submission status unknown.

a) Stop on the first terminal failure and preserve saved images (recommended); identify scene/cause, do not resend automatically or claim batch success.

b) Log failures and continue remaining scenes, delivering a partial batch.

c) Retry automatically before continuing, requiring duplicate-prevention rules.

Other: write an alternative.

**Answer:** a) Stop at the first failure, preserve completed files and do not resend automatically. Review clarified that a lost WS channel with a known prompt_id is recoverable monitoring, not itself a terminal generation failure (CA-02.19).

## R-B.7 · Per-scene seeds

**Status:** closed; owner answered on 2026-10-20. **Recorded by:** primary agent.
**Reflected in:** SPEC-01, SPEC-02. **Decision owner:** repository/product owner. **Basis:** explicit interactive response, except the free-text Git instruction shown verbatim.

**Context:** The current code randomizes once per batch; the SVG describes -1 per frame.

a) -1 draws a seed for each scene; a fixed seed repeats across scenes (recommended). Display/log the effective seed; initialize from the workflow.

b) -1 draws once and repeats for the batch, preserving current behavior.

c) Increment the supplied seed for each scene.

Other: write an alternative.

**Answer:** a) Randomize per scene for -1; repeat fixed values; initialize from the workflow.

## R-B.8 · Script format

**Status:** closed; owner answered on 2026-10-20. **Recorded by:** primary agent.
**Reflected in:** SPEC-01. **Decision owner:** repository/product owner. **Basis:** explicit interactive response, except the free-text Git instruction shown verbatim.

**Context:** The existing parser splits around parentheses without structural timestamp validation.

a) UTF-8 TXT, scenes starting with (MM:SS) or (HH:MM:SS), with multiline descriptions (recommended). Validate time/text, preserve order; parentheses inside text do not create scenes; indices distinguish repeated timestamps.

b) Same format, but exactly one scene per line.

c) Replace the input with structured JSON, requiring conversion.

Other: write an alternative.

**Answer:** a) UTF-8 TXT with timestamped scenes and multiline descriptions.

## R-A4.1 · Supported runtime

**Status:** closed; owner answered on 2026-10-20. **Recorded by:** primary agent.
**Reflected in:** ADR-0004. **Decision owner:** repository/product owner. **Basis:** explicit interactive response, except the free-text Git instruction shown verbatim.

**Context:** The manifest requires Python >=3.14 while README says 3.10+. An isolated hidden-window smoke passed with Python 3.14.3, CustomTkinter 6.0.0 and Tk 8.6.15; this is not full application evidence.

a) Support Python 3.14.x and CustomTkinter 6.0.0 (recommended); align manifests and lock during implementation; keep ComfyUI in a separate environment.

b) Also support Python 3.10–3.13, expanding compatibility validation.

Other: write an alternative.

**Answer:** a) Python 3.14.x and CustomTkinter 6.0.0, with manifest/lock work in Phase C.

## R-A3.1 · Presentation and controls

**Status:** closed; owner answered on 2026-10-20. **Recorded by:** primary agent.
**Reflected in:** ADR-0003, SPEC-01, SPEC-03. **Decision owner:** repository/product owner. **Basis:** explicit interactive response, except the free-text Git instruction shown verbatim.

**Context:** A concrete first-version proposal based on the SVG structure, without claiming visual fidelity.

a) English, dark theme, resizable/scrollable layout, no image preview or persisted preferences (recommended). Presets 1024×576, 576×1024 and 512×512 plus custom dimensions; workflow initial values; 2,000-line terminal.

b) Portuguese with all other controls and limits unchanged.

c) Include preview and persisted preferences now, expanding specifications and tasks.

Other: write an alternative.

**Answer:** a) Adopt the proposed English/dark presentation, exact presets and limits.

## R-A3.2 · Wait limits

**Status:** closed; owner answered on 2026-10-20. **Recorded by:** primary agent.
**Reflected in:** ADR-0003, SPEC-02. **Decision owner:** repository/product owner. **Basis:** explicit interactive response, except the free-text Git instruction shown verbatim.

**Context:** An unlimited wait prevents predictable closing. A local deadline does not cancel the server or authorize resubmission.

a) 30-minute editable per-scene deadline including queue and downloads (recommended); HTTP connect/read 10/60 seconds, WS checks every second, history fallback every 2 seconds, all bounded by remaining time.

b) 60-minute editable deadline with the same operation limits.

c) No total deadline; accept potentially indefinite waiting.

Other: write an alternative.

**Answer:** a) 30 minutes per scene, editable before execution, with the proposed operation limits.

## English naming instruction

The owner subsequently instructed that file/folder names and this conversation use English. Applied on 2026-10-21; see ADR-0005. This was a direct instruction, not an additional multiple-choice answer. It supersedes Portuguese naming/conversation guidance, without changing accepted product behavior.

## Phase B approval and Phase C authorization · 2026-10-21

The owner stated: “Okay, everything is good. When you're ready, let's move on to
the next phase.” Recorded by the primary agent as approval of the reviewed Phase B
specifications, ADRs and implementation plan, and authorization to proceed with
Phase C after its documented entry checks. This does not claim a merge or completed
implementation. The local ComfyUI compatibility check remains pending: the read-only
request to `http://127.0.0.1:8188/system_stats` was refused. Git metadata remains
read-only, preventing creation of the required Phase C branch and publication.

## Recording procedure

### Local ComfyUI startup and endpoint · 2026-10-21

The owner specified `C:\AI\ComfyUI_windows_portable\run_nvidia_gpu.bat` as the
startup command whenever ComfyUI needs starting, and confirmed the endpoint
`http://127.0.0.1:8188/`. Use the portable directory as the working directory because
the batch file uses relative paths. Check the endpoint first to avoid duplicate
server instances. The owner started it for this check; no launch was needed.
Read-only metadata reports ComfyUI 0.24.0 and the expected standard node schemas.

Record the context, real alternatives and their consequences before asking a spec/ADR/plan decision. Use R-NN.M for specs, R-A<N>.M for ADRs and R-PT.M for technical-plan choices. Only the primary agent asks the owner; subagents are disabled by the 2026-10-22 instruction.

Each block identifies status, affected document, dependencies, decision owner, context, recommended option and alternatives. Preserve the question and add the dated answer, recorder, basis and destination. A changed chosen option requires renewed confirmation. Review-derived questions are dated and suffixed b/c as necessary. Do not turn verifiable technical facts into preference questions.

Use the available interactive question tool within its limits, or concise text when unavailable. Existing authorization does not need repeated approval. The primary agent handles resulting edits outside docs/ and reviews them directly under the single-agent policy.

## Single-agent instruction - 2026-10-22

The owner instructed: ?For now on, no more subagents? and requested memory and
`.codex/agents` updates, citing token consumption. Effective immediately: the
primary agent performs implementation, tests and review; no spawning, resuming or
delegation. Prior independent reviews remain historical evidence; future reviews
are labeled primary-agent reviews. No measured token savings are claimed.
Protected profile/skill changes are prepared for local application by the owner.

Single-agent configuration applied by the owner on 2026-10-22: five profiles
archived as `.toml.disabled` and two skills updated. Primary agent verified the
archive filenames and active review instructions.

## Complete remaining Phase C tasks - 2026-10-24

Owner request: "Do you think you can complete all of phase C? But for each T that
you complete, always update state.md". Recorded by the primary agent as permission
to continue T11, T12 and T13 sequentially in this chat, superseding the earlier
one-completed-task-per-chat limit. Update docs/state.md after each completed task.
Single-agent review, scoped commits, owner-only merge and the Phase D gate remain.

## Open Phase D - 2026-10-26

Owner request: "can you tell me what is the next phase and the next tasks for that phase.
Once identified, you may begin working on it!" The primary agent identified Phase D
as next after the verified Phase C merge and records this as authorization to open
Phase D and begin D01. This authorizes local verification with fictional inputs;
it does not constitute acceptance of the demonstration or permission to merge.
Single-agent work, ignored generated outputs and owner-only final acceptance remain.
