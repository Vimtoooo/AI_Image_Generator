Fase: A · Fundação
Fonte conferida até: README em 620feea e prompts com hashes em docs/origem.md (2026-10-20).

## Onde paramos
- Fundação validada; revisão independente sem bloqueio material, publicação em andamento.
- Branch de trabalho: fase-a/fundacao; GUI não implementada nesta fase.
- GitHub autenticado fora do sandbox; acesso ao keyring falhou dentro dele.

## Próxima tarefa
- Testes de gestão: 7 passaram; 5 skills e 5 perfis validados.
- Publicar somente a fundação em fase-a/fundacao-codex, baseada na main remota.
- Após aprovação humana e merge, abrir a fase B e especificar pendências do README.

## Decisões
- Codex; cinco papéis, cinco skills; memória durável em docs/.
- Commit, push da branch e PR autorizados após revisão; merge humano.
- Não modificar aplicação ou trabalho local anterior nesta fundação.

## Trabalho anterior preservado
- Modificados: client.py, gui/__init__.py, main.py em apps/src/.
- Removido localmente: apps/src/tests/test_file_system_errors.py.
- Novos locais: apps/src/tests/test_client.py e test_file_system.py.
- Novo local: assets/wireframes/Comfy_Generator-Completed-Dark.svg.
- Commit local 620feea não está em origin/main (4dd9187); excluir do PR da fundação.

## Pendências e perguntas
- Aprovação humana da fundação e merge ainda pendentes.
- Fase B: compatibilidade Python, dependência GUI e critérios das entradas manuais.
- Testes de aplicação e fluxo real ComfyUI não executados nesta fase.
- Graphify não instalado; perfis precisam de nova sessão para comprovar descoberta.
