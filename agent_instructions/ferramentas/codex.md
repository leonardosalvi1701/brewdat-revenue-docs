# Ferramenta: Codex

## Onde ele acha instrucao
`AGENTS.md`, na raiz. Aquele arquivo e um ponteiro gerado, curto de proposito.
O contrato inteiro esta em `agent_instructions/contrato.md`, e abri-lo e
obrigatorio antes de alterar qualquer coisa. Um ponteiro lido e ignorado
equivale a nao ter contrato.

## Papeis
Nao ha slash command. Para assumir um papel, ler
`agent_instructions/papeis/<papel>.md` inteiro, mais a rubrica correspondente
em `agent_instructions/rubricas/`.

## Autoria de commit
O Codex nao acrescenta trailer de autoria por padrao. A regra do contrato vale
do mesmo jeito: nenhuma linha de coautoria de IA na mensagem.
