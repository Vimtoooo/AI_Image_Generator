# Foundation evidence

Date: 2026-10-20. Scope: management; this is not application or GUI validation.

Translation and naming update, 2026-10-21: the user requested English documentation and filenames. The evidence below remains a historical record of the 2026-10-20 checks, not a claim that renamed artifacts were retested.

- `python -m unittest discover -s scripts -p test_*.py`: seven tests passed.
  Tests use temporary repositories and cover Git collection, removals, gaps,
  unavailable Git, invalid base, external output and rejection of output inside the project.
  The Windows sandbox blocked temporary subdirectories; an authorized run outside it succeeded.
- The five skills passed the skill-creator's `quick_validate.py`, using
  `uv run --no-project --with pyyaml python <validator> <skill>`.
  The default Python lacked PyYAML; application dependencies were not changed.
- Five TOML files were checked with `tomllib`; AGENTS.md was below 200 lines.
- `git check-ignore` confirmed exclusions for auxiliary memory, the optional graph and checkpoints.
- SHA256 hashes of the six earlier local files were compared with a temporary inventory;
  all were preserved. The earlier deletion of test_file_system_errors.py remained intact.
- `git diff --check` reported no whitespace errors; LF/CRLF conversion warnings occurred.

## Limitations

Independent review by `revisor_fundacao` on 2026-10-20 found no material blocker.
New duplicate exclusions and ambiguity about direct/forced pushes were corrected.
State and tasks were updated with evidence; isolated publication was to be checked before pushing.

Profiles were not loaded in a fresh Codex session; their format was validated, and
roles can be supplied explicitly when delegating. No per-profile permission isolation
is claimed. No Claude hook was installed.

Not run: application tests requiring ComfyUI, GPU checks, image generation,
desktop interface tests or CI. There is no evidence here that future product criteria were completed.

## Isolated publication

At the time, local main included 620feea, absent from remote main 4dd9187 as checked
with `git ls-remote`. Publication used a temporary worktree based on origin/main and
received only foundation commits, preserving the original tree and earlier commit.

The reviewer confirmed equivalent `git range-diff` output for the two reviewed commits,
absence of 620feea from ancestry, and an empty diff in apps/ and assets/. The push completed;
[PR #1](https://github.com/Vimtoooo/AI_Image_Generator/pull/1) was created by the agent.
During session closure, `gh pr view` confirmed that the owner merged it at
2026-10-20T20:49:33Z, commit 8e6115baa27b61ae55da240572b898dd82751a07.
The agent did not merge it. At that closing checkpoint, Phase B still awaited instruction.

Historical clarification added on 2026-10-21: the user subsequently authorized Phase B
on 2026-10-20, as recorded in the current state and task board. This does not change the
scope or results of the foundation checks above.
