# Product: local image generation

Status: foundation merged; Phase B authorized on 2026-10-20. Sources: [approved request](origin.md) and **Current Tasks** and **Future Roadmap** in the [README](../README.md). This PRD records product intent; Phase B specifications define its detailed behavior.

Translation and naming update, 2026-10-21: English documentation and filenames were requested by the user. Historical decisions and dates are preserved.

## Problem and objective

People preparing images for scripts need to configure files and parameters, follow execution and identify failures without manually managing every generation. Existing automation provides the foundation for this flow; the pending interface still needs implementation.

The objective is to configure generation and follow its results in a responsive window using the computer's local resources. Product completion means the operator selects files and a model, starts generation, follows progress and messages, and obtains the corresponding images while the window remains usable.

## Audience and visibility

The intended role is a local operator responsible for the script, model selection and generated images. The operator sees execution settings, progress and errors. There is no requirement for sharing, multiple access roles or a remote dashboard.

## Scope and sources

| Capability | Source |
|---|---|
| Select script files and generation configuration | README, Current Tasks, configuration panel |
| Choose among locally available models | README, Current Tasks, checkpoint dropdown |
| Enter manual prompt, aspect-ratio and seed adjustments | README, Current Tasks, manual inputs |
| Read messages and progress during execution | README, Current Tasks, log panel |
| Interact with the window while generation runs | README, Current Tasks, background processing |
| Combine the panels in a main window | README, Current Tasks, window shell |

The foundation delivery excludes implementation of these capabilities, model training or downloads, hosted services, databases, login, image publication and changes to personal documents. Management documentation was originally specified in Portuguese; the user replaced that language choice with English in an instruction received 2026-10-20 and applied 2026-10-21. The README remains in English, with targeted corrections.

## Success and evidence

Phase A success requires coherent instructions, profiles, skills, memory, decisions and review procedures, with recorded checks and independent review before branch publication. Human approval of the structure closes that phase.

Phase B converts each capability into observable `CA-NN.M` criteria covering success, failure and responsiveness. Phase D must demonstrate the complete local flow and record evidence for each criterion. This document does not declare any product criterion implemented; quantitative limits belong in the specifications.

## Data and constraints

New examples and tests use fictional data. Do not version secrets, personal documents, checkpoints or generated images. Do not read environment files or sensitive content to complete documentation. Local execution still requires care with names and script, log and image content; the foundation does not certify compliance with Brazil's LGPD.

## Risks

| Observed risk | Consequence | Response |
|---|---|---|
| README describes a more complete product than the interface files provide | Planning around unavailable functionality | Correct the description and keep the backlog explicit |
| Installation requirements differ | Environment is hard to reproduce | Evaluate versions and dependencies in Phase B |
| Some tests depend on a local service | Variable results or blocked execution | Separate isolated checks from integration evidence; never claim an unobserved pass |
| Auxiliary memory contains unreviewed decisions | Incorrect continuity | Promote durable decisions to reviewed documentation |

## Questions and recorded answers

1. What values, validation rules and limits should manual inputs have? Owner: product owner during Phase B, after a proposal grounded in the current flow.

   Answer recorded by the principal from explicit user choices on 2026-10-20: R-B.4 defines a global positive prompt combined with the scene description and a global negative prompt; R-B.7 defines a new random seed for each scene when the value is -1, or the same fixed seed for every scene; R-B.8 defines UTF-8 TXT scripts with timestamps and multiline descriptions. These decisions are reflected in [configuration specification](specs/01-configuration.md) and [execution specification](specs/02-execution.md). Other numerical limits and presentation choices remain subject to the corresponding specifications and ratifications; these answers do not imply approval of every input constraint.

2. How should the interface communicate unavailability, interruption and generation failures? Owner: product owner during Phase B.

   Answer recorded by the principal from explicit user choices on 2026-10-20: R-B.3 stops after completing and saving the current scene without a global server interrupt. R-B.6 stops the batch at its first failure, identifies the scene and cause, preserves saved files, and does not automatically resubmit or announce batch completion. R-B.5 places results in a selected folder with a unique batch subfolder, avoiding overwrites. See [execution](specs/02-execution.md), [interface feedback](specs/03-interface-feedback.md) and the [ratification record](ratifications.md). Wait limits and detailed presentation require their own decisions.

These questions did not block the foundation. Preserve them and their dated answers; record concrete remaining alternatives in [ratifications](ratifications.md).

## What needs to return to the source

No changes have been requested to the three external prompts. Local adaptations belong in ADR-0002. Approved product requirements must be reflected in the README and specifications without silently rewriting the historical origin.