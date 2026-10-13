<!--
Padrao de documentacao de notebook. A documentacao mora no proprio notebook,
em celulas markdown intercaladas com o codigo, e nao num arquivo separado.

Exemplar: notebook 30, perguntas da revisao de negocio sobre a previsao de
conversao, no repositorio de modelagem, lido em 08/10/2026. Voz em
contracts/estilo-notebook.md. Decisao em ADR-0014.

Cada bloco abaixo e uma celula, na ordem em que aparece no notebook.
[md] e markdown, [py] e codigo. Os blocos de "Resultado" se repetem, um por
tabela ou grafico.
-->

<!-- [md] Cabecalho -->
# Notebook {NN} — {o que ele responde ou produz}

{Um paragrafo. O que o notebook entrega, para quem, e o que cada secao traz:
"Cada secao e uma pergunta, e cada resposta traz o numero, a regua usada para
medi-lo e o que ele autoriza concluir."}

| # | pergunta | onde |
|---|---|---|
| 1 | {a pergunta como quem perguntou faria} | secao 2 |

Notebook de pipeline troca a tabela de perguntas pela de etapas:

| # | etapa | produz | onde |
|---|---|---|---|

## O que ele nao responde
{O limite que um leitor apressado atravessaria. Em analise preditiva, quase
sempre: "Nenhum numero aqui e efeito causal", e qual estudo responderia.}

{O que ele grava. "O notebook nao grava nenhuma tabela" e resposta valida.
Se grava:}

| saida | grao | quem consome |
|---|---|---|

<!-- [md] Termos -->
## Termos que confundem se forem lidos sem aviso

| termo | o que e |
|---|---|
| **{termo}** | {definicao operacional, com a coluna que o materializa em `codigo`} |

{Regra de leitura que vale para o notebook inteiro, com o motivo. Ex.: "Cerveja
vem primeiro em toda leitura. BEER e perto de 90% do peso de negocio, por isso
toda tabela traz a quebra por categoria ao lado do total."}

<!-- [md] Resumo -->
## As respostas em resumo

{A regua e a data: em que populacao, periodo e data de referencia os numeros
foram medidos.}

| # | pergunta | resposta curta | onde |
|---|---|---|---|
| 1 | {pergunta} | {o numero e o que ele autoriza, com a ressalva se houver} | secao 2 |

<!-- [py] Configuracao -->
<!--
- todo caminho de tabela e todo parametro vem de widget, com valor padrao;
- comentario acima do widget quando o valor padrao nao e obvio: por que esse
  valor, e o que fica de fora dele;
- constantes: chaves, alvo, ordem das categorias;
- funcoes de contrato: require_columns na leitura, assert_unique antes de join;
- mostra(pdf, titulo): toda tabela sai com titulo numerado, igual ao da secao;
- paleta fixa por serie e por categoria, igual entre notebooks do mesmo projeto.
-->

<!-- [md] Secao 1: a regua -->
## 1. {Como foi medido}

{Antes de qualquer resultado: como a medicao foi construida e por que essa
escolha, e nao a obvia. O que e estimado, de que periodo sai, e o que fica
congelado. Decisao metodologica que ja tem ADR cita o ADR aqui.}

<!-- [md] Resultado: abertura, uma por tabela ou grafico -->
## {N}. Pergunta {k}: {a pergunta}

### {N.m} {o que esta subsecao mede}

{Paragrafo curto: o que a tabela mede, em que populacao, e por que essa
populacao. Armadilha que afeta a leitura vem aqui, onde ela morde.}

| coluna | o que e | como interpretar |
|---|---|---|
| `{coluna}` | {definicao} | {o que um valor alto ou baixo quer dizer; vazio se nao ha o que dizer} |

<!-- [py] Resultado: calculo -->
<!--
- assert de contagem depois de todo join: o join nao perde nem duplica linha;
- recorte pequeno fica de fora por regra explicita, nao por inspecao;
- mostra(tab, "{N.m} {titulo}").
-->

<!-- [md] Resultado: leitura -->
**Leitura.** {Os numeros da saida acima, no formato brasileiro, com o principal
em negrito. O que eles autorizam concluir. A excecao, quando houver, num
paragrafo proprio em negrito. A ressalva de tamanho de amostra quando o
recorte for pequeno.}
