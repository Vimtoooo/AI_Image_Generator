---
name: desenvolver-interface
description: Implementar a interface desktop CustomTkinter do gerador após aprovação de seus critérios.
---

Leia a spec e os pontos existentes em `apps/src/gui/` e `apps/src/main.py`.
Os quatro módulos de GUI estão vazios na fundação; não presuma comportamento pronto.
Respeite a separação entre seleção/configuração, feedback, worker e janela principal.
Chamadas de rede e espera de geração não podem bloquear o loop da GUI.
Atualize widgets na thread da interface, usando fila e agendamento; workers entregam
eventos/dados, não manipulam widgets diretamente. Trate erro e término da execução.
Não acrescente requisitos como cancelamento ou persistência sem spec/decisão.
Use o wireframe somente quando a tarefa o indicar, sem convertê-lo em fonte de regra.
Verifique dependências e compatibilidade Python antes de integrar CustomTkinter.
Teste comportamento sem GPU quando possível e separe a demonstração visual real.
