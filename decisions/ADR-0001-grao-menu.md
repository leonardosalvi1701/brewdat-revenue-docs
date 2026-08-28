---
id: ADR-0001
titulo: Grao colapsado por menu
status: vigente
data: 2026-07-15
projeto: desconto-qmin
autor: Leonardo Salvi
impacta: [notebook-eda-base, paper-tecnico-qmin]
---

# ADR-0001: Grao colapsado por menu

## Contexto
Promocoes escalonadas oferecem varios patamares de Qmin dentro de um mesmo menu.
Tratar cada patamar como observacao independente parecia natural, e foi a
abordagem inicial da construcao da base.

## Alternativas consideradas
| Alternativa | A favor | Contra | Descartada porque |
|---|---|---|---|
| Uma linha por oferta | granularidade maxima | patamares do mesmo menu nao sao independentes | vies em beta_1 correlacionado com porte do PDV |
| Uma linha por menu | independencia plausivel entre observacoes | perde informacao do patamar escolhido | adotada |
| Modelo hierarquico por patamar | usa toda a informacao | complexidade fora do escopo do MVP | adiada |

## Decisao
Adotamos o grao `cod_unb x cod_pdv x cod_abrev_prod x id_menu`.

## Razao
Tratar patamares escalonados como Bernoullis independentes enviesa beta_1 para
baixo, e o vies e correlacionado com porte do PDV, porque PDVs maiores recebem
mais patamares. O vies portanto nao e ruido, e sistematico na direcao que mais
importa para a decisao de desconto.

## Consequencias
- O patamar escolhido passa a ser desfecho, nunca variavel de tratamento (ver ADR-0002)
- A base de EDA colapsa por menu antes de qualquer agregacao
- Censura passa a ser medida sobre qtd_max_por_pedido

## Como falsificar
Se a estimacao hierarquica por patamar, quando construida, devolver beta_1
estatisticamente indistinguivel do colapsado por menu, o colapso deixa de ser
necessario e volta a valer a granularidade maior.
