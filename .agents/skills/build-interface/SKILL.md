---
name: build-interface
description: Implement the generator's CustomTkinter desktop interface after its criteria are approved.
---

Read the spec and the existing apps/src/gui/ and apps/src/main.py integration points.
The four GUI modules were empty at foundation time; do not assume behavior exists.
Separate configuration, feedback, worker execution and the main window.
Network calls and generation waits must not block the GUI event loop.
Workers publish data/events through a queue; the UI thread updates widgets through
scheduled callbacks. Handle failures and terminal states.
Do not add cancellation, persistence or other behavior absent from approved specs.
Use a designated wireframe as visual guidance, never as the authority for product rules.
Check declared dependencies and Python compatibility before introducing CustomTkinter.
Test without GPU where possible and distinguish actual visual/integration evidence.
