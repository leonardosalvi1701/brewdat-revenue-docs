---
tipo: card
aplica_a: [Analysis Activity, Business Story, Technical Story, Bug, Action]
---

# Padrao de card da squad Revenue

Cola no corpo do work item. As quatro secoes abaixo sao a Descricao, o DoR, o
DoD e a lista de tarefas. Extraido dos cards reais da S3-Q3-26; ver ADR-0010.

---

## Titulo

`{Tema} | {acao no contexto}`. O tema agrupa os cards de uma mesma frente e a
acao diz o que este card entrega, de forma que o titulo sozinho se entenda no
quadro. "Melhoria 1 | Regras de politica do desconto: transicoes graduais,
lambda por segmento e verificacao de canibalizacao" e o padrao;
"Implementacao de Melhoria 1" nao e.

---

## Descricao

Prosa, dois ou tres paragrafos, nesta ordem:

**Contexto e objetivo.** Por que este card existe e o que ele destrava. Uma
frase de contexto vale mais que tres de escopo: quem le a review daqui a dois
meses precisa entender a motivacao sem abrir outro card.

**Origem, quando nao for do planejamento.** Interferencia, bug de terceiro,
demanda puxada por agenda externa. Dizer de onde veio explica a diferenca
entre o planejado e o entregue na review, e some se nao for registrado agora.

### Escopo do trabalho
- item de escopo, verbo no infinitivo
- um item por entrega verificavel, nao por passo de execucao

### Validacao
- como vamos provar que funcionou: o numero ou a comparacao que confirma, com
  o valor de hoje quando houver ("razao entre realizado e previsto perto de 1;
  hoje 0,69 em cerveja")
- quem valida, quando a validacao for de outra pessoa ou area

O resultado vai para o campo `Evidencias da Validacao` na entrega, e nao para
a descricao.

### Para Bug, no lugar do escopo
**Problema:** o que se observa, com o caso concreto: PDV, SKU, id de promocao,
numero e data.
**Causa:** a causa-raiz quando conhecida. "Ainda em investigacao" e resposta
valida; hipotese apresentada como causa nao e.
**Solucao ou encaminhamento:** o que foi alinhado, e o que fica em avaliacao.

---

## DoR: pronto para comecar

Marcar antes de mover para `Waiting-Development`. Um item nao marcado e um
motivo declarado para o card nao entrar na sprint.

- [ ] Objetivo escrito no card, e nao so no titulo
- [ ] Fonte de dado identificada, e o acesso conferido nesta semana
- [ ] Ambiente de execucao disponivel: cluster, workspace, permissao
- [ ] Dependencia de terceiro nomeada, com a pessoa ou o time
- [ ] Criterio de pronto acordado com quem vai validar
- [ ] Cabe na sprint. Se nao couber, quebrar antes de comecar

---

## DoD: pronto de verdade

Marcar antes de mover para `Waiting-QA`. Card so vai para `Done` com o DoD
marcado e o QA registrado em comentario.

Escolher **um** bloco, pela natureza do trabalho, e apagar os outros. Cada
item do bloco pode ganhar o detalhe deste card depois de dois pontos
("Regra antiga versus nova documentada: comportamento anterior as alteracoes
de agosto contra o atual"), sem trocar o item por outro.

### Analise e EDA
- [ ] Fontes de dados identificadas e confiaveis
- [ ] Queries revisadas, performance e logica
- [ ] Premissas documentadas
- [ ] Limitacoes explicitadas

### Dado e pipeline
- [ ] Definicao clara das tabelas e colunas
- [ ] Regras de negocio documentadas
- [ ] Validacao de consistencia: totais, duplicidade
- [ ] Pipeline reproduzivel
- [ ] Tratamento de erros implementado
- [ ] Logs e monitoramento definidos
- [ ] Dataset com tags relacionadas a PII

### Mudanca de regra em producao
- [ ] Regra antiga versus nova documentada
- [ ] Impacto avaliado, downstream incluido
- [ ] Backfill considerado, se necessario
- [ ] Testes com dados historicos
- [ ] Validacao com stakeholders

### Codigo e documentacao tecnica
- [ ] Codigo e arquitetura explicados
- [ ] Dependencias descritas
- [ ] Passo a passo de execucao
- [ ] Limitacoes e riscos documentados

---

## Lista de tarefas

Dentro do card, e nao como work item filho: o processo da squad nao tem tipo
`Task`, e quebrar em card separado esconde o trabalho da review.

- [ ] tarefa, verbo no infinitivo, com fim verificavel
- [ ] uma tarefa por unidade que renderia um comentario de atualizacao

Tarefa que sobra no fim da sprint nao se apaga. Ela e a materia-prima da
secao de proximos passos da review.

---

## Antes de salvar

Conferir no card, e nao so no corpo:

- **sprint**: card criado sem sprint fica com o caminho da raiz do projeto em
  `System.IterationPath` e nao aparece no quadro, mesmo com a sprint
  configurada no time;
- **tag do tema**, igual a dos cards da mesma frente (por exemplo
  `Otimizacao`). Ver ADR-0013;
- **esforco** na escala da squad: 1 ponto = 1 turno = meio dia, 2 pontos por
  dia util.
