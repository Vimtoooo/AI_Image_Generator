---
name: integrate-comfyui
description: Implement or test the Python workflow, HTTP and WebSocket integration with ComfyUI.
---

Read the approved criterion before changing apps/src/comfy_generator/ or orchestration.
Preserve public APIs unless a decision explicitly changes them. Do not replace personal
models/workflows or read .env to discover settings.
Use an independent payload per scene, execution identifiers, finite waits, server errors,
socket cleanup and verified download results. A node event is not whole-prompt completion.
Mock network and use temporary files in unit tests. Real integration must be identified
and authorized in the task scope because it can use GPU and create image files.
Do not close a criterion with an assertion-free test or an undeclared local-server dependency.
Record evidence and limits in the task board.
