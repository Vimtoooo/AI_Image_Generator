# ADR-0002: adaptar o método de gestão para Codex

Data: 2026-10-20. Status: aceito pelo responsável mediante aprovação do plano de fundação. Origem e hashes: [registro de origem](../origem.md).

## Contexto

Os três prompts fornecem um método de especificação, revisão, memória e publicação. Seus exemplos usam Claude Code, outro domínio e fases de banco e servidor que não correspondem a esta aplicação local. Copiá-los literalmente produziria controles inexistentes e trabalho sem requisito.

## Decisão

| Tema | Adaptação aprovada |
|---|---|
| Instruções do projeto | `AGENTS.md`, até 200 linhas, com leitura explícita de estado e tarefas |
| Perfis | Cinco arquivos `.codex/agents/*.toml`: explorador, redator, implementador, testador e revisor; modelos herdados da sessão |
| Procedimentos | Cinco skills em `.agents/skills/`, incluindo os onze procedimentos do método; não são comandos nativos de barra |
| Memória | `docs/estado.md` e `docs/tarefas.md` versionados; `.codex/agent-memory/` auxiliar ignorada |
| Equipe | Principal coordena até três subagentes simultâneos, com escopos sem escrita concorrente; subagentes não delegam nem publicam |
| Revisão | Autor e revisor diferentes; máximo de duas rodadas de correção, depois reportar impedimento |
| Git | Commit, push da branch e PR automáticos após verificações e revisão; merge humano, sem push direto na `main` ou push forçado |
| Documentos | Gestão em `docs/`, português; `documents/` intocada; README mantém seu idioma |
| Fases | A: fundação; B: especificação; C: implementação; D: verificação local |
| Ferramentas | Gerador de PR em Python; Graphify opcional, sem instalação nesta entrega |

## Sustentação e limites

Permissões e sandbox são os mecanismos executados pelo ambiente. Markdown, TOML e limites escritos dos papéis orientam agentes, mas não constituem isolamento de arquivos, bloqueio de shell ou garantia de obediência. `.gitignore` reduz inclusão acidental e não protege arquivos já rastreados nem impede leitura.

Não copiar `settings.json`, hooks `PreToolUse`, campos de permissões ou comandos exclusivos do Claude como se fossem controles ativos do Codex. Não alterar permissões globais nem contornar negativa de ferramenta. Caso a sessão não carregue perfis locais automaticamente, o principal deve transmitir explicitamente o papel e os limites no pedido de delegação; isso continua sendo uma instrução, não uma barreira técnica.

O principal confere o diff e a lista preparada para commit, preservando alterações anteriores. Segredos, documentos pessoais, checkpoints e imagens geradas não entram na publicação. Bloqueios de autenticação ou permissão são registrados, sem alegar publicação concluída.

## Alternativas descartadas

Copiar `.claude/` literalmente criaria expectativas falsas de funcionamento. Instalar Graphify seria trabalho adicional opcional. Introduzir fases de banco e login desviaria do produto. Manter proibição absoluta de push contrariaria a aprovação explícita do plano e a revisão de autonomia registrada nas normas.

## Consequências e revisão

O método conserva rastreabilidade e revisão com artefatos compatíveis com a tarefa. Perde-se a equivalência literal com hooks e menus do ambiente original. As consequências fora de `docs/` são aplicadas pelo principal em `AGENTS.md`, perfis, skills, exclusões e gerador; todas passam pela revisão da fundação.

Revisar quando houver mudança de capacidades do Codex, permissões, tamanho da equipe ou necessidade de controles executáveis adicionais. A aprovação deste ADR não aprova automaticamente os entregáveis finais nem abre a Fase B.
