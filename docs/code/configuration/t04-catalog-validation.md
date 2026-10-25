# T04 catalog and parameter validation

Date: 2026-10-22. Primary-agent implementation, tests and review; no subagents.

`ComfyUIClient.get_catalog()` reads `/object_info` with finite 10/60-second
connect/read timeouts, checks HTTP status, closes the response, and returns a
detached immutable catalog. Unavailable or malformed metadata raises `CatalogError`.
The legacy sampler method now returns its extracted list. The owner's renamed
`get_available_samplers` remains, with an alias for `get_available_sampler_names`.
Existing legacy list APIs retain their contracts; the desktop uses the strict API.

`parse_catalog` validates standard-node choices and numeric bounds.
`validate_generation_parameters` checks checkpoint, sampler, scheduler, dimensions,
steps, CFG and seed before `PayloadManager.apply_parameters` updates a private
payload atomically. Empty/missing choices block generation without substitution.
Both integer and fractional CFG values are accepted; booleans and nonfinite
numbers are rejected. Seed -1 is a sentinel to resolve per scene in T07.

Evidence: **101 tests passed** across the explicit T02/T03/T04 test files using
Python 3.14.3, pytest 9.1.1 and the documented T02 temporary-directory wrapper.
Tests cover catalog failure, HTTP/JSON errors, response cleanup, metadata limits,
choice mismatches, immutable snapshots, valid boundary values and unchanged payloads
after invalid edits. Primary-agent scoped review and `git diff --check` passed.

Earlier owner changes in `client.py` were inspected and preserved: method rename,
exception documentation corrections and getter-section naming. They must remain
separately identified during publication; no previous changes were silently discarded.

The Graphify index was refreshed incrementally for two changed backend files:
154 nodes, 244 edges. Context7 supplied Requests timeout/error-handling documentation;
the earlier ComfyUI object_info documentation was reused. No image generation occurred.

Live catalog check on 2026-10-22: localhost:8188 refused connection. The owner-
authorized batch launcher was started hidden from its portable directory, but
the endpoint remained unavailable after bounded retries. Live catalog behavior
is not claimed as demonstrated; no generation was submitted.
