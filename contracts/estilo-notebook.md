# Contrato de estilo: notebook

Carregado sempre no prompt de quem escreve ou revisa documentacao de notebook.
Nao vai para o indice de busca, porque estilo e configuracao, nao
conhecimento.

O padrao foi extraido do notebook 30, perguntas da revisao de negocio sobre a
previsao de conversao, no repositorio de modelagem, lido em 08/10/2026: 55
celulas, 37 de markdown e 18 de codigo, com 17 tabelas de colunas e 18
leituras. O notebook nao e copiado para este
repo, porque modelagem se referencia e nao se copia. Quando este contrato e o
exemplar divergirem, o exemplar manda. Ver ADR-0014.

## Onde a documentacao mora
No proprio notebook, em celulas markdown intercaladas com o codigo. Um
documento separado sobre o notebook desatualiza no primeiro commit que muda
uma celula, e quem abre o notebook nao o encontra.

## Estrutura
`templates/notebook-doc.md`. Tres celulas de abertura, nesta ordem, antes de
qualquer codigo:

1. **Cabecalho**: o tema e o contexto de negocio, por que a analise existe,
   o que o notebook entrega, a tabela de perguntas com a secao de cada uma,
   e `O que ele nao responde`;
2. **Termos e variaveis**: os conceitos que confundem quando lidos sem aviso,
   um dicionario das variaveis de negocio e derivadas, e a regra de leitura
   que vale para o notebook inteiro;
3. **Resumo**: a regua e a data dos numeros, a abordagem metodologica em uma
   frase, e uma resposta curta por pergunta, com numero e interpretacao.

Quem le so as tres primeiras celulas sai com a resposta. O resto e lastro.

## Contexto e explicacao dos conceitos
Documentacao nao pode depender de o leitor conhecer o tema ou ter acompanhado
o desenvolvimento. Antes de apresentar uma analise nova, explique em prosa
Markdown qual problema de negocio esta sendo observado, quais conceitos de
volume, desconto ou outros termos centrais significam neste contexto, e como
eles se relacionam. Diga por que cada bloco de analise existe e como ele
prepara a leitura do proximo. Uma tabela de variaveis complementa essa
explicacao, mas nao a substitui.

Cada secao que introduz pergunta, conceito, fonte ou logica nova comeca com
um texto que explique o objetivo da secao e a ideia que sera aplicada, antes
do codigo e dos resultados. Ao mudar a populacao, a unidade de analise, a
definicao de uma variavel ou a regra de calculo entre secoes, explique a
mudanca no ponto em que ela ocorre e o efeito que pode ter na comparacao.

## Metodologia
A secao de metodologia declara, em linguagem de negocio e com os nomes de
codigo quando necessario:

- a pergunta ou hipotese que orienta a analise;
- a populacao, unidade de analise, grupos comparados e criterios de inclusao
  ou exclusao;
- as fontes, o periodo observado, a janela de referencia e as datas de corte;
- como volume, desconto, linha de base, metricas e indicadores sao calculados,
  incluindo formulas e transformacoes que afetam a interpretacao;
- por que essa comparacao responde a pergunta, quais premissas exige e quais
  conclusoes ela nao permite.

Quando a metodologia muda de uma pergunta para outra, descreva a variacao na
abertura da secao correspondente. Nao deixe filtros, denominadores, grupos de
referencia ou diferencas entre valores cadastrados e realizados implicitos no
codigo.

## Dicionario de variaveis
O dicionario registra as variaveis relevantes para a conclusao: entradas,
variaveis de negocio, variaveis derivadas, desfechos, grupos e indicadores.
Use os nomes exatamente como aparecem no codigo e inclua:

| variavel no codigo | significado no contexto | origem ou calculo | unidade/grao | uso na analise |
|---|---|---|---|---|
| `{nome}` | {o que representa, em termos de negocio} | {fonte ou formula} | {unidade e nivel de observacao} | {como entra na comparacao e como ler valores} |

Explique siglas e diferencie variaveis parecidas, por exemplo desconto
cadastrado de desconto realizado, volume ofertado de volume convertido, ou
valor absoluto de percentual. Se a mesma variavel muda de significado,
unidade ou calculo entre secoes, documente cada uso junto da secao. Nao liste
nomes tecnicos sem explicar o que representam; nao inclua variaveis auxiliares
de codigo que nao mudam a leitura do negocio.

Depois vem a configuracao, a secao 1 com a metodologia e a regua, e uma secao
por pergunta. Cada secao introduz seu conceito, objetivo, recorte e logica em
Markdown. Dentro de cada secao, cada tabela ou grafico e um ciclo de tres
celulas: abertura em Markdown, calculo em codigo, leitura em Markdown. Ao
fim, uma sintese interpreta o conjunto das secoes e responde a pergunta
principal do notebook.

## O que ele nao responde
Obrigatorio, e logo no cabecalho. E o limite que um leitor apressado
atravessaria. No exemplar: "Nenhum numero aqui e efeito causal da politica de
desconto", seguido de qual estudo responderia, o experimento de campo com
controle e tratamento sorteados.

Declara tambem o que o notebook grava. "Nao grava nenhuma tabela e nao
reestima o modelo em producao" e resposta, e e a primeira coisa que quem vai
rodar precisa saber.

## A tabela de colunas
Toda tabela de resultado e precedida, na celula de abertura, por uma tabela
`coluna | o que e | como interpretar`. A coluna vai em codigo, exatamente
como sai no print. "Como interpretar" diz o que um valor alto ou baixo quer
dizer, ou qual valor reprova. Fica vazia quando nao ha o que dizer: celula
vazia e melhor que obviedade.

