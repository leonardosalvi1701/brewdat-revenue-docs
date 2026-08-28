# Contrato de estilo: comentario de card

Este arquivo e carregado sempre no prompt do agente escritor. Nao vai para o
indice de busca, porque estilo e configuracao, nao conhecimento.

## Formato
Cabecalho `📌 **Atualizacao {tipo} {numero} - {DD/MM/AAAA}**`, seguido de
secoes numeradas: Contexto, O que foi feito, Resultado ou decisao,
Proximos passos.

## Regras
- Data sempre em dd/mm/aaaa
- Maxima densidade de informacao em minimo de palavras
- Verbo no passado em "o que foi feito", presente em "resultado"
- Commits citados por sha curto e mensagem
- Sem travessao em prosa corrida. Virgula, dois pontos ou parenteses.
  Travessao permitido apenas em itemizacao.
- Nunca inventar numero. Se o snapshot nao tem, o comentario nao afirma.

## Fonte do conteudo
Snapshot de `knowledge/cards/`, secao `_commits` do card em questao, e a
transcricao verbal do autor quando houver. O agente estrutura, nao inventa.
