# T12 - Desktop integration validation

Date: 2026-10-25. Primary-agent implementation and review; no subagents.
Status: automated verification passed; visible interaction checks pending.

## Executed evidence

Python 3.14.3 / pytest 9.1.1 / CustomTkinter 6.0.0 / Tk 8.6.15, Windows.
No real ComfyUI instance or GPU used. Fictional scripts, graphs and image bytes
are created only in fresh temporary test directories. Real loopback HTTP and
WebSocket sockets use an ephemeral 127.0.0.1 port, never the user's server.

Each offline module ran in its own Python process using the T02 directory-mode
wrapper, -q -s -p no:cacheprovider and a unique comfy-phase-c-<uuid> basetemp.
All **287 application tests** passed; no suite emitted stderr. Module counts:

| test_ module | Passed |
|---|---:|
| scene_parsing | 32 |
| workflow_mapping | 30 |
| catalog_validation | 39 |
| transport_protocol | 20 |
| output_storage | 25 |
| runner | 28 |
| config_panel | 27 |
| file_system | 5 |
| gui_worker | 20 |
| log_panel | 25 |
| main_window | 16 |
| entrypoints | 6 |
| desktop_integration | 14 |

Final desktop integration run: **14 passed in 21.42s**. Full-window heartbeat:
50 samples over 5 seconds, maximum interval **0.102s** during simulated batch I/O.
Existing T09 heartbeat also passed (0.103s). Seven management tests passed in
3.885s using approved elevation for their temporary Git repositories.

Ten new isolated Tk scenarios combine the actual configuration, feedback, window,
worker and runner: completion, partial-download failure, Stop, cancel/confirm
close, delayed worker exit after terminal, close during catalog work, obsolete
catalog requests, unavailable catalog, heartbeat and 12,000 queued log events.
The log flood proves bounded delivery and preserved terminal feedback, not a
general throughput guarantee. Four loopback scenarios run the real runner and
transport through normal progress, cached completion, WebSocket disconnect and
truncated HTTP download. They assert WS-before-POST, unrelated-event filtering,
no duplicate POST, no /interrupt, terminal counts and stored bytes/partial cleanup.

## Regression found and corrected

The first ten desktop scenarios passed behavioral assertions but failed on Tk
stderr: pending CustomTkinter callbacks outlived destroyed widgets. T12 therefore
includes a bounded correction in T11's main_window.py: after both workers exit,
cancel remaining timers in this window's owned interpreter before destroying it.
Cancel at the Tcl timer level so child widgets still own their command cleanup.
No polling or producer is canceled before worker shutdown. The unchanged strict
stderr checks pass after the correction. Context7 CPython after_info/after_cancel
and ThreadingHTTPServer/shutdown documentation informed the correction/harness.

## Visible checks still required

An offline preview was launched with the committed test harness and fictional
inputs. Native desktop control failed with "Computer Use native pipe is
unavailable ... The system cannot find the file specified (os error 2)".
Retry, session reset and the alternative desktop interface produced the same
failure. No screenshot or native interaction evidence was obtained. Automated
withdrawn-widget assertions are not a substitute for visual acceptance.

Once desktop access is restored, use test_desktop_integration.preview with a fresh
temporary directory. Confirm at normal and minimum size: readable configuration,
scroll access to prompts/Reset, visible Generate/Stop and both progress displays;
cancel native file dialogs preserving selections; prompt replacement confirmation;
Reset; Stop during the eight-second fictional current scene; cancel/confirm close.
Do not point this harness at real ComfyUI. The preview has a fictional catalog and
runner. Keep generated fixture bytes out of Git.

## Review and traceability

Primary-agent review confirmed scoped tests, deterministic race barriers, actual
Tk-thread delivery, real socket boundaries, finite test waits and the shutdown
correction. No blocking code findings. git diff --check passed. The remaining
visual evidence is an explicit verification gap, so T12 is not marked complete
and T13 final delivery remains pending. See the 53-criterion matrix below.

All rows identify executed offline evidence; none claims real ComfyUI acceptance.
Test names are within apps/src/tests/. Earlier detailed evidence remains in T02-T11.

