# T11 - Window and launch validation

Date: 2026-10-24. Primary-agent implementation and review; no subagents.
Branch phase-c/window-launch starts at reviewed T10 6f0c6bd. PR #11 is its
dependency until merged into main. No merging performed by the agent.

MainWindow assembles the scrollable configuration and read-only feedback panels,
catalog adapter and Generate/Stop controls. Initial theme is dark; minimum size
is 900x540. Lifecycle state is separate from feedback stage. Generate snapshots
the configuration and a finite positive deadline (minutes, default 30) before
starting a worker. Initial destination is assets/generated_images; its tracked
.gitkeep provides the directory. Custom destinations remain selectable.

Controls remain locked through terminal delivery until worker.busy clears.
Repeated Generate/Stop is guarded. Closing during execution offers returning or
cooperative stopping; Tk and feedback remain alive until controller.close invokes
its completion callback. Idle closing also waits for catalog work to exit.
Validation/start failures identify the problem and retry action in the terminal.

main() retains the CLI body and public calls. entrypoint([]) calls main(); --gui
late-imports gui.launch. Importing main or requesting --help does not import Tk.
The existing MediaUtils reference now binds explicitly to utils.media_utils;
the legacy comment and defaults are preserved.

## Executed tests

Python 3.14.3 / pytest 9.1.1 / CustomTkinter 6.0.0, Windows; no ComfyUI/GPU.
From apps/ with .venv/Scripts/python.exe:

- pytest src/tests/test_main_window.py -q -p no:cacheprovider: **16 passed in 1.91s**.
- test_entrypoints.py using the T02 fresh-directory wrapper: **6 passed in 1.21s**.
- git diff --check: passed.

Window tests use actual withdrawn widgets and a deterministic controller. They
verify initial catalog dispatch/dark theme/layout, locked controls, duplicate
Generate, terminal/exit lag, Stop with inflight events, stale events, three final
states, close cancellation/waiting, worker-start errors and deadline validation.
CLI tests use fictional files/transport and assert existing public call shapes
for landscape, portrait and custom, plus GUI/no-argument dispatch and lazy import.

CA-02.12, CA-03.1/2/3/13/15 have implementation and automated widget evidence;
visible resizing, native dialogs and full worker integration are T12 evidence.
R-B.5 initial destination and R-A3.2 editable deadline were missing from the T08
panel; T11 supplies them in its owned assembly file, preserving requirements.

## Primary-agent review

Confirmed scope: main_window.py, gui/__init__.py, main.py and their two new tests,
plus evidence/decision/state records. Reviewed diff, new tests and source criteria;
no blocking findings. Existing CLI comments and behavior retained. No secrets,
personal input or generated images included. Context7 CustomTkinter official
CTk geometry/grid documentation used; prior T08 Graphify findings reused.
Real end-to-end generation and Phase D remain unopened.
