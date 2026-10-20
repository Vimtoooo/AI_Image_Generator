# Origem da fundação

Registro de 2026-10-20. Este documento preserva a origem do trabalho; alterações de decisão devem ser registradas em ADR, sem reescrever o pedido histórico.

## Pedido e autorização

O responsável apresentou este repositório como uma automação de geração local de imagens com ComfyUI e modelos `.safetensors`. Pediu a leitura dos três prompts em `../../IA/Prompts`, a organização dos recursos e da memória para subagentes e, depois, o atendimento dos requisitos pendentes do README.

Na mesma sessão, aprovou a execução do plano **Fundação de trabalho do repositório ComfyUI** com “Implement the plan”. O plano autoriza a Fase A, a adaptação para Codex e commit, push da branch e abertura de PR após verificação e revisão independente. Merge continua humano. As fases seguintes dependem de aprovação dos respectivos entregáveis.

## Fontes conferidas

| Fonte | Papel | Referência em 2026-10-20 |
|---|---|---|
| `../README.md` | Capacidades e pendências do produto | Base Git `620feea`; inspeção também considera alterações locais, sem atribuí-las à fundação |
| `../../IA/Prompts/ESTRUTURA.md` | Molde de artefatos | SHA256 `E827F899154BC7092FBB8E4301AFD9534669D0DF8A3AB4AC5923F5B2AA58B180` |
| `../../IA/Prompts/NORMAS.md` | Gestão, revisão e memória | SHA256 `0AD936FEADE151C5A48184BFA31B82E2F48612273CDB270D63F2F543AF622970` |
| `../../IA/Prompts/PROMPT.md` | Sequência de implantação do método | SHA256 `C77CC1547F665387C292606CE11496188350AF32DA7A7E12D9E20E72215B7BA4` |

Os caminhos da pasta externa são relativos à raiz do repositório, não a este arquivo. A leitura autorizada abrange somente os três arquivos nomeados; não autoriza varrer pastas vizinhas. Os hashes permitem detectar mudança da fonte sem depender de ela ser um repositório Git. Não há cópia integral desses documentos nem de conteúdos pessoais neste repositório.

## Precedência e limites

O pedido e o plano aprovados orientam a adaptação dos exemplos dos prompts, originalmente voltados ao Claude Code e a outro domínio. As escolhas locais estão no [ADR-0002](adr/0002-metodo-codex.md). Instruções e permissões do ambiente continuam vigentes. Nenhuma aprovação do plano substitui uma restrição técnica da sessão.

`docs/` contém gestão versionada; `documents/` permanece intocada. A fundação não autoriza implementar a interface, modificar o backend, instalar Graphify ou criar banco, login e infraestrutura de nuvem.
