# Contrato de estilo: card

Carregado sempre no prompt do agente escritor. Nao vai para o indice de busca,
porque estilo e configuracao, nao conhecimento.

O padrao foi extraido dos 43 cards e 170 comentarios da sprint S3-Q3-26, lidos
em 31/08/2026. Onde este contrato e os cards divergirem, conferir o snapshot
antes de assumir que o contrato esta certo. Ver ADR-0010.

## Corpo do card
`templates/card.md`. Quatro secoes: Descricao, DoR, DoD e lista de tarefas.

- descricao em prosa, contexto e objetivo antes do escopo;
- card fora do planejamento declara a origem. Sem isso a review nao consegue
  explicar a diferenca entre planejado e entregue;
- Bug nao usa escopo. Usa Problema, Causa e Solucao ou encaminhamento, com o
  caso concreto: PDV, SKU, id de promocao;
- o DoD tem quatro blocos e se escolhe um, pela natureza do trabalho. Blocos
  nao usados se apagam: checklist que nao se aplica ensina a ignorar checklist.

## Comentario de atualizacao
`templates/card-comment.md`.

Cabecalho `📌 Update — {TIPO EM CAIXA ALTA} {numero}: {titulo}`, data em
dd/mm/aaaa na linha seguinte, paragrafo de abertura, e temas numerados em
negrito quando houver mais de um assunto.

Rotulos, todos opcionais menos o Status: `Status`, `Proximos passos`,
`Impedimento`, `QA realizado`.

## Regras de escrita
- maxima densidade de informacao em minimo de palavras;
- verbo no passado no relato, presente no resultado;
- numero sempre com fonte. "Descartava 45,7% do historico e 103.492 PDVs" e o
  padrao; "descartava boa parte" nao e;
- incerteza declarada. "Ainda em investigacao" e resposta valida; hipotese
  escrita como causa nao e;
- commits citados por sha curto e mensagem;
- sem travessao em prosa corrida. Virgula, dois pontos ou parenteses.
  Travessao permitido em itemizacao e no em dash do cabecalho.

## Um comentario por unidade de trabalho
O comentario e a materia-prima da sprint review, e e a unica fonte de "por que
foi feito" e "o que ficou decidido", que nao existem em campo nenhum do
DevOps. Card sem comentario chega na review como titulo e estado, e vira um
bloco que ninguem consegue escrever.

O cabecalho repete tipo, numero e titulo de proposito: comentario copiado para
outro card com o cabecalho antigo ja aconteceu nesta squad, e o cabecalho
completo e o que torna o erro visivel.

## Fonte do conteudo
Snapshot de `knowledge/cards/`, a secao `_commits` do card, e a transcricao
verbal do autor quando houver. O agente estrutura, nao inventa.
