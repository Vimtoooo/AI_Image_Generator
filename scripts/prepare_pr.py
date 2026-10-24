"""Prepare a PR description using local evidence without publishing or changing Git."""

import argparse
import re
import subprocess
import sys
from pathlib import Path


SECTIONS = (
    "🧭 What changes",
    "❓ Why",
    "⚙️ How it works",
    "🧾 Commits",
    "✅ Acceptance criteria",
    "📁 Files",
    "🗑️ Removals",
    "🔎 Verification",
    "🛡️ Scope and data checks",
    "⏳ Limitations and questions",
    "🙋 What needs your action",
)


class PreparationError(Exception):
    """Expected collection or output failure."""


def git(repo, *args):
    try:
        result = subprocess.run(
            ["git", "--no-optional-locks", "-C", str(repo), *args],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError as exc:
        raise PreparationError(f"Could not execute Git: {exc}") from exc
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise PreparationError(f"Git failed ({' '.join(args)}): {detail}")
    return result.stdout.rstrip("\r\n")


def generate(repo, base, title=None, summary=None):
    root = Path(git(repo, "rev-parse", "--show-toplevel")).resolve()
    # Resolve first so a supplied reference cannot be interpreted as an option.
    revision = git(root, "rev-parse", "--verify", "--end-of-options", f"{base}^{{commit}}")
    git(root, "rev-parse", "--verify", "HEAD^{commit}")
    branch = git(root, "symbolic-ref", "--short", "-q", "HEAD")
    commits = git(root, "log", "--format=%h %s", f"{revision}..HEAD", "--")
    messages = git(root, "log", "--format=%B", f"{revision}..HEAD", "--")
    diff = git(root, "diff", "--no-ext-diff", "--name-status", "--no-renames", f"{revision}...HEAD", "--")
    status = git(root, "status", "--porcelain")
    removed = [line[2:] for line in diff.splitlines() if line.startswith("D\t")]
    criteria = sorted(set(re.findall(r"\bCA-\d{2}\.\d+\b", messages)))
    title = " ".join((title or "Prepare changes for review").split())
    summary = summary.strip() if summary else "[GAP] Describe the problem and resulting behavior."
    contents = (
        f"{summary}\n\nBranch: `{branch}`. Base: `{base}` (`{revision[:12]}`).\n"
        "Collection includes only commits and differences through HEAD.",
        "[GAP] Link the change to its motivating requirement or problem.",
        "[GAP] Explain the behavior and decisions relevant to review.",
        "\n".join(f"- {line}" for line in commits.splitlines()) or "[GAP] No unique commits found.",
        ("IDs cited in commits: " + ", ".join(f"`{item}`" for item in criteria) + ".\n\n" if criteria else "")
        + "[GAP] Link each criterion to acceptance evidence. Commit citations do not prove completion.",
        "\n".join(f"- `{line}`" for line in diff.splitlines()) or "No file differences from the base.",
        ("\n".join(f"- `{item}` — [GAP] Justify the removal and document compliance with preservation rule 7." for item in removed)
         if removed else "No removals identified in the diff."),
        "[GAP] Record executed commands, results, and evidence. The generator does not run tests.",
        "[GAP] Record primary-agent review, scope, secrets checks, and preservation of local work.\n\n"
        + ("Local changes are excluded from collection; review them before publishing." if status else "Git reported no local changes during collection."),
        "[GAP] Record limitations, dependencies, and open questions.",
        "- [ ] Review gaps and acceptance evidence.\n- [ ] Approve the phase and merge when appropriate.",
    )
    text = f"# {title}\n\n**{' '.join(summary.split())}**\n\n"
    text += "\n\n".join(f"## {section}\n\n{content}" for section, content in zip(SECTIONS, contents))
    return root, text + "\n\n---\nGenerated with Codex.\n"


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--base", default="origin/main")
    parser.add_argument("--title")
    parser.add_argument("--summary", type=Path, help="UTF-8 file containing a human-written summary")
    parser.add_argument("--output", type=Path, help="File outside the repository; default: UTF-8 stdout")
    args = parser.parse_args(argv)
    try:
        summary = args.summary.read_text(encoding="utf-8") if args.summary else None
        root, text = generate(args.repo, args.base, args.title, summary)
        if args.output:
            destination = args.output.resolve()
            if destination == root or root in destination.parents:
                raise PreparationError("--output must be outside the repository.")
            destination.write_text(text, encoding="utf-8")
        else:
            sys.stdout.write(text)
    except (PreparationError, OSError, UnicodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
