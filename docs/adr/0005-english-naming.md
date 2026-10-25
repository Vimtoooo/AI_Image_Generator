# ADR-0005 · English naming and communication

Date: 2026-10-21. Status: accepted by the owner's direct instruction received on 2026-10-20.

## Context and decision

During Phase B, the owner requested English file/folder names for consistency and
English conversation. Translate active project-management documents and procedures,
rename their paths, and update references as one reviewed change. Preserve historical
dates, decisions, acceptance IDs and quotations. External source prompts remain untouched.

| Previous convention | Active convention |
|---|---|
| estado / tarefas / ratificacoes / origem / plano | state / tasks / ratifications / origin / implementation-plan |
| docs/codigo/configuracao | docs/code/configuration |
| Portuguese spec and ADR suffixes | English configuration, execution, interface and environment suffixes |
| Portuguese skill/profile names | English names matching their folders and TOML name fields |
| preparar_pr.py / test_preparar_pr.py | prepare_pr.py / test_prepare_pr.py |
| --titulo / --resumo / --saida | --title / --summary / --output |
| Portuguese branch/commit wording for future work | phase-<letter>/<topic> and English imperative commit messages |

The eleven PR sections retain their purposes and order, translated to English.
The helper's unverified-field marker is now [GAP]; its tests must retain coverage.
Existing published branches and commits are historical records, not renamed remotely.
The owner explicitly extended this preference to branches and commits on 2026-10-21.
The current local branch is `phase-b/specifications`; the isolated publication branch
is `phase-b/gui-specifications`. New commits use English imperative messages.
Existing commit messages remain unchanged because translating them rewrites commit
identities; previous application work is outside this migration.
Application modules already use English and are not refactored by this migration.

## Consequences and verification

Old management paths and CLI option names are replaced; there are no known callers
outside this repository. Update all active examples and imports together, run the
seven PR-helper tests, validate skill metadata and TOML names, check local Markdown
links and scan for stale active references. Git history retains original content.
Historical quotations and the external filenames ESTRUTURA.md, NORMAS.md and PROMPT.md
keep their original spelling. This replaces ADR-0002's Portuguese communication
choice but preserves its workflow, authority boundaries and phase gates.

Reconsider only if a consumer requires compatibility aliases or the owner changes
the language convention. A future localization feature is a separate product decision.
