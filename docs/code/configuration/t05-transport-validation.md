# T05 correlated transport and history confirmation

Date: 2026-10-22. Primary-agent implementation and scoped review completed.

`generate_images` opens WebSocket before a single POST, emits only correlated
progress, and confirms successful history before returning every image from the
mapped SaveImage node. Node-level `executed` events cannot complete a scene.
The optional submission-boundary callback supports the synchronized Stop control
to be implemented in T07; no network I/O occurs inside that callback.

WebSocket loss after prompt ID receipt falls back to history polling every two
seconds. Lost POST responses report an unknown submission result without retry.
Execution errors/interruption, missing images and invalid history fail explicitly.
Failed history with `completed=false` is handled immediately. Deadlines use an
injectable monotonic clock; HTTP timeouts are capped at 10/60 seconds and remaining
time, WebSocket waits at one second and remaining time. Cleanup closes responses
and sockets. No global interrupt request is made.

The legacy `queue_workflow` retains its prompt-ID return with finite requests;
`track_generation_progress` retains its first-image-dictionary return through a
history-confirming adapter. Its former WebSocket description is explicitly marked
historical. Existing owner edits in client.py remain present.

Validation:

- Combined T02-T05 offline suite: **120 tests passed** before adding the loopback case.
- Final transport suite: **20 tests passed**, including the added real HTTP/WS
  loopback-server test. Across all four files, 121 distinct tests have passed.
- The loopback test performs a WebSocket handshake before POST, deliberately drops
  that socket and confirms recovery through HTTP history with exactly one POST.
- Fake-clock tests cover deadline expiry, unrelated/malformed events, known/unknown
  submission failures, cleanup, cached output, missing descriptors and Stop before POST.
- Primary-agent review found no blockers in the scoped transport changes.

No real ComfyUI generation was submitted. Scene storage remains T06, full Stop
synchronization and counters T07, and real local generation acceptance Phase D.
