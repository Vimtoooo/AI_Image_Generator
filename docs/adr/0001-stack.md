# ADR-0001: preservar a stack existente na fundação

Data: 2026-10-20. Status: aceito no plano da fundação pelo responsável; registra preservação, não aprovação de novas versões.

## Contexto

O [README](../../README.md) descreve geração local por ComfyUI e uma interface planejada com CustomTkinter. O projeto Python já existe em `apps/`. A Fase A organiza o trabalho sem mudar a aplicação ou absorver alterações locais anteriores.

## Decisão

| Camada | Escolha nesta fase |
|---|---|
| Aplicação | Preservar Python e a estrutura `apps/src/` |
| Geração | Preservar integração com ComfyUI local e workflows em formato de API |
| Comunicação | Preservar dependências HTTP e WebSocket declaradas |
| Interface | Manter CustomTkinter como intenção do README; implementação pendente |
| Gestão | Documentos Markdown e gerador de descrição de PR em Python |
| Persistência e acesso | Não introduzir banco, login ou infraestrutura de nuvem |

Inspeção em 2026-10-20: `apps/pyproject.toml` declara Python `>=3.14`, enquanto o README informa `3.10+`; CustomTkinter não consta no manifesto nem em `apps/requirements.txt`. Os quatro módulos da interface estão vazios. Existem testes no estado local de trabalho; parte depende de rede. Esses fatos geram investigação na Fase B, não correções de dependências nesta fase.

## Alternativas e consequências

Migrar a stack ou adicionar serviços agora ampliaria o escopo sem requisito. Introduzir Node apenas para copiar o gerador do método adicionaria uma ferramenta desnecessária; Python atende a automação de gestão.

Preservar a stack reduz o risco de regressão e mantém o trabalho local. Aceita-se que a instalação e os testes completos da aplicação ainda não estejam validados pela fundação. A compatibilidade entre versão de Python, biblioteca de interface e ambiente local deve ser verificada antes da implementação.

## Quando revisar

Na Fase B, antes de aprovar o plano técnico, ou quando um requisito demonstrar necessidade de nova dependência. Mudanças de versão ou arquitetura devem ter evidência e decisão explícita, sem tratar este ADR como autorização para atualização automática.
