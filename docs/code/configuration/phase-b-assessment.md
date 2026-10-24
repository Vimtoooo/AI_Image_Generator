# Phase B assessment

Date: 2026-10-20. Translated: 2026-10-21. Static inspection for specification,
not acceptance evidence. References: [plan](../../implementation-plan.md),
[state](../../state.md), [ADR-0004](../../adr/0004-python-environment.md).

## Provenance and preservation

Inspection covers the local working tree, including earlier changes to
`apps/src/comfy_generator/client.py`, `apps/src/gui/__init__.py` and
`apps/src/main.py`, local deletion of `test_file_system_errors.py`, and new
`test_client.py`/`test_file_system.py` files. The reference SVG is also a prior
local file. These contents are not delivered by Phase B.

State records README inspected at 620feea and foundation publication isolated
from that commit. Local findings do not establish that origin/main contains the
same code. Before Phase C, record the actual base/diff, review earlier work
separately and preserve its authorship/provenance.

## Static findings and planned treatment

| Finding | Consequence | Planned treatment |
|---|---|---|
| Client returns an empty sampler list | GUI receives no real options | T04: object_info catalog |
| Payload fixes IDs and writes sampler into checkpoint node | Incorrect or incompatible workflow mutation | T03/T04: validated chain and KSampler updates |
| CFG validation rejects valid integer 8 | Valid input can fail on Python type | T04: finite numeric normalization and limits |
| Main references MediaUtils without an identified valid binding | CLI path may fail before generation | T11: adapter/import and regression without changing defaults |
| Dimension calculation rounds ratios inadequately | Resolution may differ from selected ratio | T08: ratified exact pairs and validated custom dimensions |
| Parser splits parentheses without structural context | Parentheses in descriptions may create invalid scenes | T02: line-start timestamps and multiline continuation |
| Legacy tracking returns the first image | Does not prove all output files are saved | T05: new list contract with preserved legacy adapter |
| GUI files do not deliver the described interface | Backend does not prove desktop behavior | T08–T11 and D01 demonstration |

Findings define test targets, not permission to remove existing tests or absorb
earlier changes. Regression tests must make corrections observable. No application
fix was performed during this assessment.

## Environment evidence, scope and gaps

The principal reported an isolated smoke using `uv run --no-project --python
3.14 --with customtkinter`: Python 3.14.3, CustomTkinter 6.0.0, Tk 8.6.15. Creating
CTk, hiding it, processing idle and destroying it produced
`Hidden window smoke test OK`. ADR-0004 records the command and scope. It did not
use the full application environment or prove generation, every widget, lock-based
installation or server compatibility.

README and manifest disagree on Python; CustomTkinter still needs declaration in
implementation. R-A4.1 selected Python 3.14.x and CustomTkinter 6.0.0; dependency
and lock alignment is T01, not completed work.

SVG elements/text were inspected but rendering failed. There is no demonstrated
visual comparison, responsiveness measurement or generation benchmark in this
phase. Planned HTTP/WS, storage and real-workflow tests are future work; offline
evidence and ComfyUI integration evidence will remain distinct.
