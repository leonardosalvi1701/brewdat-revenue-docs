<!-- GERADO POR scripts/sync_agent_files.py. NAO EDITAR A MAO. -->

<!-- Fonte: agent_instructions/. Alterar la, depois rodar o script. -->

# Instrucoes do repositorio

O contrato deste repositorio esta em `agent_instructions/contrato.md`, e
vale para todos os agentes de IA. Ler antes de qualquer alteracao.

@../agent_instructions/contrato.md
@../agent_instructions/ferramentas/claude.md

## Papeis disponiveis como slash command

- `/curador`: Voce decide o que entra no contexto dos agentes escritores e revisores.
- `/escritor-sprint-review`: Voce transforma o rascunho de uma sprint review, que so tem estrutura e cards, no texto que a squad apresenta na cerimonia de encerramento.
- `/revisor-negocio`: Voce revisa documentos destinados a leitores de negocio sem formacao tecnica.
- `/revisor-tecnico`: Voce revisa documentos destinados a pares tecnicos: cientistas de dados, engenheiros e o time que construiu as solucoes que este documento referencia.
