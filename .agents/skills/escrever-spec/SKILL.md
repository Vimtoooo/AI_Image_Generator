---
name: escrever-spec
description: Escrever PRD, especificações e ADRs rastreáveis para requisitos deste gerador ComfyUI.
---

Leia fase e tarefa em `docs/estado.md` e `docs/tarefas.md`. Escreva somente em `docs/`,
sem modificar `docs/origem.md`. Não escreva specs de fase B enquanto A não for aprovada.
Para nova-spec, cite a seção do README ou decisão que origina cada regra; descreva
contexto, comportamento, limites, falhas e CA-NN.M em Dado/Quando/Então.
Um critério deve poder ser observado sozinho; não reutilize IDs aposentados.
Para novo-adr, registre contexto, opções, consequências e motivo de revisão.
Decisão aberta nasce proposta; não a marque aceita sem resposta do usuário.
Registre lacunas e blocos R-NN.M em `docs/ratificacoes.md`, com recomendação,
alternativas e consequências. Devolva dúvidas ao principal para perguntar.
Registre resposta datada abaixo da pergunta, preservando histórico e refletindo
a decisão na spec/ADR. Se mudar uma opção já escolhida, peça nova ratificação.
Mudanças necessárias fora de docs são entregues ao principal, não executadas aqui.
