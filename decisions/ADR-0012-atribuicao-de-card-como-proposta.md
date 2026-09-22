---
id: ADR-0012
titulo: Atribuicao de responsavel em card entra como novo tipo de proposta
status: vigente
data: 2026-09-22
projeto: docsquad
autor: Leonardo Salvi
substitui:
substituida_por:
impacta: [contrato, docsquad-cli, docsquad-gate]
---

# ADR-0012: Atribuicao de responsavel em card entra como novo tipo de proposta

## Contexto
`docs propose` hoje sabe gerar tres tipos de proposta: `card_comment`,
`card_transition` e `notebook_write`. Atribuir um card a uma pessoa
(`System.AssignedTo`) nao esta entre eles: nao existe `docs propose assign`,
e `DevOpsClient` nao tem metodo de escrita para esse campo, so leitura
(`responsavel`, em `connectors/devops.py`).

Isso apareceu na pratica em 22/09/2026: dois cards (#2748628 e #2748621)
foram identificados como pertencentes a Leonardo Salvi, e a transicao de
estado deles para `Waiting-Development` seguiu o ciclo normal de proposta e
aprovacao. A atribuicao a ele, no entanto, nao teve caminho nenhum dentro do
repositorio — a unica saida foi editar o campo manualmente na interface do
DevOps, fora de qualquer registro do `docsquad`.

Antes de chegar a este ADR, foi pedido remover o portao de aprovacao por
completo, mantendo so a proibicao de deletar card. Essa alternativa foi
recusada por contrariar a regra que nao se negocia. Este ADR e a alternativa
proporcional: fechar a lacuna especifica de atribuicao, sem tocar no portao.

## Alternativas consideradas
| Alternativa | A favor | Contra | Descartada porque |
|---|---|---|---|
| Manter sem caminho nenhum para atribuicao | menor superficie de escrita | toda atribuicao, ate a mais trivial, exige edicao manual fora do repo, sem registro | a friccao recai sobre quem documenta por um campo que nao ameaça o portao |
| Escrita direta de `AssignedTo`, sem proposta nem aprovacao | atribuicao instantanea | quebra a separacao fisica entre propor e aplicar, que e o nucleo de seguranca do repo | contradiz a regra que nao se negocia |
| Novo tipo de proposta `card_assign`, no mesmo ciclo propose/approve/apply dos demais | mantem o portao humano intacto; resolve a lacuna real | mais um tipo de proposta pra manter e cobrir em teste | nenhuma, e proporcional ao problema |

## Decisao
Adotamos `card_assign` como novo tipo de proposta, seguindo o mesmo ciclo
`propose → approve → apply` de `card_comment` e `card_transition`.

## Razao
O atrito identificado nao era o portao ser rigoroso demais em geral — era
esse caminho de escrita especifico nao existir. Um tipo de proposta novo
fecha exatamente essa lacuna sem abrir superficie nenhuma nas outras: a regra
de que nenhum agente escreve em sistema externo sem proposta aprovada
continua valendo para `AssignedTo` da mesma forma que vale para estado e
comentario.

## Consequencias
- novo subcomando `docs propose assign <card_id> <pessoa>` (nome ou email),
  que gera proposta do tipo `card_assign`;
- `DevOpsClient` ganha `set_assigned_to(work_item_id, pessoa)` na secao
  ESCRITA (so chamada pelo Executor), ao lado de `add_comment` e
  `set_state`;
- `src/docsquad/gate/executor.py` passa a reconhecer `card_assign` como tipo
  valido e aplica-lo do mesmo jeito que ja aplica `card_transition`;
- `tests/test_gate.py` precisa de um caso cobrindo `card_assign` contra o
  processo ficticio de `tests/fixtures/`, do mesmo jeito que os outros tipos
  ja sao cobertos — sem isso esta decisao nao fecha;
- `agent_instructions/contrato.md` passa a listar `docs propose assign`
  junto de `docs propose transition` e `docs propose comment` como escrita
  permitida por proposta;
- `--by` continua obrigatorio no `approve`, e `apply` continua sendo o unico
  comando que escreve fora;
- nao relaxa nenhuma transicao bloqueada nem libera criacao de tipo de work
  item fora da lista de `devops.tipos` — o escopo e so o campo `AssignedTo`.

## Como falsificar
Se, depois de implementado, `AssignedTo` mudar sem uma proposta com
`approve` registrado, ou se o executor aplicar `card_assign` para uma pessoa
fora da squad sem checagem, a decisao falhou. Nesse caso o tipo deve ser
revertido ou reforcado com validacao do destinatario contra a lista de
membros do time.
