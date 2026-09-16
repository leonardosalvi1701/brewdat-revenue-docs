---
id: ADR-0011
titulo: Agente le sistema externo pela credencial da pessoa, e continua sem escrever
status: vigente
data: 2026-09-16
projeto: docsquad
autor: Leonardo Salvi
substitui:
substituida_por:
impacta: [agent-instructions, contrato, ferramentas-claude, knowledge-notebooks]
---

# ADR-0011: Agente le sistema externo pela credencial da pessoa, e continua sem escrever

## Contexto
O contrato proibia o agente de chamar a API do Azure DevOps, do GitHub e do
Databricks diretamente, inclusive para leitura. Na pratica, o agente so via o
que `docs collect` grava em `knowledge/cards/`, e do Databricks isso e um
inventario com as 15 primeiras linhas de cada notebook.

`knowledge/notebooks/` existe e o papel `revisor-tecnico` le dali para
rastrear numeros, mas nenhum comando grava nessa pasta. Para o agente ler um
notebook inteiro, a pessoa precisava exportar a mao.

Em 16/09/2026 a autenticacao do Databricks passou a aceitar o perfil SSO da
CLI (`DATABRICKS_CONFIG_PROFILE`), porque ha quem nao tenha permissao de gerar
PAT. Com isso, a mesma credencial serve a CLI, a extensao do VS Code e o
`docs`, e a pessoa ja esta autenticada enquanto trabalha com o agente.

## Alternativas consideradas
| Alternativa | A favor | Contra | Descartada porque |
|---|---|---|---|
| Manter a proibicao total | nenhuma chamada externa sai do agente | agente cego para notebook; pessoa vira intermediaria de export | o custo recai toda vez sobre quem esta documentando |
| Liberar leitura e escrita | agente autonomo | escrita deixa de passar pelo portao, que e a garantia central do repo | contradiz a regra que nao se negocia |
| Liberar so leitura, so no Databricks | menor superficie | DevOps e GitHub continuam exigindo `docs` para qualquer consulta pontual | a squad preferiu tratar os tres sistemas da mesma forma |
| Servidor MCP do Databricks no agente | integracao pronta | expoe ferramentas de escrita e execucao junto com as de leitura | a fronteira de escrita ficaria na configuracao do servidor, e nao no contrato |

## Decisao
O agente pode ler do Azure DevOps, do GitHub e do Databricks pela credencial
que a pessoa configurou, e continua proibido de escrever neles por qualquer
caminho que nao seja proposta aprovada.

## Razao
Leitura nao altera estado externo, e o que o agente le a pessoa ja pode ler
com a mesma credencial. O risco que o portao existe para conter, escrita sem
aprovacao humana, fica exatamente onde estava.

A execucao de SQL e de codigo em compute fica de fora mesmo sendo "consulta":
SQL escreve tanto quanto le, e a diferenca entre `SELECT` e `INSERT` nao e
uma fronteira que o contrato consiga policiar. Alem disso, compute custa.

## Consequencias
- `agent_instructions/contrato.md` lista o que e leitura permitida e o que e
  escrita proibida, e `ferramentas/claude.md` repete a fronteira para a
  ferramenta que tem shell;
- a separacao continua fisica para escrita e passa a ser contratual para
  leitura: a credencial da pessoa permite escrever, e o agente nao escreve
  porque o contrato proibe. Esse e o ponto fraco desta decisao;
- export de notebook vai para `knowledge/notebooks/`, que esta no
  `.gitignore`, e nao entra no repo;
- token nunca aparece em saida repassada pelo agente.

## Como falsificar
Rever se aparecer, em transcricao ou log, um agente que escreveu em sistema
externo usando a credencial liberada para leitura. Nesse caso a leitura volta
a passar por `docs`, com credencial restrita a leitura, e nao pela credencial
da pessoa.
