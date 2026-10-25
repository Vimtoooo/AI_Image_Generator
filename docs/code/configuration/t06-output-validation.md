# T06 - Safe output storage validation

Date: 2026-10-22. Phase C. Primary-agent implementation and review; no subagents.
Sources: implementation-plan T06; execution specification R-B.5, CA-02.13 and CA-02.14.

## Implemented

- `file_system.create_batch_directory` allocates an exclusive batch folder and
  verifies writes with a flushed probe. The runner must call it before submission (T07).
- Local names combine scene index, sanitized timestamp, image index and a restricted
  returned extension. Remote filenames/subfolders are HTTP parameters, never local paths.
- `write_chunks_atomic` writes an exclusive temporary file beside the target, checks
  nonempty content and supplied length, flushes and fsyncs, then publishes without
  replacement. Windows uses rename; POSIX uses an exclusive hard link. Collisions
  choose a suffix for batch output. Only the attempt's own temporary file is cleaned.
- `client.download_images` streams all selected descriptors, closes responses, uses
  finite HTTP timeouts and checks the shared deadline between chunks and before
  publication. Completed files remain available through `on_saved` if a later file fails.
- Legacy `download_image` keeps its signature, offline guard and boolean result;
  an existing destination now yields False instead of being overwritten.

## Evidence

Validated with Python 3.14.3 / Requests 2.34.2 from the T01 temporary environment.
Explicit offline suites: test_scene_parsing, test_workflow_mapping,
 test_catalog_validation, test_transport_protocol and test_output_storage.
Result: **146 passed in 3.23s** (25 output-storage tests). Used the fresh temporary
folder permissions wrapper documented in T02; no existing ACLs were changed.

Coverage includes exclusive folders, failed write probes, server path isolation,
collision races, preservation of existing temporary files, disk flush/publication
failures, empty/mismatched lengths, interrupted streams, expired deadlines,
response cleanup, all-image downloads and legacy compatibility. An ephemeral
loopback HTTP server verified actual Requests streaming and truncated Content-Length
handling: the complete first image survived and the incomplete second had no final file.
No ComfyUI server, GPU, model, personal script or real generation was involved.

## Primary-agent review

Confirmed: CA-02.13 and CA-02.14 at the storage/transport boundary. No blocking
findings. Existing application explanations remain; the legacy streaming description
is marked historical. Earlier owner changes and unrelated files were preserved.
`git diff --check` passed (line-ending warnings only). Git metadata remains read-only;
no commit, push or PR was created. Runner integration and pre-POST ordering belong to T07.

Deadline checks are cooperative around blocking reads and filesystem operations;
Requests read timeout is an inactivity timeout, not a hard wall-clock cancellation.
Unexpected compressed responses are rejected because Content-Length then describes
encoded bytes. Image decoding is not performed. POSIX publication was not runtime-tested
in this Windows session. Cleanup cannot guarantee deletion if the filesystem denies it;
errors are surfaced and no partial final image is published.

Context7 references reused: /python/cpython (non-replacing Windows rename semantics)
and /psf/requests (stream context cleanup, decoding, inactivity timeout). Graphify's
existing code-only backend index guided the bounded change and was refreshed afterward.