| Criterion | Executed evidence / remaining limit |
|---|---|
| CA-01.1 | config_panel: widget_defaults_cancel_reset_and_snapshot; native dialog pending |
| CA-01.2 | scene_parsing: multiline_order_duplicates_and_parentheses |
| CA-01.3 | scene_parsing invalid/empty cases; config_panel snapshot errors |
| CA-01.4 | workflow_mapping invalid_json_shape; config_panel failed_load_preserves_last_valid |
| CA-01.5 | workflow_mapping changed_ids_and_extraction |
| CA-01.6 | workflow_mapping ambiguity_requires_explicit_mapping; config_panel multiple chains |
| CA-01.7 | workflow_mapping wrong_slot/unsupported_topology; config_panel unapplied mapping |
| CA-01.8 | catalog_validation catalog request; desktop loopback /object_info; live server pending |
| CA-01.9 | config_panel stale/failure/missing selection; desktop catalog_failure |
| CA-01.10 | config_panel workflow_defaults_and_detached_snapshot, widget defaults |
| CA-01.11 | catalog_validation field_errors_before_mutation; config_panel snapshot_field_errors |
| CA-01.12 | config_panel presets_and_custom, widget_mapping_and_presets |
| CA-01.13 | workflow_mapping prompt_combinations |
| CA-01.14 | workflow_mapping prompt_combinations |
| CA-01.15 | config_panel prompt_confirmation_and_source_preservation; native confirm pending |
| CA-01.16 | runner fixed_seed, random_seed_is_drawn_and_recorded_per_scene |
| CA-01.17 | config_panel reset_preserves_selections_and_sources, widget Reset; visible check pending |
| CA-01.18 | scene_parsing file reader/errors; config_panel failed load/encoding cases |
| CA-02.1 | runner invalid_configuration and invalid_later_scene prevent submissions |
| CA-02.2 | gui_worker duplicate start; main_window terminal exit gap; desktop terminal_lag |
| CA-02.3 | workflow_mapping frozen_and_independent_payloads; runner isolated payloads |
| CA-02.4 | transport_protocol ws_before_post; desktop loopback socket handshake assertion |
| CA-02.5 | transport_protocol unrelated events; desktop loopback foreign prompt |
| CA-02.6 | transport_protocol unrelated_errors_and_node_executed_do_not_complete_scene |
| CA-02.7 | transport_protocol cache/all descriptors; desktop cached; output_storage all images |
| CA-02.8 | transport_protocol missing_or_invalid_mapped_images_fail |
| CA-02.9 | runner partial_scene_preserves_files; desktop failed; log_panel partial counts |
| CA-02.10 | runner stop_race after authorization; desktop stopped/close |
| CA-02.11 | runner stop_race before authorization; transport stop sends no POST |
| CA-02.12 | main_window close cancellation; desktop close waits for terminal/exit; native dialog pending |
| CA-02.13 | output_storage exclusive batches/collisions/publication race |
| CA-02.14 | output_storage failed streams; desktop truncated real HTTP response |
| CA-02.15 | runner first_error_stops_without_retry; partial files retained |
| CA-02.16 | transport_protocol lost_post_is_unknown_and_never_retried |
| CA-02.17 | transport_protocol deadline_after_submission_never_interrupts_server; storage deadline |
| CA-02.18 | runner success totals; desktop completed, four fictional files |
| CA-02.19 | transport_protocol WS loss; desktop disconnect with real sockets |
| CA-03.1 | main_window layout assertions; complete assembly in desktop tests; visible inspection pending |
| CA-03.2 | scrollable configuration instantiated; visible minimum-size scrolling pending |
| CA-03.3 | main_window locked controls; desktop configuration re-enabled after exit |
| CA-03.4 | full-window five-second heartbeat max 0.102s; native interaction pending |
| CA-03.5 | main_window loading label; desktop delayed/stale/closing catalog workers |
| CA-03.6 | log_panel actual_read_only_widgets reject insertion/deletion |
| CA-03.7 | log_panel log_fields_and_no_payload_dump |
| CA-03.8 | log_panel real fractions; desktop loopback correlated progress |
| CA-03.9 | log_panel twelve invalid/uncorrelated cases and actual indeterminate bar |
| CA-03.10 | log_panel sampler_completion_and_downloads_do_not_count_as_saved |
| CA-03.11 | log_panel saved scene bar; desktop successful completion |
| CA-03.12 | gui_worker idempotent Stop; main_window inflight events; desktop stopped |
| CA-03.13 | main_window three terminal states; desktop completed/stopped/failed |
| CA-03.14 | log_panel summaries/partial files; desktop success/failure/Stop |
| CA-03.15 | main_window validation/start errors; desktop unavailable catalog; structured runner errors |
| CA-03.16 | log_panel physical-line eviction and summary; desktop 12,000-event bounded flood |

## Owner manual verification - 2026-10-25 (in progress)

The owner chose guided manual checks after desktop control remained unavailable
in this session. Fresh offline preview uses fictional inputs and no real ComfyUI.
Owner reported manual checks 1-4 passed:

- Resizing smaller keeps Generate, Stop, logs and progress visible.
- Configuration scrolling reaches both prompt fields and Reset.
- Canceling the Script TXT native dialog retains the selected script.
- Canceling workflow and destination dialogs retains both selections.

These are owner-reported manual results, not agent-observed screenshots.
Prompt replacement confirmation, Reset, running/Stop and close checks remain.
Current fixture directory: %TEMP%/comfy-t12-manual-29cdac5084d54df9934c9a8d682cff7e.
It includes positive.txt containing "A fictional watercolor style".
Earlier statements that no native interaction evidence existed describe the
pre-manual-check stopping point; the results above supersede those specific gaps.

## Run the manual offline preview

From the repository root in PowerShell, run the block below. It creates a fresh
fictional fixture folder, prints its path, and opens the test window. It requires
the existing development environment (including pytest) because the harness
reuses test fixtures. No ComfyUI service or GPU is needed.

```powershell
@'
import sys
import tempfile
from pathlib import Path
sys.path[:0] = ['apps/src', 'apps/src/tests']
from test_desktop_integration import preview
folder = Path(tempfile.mkdtemp(prefix='comfy-manual-'))
(folder / 'positive.txt').write_text('A fictional watercolor style', encoding='utf-8')
(folder / 'negative.txt').write_text('blur, low detail', encoding='utf-8')
print(f'Test files: {folder}', flush=True)
preview(folder)
'@ | .\apps\.venv\Scripts\python.exe -
```

The harness also creates fictional.txt and fictional.json in that folder and
preselects them. The simulated runner waits eight seconds per scene and writes
fictional bytes, not viewable generated images. Complete tests 5-13 from the
conversation checklist; 1-4 already have owner-reported passes.

The real GUI launches from the repository root with
`.\apps\.venv\Scripts\python.exe .\apps\src\main.py --gui`.
It uses the actual local ComfyUI endpoint, so it is not the offline test harness.
Omitting --gui starts the legacy CLI; it is not the manual GUI testing command.
Phase D real-generation demonstration remains unopened.
