# ADR-0004 · Desktop Python environment

Date: 2026-10-20. Translated: 2026-10-21. Status: accepted by the owner through
R-A4.1; implementation and the Phase B gate remain pending.

## Context and evidence

ADR-0001 preserved the stack without resolving README (3.10+) versus
apps/pyproject.toml (>=3.14). Current manifests do not declare CustomTkinter.

Isolated test, without changing project dependencies or starting generation:
`uv run --no-project --python 3.14 --with customtkinter python <smoke>`.
The smoke imported CustomTkinter, created CTk, hid it, processed idle and destroyed
it. Observed output: Python 3.14.3; CustomTkinter 6.0.0; Tk 8.6.15;
`Hidden window smoke test OK`. This proves basic initialization, not all widgets,
networking, packaging or compatibility with ComfyUI server environments.

## Decision ratified on 2026-10-20

- Desktop application: Python `>=3.14,<3.15`; CustomTkinter `==6.0.0`.
- ComfyUI remains a separate process and environment accessed through the local API.
- In Phase C, align README and requirements with pyproject and generate a uv lock.
- Preserve existing dependencies until validation; pytest belongs in development
  dependencies rather than being a product runtime requirement.
- Validate full resolution and GUI smoke before claiming installation readiness.
- Initially distribute through a Python environment; a packaged executable is out of scope.

## Alternatives and consequences

Supporting 3.10–3.13 expands the matrix and may require dependency changes.
Allowing untested future versions appears flexible but does not establish
compatibility. Pinning the tested version reduces variation and requires renewed
validation for an upgrade.

Ratification: R-A4.1, option a, owner response on 2026-10-20. Supplements ADR-0001
in Phase C; does not change source history or authorize dependency installation
in this documentation phase.

## Sources

- [Official CustomTkinter documentation](https://customtkinter.tomschimansky.com/documentation/).
- [Package metadata](https://pypi.org/pypi/customtkinter/json).
- [Tkinter event/thread model](https://docs.python.org/3/library/tkinter.html).
- Local evidence above; repeat in the final environment after resolving all dependencies.
