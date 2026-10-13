---
tipo: sprint-review
sprint:
periodo:
squad: Revenue
autor:
data:
snapshot:
---

# [Review] {sprint}

## 1. Objetivo do paper
Visando dar clareza e tornar objetiva as cerimonias de encerramento de sprint,
o paper apresenta os artefatos entregaveis ao final da sprint, com imagens
ilustrativas, trechos de codigo e exemplos praticos. Escrever sobre a entrega
tambem obriga a refletir sobre como as atividades contribuem para o produto, e
conecta pontas soltas entre elas.

## 2. Descricao da sprint

### 2.1 Objetivo
| # | Deliverable | Descricao da entrega | Impacto esperado |
|---|---|---|---|
| 1 |  |  |  |

### 2.2 Duracao da sprint
{sprint}: {inicio} a {fim}

## 3. Metricas da sprint
Indicadores que ajudem a acompanhar o fluxo de trabalho e a saude do delivery
da squad.

| # | KPI | Valor da sprint | Observacao |
|---|---|---|---|
| 1 | Story Points planejados |  |  |
| 2 | Story Points entregues |  |  |
| 3 | Taxa de entrega planejado (%) |  |  |
| 4 | Bugs encontrados |  |  |
| 5 | Bugs resolvidos |  |  |
| 6 | Lead time medio |  |  |
| 7 | Cycle time medio |  |  |

## 4. Atividades desenvolvidas
Uma subsecao por frente de trabalho, nao por card. A frente e o produto ou a
solucao, e e ela que o leitor reconhece: Modelo de Volume, Promo Removal,
Otimizador de Cobertura. Dentro da frente, um bloco por atividade, com titulo
que diga o que foi feito. Produtos parecidos e etapas diferentes da
produtizacao (por exemplo, features/treino e predict/serving) nao devem ser
fundidos quando tiverem resultados ou bloqueios distintos. Agrupe os cards na
frente certa, mas preserve a entrega e o estado de cada etapa.

Para card transbordado, descreva o progresso ate o fechamento da sprint, o que
ficou pendente e o motivo. Consulte o snapshot seguinte ou a leitura mais
recente do card se ele nao aparecer no snapshot original, e registre essa
fonte adicional no frontmatter. Nao use status posterior como se fosse o
status no encerramento.

Fechadores opcionais ao fim de cada bloco, so quando houver o que dizer:
`Pontos Positivos`, `Pontos Negativos`, `Pontos de Atencao`, `Proximos Passos`.
Bullet vazio nao se inventa.

### 4.1 {Frente}
Responsavel: {nome}

#### {Atividade}
O que foi feito, por que foi feito e o que ficou decidido. Prosa corrida, verbo
no passado, voz impessoal. Numero so com fonte.

Pontos Positivos
- o que funcionou, especifico o suficiente para ser repetido

Pontos de Atencao
- dependencia ou risco que sobrevive ao fim da sprint

Proximos Passos
- proxima etapa, com responsavel quando nao for o autor

#### {Atividade transbordada, se houver}
O que foi concluido ate o fechamento da sprint, o que ficou pendente, o
bloqueio e a passagem para a sprint seguinte. Cite comentario e data. Se o
card tiver avancado depois, marque esse avanco como posterior.

#### Cards validados
Validacoes tecnicas de entregas conduzidas por outras pessoas do time. Um
bullet por card validado, com quem conduziu e o que saiu da validacao.

- {entrega validada}
  Responsavel: {quem conduziu}. {o que a validacao apontou}.

### 4.x Demais atividades e interferencias
Responsavel: {nome}

O que nao estava planejado e consumiu sprint: interferencia, bug de terceiro,
indisponibilidade de ambiente. Vai aqui com o mesmo nivel de detalhe do resto,
porque e isso que explica a diferenca entre planejado e entregue. Para trabalho
sem card, identifique a transcricao do autor como fonte e diga que nao houve
card dedicado. Nao atribua o trabalho a um card de outra pessoa que recebeu
apoio.

Verifique que cada imagem veio do comentario da atividade que ilustra. Confira
visualmente o assunto e identifique produto/DAG e data na legenda. Nao reutilize
uma imagem de outra frente so porque os trabalhos ocorreram na mesma sprint.

## 5. Reconhecimentos
Espaco para reconhecer contribuicoes relevantes de membros do time durante a
sprint.

| # | Pessoa | Reconhecimento | Contexto |
|---|---|---|---|
| 1 |  |  |  |
