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

## Aprovacao
`.codex/rules/docsquad.rules`, gerado, tem `prefix_rule` com
`decision = "prompt"` para `docs approve`, `apply`, `reject` e `decidir`, em
cada forma de chamar o `docs`. O Codex para e pergunta antes de cada um.

Duas condicoes, sem as quais a pergunta nao acontece:

- o projeto precisa estar marcado como confiavel. Regra de projeto so carrega
  assim: responder que sim quando o Codex perguntar na primeira vez;
- nao rodar com aprovacao desligada (`--yolo`, ou `approval_policy = "never"`).
  Nesses modos, comando com `prompt` e recusado, e nao executado: o
  `approve` falha, e a pessoa aprova pelo `docs decidir`.
