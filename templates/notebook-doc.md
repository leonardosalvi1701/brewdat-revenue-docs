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

{Apresente o tema para quem ainda nao o conhece: qual problema de negocio esta
sendo observado, por que esta analise foi feita, o que o notebook entrega e
como as secoes se conectam. Explique os conceitos centrais em prosa Markdown;
nao pressuponha que o leitor conhece o experimento, as variaveis ou as
decisoes anteriores. Cada secao deve preparar a pergunta e a leitura da
seguinte.}

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
## Termos e dicionario de variaveis

{Explique em prosa os conceitos do dominio que o leitor precisa entender
antes de ver os resultados e como eles se relacionam neste notebook.}

| termo | o que e |
|---|---|
| **{termo}** | {definicao operacional, com a coluna que o materializa em `codigo`} |

| variavel no codigo | significado no contexto | origem ou calculo | unidade/grao | uso na analise |
|---|---|---|---|---|
| `{variavel}` | {o que representa em termos de negocio} | {fonte ou formula} | {unidade e nivel de observacao} | {papel na analise e como interpretar} |

{Inclua entradas, variaveis de negocio, variaveis derivadas, desfechos,
grupos e indicadores relevantes para as conclusoes. Diferencie variaveis
parecidas, como desconto cadastrado e realizado ou volume ofertado e
convertido. Use exatamente os nomes do codigo.}

{Regra de leitura que vale para o notebook inteiro, com o motivo. Ex.: "Cerveja
vem primeiro em toda leitura. BEER e perto de 90% do peso de negocio, por isso
toda tabela traz a quebra por categoria ao lado do total."}

<!-- [md] Resumo -->
## As respostas em resumo

{Declare a populacao, unidade de analise, grupos comparados, periodo observado,
data de referencia e abordagem metodologica em uma frase clara.}

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
## 1. Metodologia: {nome da abordagem}

{Antes de qualquer resultado, explique a pergunta ou hipotese; a populacao e
a unidade de analise; os grupos, criterios de inclusao e exclusao; as fontes,
periodos e datas de corte; e como a referencia, os descontos, os volumes e as
metricas sao construidos. Inclua formulas e denominadores quando afetarem a
interpretacao. Explique por que a comparacao responde a pergunta, quais
premissas exige e quais conclusoes nao permite. Decisao metodologica que ja
tem ADR cita o ADR aqui.}

<!-- [md] Resultado: abertura, uma por tabela ou grafico -->
## {N}. Pergunta {k}: {a pergunta}

### {N.m} {o que esta subsecao mede}

{Apresente o conceito e o objetivo desta secao antes do codigo. Explique o
recorte, a populacao, as variaveis usadas e a logica da comparacao. Conecte a
secao com a anterior e diga como ela ajuda a responder a pergunta principal.
Se uma definicao, filtro, denominador ou regra de calculo mudou, explique a
mudanca e seu efeito aqui. Armadilha que afeta a leitura vem aqui, onde ela
morde.}

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
em negrito. Interprete o padrao observado no contexto do conceito, da
metodologia e da pergunta desta secao; diga o que ele mostra e o que nao
permite afirmar. A excecao, quando houver, num paragrafo proprio em negrito.
A ressalva de tamanho de amostra quando o recorte for pequeno.}

<!-- [md] Sintese final -->
## O que os resultados mostram

{Retome a pergunta principal e interprete em conjunto os resultados das
secoes. Explique quais achados convergem ou divergem, o que os dados sustentam
e quais limites permanecem. Diferencie associacao observada de efeito causal.
Se as saidas do notebook nao estiverem disponiveis, declare que a sintese
quantitativa depende da execucao e nao especule sobre o resultado.}
