"""Test real Git collection using only temporary repositories."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import prepare_pr


class PreparePRTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "repo"
        self.repo.mkdir()
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Local Test")
        self.git("config", "user.email", "test@example.invalid")
        (self.repo / "old.txt").write_text("before", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-m", "Initial state")
        self.git("update-ref", "refs/remotes/origin/main", "HEAD")
        self.git("switch", "-c", "phase-a/foundation")
        (self.repo / "old.txt").unlink()
        (self.repo / "new.txt").write_text("after", encoding="utf-8")
        self.git("add", "-A")
        self.git("commit", "-m", "Document CA-01.1", "-m", "Also cites CA-02.3.")

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.repo), *args], check=True, capture_output=True)

    def cli(self, *args):
        return subprocess.run(
            [sys.executable, str(Path(prepare_pr.__file__).resolve()), "--repo", str(self.repo), *args],
            capture_output=True, encoding="utf-8", errors="replace",
        )

    def test_section_order_and_real_evidence(self):
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        text = result.stdout
        self.assertEqual([line[3:] for line in text.splitlines() if line.startswith("## ")], list(prepare_pr.SECTIONS))
        for snippet in ("phase-a/foundation", "new.txt", "old.txt", "Document CA-01.1", "CA-02.3", "[GAP]", "do not prove completion", "- [ ]", "Generated with Codex"):
            self.assertIn(snippet, text)
        self.assertNotIn("- [x]", text)
        self.assertEqual(self.git("status", "--porcelain").stdout, b"")

    def test_missing_base(self):
        result = self.cli("--base", "missing")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Git failed", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_no_commits_does_not_invent_evidence(self):
        result = self.cli("--base", "HEAD")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[GAP] No unique commits found.", result.stdout)
        self.assertNotIn("IDs cited in commits:", result.stdout)
        self.assertIn("No removals identified", result.stdout)

    def test_git_unavailable(self):
        with patch.object(prepare_pr.subprocess, "run", side_effect=FileNotFoundError("git")):
            with self.assertRaisesRegex(prepare_pr.PreparationError, "Could not execute Git"):
                prepare_pr.generate(self.repo, "origin/main")

    def test_non_git_directory(self):
        result = self.cli("--repo", self.temp.name)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Git failed", result.stderr)

    def test_internal_output_rejected(self):
        destination = self.repo / "description.md"
        result = self.cli("--output", str(destination))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("outside the repository", result.stderr)
        self.assertFalse(destination.exists())

    def test_external_output_and_summary(self):
        summary = Path(self.temp.name) / "summary.txt"
        summary.write_text("Organize review and memory.", encoding="utf-8")
        destination = Path(self.temp.name) / "pr.md"
        result = self.cli("--output", str(destination), "--summary", str(summary), "--title", "Organize the foundation")
        self.assertEqual(result.returncode, 0, result.stderr)
        text = destination.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# Organize the foundation\n"))
        self.assertIn("**Organize review and memory.**", text)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
