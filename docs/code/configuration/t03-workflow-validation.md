# T03 workflow mapping and payload isolation

Date: 2026-10-22. Status: complete; primary-agent review passed under the single-agent policy.

Scope: `payload_mgr.py`, positive prompt composition in `formatting_utils.py`,
and fictional `test_workflow_mapping.py` fixtures. No user workflow was read.

The implementation detects and validates the connected seven-role standard chain,
including node classes, output slots, distinct prompt encoders and batch size one.
An ambiguous graph requires explicit mapping; selected payloads contain only those
seven nodes. Each scene receives a fresh mutable copy even when the source is a
frozen snapshot. Empty positive text leaves only the scene description; empty
negative text remains empty. Sampler updates target KSampler.

Legacy fluent update methods remain, with node IDs derived per instance.
`current_payload` returns an isolated copy; reset restores workflow defaults.
The constructor now rejects incomplete or unsupported graphs, replacing fixed-ID
assumptions and swallowed missing-node errors under the approved chain contract.

Validation: **62 tests passed** (32 T02 + 30 T03) on Python 3.14.3. The run used
the [documented temporary-directory wrapper](t02-script-validation.md) with both
explicit test files. `git diff --check` passed. Numeric/catalog validation remains
T04; GUI mapping selection remains later interface work.

Graphify indexed the six backend code files locally (131 nodes, 206 edges at the
first snapshot), with output under `%TEMP%\comfy-code-map\graphify-out`. An
incremental check after implementation found no further changes. It did not index
personal documents, images or models, and used no LLM extraction tokens. Graph
inferences guide targeted inspection; tests and source remain the evidence.

The attempted independent review did not execute because the agent tool reported a
usage limit. No independent T03 review is claimed. The owner subsequently disabled
subagents. The primary agent reviewed graph shape, role/slot validation, ambiguity,
copy isolation and legacy adapters, then reran all 62 tests successfully (0.46s).
No T03 blockers were found. Numeric validation is covered separately by T04.
