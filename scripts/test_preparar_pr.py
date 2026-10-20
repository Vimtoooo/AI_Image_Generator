"""Testes reais de coleta Git, usando somente repositórios temporários."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import preparar_pr


class PrepararPRTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "repo"
        self.repo.mkdir()
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Teste Local")
        self.git("config", "user.email", "teste@example.invalid")
        (self.repo / "antigo.txt").write_text("antes", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-m", "Estado inicial")
        self.git("update-ref", "refs/remotes/origin/main", "HEAD")
        self.git("switch", "-c", "fase-a/fundacao")
        (self.repo / "antigo.txt").unlink()
        (self.repo / "novo.txt").write_text("depois", encoding="utf-8")
        self.git("add", "-A")
        self.git("commit", "-m", "Documentar CA-01.1", "-m", "Também cita CA-02.3.")

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.repo), *args], check=True, capture_output=True)

    def cli(self, *args):
        return subprocess.run(
            [sys.executable, str(Path(preparar_pr.__file__).resolve()), "--repo", str(self.repo), *args],
            capture_output=True, encoding="utf-8", errors="replace",
        )

    def test_ordem_e_evidencias_reais(self):
        resultado = self.cli()
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        texto = resultado.stdout
        self.assertEqual([linha[3:] for linha in texto.splitlines() if linha.startswith("## ")], list(preparar_pr.SECOES))
        for trecho in ("fase-a/fundacao", "novo.txt", "antigo.txt", "Documentar CA-01.1", "CA-02.3", "[LACUNA]", "não comprovam conclusão", "- [ ]", "Gerado com Codex"):
            self.assertIn(trecho, texto)
        self.assertNotIn("- [x]", texto)
        self.assertEqual(self.git("status", "--porcelain").stdout, b"")

    def test_base_ausente(self):
        resultado = self.cli("--base", "inexistente")
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("Git falhou", resultado.stderr)
        self.assertEqual(resultado.stdout, "")

    def test_sem_commits_nao_inventa_evidencias(self):
        resultado = self.cli("--base", "HEAD")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("[LACUNA] Nenhum commit exclusivo encontrado.", resultado.stdout)
        self.assertNotIn("IDs citados nos commits:", resultado.stdout)
        self.assertIn("Nenhuma remoção identificada", resultado.stdout)

    def test_git_indisponivel(self):
        with patch.object(preparar_pr.subprocess, "run", side_effect=FileNotFoundError("git")):
            with self.assertRaisesRegex(preparar_pr.ErroPreparacao, "Não foi possível executar Git"):
                preparar_pr.gerar(self.repo, "origin/main")

    def test_diretorio_sem_git(self):
        resultado = self.cli("--repo", self.temp.name)
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("Git falhou", resultado.stderr)

    def test_saida_interna_recusada(self):
        destino = self.repo / "descricao.md"
        resultado = self.cli("--saida", str(destino))
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("fora do repositório", resultado.stderr)
        self.assertFalse(destino.exists())

    def test_saida_externa_e_resumo(self):
        resumo = Path(self.temp.name) / "resumo.txt"
        resumo.write_text("Organiza a revisão e a memória.", encoding="utf-8")
        destino = Path(self.temp.name) / "pr.md"
        resultado = self.cli("--saida", str(destino), "--resumo", str(resumo), "--titulo", "Organizar a fundação")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        texto = destino.read_text(encoding="utf-8")
        self.assertTrue(texto.startswith("# Organizar a fundação\n"))
        self.assertIn("**Organiza a revisão e a memória.**", texto)
        self.assertEqual(resultado.stdout, "")


if __name__ == "__main__":
    unittest.main()
