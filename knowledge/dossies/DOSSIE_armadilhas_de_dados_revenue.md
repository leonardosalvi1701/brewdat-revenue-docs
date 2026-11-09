# Dossiê de armadilhas de dados e de ambiente da squad Revenue
### O que produz número errado ou trabalho perdido sem dar erro

**Origem:** casos medidos pela squad entre agosto e novembro de 2026, cada um com a data em que foi
verificado. Vale para quem documenta, revisa ou lê resultado; o que é específico de um repositório
de modelagem fica lá.

**Uso:** antes de afirmar um número que dependa destas fontes, conferir se a armadilha se aplica.
Quando ela aparece num notebook ou paper, a ressalva vai no parágrafo onde ela morde, como pede
`contracts/estilo-notebook.md`.

---

## 1. Aderência registra a compra com atraso

`br_aderencia_ttv` leva **2 a 5 dias** para registrar uma compra, e a conversão de hoje só aparece
na semana seguinte. Medido em 13/10/2026 no experimento de desconto iniciado em 07/10: cobertura de
nota sobre uso de 72% em 07/10, 54% em 08/10, 30% em 09/10 e perto de zero de 10/10 em diante.

- leitura de experimento só cerca de 5 dias depois do fim da vigência;
- a leitura tem data fixa, como parâmetro do notebook (`data de leitura` no glossário). Sem ela,
  cada execução sai com um número diferente;
- acompanhamento de orçamento em tempo real subestima o gasto.

## 2. Feature store do volume publica a semana corrente pela metade

`gld_saz_sales_revenue_promophoenix_volume.features` é reescrita inteira no domingo à noite e
publica a semana corrente incompleta, herdando o atraso da aderência. Em 28/09/2026 a semana 202639
tinha 1,6 milhão de linhas contra cerca de 4 milhões das anteriores, com queda uniforme em todas as
geos. Ao pontuar perto de uma data de largada, tratar a última semana como não publicada, ou
conferir a contagem de linhas dela contra as anteriores.

## 3. O vetor de features do volume muda de tamanho e de ordem a cada carga

Verificado em 23/09/2026: o vetor `features` foi de 155 para 157, 156 e 155 posições, porque o
one-hot só inclui as categorias presentes na carga, e os índices das 111 numéricas são
reembaralhados a cada carga. `tag_digitalization` foi recalculada para todo o histórico (na semana
202632, 12% de zeros até 06/09 e 87% em 20/09). Variáveis mensais de uma semana continuam mudando
enquanto o mês está aberto. O histórico Delta guarda cerca de 5 semanas.

- ler as colunas por nome, nunca o vetor por posição;
- para comparar cargas, usar `versionAsOf` e a metadata `ml_attr` do campo `features`.

## 4. Estoque diário migrou de tabela e diverge da legada

Desde 27/10/2026 a feature store lê `gld_saz_sales_pricing_on_estoque.br_estoque_diario`, da
BrewDat. Até 18/10 ela era cópia exata da legada do IRIS; desde 19/10 é calculada por conta própria
e diverge. Comparação de 06/11/2026: as features de estoque divergem em cerca de 20 a 27% dos
grupos de SKU e semana em `dias_com_estoque`. As features de outubro de 2026 em diante já refletem
a tabela nova, e a legada vai ser apagada.

## 5. Ambiente

- **Dev do Airflow cancela runs sem erro.** Run `CANCELED` com "Run cancelled by user", sem
  cancelamento manual nem deploy por perto, é instabilidade conhecida do dev da BrewDat (confirmado
  em 30/09/2026). Redisparar; investigar só se repetir no mesmo ponto ou vier com erro.
- **Job do workspace de dev não é referência durável.** Jobs recriados no workspace de dev
  desaparecem em horas, e o id muda a cada recriação (verificado em 31/08/2026). Em card e em
  documento, citar o notebook no workspace, cujo link sobrevive a deploy enquanto o arquivo não é
  movido.
- **Notebook rodado só pela API de comandos fica sem saídas.** O notebook que alguém vai abrir é
  publicado já executado, com as saídas do run que a leitura cita.
