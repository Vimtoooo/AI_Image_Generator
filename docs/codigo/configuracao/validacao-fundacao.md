# Evidências da fundação

Data: 2026-10-20. Escopo: gestão; não é validação da aplicação ou da GUI.

- `python -m unittest discover -s scripts -p test_*.py`: sete testes passaram.
  Os testes usam repositórios temporários, cobrem coleta Git, remoções, lacunas,
  Git ausente, base inválida, saída externa e recusa de saída dentro do projeto.
  O sandbox Windows bloqueou subdiretórios temporários; execução autorizada fora dele.
- As cinco skills passaram no `quick_validate.py` da skill-creator, usando
  `uv run --no-project --with pyyaml python <validador> <skill>`.
  O Python padrão não tinha PyYAML; não se alteraram dependências da aplicação.
- Cinco TOML conferidos com `tomllib`; AGENTS.md abaixo de 200 linhas.
- `git check-ignore` confirmou memória auxiliar, grafo opcional e checkpoints excluídos.
- Hashes SHA256 dos seis arquivos locais anteriores comparados com inventário temporário;
  todos preservados. A remoção anterior de test_file_system_errors.py permaneceu intacta.
- `git diff --check` não reportou erro de whitespace; houve avisos de conversão LF/CRLF.

## Limites

Revisão independente por revisor_fundacao em 2026-10-20: nenhum bloqueio material.
Corrigidas duplicação nova de exclusões e ambiguidade sobre push direto/forçado.
Estado/quadro atualizados com evidências; publicação isolada será conferida antes do push.

Os perfis não foram carregados em uma nova sessão Codex; o formato foi validado e
os papéis podem ser passados explicitamente ao delegar. Não se afirma isolamento de
permissões por perfil. Nenhum hook do Claude foi instalado.

Não executados: testes de aplicação que dependem de ComfyUI, GPU, geração de imagem,
interface desktop ou CI. Não há evidência de conclusão dos critérios futuros do produto.

## Publicação isolada

A main local inclui 620feea, ainda ausente da main remota 4dd9187, conferida com
`git ls-remote`. A publicação usará worktree temporário baseado em origin/main e
receberá somente commits da fundação, preservando a árvore original e o commit anterior.
