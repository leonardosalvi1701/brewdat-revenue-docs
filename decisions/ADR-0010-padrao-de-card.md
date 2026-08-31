---
id: ADR-0010
titulo: Padrao de card extraido dos cards reais, com DoD como portao de Waiting-QA
status: vigente
data: 2026-08-31
projeto: docsquad
autor: Leonardo Salvi
substitui:
substituida_por:
impacta: [templates-card, templates-card-comment, contracts-estilo-card, settings-yaml]
---

# ADR-0010: Padrao de card extraido dos cards reais, com DoD como portao de Waiting-QA

## Contexto
Os 43 cards e 170 comentarios da sprint S3-Q3-26 foram lidos em 31/08/2026,
pelo snapshot `knowledge/cards/snapshot-S3-Q3-26-REVENUE-DI-2026-08-31.json`.
O que existe hoje:

- **Descricao**: 40 dos 43 cards tem. O formato recorrente e prosa de contexto
  e objetivo, seguida de `Escopo do trabalho:` em bullets. Bug e a excecao:
  3 dos 4 estao com descricao vazia, e o que tem descricao usa Problema e
  Solucao, o mesmo vocabulario que o paper de review ja usa para bug;
- **DoR**: nao existe, em nenhuma forma;
- **DoD**: existe como `Checklist QA:` com itens `[ ]`, em 20 dos 43 cards.
  Os 92 itens de checklist da sprint estao **todos desmarcados**, inclusive
  nos 31 cards que chegaram a `Done`. Os itens se agrupam em quatro familias
  estaveis, por natureza do trabalho, e nao por tipo de work item;
- **Lista de tarefas**: nao existe como work item filho. O processo da squad
  nao tem tipo `Task`. O que faz esse papel e o `Escopo do trabalho:`;
- **Comentario**: 57 dos 170 tem o pin 📌, e 55 o cabecalho
  `📌 Update — {TIPO} {id}: {titulo}`.
  O rotulo `Status` aparece 50 vezes, `Impedimento` 8, `Proximos passos` 3,
  `QA realizado` 3. Quatro cards nao tem comentario nenhum.

O `contracts/estilo-card.md` que estava no repo prescrevia outra coisa:
cabecalho `📌 **Atualizacao {tipo} {numero} - {DD/MM/AAAA}**` e secoes
numeradas Contexto, O que foi feito, Resultado ou decisao, Proximos passos.
Nenhum dos 170 comentarios usa esse cabecalho, e nenhum usa as secoes
numeradas. O contrato descrevia um padrao que nunca existiu.

Convivem hoje tres estilos: 55 comentarios com `📌 Update —`, 7 abrindo com
`Atualizacoes:` como rotulo solto, e o restante em prosa sem cabecalho.

## Alternativas consideradas
| Alternativa | A favor | Contra | Descartada porque |
|---|---|---|---|
| Manter o contrato antigo e pedir adesao | ja estava escrito | descreve um padrao que 170 comentarios ignoram | um padrao que ninguem seguiu em uma sprint inteira nao e padrao, e proposta |
| Padronizar o DoD por tipo de work item | casa com o campo que ja existe no board | a mesma Technical Story ja usou tres checklists diferentes | o tipo nao prediz a natureza do trabalho |
| Deixar o `Checklist QA` como esta, informativo | nao muda processo | 92 de 92 itens desmarcados, 31 em Done | checklist que nunca se marca ensina a ignorar checklist |
| Extrair o padrao dos cards e amarrar o DoD a uma transicao | descreve o que a squad faz, e fecha o unico buraco | exige disciplina numa transicao | adotada |

## Decisao
Adotamos `templates/card.md` como padrao de corpo de card, com quatro secoes:
Descricao, DoR, DoD e lista de tarefas. O DoD tem quatro blocos, escolhidos
pela natureza do trabalho, e o card so vai para `Done` com o bloco escolhido
marcado e o QA registrado em comentario.

`templates/card-comment.md` e `contracts/estilo-card.md` passam a descrever o
formato de comentario que a squad de fato usa.

## Razao
O padrao foi extraido, e nao desenhado. Cada item do DoD e um item que a squad
ja escreveu em pelo menos tres cards; as quatro familias sao as que emergiram
do agrupamento, e nao categorias inventadas por simetria.

As duas excecoes sao deliberadas e estao declaradas:

**O DoR nao foi extraido, porque nao existia.** Ele foi construido a partir do
que travou esta sprint: a perda de acesso aos dois clusters de desenvolvimento
de Revenue em 20/08/2026, registrada em tres cards, e as tags `Bloqueado` e
`Blocked` em quatro. Por isso os itens sao fonte de dado acessivel, ambiente
disponivel e dependencia nomeada, e nao uma lista generica de prontidao.

**O DoD virou portao numa transicao.** Como checklist informativo ele ja foi
testado por uma sprint inteira e o resultado foi 92 itens desmarcados em 92.
Amarrar em `Waiting-QA` e o menor acoplamento possivel ao processo: e a
transicao que ja existe, ja e humana e ja significa "acabei, confere".

## Consequencias
- `templates/card.md` passa a existir, e `templates/` deixa de ter cinco
  padroes de documento para ter seis;
- Bug ganha forma propria, com Problema, Causa e Solucao. Descricao vazia em
  bug deixa de ser aceitavel: dos 4 bugs da sprint, 3 estavam sem;
- a lista de tarefas mora dentro do card, e nao como work item filho, porque o
  processo nao tem tipo `Task` e quebrar em card separado esconde trabalho da
  review;
- o comentario passa a carregar tipo, numero e titulo no cabecalho. Nesta
  sprint um comentario do card 2680722 abre com o cabecalho do card 2680715,
  e o cabecalho completo e o que torna esse erro visivel;
- `contracts/estilo-card.md` deixa de prescrever secoes numeradas fixas.

## Como falsificar
Se na proxima sprint os cards continuarem chegando a `Done` com o DoD
desmarcado, o portao nao pegou, e o problema nao e de formato: e de onde a
marcacao acontece. O caminho passa a ser marcar no proprio DevOps, com regra
de transicao, e nao em texto colado na descricao.

Se o DoR passar a ser marcado inteiro em todo card sem nenhum card ser barrado,
ele virou formalidade. Um DoR que nunca reprova nao esta medindo prontidao.
