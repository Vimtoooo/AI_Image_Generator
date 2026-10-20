# Configuração da gestão

Esta página descreve os artefatos da Fase A e seu uso. As decisões estão no [ADR-0002](../../adr/0002-metodo-codex.md); a fonte histórica está em [origem](../../origem.md).

## Recursos e memória

`AGENTS.md` orienta o principal e exige leitura explícita de `docs/estado.md` e `docs/tarefas.md` ao retomar. O estado resume fase, fontes, ponto de parada, próxima tarefa e impedimentos em aproximadamente 40 linhas. O quadro mantém o histórico de conclusão e evidências.

Os cinco perfis em `.codex/agents/` descrevem quando delegar, escopo de escrita, limites e formato de retorno de até 300 palavras. Modelos são herdados da sessão. A existência dos arquivos não prova que uma sessão os carregou; o principal verifica o mecanismo disponível e, quando necessário, transmite suas instruções ao delegar. Perfis não substituem as permissões do ambiente.

Anotações auxiliares ficam em `.codex/agent-memory/`, ignoradas pelo Git. São rascunhos, não fonte da verdade. Decisões que precisam sobreviver a uma sessão vão para documentos revisados. Não registrar segredos ou conteúdo pessoal nessa memória.

## Skills e procedimentos

As skills ficam em `.agents/skills/`: `gestao-sessao`, `escrever-spec`, `integrar-comfyui`, `desenvolver-interface` e `revisar-entrega`. O nome de um procedimento abaixo é uma convenção de trabalho, não uma declaração de comando nativo disponível na interface do Codex.

| Procedimento | Execução esperada |
|---|---|
| retomar | Ler estado e quadro, conferir Git e fontes, resumir fase e próxima tarefa autorizada |
| encerrar | Atualizar quadro e estado, registrar evidências e impedimentos, publicar somente após revisão |
| fase | Mostrar fase vigente, entregável, condição de saída e aprovação faltante |
| proxima-tarefa | Escolher tarefa da fase aberta, delimitar escopo, executar e submeter a verificação e revisão |
| nova-spec | Na Fase B, redigir comportamento e critérios com fontes e lacunas explícitas |
| novo-adr | Registrar decisão; quando aberta, propor alternativas e ratificações antes de consolidá-la |
| verificar | Executar checks pertinentes, separar resultados de infraestrutura, registrar comandos e saídas reais |
| revisar | Obter leitura independente do diff e relatar achados sem suavizar |
| explicar | Explicar o tema e sua evidência, sem mudar código |
| preparar-pr | Gerar descrição, preencher lacunas com evidência e publicar após verificação e revisão |
| conferir-metodo | Comparar hashes dos três arquivos autorizados, analisar mudanças e registrar impacto local |

O gerador `scripts/preparar_pr.py` produz uma descrição com as onze seções do método. Sua execução não publica nada. Campos sem evidência permanecem identificados como lacunas; a conclusão do teste ou da revisão não pode ser inferida do histórico Git. Consultar `python scripts/preparar_pr.py --help` para as opções implementadas.

## Rotina Git e revisão

Abrir branch de trabalho antes da primeira edição. Inventariar alterações locais e preparar arquivos por nome; não usar inclusão indiscriminada. Não descartar alterações anteriores para limpar a árvore. Após verificação, um agente diferente do autor revisa o diff a publicar. O principal confirma achados e limita a duas rodadas de correção; bloqueios remanescentes voltam ao responsável.

Commit, push da branch e abertura de PR estão autorizados pelo plano. Merge é exclusivo do usuário; agentes não executam push direto na `main` nem push forçado. Mudanças nas permissões não são consequência automática dessa autorização. Se uma ferramenta negar a ação, registrar o motivo e respeitar a restrição.

## Fronteiras e manutenção

Manter `documents/` intocada. Exemplos novos usam dados fictícios. Não ler segredos ou arquivos de ambiente, salvo o modelo público `.env.example`; não publicar checkpoints ou imagens geradas. `.gitignore` não retira arquivos já versionados e não controla leituras: a revisão da lista preparada é necessária.

Não há hook do Claude ativo por efeito desta configuração. Graphify é opcional e não foi instalado pela fundação; se houver proposta futura de uso, revisar exclusões antes de indexar e nunca ignorar fronteiras para gerar o mapa.

Documentação longa de implementação vai em `docs/codigo/<area>/`; comentários no código explicam somente intenção não evidente. Não remover documentação existente para satisfazer esse padrão sem preservar o conteúdo e justificar a mudança. O README recebe correções pontuais e permanece em seu idioma atual.
