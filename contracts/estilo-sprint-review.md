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

Frentes com etapas diferentes continuam separadas quando isso muda o que foi
entregue ou o que bloqueou a entrega. Nao misture a migracao de um modelo ja
existente com a produtizacao de outro, mesmo que ambos usem o Monorepo ou o
Airflow. Confirme pelo titulo, descricao, tags e comentarios dos cards qual
modelo e etapa cada atividade descreve.

Card e rastreabilidade, nao fronteira narrativa. Um produto pode ter cards
separados para features/treino, predict/serving e documentacao. Agrupe-os na
frente do produto, mas preserve cada etapa e seu estado no fechamento da
sprint. Nao apresente como entrega concluida uma etapa cujo codigo passou em
desenvolvimento enquanto a publicacao ou execucao em producao ficou bloqueada.

## Voz
- prosa corrida, paragrafos, nao bullets. Bullet so nos fechadores;
- verbo no passado e voz impessoal: "foi concluida a validacao", nao
  "eu validei";
- o card e rastreabilidade, nao assunto. O numero do card nao aparece no
  corpo do texto. O que aparece e a atividade;
- sem travessao em prosa corrida. Virgula, dois pontos ou parenteses.
  Travessao permitido apenas em itemizacao.

## Formato do bloco
Dois formatos convivem no exemplar. A escolha e pelo conteudo do bloco, nao
por preferencia de quem escreve.

Prosa corrida direta serve para um bloco com poucas decisoes concentradas:
um bug, uma negociacao de escopo, um ajuste pontual.

Rotulo fixo serve para EDA e modelagem, onde o bloco carrega muito metodo e
quem le precisa achar as tres perguntas sem ler tudo. Cada rotulo e prosa por
baixo, nao lista:

**O que foi realizado.** O resultado, numa frase, sem metodo.

**Por que foi realizado.** O problema que motivou a atividade, nao a
descricao da atividade.

**Como foi realizado.** O metodo e os numeros, com fonte.

Fecha com um paragrafo **Ou seja:**, formatado como citacao, que sintetiza a
decisao que o bloco sustenta. E o paragrafo que quem le rapido precisa achar
sem ler o resto do bloco.

O exemplar da S2 e o da S3 usam os dois formatos lado a lado, no mesmo
documento. Nenhum dos dois substitui os fechadores abaixo.

## Fechadores
Ao fim de um bloco, so quando houver o que dizer: `Pontos Positivos`,
`Pontos Negativos`, `Pontos de Atencao`, `Proximos Passos`. Um bullet por
item, especifico o suficiente para mudar comportamento na proxima sprint.

Fechador sem conteudo real nao entra. Bullet generico ocupa a linha em que
caberia o aprendizado.

## Imagens
Ate 5 por documento, as mais relevantes quando o card trouxer mais candidatas
do que isso. Vem do anexo do comentario do card, nunca gerada ou buscada por
fora. Politica registrada em 09/2026
(`review-log/2026-09-09-sprint-review-S4-Q3-26-REVENUE-DI-alice.md`). A
verificacao de correspondencia entre imagem, frente e legenda foi detalhada
apos a revisao registrada em
`review-log/2026-10-13-sprint-review-S5-leonardo.md`; quando houver um paper
apresentado com imagem em `knowledge/sprint-reviews/`, confira se o exemplar
confirma este contrato.

Cada imagem deve vir do comentario da atividade que ilustra. Confira o
conteudo visual e o nome do produto ou da DAG antes de inserir. Uma imagem de
execucao de um modelo nao serve como evidencia de outro produto so porque ambos
foram migrados na mesma sprint. A legenda deve dizer o que aparece e quando;
se a imagem nao puder ser aberta ou nao corresponder ao bloco, nao a use e
registre a lacuna.

## O que a review precisa dizer e o card nao diz
Um bloco bom responde tres coisas: o que foi feito, por que foi feito, e o que
ficou decidido. O card responde a primeira. As outras duas so existem se quem
viveu a sprint escrever.

Interferencia conta como trabalho. Bug de terceiro, ambiente indisponivel,
esteira de CI travada e descomissionamento de fonte entram no texto com o
mesmo nivel de detalhe do resto, porque e isso que explica a diferenca entre o
planejado e o entregue.

Nao confunda transbordo com trabalho nao planejado. Card transbordado e
atividade planejada que nao terminou na sprint: registre o que foi concluido
ate a data de fechamento, o que ficou pendente, o bloqueio e a passagem para a
proxima sprint. Trabalho nao planejado sem card deve ser identificado como
tal, ter a memoria do autor como fonte e ficar separado das atividades
rastreadas. Nao crie um card imaginario nem atribua esse esforco ao card da
pessoa que recebeu apoio.

Documentacao tambem e atividade. Quando houver versoes tecnica e menos
tecnica do mesmo tema, identifique cada publico e registre o avanco ocorrido
na sprint. Se uma revisao ou complemento aconteceu depois, apresente-o como
continuacao posterior, com a data da fonte, sem reclassifica-lo como entrega
da sprint.

## Numero
Todo numero cita a fonte, com data. Metrica de sprint sem valor apurado fica
em branco na tabela: celula vazia e leitura honesta, numero estimado nao e.

## Fonte do conteudo
O rascunho de `docs sprint-review`, que traz a estrutura e a materia-prima de
cada card em comentario, e a memoria de quem fez o trabalho. O agente
estrutura e revisa. Ele nao afirma o que nao esta no snapshot nem na
transcricao do autor.

O snapshot citado no frontmatter pode nao conter cards movidos para a sprint
seguinte. Quando a narrativa precisar explicar esse transbordo, consulte o
snapshot da sprint seguinte ou a leitura atual do card. Registre no frontmatter
todas as fontes adicionais usadas. Use comentarios posteriores apenas para
explicar a continuacao; a situacao no encerramento vem do ultimo comentario
ate a data final da sprint. Deixe explicita a data quando resumir um estado
posterior. O card atual sozinho nao prova qual era a situacao no encerramento.
