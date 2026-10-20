# Produto: geração local de imagens

Status: fundação em revisão, 2026-10-20. Origem: [pedido aprovado](origem.md) e seções **Current Tasks** e **Future Roadmap** do [README](../README.md). Este PRD registra intenção; não substitui as especificações da Fase B.

## Problema e objetivo

Quem prepara imagens para roteiros precisa configurar arquivos e parâmetros, acompanhar a execução e identificar falhas sem conduzir manualmente cada geração. A automação existente oferece a base desse fluxo; a interface descrita nas pendências ainda precisa ser especificada e implementada.

O objetivo é permitir configurar a geração e acompanhar seu resultado em uma janela responsiva, usando os recursos locais do computador. Critério de pronto do produto: a pessoa seleciona os arquivos e o modelo, inicia a geração, acompanha progresso e mensagens e obtém as imagens correspondentes, mantendo a janela utilizável.

## Público e visibilidade

O papel previsto é o de operador local, responsável pelo roteiro, pela escolha do modelo e pelas imagens geradas. Ele vê a configuração da execução, seu andamento e seus erros. Não há requisito de compartilhamento, múltiplos perfis ou painel remoto.

## Escopo e fontes

| Capacidade | Fonte |
|---|---|
| Selecionar arquivos de roteiro e configuração da geração | README, Current Tasks, painel de configuração |
| Escolher entre os modelos disponíveis localmente | README, Current Tasks, lista de checkpoints |
| Informar ajustes manuais de prompt, proporção e semente | README, Current Tasks, entradas manuais |
| Ver mensagens e progresso durante a execução | README, Current Tasks, painel de logs |
| Interagir com a janela enquanto a geração ocorre | README, Current Tasks, processamento em segundo plano |
| Integrar os painéis em uma janela principal | README, Current Tasks, janela principal |

Não fazem parte desta entrega de fundação: implementação dessas capacidades, treinamento ou download de modelos, serviço hospedado, banco de dados, login, publicação de imagens e alteração de documentos pessoais. A documentação de gestão é em português; o README conserva seu idioma e conteúdo, com correções pontuais de estado.

## Sucesso e evidências

Na Fase A, sucesso significa ter instruções, perfis, skills, memória, decisões e rotina de revisão coerentes, com verificações registradas e revisão independente antes da publicação da branch. A aprovação humana da estrutura encerra a fase.

Para o produto, a Fase B deve converter cada capacidade da tabela em critérios observáveis `CA-NN.M`, cobrindo sucesso, falha e responsividade. A Fase D deve demonstrar o fluxo completo local e registrar evidência por critério. Nenhum critério do produto está declarado atendido por este documento; tempos e limites quantitativos serão definidos na especificação.

## Dados e restrições

Exemplos e testes novos usam dados fictícios. Não versionar segredos, documentos pessoais, checkpoints ou imagens geradas. Não ler arquivos de ambiente ou conteúdo sensível para completar a documentação. A execução local não elimina o cuidado com nomes e conteúdo de roteiros, logs e imagens; a fundação não é uma certificação de conformidade com a LGPD.

## Riscos

| Risco observado | Consequência | Resposta |
|---|---|---|
| README apresenta estado mais completo que os arquivos da interface | Planejamento baseado em funcionalidade inexistente | Corrigir a descrição e manter backlog explícito |
| Requisitos de instalação divergem | Ambiente difícil de reproduzir | Avaliar versões e dependências na Fase B |
| Parte dos testes depende de serviço local | Resultado variável ou execução bloqueada | Separar evidência isolada de integração, sem alegar aprovação não observada |
| Memória auxiliar contém decisões sem revisão | Continuidade incorreta | Promover decisões duráveis para documentação revisada |

## Perguntas abertas

1. Quais valores, validações e limites devem existir nas entradas manuais? Responsável: responsável pelo produto, durante a Fase B, após proposta fundamentada no fluxo atual.
2. Como a interface deve comunicar indisponibilidade, interrupção e falha de geração? Responsável: responsável pelo produto, durante a Fase B.

Essas questões não bloqueiam a fundação. Quando houver alternativas concretas, registrar os blocos em [ratificações](ratificacoes.md), mantendo as perguntas e acrescentando respostas datadas.

## O que precisa ir para a fonte

Não há alteração solicitada aos três prompts externos. Adaptações locais ficam no ADR-0002. Novos requisitos de produto devem voltar ao README e às especificações após aprovação, sem editar silenciosamente a origem histórica.
