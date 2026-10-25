# T02 script parsing and immutable contracts

Date: 2026-10-22. Status: 32 targeted tests passed; independent review passed.

The reviewer independently reran 27 read-only tests successfully, excluding five
filesystem/snapshot cases covered by the implementer's full run. No blockers found.

Scope: `models.py`, pure parsing in `formatting_utils.py`, script reading in
`file_system.py`, and isolated `test_scene_parsing.py` tests.

The intended behavior follows CA-01.2, CA-01.3 and the file-error portion of
CA-01.18: UTF-8/BOM input, timestamps at the beginning of a line, multiline
descriptions, retained scene order and duplicate timestamps, and physical line
numbers for invalid input. File failures must propagate without replacing state.
The GUI's last-valid-selection behavior remains for T08/T12.

Legacy `load_video_script` and `format_timestamp_line` return shapes are retained
through adapters. Prompt composition belongs to T03.

Tests use fictional temporary files and the validated T01 environment. They do not
read personal scripts or connect to ComfyUI. No product criterion is declared
fully demonstrated until the corresponding integration and UI evidence exists.

Preservation check on 2026-10-22: all six previously recorded user-file SHA-256
hashes match, and the previous test deletion remains unchanged.

## Executed tests

Python 3.14.3 / pytest 9.1.1: **32 passed**, using the validated T01 environment.
Normal pytest failed when its new mode-0700 directories were inaccessible in this
Windows sandbox. The successful run used the following process-local wrapper from
`apps/`; production code and test assertions were unchanged. Only creation modes
for new test directories changed; no existing directory permissions were modified.

```python
import tempfile, uuid
from pathlib import Path
import pytest

original_mkdir = Path.mkdir
def inherited_mkdir(self, mode=0o777, parents=False, exist_ok=False):
    return original_mkdir(self, mode=0o755 if mode == 0o700 else mode,
                          parents=parents, exist_ok=exist_ok)
Path.mkdir = inherited_mkdir
root = Path(tempfile.gettempdir()) / ("comfy-t02-" + uuid.uuid4().hex)
raise SystemExit(pytest.main([
    "src/tests/test_scene_parsing.py", "-p", "no:cacheprovider",
    "--basetemp", str(root),
]))
```
