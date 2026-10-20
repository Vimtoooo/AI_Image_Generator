---
name: integrar-comfyui
description: Implementar ou testar integração Python com workflows, HTTP e WebSocket do ComfyUI neste projeto.
---

Leia o critério aprovado antes de alterar `apps/src/comfy_generator/` ou a orquestração.
Preserve APIs existentes salvo decisão explícita. Não troque modelos ou workflows
pessoais e não leia `.env` para descobrir configuração.
Considere cópias independentes de payload por frame, identificação da execução,
timeouts, erros do servidor, encerramento do WebSocket e resultado do download.
Não suponha que evento de nó equivale a conclusão de toda a execução.
Isole rede nos testes unitários com mocks e arquivos temporários; integração real
deve ser identificada e autorizada no escopo, pois pode usar GPU e gerar arquivos.
Não marque critério fechado com teste sem assertiva ou que dependa silenciosamente
de servidor local. Mantenha evidência e limitações no quadro.
