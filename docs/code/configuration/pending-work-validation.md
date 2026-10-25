# Pending repository work - commit review

Started: 2026-10-23. Resumed: 2026-10-24. Owner explicitly requested committing the remaining modified,
renamed, deleted and untracked project files. Primary-agent review; no subagents.
Branch: `phase-c/commit-pending-work`. This records existing work, not a new phase.

## Scope and preservation

- English management migration: renamed docs, five skills, PR generator/tests,
  approved specs/ADRs/plan and task board. Previous Phase B reviews remain evidence.
- Single-agent policy: owner-applied archived `.toml.disabled` profiles retain
  historical instructions; active AGENTS/skills govern current work.
- T01 environment: Python bounds, CustomTkinter, dev pytest, lock and hashed runtime
  requirements. No further dependency update was made in this cleanup.
- T02-T06: immutable contracts, parser, graph mapping, catalog validation,
  correlated transport and atomic storage, with their existing tests/evidence.
  These are the missing dependencies of the already committed T07/T08 work.
- Earlier owner edits: CLI sampler selection, GUI package guard, manual client
  tests, renamed filesystem tests and SVG wireframe. Client method rename and
  documentation edits overlap the T04-T06 file and are preserved there.
- Deleted Portuguese management paths are replaced by their English counterparts.
  The five filesystem error scenarios survive in `test_file_system.py`; the old
  filename deletion is a rename, not removal of coverage.

Review corrections: README reflects T08 completion; the PR helper now requests
primary-agent review. The filesystem platform test patched `sys.platform`, but
the module binds `platform` at import time. Patching the module's binding makes
the existing unsupported-platform assertion exercise the intended branch. No test
was removed or relaxed. Previous setter expectation was already changed by the
owner to AttributeError, matching assignment to the read-only property.

## Verification

- `python -m unittest discover -s scripts -p "test_*.py"`: **7 passed**.
- Python 3.14.3/pytest 9.1.1, explicit T02-T08 test files plus
  `src/tests/test_file_system.py`: **206 passed in 5.15s**. Used the T02 documented
  fresh-temp-directory wrapper, with cacheprovider disabled.
- Five archived TOML profiles parsed; five active SKILL.md files checked.
- SVG parsed as XML, without script, foreignObject or image elements. This is
  structural inspection only, not rendered visual acceptance.
- Scoped diff and staged-path review; `git diff --check` passed with LF/CRLF warnings.

## Limitations and publication

The older `test_client.py` contains server-dependent/manual scenarios, including
an assertion-free setup scenario that reads default workflow/script/prompt files.
It is preserved, not counted as passing evidence, and was not executed. The CLI
still has the previously identified MediaUtils binding issue, assigned to T11;
its end-to-end execution is not claimed. The existing GUI version guard message
names utils and Python 3.10; project installation is constrained to Python 3.14.
These historical limitations do not establish desktop delivery readiness.

No secrets, personal documents/scripts, model files or generated images were
staged. No ComfyUI generation or new implementation task was started. Existing
local skill backups are retained on disk and explicitly ignored after they
appeared as untracked on resumption. Local commits do not constitute a PR,
merge, Phase D authorization or final acceptance. Prior branch ancestry still
contains 620feea and must be handled separately before publication. Historical
evidence documents describing blocked Git writes remain dated records; current
state supersedes their publication status.
