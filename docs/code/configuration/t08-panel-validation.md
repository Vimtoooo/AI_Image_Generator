# T08 - Configuration panel validation

Date: 2026-10-23. Phase C. Primary-agent implementation and review; no subagents.
Scope: `gui/config_panel.py`, `tests/test_config_panel.py`. T09 has not started.

## Implementation and integration contract

`ConfigPanel` is a scrollable CustomTkinter frame. `ConfigurationDraft` separates
file/default handling from widgets. Native file dialogs select script, API workflow,
prompt TXT and destination. Invalid reads preserve previous valid selections;
cancel leaves edits intact. Multiple chains require explicit IDs for all seven
roles. Applying mapping validates topology; unapplied ID edits block snapshot creation.
Workflow values initialize controls; Reset restores those values while preserving
files and destination. Prompt TXT replacement confirms manual changes.

`snapshot()` returns the existing frozen GenerationConfig after local validation;
it raises a field-specific ValueError/WorkflowError/CatalogError on invalid input.
T11 must display those failures before launching a worker. The checkpoint choice
is stored in the snapshot's mapped loader. No batch directory or POST is created.

T09 must implement `request_catalog(request_id, server_url, deliver)` as a prompt
returning dispatcher. Queue results and invoke `deliver(request_id, catalog, error)`
on the Tk thread; never call it from the network worker. Catalog is a
GenerationCatalog or None; error is text or None. Refresh invalidates the current
catalog; stale responses and callbacks after panel destruction are ignored.
Choices never silently replace the current value. T11 owns initial refresh and
window state wiring; call `set_enabled(False)` during active states. All panel
methods are UI-thread-only. The server URL is supplied by the host constructor.

## Executed evidence

Python 3.14.3, pytest 9.1.1, CustomTkinter 6.0.0. The test venv initially lacked
CustomTkinter; approved `uv sync --frozen` restored CustomTkinter and darkdetect
without changing the declared dependencies or lockfile. No ComfyUI was contacted.

From `apps/`, using `apps/.venv/Scripts/python.exe` and the process-local
fresh-directory creation wrapper documented in T02:

```text
src/tests/test_scene_parsing.py src/tests/test_workflow_mapping.py
src/tests/test_catalog_validation.py src/tests/test_transport_protocol.py
src/tests/test_output_storage.py src/tests/test_runner.py
src/tests/test_config_panel.py -p no:cacheprovider --basetemp <fresh temp directory>
```

Final result: **201 passed in 5.22s**, including **27 T08 tests**. Six original
widget scenarios plus the mapping regression use real widgets in one withdrawn
Tk root, with fake dialogs/messages and catalog callbacks. Repeated Tk root
creation failed during initial testing; the fixture now reuses one interpreter.

| Criterion | Evidence |
|---|---|
| CA-01.1 | Canceled script/workflow/destination dialogs retain paths and edits |
| CA-01.10 | Workflow defaults appear in actual widgets and frozen snapshot |
| CA-01.12 | All three preset dimensions; Custom preserves dimensions |
| CA-01.15 | Edited positive/negative prompt replacement cancel/confirm; source bytes unchanged |
| CA-01.17 | Reset restores workflow values; files/destination retained; no execution callback |

Additional checks cover BOM/multiline scripts, bad JSON/Canvas/encoding/read errors,
explicit multiple-chain mapping, numeric/catalog errors, empty prompts, immutable
snapshots, stale/failed catalogs, removed models, disabled controls and destruction.

## Primary-agent review and limitations

Confirmed after scoped review and one correction pass: changed-but-unapplied node
IDs now block snapshots instead of using a previously applied mapping. The new
regression and combined suite pass. Initial widget tests also caught and corrected
a helper-name collision with CTkScrollableFrame's internal label. No unresolved
blocking T08 code finding. `git diff --check` passes with line-ending warnings only.

No visual acceptance, native-dialog interaction, full-window integration,
responsiveness under real asynchronous I/O or real generation is claimed. These
remain T09-T12 and authorized Phase D work. Configuration file reads are local and
synchronous; catalog networking is delegated through the documented boundary.

Context7 `/tomschimansky/customtkinter` supplied official CTkScrollableFrame,
CTkOptionMenu and CTkTextbox documentation from the project's GitHub wiki.
The existing scoped Graphify map confirmed detect_node_mapping ->
validate_node_mapping, apply_parameters -> validate_generation_parameters and
get_catalog -> parse_catalog. No index rebuild or model calls were used for this query.

Publication remains blocked by uncommitted Phase B/T02-T06 dependencies and the
unreviewed earlier commit 620feea in branch ancestry. T08 is locally scoped;
publishing the whole branch would include that unrelated work. Preserve prior
changes and resolve dependency publication separately. Stop after this task;
T09 begins in a new chat under the owner's one-task-per-chat instruction.
