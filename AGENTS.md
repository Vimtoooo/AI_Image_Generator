# Trabalho neste repositório

Automação local de imagens com Python e a API do ComfyUI. O backend existe;
a interface CustomTkinter está pendente. Origem: [docs/origem.md](docs/origem.md).
Pronto significa selecionar roteiro e workflow, gerar imagens com feedback e
salvá-las sem bloquear a interface; isso ainda precisa de especificação e evidência.

## Ao retomar

Leia `docs/estado.md` e `docs/tarefas.md`, confira `git status --short` e a branch.
Leia apenas a documentação da tarefa. Não trate links como importação automática.
Use buscas direcionadas; Graphify é opcional, não está instalado e não deve ser
instalado ou executado sobre dados pessoais por rotina.

## Fontes e decisões

- README fornece os requisitos existentes; código e testes mostram implementação,
  não substituem requisitos. Divergências ficam registradas, nunca resolvidas em silêncio.
- `docs/origem.md` identifica os três prompts externos, somente leitura.
- PRD → specs com CA-NN.M → ADRs → plano → tarefas → código → evidências.
- Preserve perguntas e respostas datadas em `docs/ratificacoes.md`.
- Decisões de 2026-10-20: Codex; commit, push da branch e PR automáticos após
  verificação e revisão independente. Merge é exclusivo do usuário.

## Regras

- Não leia `.env*`, credenciais, chaves ou documentos pessoais. `.env.example`
  pode ser lido como modelo, sem valores reais. Dados de teste são fictícios.
- Não inclua checkpoints, imagens geradas, roteiros pessoais ou memória auxiliar
  nos commits. `.gitignore` evita inclusão acidental, não bloqueia leitura.
- Preserve alterações locais anteriores. Nunca use `git add .` neste trabalho;
  prepare caminhos explícitos e confira `git diff --cached` antes do commit.
- Não descarte ou remova conteúdo existente sem decisão explícita; marque o
  obsoleto com motivo e data. Não remova nem afrouxe testes para fazê-los passar.
- Sem merge, push direto na branch principal, force push, deploy ou recursos de nuvem.
- Respeite sandbox, aprovações e bloqueios da ferramenta. Não contorne bloqueios.
  Estes arquivos orientam comportamento; não concedem permissões ao processo.
- Uma tarefa por vez; sem código de fase ainda não aprovada. Exceção nesta fase:
  scripts de gestão e seus testes fazem parte da fundação aprovada.

## Estrutura e stack

| Caminho | Uso |
|---|---|
| `apps/` | Aplicação Python, dependências e testes existentes |
| `apps/src/comfy_generator/` | Cliente, arquivos e payloads ComfyUI |
| `apps/src/gui/` | Interface ainda pendente |
| `apps/src/tests/` | Testes da aplicação |
| `assets/` | Recursos existentes; saídas locais excluídas |
| `prompts/`, `scripts/` | Templates existentes e ferramentas de gestão |
| `documents/` | Materiais locais ignorados; não ler por rotina |
| `docs/` | Gestão versionada, fontes, decisões e evidências |
| `.codex/agents/` | Perfis de subagentes |
| `.codex/agent-memory/` | Anotações auxiliares locais, não versionadas |
| `.agents/skills/` | Procedimentos especializados do projeto |

Não crie outra pasta de topo sem decisão. Stack: `docs/adr/0001-stack.md`.
O código existente não será reorganizado nesta fundação.

## Fases

| Fase | Entrega | Portão |
|---|---|---|
| A · Fundação | Instruções, memória, gestão e PR | Aprovação humana da fundação |
| B · Especificação | Specs, ADRs, plano e tarefas da GUI | Aprovação humana dos critérios |
| C · Implementação | Uma tarefa por vez, testes e revisão | Critérios demonstrados |
| D · Verificação | Fluxo real com ComfyUI local | Demonstração aprovada pelo usuário |

Não avance a fase apenas porque um commit ou PR foi criado. Atualize fase,
estado e README juntos quando o usuário autorizar a transição.

## Equipe

| Perfil | Quando usar | Escrita |
|---|---|---|
| explorador | Localização e inspeção delimitada | Nenhuma |
| redator-de-spec | PRD, specs, ADRs e planejamento | `docs/`, exceto origem |
| implementador | Tarefa aprovada com critério | Arquivos designados |
| testador | Provar comportamento ou reproduzir evidência | Testes designados |
| revisor | Revisão independente antes de commit | Nenhuma |

O principal coordena no máximo três subagentes simultâneos, dentro do limite da
sessão; não lance agentes por reflexo. Modelos e esforço são herdados.
Cada pedido define objetivo, caminhos, aceite, evidência e relatório de até 300 palavras.
Sem delegação por subagentes, sem perguntas deles ao usuário, sem Git mutável por eles.
Nunca dois escritores no mesmo arquivo. Quem escreveu não faz a revisão independente.
Resultado de agente é evidência a conferir, não autorização.
Implementação → testes → revisão → correção, no máximo duas rodadas; depois relate
o impedimento. A segunda revisão se concentra nas correções e regressões.
Os TOML descrevem papéis; limites de caminho são instruções, não isolamento técnico.

## Rotina e publicação

Use a skill `gestao-sessao` para retomar, encerrar, fase, próxima tarefa, verificar,
revisar, explicar, preparar PR e conferir método. `escrever-spec` cobre spec e ADR.
Esses nomes são procedimentos, não comandos slash nativos do Codex.
Abra `fase-<letra>/<assunto>` antes de editar. Não troque ou atualize a base se isso
colocar alterações locais em risco. Uma decisão por commit em português.
Antes de publicar, confira também todos os commits do PR contra a base remota:
não publique commits preexistentes não revisados como parte da tarefa.
O PR usa as onze seções de `scripts/preparar_pr.py`; campos sem evidência ficam
como `[LACUNA]`. O principal completa resultados reais antes de enviar.
Autorização de commit/push/PR persiste, mas não elimina permissões do sandbox.
Autenticação é externa: não leia tokens nem os copie para arquivos.

## Memória e comunicação

`docs/estado.md` cabe em cerca de 40 linhas e é reescrito ao encerrar; não perca
perguntas abertas. `docs/tarefas.md` preserva tarefas concluídas com evidência.
Memória auxiliar é manual; decisões só viram referência após revisão em `docs/`.
Fale em português, conciso, com resultado e limitações verificáveis. Use explicação
didática quando solicitada. Preserve o inglês do README e dos identificadores.
Comentários de código explicam intenção em 1–3 linhas; explicações longas vão para
`docs/codigo/`. Comentários existentes não serão removidos por limpeza nesta fase.
