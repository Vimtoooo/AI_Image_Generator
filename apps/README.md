# Desktop application environment

Use Python 3.14.x. ComfyUI runs separately in its own environment.

From this directory, run `uv sync --locked` to install the locked runtime and
development dependencies. Use `uv sync --locked --no-dev` for runtime only.
Alternatively, in a Python 3.14 virtual environment, run
`python -m pip install --require-hashes -r requirements.txt` for runtime only.

After changing dependencies, run `uv lock`, then regenerate runtime requirements:

```powershell
uv export --locked --no-dev --no-emit-project --format requirements-txt --output-file requirements.txt
```

See the [project README](../README.md) for application setup and current status.
The GUI is still under implementation; installing CustomTkinter does not complete it.
