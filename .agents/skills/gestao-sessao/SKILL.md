---
name: gestao-sessao
description: Retomar, encerrar e conduzir tarefas, verificações e publicação de PR neste repositório ComfyUI.
---

Leia `AGENTS.md`, `docs/estado.md` e `docs/tarefas.md` a partir da raiz.
Escolha somente o procedimento solicitado; os nomes abaixo não são slash commands.

- **retomar:** confira branch e status; resuma fase, ponto de parada, trabalho local,
  perguntas e próxima tarefa. Autorização já dada vale; não peça confirmação repetida.
- **encerrar:** atualize evidências no quadro e reescreva estado sem perder perguntas.
  Revise as mudanças; commit de estado separado do conteúdo. Publique branch e PR
  se fizerem parte do trabalho autorizado, sem merge.
- **fase:** informe critério de saída e o que falta. Avance somente com decisão humana.
- **proxima-tarefa:** escolha a primeira tarefa liberada da fase; leia fonte e aceite;
  delegue implementação delimitada, depois teste e revisão independente. Teto de duas rodadas.
- **verificar:** rode verificações pertinentes. Para gestão: `python -m unittest discover
  -s scripts -p "test_*.py"`. Não rode testes da aplicação que conectam ao ComfyUI
  como se fossem offline. Falha não relacionada deve ser registrada, não escondida.
- **revisar:** peça a outro agente diff e critérios; confira achados por arquivo/linha.
- **explicar:** explique o tema sem editar código, salvo solicitação adicional.
- **preparar-pr:** confira base e todos os commits incluídos; gere texto com
  `python scripts/preparar_pr.py --base origin/main`; complete lacunas com evidência,
  preserve as onze seções. Use arquivo temporário e `gh pr create --body-file`.
  Commits, push da branch e PR estão autorizados após testes/revisão; merge não.
- **conferir-metodo:** leia somente os três arquivos identificados em `docs/origem.md`,
  compare hashes, registre diferenças aplicáveis e revise antes de atualizar o registro.

`nova-spec` e `novo-adr` estão na skill `escrever-spec`. Não invente aprovação de fase.
Não inclua mudanças anteriores do usuário. Memória auxiliar em `.codex/agent-memory/`
é opcional e manual; transfira decisões verificadas para `docs/`.
