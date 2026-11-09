---
id: ADR-0016
titulo: Regua de leitura de experimento de desconto com tres ROIs nomeados
status: vigente
data: 2026-11-09
projeto: desconto-qmin
autor: Leonardo Salvi
substitui:
substituida_por:
impacta: [glossario, paper-resultado-experimento, notebooks-de-resultado-de-experimento, sprint-review]
---

# ADR-0016: Regua de leitura de experimento de desconto com tres ROIs nomeados

## Contexto
O experimento de desconto de outubro de 2026 comparou 6.000 PDVs pequenos e
medios, sorteados entre grupo de tratamento (desconto do modelo) e grupo de
controle (pratica), de 07/10 a 01/11/2026. A leitura final, de 06/11/2026 com
notas ate 01/11, foi feita com tres contas de retorno diferentes, e elas
discordam no sinal. Na cerveja, tratamento menos controle:

| ROI | Cerveja (T - C) |
|---|---|
| tecnico ajustado | 1,49, sem significancia |
| tecnico de Revenue | 0,07 |
| do dashboard | -0,38 |

Fonte: paper "Experimento de desconto de outubro: resultados e melhorias",
publicado no Loop em novembro de 2026, e notebooks 07 e 33 da pasta
`brewopt-modelagem` do workspace.

Cada conta responde a uma pergunta:

- **ROI tecnico ajustado**: faturamento a mais do tratamento sobre o controle,
  por regressao por par (aparada em p99,5, ajustada pela compra antes da
  selecao, erro agrupado por PDV), dividido pelo gasto a mais. Mede quanto o
  desconto do modelo rendeu a mais que a pratica. So existe na diferenca;
- **ROI tecnico de Revenue**: uplift contra a media dos mesmos pares no mesmo
  dia da semana nas 12 semanas antes, dividido pelo gasto. Mede quanto cada
  grupo vendeu acima do proprio passado;
- **ROI do dashboard**: o KPI de eficiencia de volume da area, crescimento
  contra os 110 dias anteriores menos o do cluster UNB x segmentacao x faixa
  de faturamento, ponderado pela fatia da iniciativa, dividido pelo
  investimento, mais 1. O dashboard nao mede iniciativa fora do calendario
  dele, e por isso a conta foi replicada no notebook 33 e validada numa
  iniciativa que ele ja tinha medido: INI-74798, setembro de 2026, replica
  4,86 contra 4,88 do dashboard.

Duas armadilhas apareceram na leitura. A cesta saiu das 4 semanas antes do
sorteio, so com pares que compraram, e essa janela esta dentro da linha de
base de 12 semanas: o pico de selecao puxou a linha de base para cima e gerou
uplift negativo no controle de NAB e MATCH (-5,4%), sem relacao com o
desconto. E o teste placebo do ROI do dashboard, aplicado as semanas antes do
inicio, tambem sai alto: o nivel dele nao e efeito.

## Alternativas consideradas
| Alternativa | A favor | Contra | Descartada porque |
|---|---|---|---|
| So o ROI do dashboard | e o numero que a area reconhece e usa para comparar iniciativas | o nivel nao passa no placebo; nao mede iniciativa fora do calendario | sozinho, atribui ao desconto um crescimento que ja existia antes |
| So o ROI tecnico de Revenue | simples, por grupo, ja acompanhado durante o experimento | a linha de base contem a janela de selecao da cesta | gera uplift negativo que nao e efeito do desconto |
| So o ROI tecnico ajustado | e a unica conta causal: compara grupos sorteados | so existe na diferenca, e a area nao o reconhece | sozinho, nao conversa com o numero que o negocio acompanha |
| Os tres, sempre nomeados, com a pergunta de cada um | cada leitor encontra a conta que usa, e a divergencia fica explicada | mais colunas por tabela | adotada |

## Decisao
Adotamos os tres ROIs como regua de leitura de experimento de desconto, sempre
com o nome completo, e nunca "ROI" sozinho.

## Razao
As tres contas discordam no sinal na mesma leitura. Escolher uma esconde as
outras duas perguntas, e o leitor que conhece so o dashboard le a divergencia
como erro. A replica do dashboard, validada com diferenca de 0,02, permite
reporta-lo tambem para iniciativas fora do calendario dele.

## Consequencias
- `config/glossario.yaml` ganha os tres termos, distintos do estimador de ROI,
  que continua sendo trava de eficiencia;
- tabela de resultado de experimento traz as tres colunas, e o dicionario de
  colunas diz a pergunta de cada uma;
- o nivel do ROI do dashboard nao e lido como efeito: so a diferenca entre os
  grupos;
- o gasto do tratamento se decompoe em manutencao das conversoes, gasto a mais
  em desconto e conversoes novas, para dizer em que a verba a mais foi gasta.
  Na cerveja de outubro, na leitura parcial de 27/10/2026, 66% da verba a
  mais foi gasto a mais em desconto.

## Como falsificar
- se o placebo do ROI do dashboard passar a sair perto de zero, o nivel dele
  volta a ser lido como efeito;
- se o desenho do experimento tirar a janela de selecao da linha de base
  (ADR-0017), o ROI tecnico de Revenue por grupo deixa de ter o vies de
  selecao, e a ressalva sai;
- se a area adotar uma conta com grupo de controle sorteado, ela substitui o
  ROI do dashboard nesta regua.
