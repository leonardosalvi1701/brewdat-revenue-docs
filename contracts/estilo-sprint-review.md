# Contrato de estilo: sprint review

Carregado sempre no prompt de quem escreve a review. Nao vai para o indice de
busca, porque estilo e configuracao, nao conhecimento.

O padrao foi extraido do paper real da squad, em
`knowledge/sprint-reviews/`. Quando este contrato e o exemplar divergirem, o
exemplar manda, e este arquivo e que esta desatualizado.

## Estrutura
`templates/sprint-review.md`. Cinco secoes, nesta ordem: objetivo do paper,
descricao da sprint, metricas, atividades desenvolvidas, reconhecimentos.

A secao 4 se organiza por frente, e nao por card. A frente e o produto ou a
solucao que o leitor reconhece: Modelo de Volume, Promo Removal, Otimizador de
Cobertura. Cada frente declara `Responsavel:` e contem um bloco por atividade,
com titulo que diz o que foi feito, e nao o numero do card.

## Voz
- prosa corrida, paragrafos, nao bullets. Bullet so nos fechadores;
- verbo no passado e voz impessoal: "foi concluida a validacao", nao
  "eu validei";
- o card e rastreabilidade, nao assunto. O numero do card nao aparece no
  corpo do texto. O que aparece e a atividade;
- sem travessao em prosa corrida. Virgula, dois pontos ou parenteses.
  Travessao permitido apenas em itemizacao.

## Fechadores
Ao fim de um bloco, so quando houver o que dizer: `Pontos Positivos`,
`Pontos Negativos`, `Pontos de Atencao`, `Proximos Passos`. Um bullet por
item, especifico o suficiente para mudar comportamento na proxima sprint.

Fechador sem conteudo real nao entra. Bullet generico ocupa a linha em que
caberia o aprendizado.

## O que a review precisa dizer e o card nao diz
Um bloco bom responde tres coisas: o que foi feito, por que foi feito, e o que
ficou decidido. O card responde a primeira. As outras duas so existem se quem
viveu a sprint escrever.

Interferencia conta como trabalho. Bug de terceiro, ambiente indisponivel,
esteira de CI travada e descomissionamento de fonte entram no texto com o
mesmo nivel de detalhe do resto, porque e isso que explica a diferenca entre o
planejado e o entregue.

## Numero
Todo numero cita a fonte, com data. Metrica de sprint sem valor apurado fica
em branco na tabela: celula vazia e leitura honesta, numero estimado nao e.

## Fonte do conteudo
O rascunho de `docs sprint-review`, que traz a estrutura e a materia-prima de
cada card em comentario, e a memoria de quem fez o trabalho. O agente
estrutura e revisa. Ele nao afirma o que nao esta no snapshot nem na
transcricao do autor.
