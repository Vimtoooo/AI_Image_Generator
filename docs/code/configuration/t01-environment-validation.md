# T01 environment validation

Date: 2026-10-21. Scope: desktop environment; ComfyUI remains separate.

The owner created `phase-c/environment` and ran the prepared environment's
`uv lock`, `uv sync --locked`, and `smoke_environment.py`. Resolution found 17
packages; installation included 16 dependencies. The reported smoke passed.
The primary agent repeated the smoke using that environment's Python executable:
Python 3.14.3, Tk 8.6.15, CustomTkinter 6.0.0, Pillow 12.2.0,
python-dotenv 1.2.2, requests 2.34.2, websocket-client 1.9.0, pytest 9.1.1.

The verified manifest and generated lock were copied into `apps/`.
`uv lock --check --offline --directory apps` with a permitted temporary cache
passed (17 packages). Runtime requirements were exported with `--locked --no-dev
--no-emit-project`, including hashes. Pytest and its exclusive development
dependencies remain in the lock's development group, not runtime requirements.

Added `apps/README.md` to satisfy existing project metadata and document locked
installation. Root README now specifies Python 3.14.x and separate ComfyUI runtime.

The smoke imports runtime modules, creates a hidden CTk window, processes idle
events and destroys it. This verifies initialization, not complete GUI behavior.
The tested environment is `%TEMP%\comfy-phase-c-t01\.venv`; the repository's own
environment was not synchronized. No GPU generation was performed.

Git writes and publication remain unavailable to the agent. Existing application
edits and tests were preserved. Independent final review is recorded in the task board.
