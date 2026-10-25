# ADR-0001: preserve the existing stack during the foundation

Date: 2026-10-20. Status: accepted by the owner through the foundation plan; this records preservation, not approval of new versions.

Translation note, 2026-10-21: English documentation and filenames were requested by the user; historical scope and findings are preserved.

## Context

The [README](../../README.md) describes local generation through ComfyUI and a planned CustomTkinter interface. The Python project already exists in `apps/`. Phase A organizes work without changing the application or absorbing earlier local changes.

## Decision

| Layer | Choice for this phase |
|---|---|
| Application | Preserve Python and the `apps/src/` structure |
| Generation | Preserve integration with local ComfyUI and API-format workflows |
| Communication | Preserve declared HTTP and WebSocket dependencies |
| Interface | Retain CustomTkinter as the README's intended choice; implementation pending |
| Management | Markdown documents and a Python PR-description generator |
| Persistence and access | Do not introduce a database, login or cloud infrastructure |

Inspection on 2026-10-20: `apps/pyproject.toml` declares Python `>=3.14`, while the README states `3.10+`; CustomTkinter is absent from both the manifest and `apps/requirements.txt`. The four interface modules are empty. Tests exist in the local working tree; some require network access. These findings call for investigation in Phase B, not dependency changes in Phase A.

## Alternatives and consequences

Migrating the stack or adding services now would expand scope without a requirement. Adding Node solely to copy the method's generator would introduce an unnecessary tool; Python supports the management automation.

Preserving the stack reduces regression risk and protects local work. The foundation does not validate the complete application installation or test suite. Compatibility between Python, the interface library and the local environment must be checked before implementation.

## When to revisit

Revisit during Phase B before approving the technical plan, or when a requirement demonstrates the need for a new dependency. Version or architecture changes need evidence and an explicit decision; this ADR does not authorize automatic upgrades.

Follow-up recorded on 2026-10-21: [ADR-0004](0004-python-environment.md) records the Phase B environment decision accepted through R-A4.1 on 2026-10-20. It resolves the environment question for future implementation without changing this ADR's historical Phase A preservation decision.