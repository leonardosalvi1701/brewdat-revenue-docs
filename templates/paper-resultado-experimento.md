---
tipo: paper-resultado-experimento
projeto:
audiencia: ambos            # negocio no resumo, tecnica nas secoes de resultado
status: rascunho            # rascunho | em-revisao | vigente | superseded
autor:
co-owners: []
data:
data_de_leitura:            # data fixa das notas usadas; leitura parcial ou final
experimento:                # orcamentos, vigencia, populacao
adrs_relacionadas: [ADR-0016]
---

# [DD.MM.AAAA] Experimento {nome}: resultados e melhorias

## 1. Resumo executivo
Tres a cinco itens, cerveja primeiro, cada um com o numero que decide e a data
de leitura: conversao, gasto em vezes a pratica, custo por conversao, os tres
ROIs e para onde foi a verba a mais. Fecha com o que muda no modelo.

## 2. Contexto
### 2.1 O modelo testado
Funcao objetivo e travas em vigor no experimento, com leitura em linguagem
natural de cada formula. Decisao ja registrada cita o ADR, sem reexplicar.
### 2.2 O experimento
Populacao, sorteio, grupo de tratamento e grupo de controle, cesta, orcamentos,
vigencia planejada e efetiva, e as datas de leitura.

## 3. Resultados
### Como as comparacoes sao feitas
As reguas antes do primeiro numero: os tres ROIs com a pergunta de cada um
(ADR-0016), a linha de base de cada um, e as tres partes do gasto
(manutencao das conversoes, gasto a mais em desconto, conversoes novas).
### 3.1 Leitura final
Uma tabela geral por grupo e a diferenca, e uma tabela por orcamento. Valores
em R$ e hL, com o percentual ao lado. Resultado inesperado (uplift negativo,
sinal trocado entre reguas) explicado no paragrafo onde aparece.
### 3.{n} {tema do diagnostico}
Uma secao por limitacao encontrada. Antes de cada figura, os termos que ela
usa; depois, a leitura. Cada secao fecha com os Pontos de melhoria que ela
motiva:

> **Ponto {n.m}. {titulo}**
> **Problema:** o que o resultado mostra que esta errado.
> **Evidencia:** o numero, a figura ou a tabela, com a data de leitura.
> **Solucao:** o que muda no modelo ou no desenho, e como saberemos que funcionou.

## 4. Indice dos Pontos
Tabela com todos os Pontos, a secao de origem e a categoria (politica,
modelo, dado, desenho de experimento).

## 5. Priorizacao e selecao
Criterios e pesos (impacto, risco, dependencia, esforco), a nota de cada Ponto,
os selecionados e os que ficam de fora, com o motivo. Esforco na escala da
squad: 1 ponto = 1 turno.

## 6. Roadmap
Sprint a sprint, com o card de cada Ponto selecionado.

<!--
Restricoes deste template:
- todo numero com a data de leitura; secao lida em outra data diz qual
- cada resultado e detalhado na primeira mencao e so citado nas seguintes
- tabela de negocio sem intervalo de confianca; significancia vai no texto
  quando muda a leitura
- ROI sempre com o nome completo (ADR-0016)
- "grupo de tratamento" e "grupo de controle", nunca "braco"
- figuras e numeros saem do run executado do notebook, nunca recalculados a
  mao. A cada nova execucao, reextrair e conferir o texto
- tabela nova ou trocada: esboco com as colunas antes de escrever
- sem travessao em prosa corrida
-->
