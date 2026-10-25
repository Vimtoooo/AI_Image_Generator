# Foundation origin

Record dated 2026-10-20. This document preserves the origin of the work; changes to decisions belong in ADRs rather than replacing the historical request.

Translation note, 2026-10-21: the user requested English documentation and filenames. This translation preserves the original request, decisions, dates and source hashes. Active local references use the renamed files; the external prompts remain unchanged.

## Request and authorization

The repository owner described this project as local image-generation automation using ComfyUI and `.safetensors` models. They requested reading the three prompts in `../../IA/Prompts`, organizing resources and memory for subagents, and then addressing the pending README requirements.

In the same session, they approved the **Fundação de trabalho do repositório ComfyUI** plan with “Implement the plan”. The plan authorizes Phase A, adaptation to Codex, commits, branch pushes and PR creation after verification and independent review. Merging remains a human action. Later phases require approval of their respective deliverables.

## Sources checked

| Source | Role | Reference on 2026-10-20 |
|---|---|---|
| `../README.md` | Product capabilities and pending work | Git baseline `620feea`; inspection also considers local changes without attributing them to the foundation |
| `../../IA/Prompts/ESTRUTURA.md` | Artifact template | SHA256 `E827F899154BC7092FBB8E4301AFD9534669D0DF8A3AB4AC5923F5B2AA58B180` |
| `../../IA/Prompts/NORMAS.md` | Management, review and memory | SHA256 `0AD936FEADE151C5A48184BFA31B82E2F48612273CDB270D63F2F543AF622970` |
| `../../IA/Prompts/PROMPT.md` | Method setup sequence | SHA256 `C77CC1547F665387C292606CE11496188350AF32DA7A7E12D9E20E72215B7BA4` |

External-folder paths are relative to the repository root, not this file. Authorized reading covers only the three named files; it does not authorize scanning neighboring folders. Hashes detect source changes without requiring a Git repository. Neither the complete source documents nor personal content have been copied into this repository.

## Precedence and boundaries

The approved request and plan guide adaptation of the prompt examples, originally written for Claude Code and another domain. Local choices are recorded in [ADR-0002](adr/0002-codex-workflow.md). Environment instructions and permissions remain applicable. Plan approval does not override a technical restriction of the session.

`docs/` contains versioned management documents; `documents/` remains untouched. The foundation does not authorize implementing the interface, changing the backend, installing Graphify, or creating a database, login or cloud infrastructure.