# Ratificações

0 abertas · 2 fechadas em 2026-10-20.

As duas decisões abaixo foram perguntadas durante o planejamento, antes da criação dos arquivos. O registro é retrospectivo e fiel às respostas; a execução do plano foi aprovada em seguida. Questões futuras do PRD dependem da proposta da Fase B.

## R-A2.1 · Ferramenta de agentes

**Status:** fechada em 2026-10-20. **Onde:** ADR-0002. **Depende:** nada. **Responde:** responsável pelo repositório.

**Contexto:** os prompts usam Claude Code; esta sessão usa Codex.

- a) Codex (recomendado): adaptar instruções e recursos ao ambiente atual.
- b) Codex e Claude Code: manter base comum e configurações para ambos.
- Outra: escreva.

**Resposta:** a), Codex. **Registrado em:** 2026-10-20 pelo agente principal, com resposta explícita do responsável na ferramenta de perguntas. **Refletido em:** ADR-0002, perfis e skills.

## R-A2.2 · Autonomia Git

**Status:** fechada em 2026-10-20. **Onde:** ADR-0002. **Depende:** revisão independente e verificações. **Responde:** responsável pelo repositório.

**Contexto:** os prompts divergem entre proibir publicação e permitir autonomia após revisão.

- a) Commit sob aprovação (recomendação apresentada): publicação pelo responsável.
- b) Commit automático: push e PR pelo responsável.
- c) Commit, push e PR automáticos após revisão; merge e operações destrutivas pelo responsável.
- Outra: escreva.

**Resposta:** texto livre: “Eu quero que os comandos de git commit, push e PR sejam automáticos, mas deixa a merge para mim fazer.” **Registrado em:** 2026-10-20 pelo agente principal. Lastro: instrução explícita e posterior aprovação do plano; não presumir autorização de merge ou force push. **Refletido em:** ADR-0002 e AGENTS.md.

## Procedimento

Antes de perguntar uma decisão de spec, ADR ou plano técnico, registrar contexto, alternativas reais e consequência de cada uma. Usar `R-NN.M` para spec, `R-A<N>.M` para ADR e `R-PT.M` para plano técnico. Subagentes devolvem dúvidas ao principal; somente ele pergunta ao responsável.

Cada bloco contém: **Status** (aberta ou fechada com data), **Onde**, **Depende**, **Responde**, **Contexto**, opções `a)` recomendada, `b)` e, quando útil, `c)`, além de “Outra: escreva”. Ao concluir, acrescentar **Resposta**, **Registrado em** (data e papel do autor), lastro da decisão e referência à spec ou ADR atualizado.

Pergunta fechada não se apaga. Dúvida nascida da revisão entra antes da pergunta, em subseção datada e com sufixo `b`, `c` etc. Se uma opção mudar de sentido depois de escolhida, confirmar novamente e registrar a confirmação. Não transformar achado técnico verificável em pergunta de preferência.

Usar a ferramenta de pergunta quando estiver disponível e for aplicável; respeitar seu limite de perguntas. Na ausência, perguntar em texto curto. Decisões já autorizadas não exigem nova aprovação. Mudanças decorrentes fora de `docs/` são realizadas pelo principal e entram no mesmo ciclo de revisão.
