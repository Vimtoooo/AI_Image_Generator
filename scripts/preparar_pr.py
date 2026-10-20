"""Prepara uma descrição de PR com evidências locais, sem publicar ou alterar Git."""

import argparse
import re
import subprocess
import sys
from pathlib import Path


SECOES = (
    "🧭 O que muda",
    "❓ Por quê",
    "⚙️ Como funciona",
    "🧾 Commits",
    "✅ Critérios fechados",
    "📁 Arquivos",
    "🗑️ Remoções (regra 7)",
    "🔎 Verificação",
    "🛡️ Checagem de fronteira",
    "⏳ O que não foi verificado / perguntas",
    "🙋 O que depende de você",
)


class ErroPreparacao(Exception):
    """Falha esperada na coleta ou na saída."""


def git(repo, *args):
    try:
        resultado = subprocess.run(
            ["git", "--no-optional-locks", "-C", str(repo), *args],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError as exc:
        raise ErroPreparacao(f"Não foi possível executar Git: {exc}") from exc
    if resultado.returncode:
        detalhe = resultado.stderr.strip() or resultado.stdout.strip()
        raise ErroPreparacao(f"Git falhou ({' '.join(args)}): {detalhe}")
    return resultado.stdout.rstrip("\r\n")


def gerar(repo, base, titulo=None, resumo=None):
    raiz = Path(git(repo, "rev-parse", "--show-toplevel")).resolve()
    # Resolver primeiro impede que uma referência fornecida seja tratada como opção.
    revisao = git(raiz, "rev-parse", "--verify", "--end-of-options", f"{base}^{{commit}}")
    git(raiz, "rev-parse", "--verify", "HEAD^{commit}")
    branch = git(raiz, "symbolic-ref", "--short", "-q", "HEAD")
    commits = git(raiz, "log", "--format=%h %s", f"{revisao}..HEAD", "--")
    mensagens = git(raiz, "log", "--format=%B", f"{revisao}..HEAD", "--")
    diff = git(raiz, "diff", "--no-ext-diff", "--name-status", "--no-renames", f"{revisao}...HEAD", "--")
    estado = git(raiz, "status", "--porcelain")
    removidos = [linha[2:] for linha in diff.splitlines() if linha.startswith("D\t")]
    criterios = sorted(set(re.findall(r"\bCA-\d{2}\.\d+\b", mensagens)))
    titulo = " ".join((titulo or "Preparar alterações para revisão").split())
    resumo = resumo.strip() if resumo else "[LACUNA] Descrever o problema e o comportamento resultante."
    conteudos = (
        f"{resumo}\n\nBranch: `{branch}`. Base: `{base}` (`{revisao[:12]}`).\n"
        "A coleta inclui somente commits e diferenças até HEAD.",
        "[LACUNA] Relacionar a mudança ao requisito ou problema que a motivou.",
        "[LACUNA] Explicar o comportamento e as decisões relevantes para revisão.",
        "\n".join(f"- {linha}" for linha in commits.splitlines()) or "[LACUNA] Nenhum commit exclusivo encontrado.",
        ("IDs citados nos commits: " + ", ".join(f"`{item}`" for item in criterios) + ".\n\n" if criterios else "")
        + "[LACUNA] Associar cada critério à evidência de aceite. Citações em commits não comprovam conclusão.",
        "\n".join(f"- `{linha}`" for linha in diff.splitlines()) or "Nenhuma diferença de arquivo em relação à base.",
        ("\n".join(f"- `{item}` — [LACUNA] Justificar a remoção e comprovar a regra 7." for item in removidos)
         if removidos else "Nenhuma remoção identificada no diff."),
        "[LACUNA] Registrar comandos executados, resultados e evidências. O gerador não executa testes.",
        "[LACUNA] Registrar revisão independente, escopo, segredos e preservação do trabalho local.\n\n"
        + ("Há alterações locais fora da coleta; conferir antes de publicar." if estado else "O Git não reportou alterações locais na coleta."),
        "[LACUNA] Registrar limitações, dependências e perguntas ainda abertas.",
        "- [ ] Revisar as lacunas e as evidências de aceite.\n- [ ] Aprovar a fase e realizar o merge quando apropriado.",
    )
    texto = f"# {titulo}\n\n**{' '.join(resumo.split())}**\n\n"
    texto += "\n\n".join(f"## {secao}\n\n{conteudo}" for secao, conteudo in zip(SECOES, conteudos))
    return raiz, texto + "\n\n---\nGerado com Codex.\n"


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--base", default="origin/main")
    parser.add_argument("--titulo")
    parser.add_argument("--resumo", type=Path, help="Arquivo UTF-8 com resumo humano")
    parser.add_argument("--saida", type=Path, help="Arquivo fora do repositório; padrão: stdout UTF-8")
    args = parser.parse_args(argv)
    try:
        resumo = args.resumo.read_text(encoding="utf-8") if args.resumo else None
        raiz, texto = gerar(args.repo, args.base, args.titulo, resumo)
        if args.saida:
            destino = args.saida.resolve()
            if destino == raiz or raiz in destino.parents:
                raise ErroPreparacao("--saida deve estar fora do repositório.")
            destino.write_text(texto, encoding="utf-8")
        else:
            sys.stdout.write(texto)
    except (ErroPreparacao, OSError, UnicodeError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