Colunas que andam juntas dividem a linha: "`com_recomendacao` e
`pct_com_recomendacao`". Quando o denominador muda entre colunas parecidas, a
tabela diz qual e: "a fatia **dentro da categoria**" contra "o peso deles
**no universo inteiro**".

## A leitura
Toda saida e seguida de uma celula que comeca com `**Leitura.**`. Ela:

- repete os numeros da saida que sustentam a conclusao, e nao todos;
- poe o numero principal em negrito: "a nossa probabilidade ordena a
  conversao com **AUC 0,925**";
- diz o que o numero autoriza concluir, e para por ai;
- interpreta o resultado no contexto do conceito e da hipotese apresentados,
  explicando o que o padrao observado mostra e como se relaciona a pergunta;
- separa a excecao em paragrafo proprio, com abertura em negrito: "**A
  excecao e o par sem historico proprio**";
- explica a excecao quando ha explicacao, e diz quanto ela pesa: "esse grupo
  converte 0,07% e responde por menos de 2% das conversoes".

Leitura nao repete a tabela em prosa. Se todas as linhas importam, a tabela ja
disse.

## Sintese final
Depois dos resultados, inclua uma sintese em Markdown que retome a pergunta
principal e interprete conjuntamente os achados das secoes. Explique quais
padroes convergem, quais divergem, o que os resultados sustentam e quais
limites impedem conclusoes mais fortes. Diferencie resultado observado de
efeito causal e nao invente explicacoes que os dados ou o notebook nao
mostram. Quando nao houver saidas de execucao disponiveis, declare que a
interpretacao quantitativa esta pendente; nao substitua a sintese por uma
conclusao especulativa.

## Numero
- formato brasileiro: 0,925, 683.661, 3,94 milhoes. A saida do codigo pode
  sair em formato americano; a leitura converte;
- data em dd/mm/aaaa na prosa. Semana e mes em codigo ficam como o dado traz;
- a regua e a data de referencia aparecem uma vez, no resumo, e de novo em
  toda secao que use outra regua;
- amostra pequena se declara junto do numero: "com 42 conversoes a AUC tem
  incerteza de alguns centesimos. O que eles mostram e ordem de grandeza";
- metrica que mede uma coisa nao responde por outra. No exemplar, AUC mede
  ordenacao e observado sobre previsto mede nivel, e as duas se leem
  separadas. Metrica que so se compara na mesma populacao diz isso: "Log-loss
  e Brier ficam menores fora do tempo porque a conversao do periodo avaliado
  e menor, e nao porque o modelo melhorou."

## Recortes
Total e quebra por categoria lado a lado, na ordem fixa BEER, NAB, MATCH.
Cerveja e a linha que decide, e a leitura comeca por ela quando ela diverge
do total.

O recorte que infla o agregado se declara. No exemplar, a AUC do total
mistura dois grupos que convertem em niveis muito diferentes, e a
discriminacao real e lida dentro de cada grupo, com o piso
`auc_so_historico` ao lado para mostrar quanto vem so da separacao.

## Comparacao com modelo de outro time
Antes de qualquer numero, uma tabela do que cada um preve: evento, grao, do
que depende, para que serve. O exemplar abre a secao 2 com "os dois modelos
respondem perguntas diferentes" e so depois compara.

A comparacao mede quanto o score do outro informa a nossa decisao, e nao qual
modelo faz melhor o proprio trabalho. Nunca critica a viabilidade ou o impacto
do trabalho de outro time, mesma regra de `templates/paper-negocio.md`.

## Armadilha
Documentada onde ela morde, no paragrafo da secao que a encontra, com o caso
concreto: "o Phoenix rotula o SKU 'BRAHMA CHOPP 600ML' como
`SKOL_PILSEN_INTEIRA`". E protegida por assert no codigo quando da para
verificar. A secao de armadilhas no fim do notebook nao existe mais: ninguem
le o fim antes de errar.

## Codigo
- todo caminho de tabela e todo parametro vem de widget, com padrao. Quando o
  padrao nao e obvio, o comentario acima diz por que esse valor;
- `require_columns` na leitura de toda tabela externa, com a mensagem dizendo
  qual contrato quebrou;
- `assert_unique` antes de join, e assert de contagem depois: o join nao
  perde nem duplica linha;
- `mostra(pdf, titulo)` em toda tabela, com titulo numerado igual ao da
  secao, para o print do run ser legivel fora do notebook;
- paleta fixa por serie e por categoria, igual entre notebooks do mesmo
  projeto, e rotulo direto na serie em vez de legenda;
- comentario de codigo diz por que, nunca o que.

## Voz
- primeira pessoa do plural para o nosso trabalho: "a nossa probabilidade",
  "prevemos";
- presente no resultado, passado so no que aconteceu uma vez: "foi
  reajustado com o mesmo codigo";
- termo canonico de `config/glossario.yaml`. Termo que o notebook define e o
  glossario nao tem entra na celula de termos, e vira candidato ao glossario;
- sem travessao em prosa corrida. Virgula, dois pontos ou parenteses.
  Travessao permitido no titulo do notebook e em itemizacao.

## Fonte do conteudo
O proprio notebook, com as saidas do run que a leitura cita. Leitura escrita
antes do run, ou sobre saida de outro run, nao vale: o numero da prosa tem que
ser o numero da celula acima dela.
