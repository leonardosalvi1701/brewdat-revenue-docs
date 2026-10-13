---
id: ADR-0014
titulo: Documentacao de notebook dentro do notebook, com padrao extraido do notebook 30
status: proposta
data: 2026-10-08
projeto: docsquad
autor: Leonardo Salvi
substitui:
substituida_por:
impacta: [templates-notebook-doc, contracts-estilo-notebook, glossario]
---

# ADR-0014: Documentacao de notebook dentro do notebook, com padrao extraido do notebook 30

## Contexto
`templates/notebook-doc.md` previa um documento separado sobre o notebook,
com Proposito, Entradas, Saidas, Decisoes embutidas, Blocos, Armadilhas e
Como executar. Nao havia contrato de estilo para notebook, e nenhum
documento no corpus seguia esse template.

O notebook 30, perguntas da revisao de negocio sobre a previsao de conversao,
no repositorio de modelagem, foi lido em 08/10/2026. Ele tem 55 celulas, 37 de
markdown e 18 de codigo, e documenta a si mesmo:

- tres celulas de abertura, antes de qualquer codigo: cabecalho com a tabela
  de perguntas e `O que ele nao responde`, termos que confundem, e resumo com
  uma resposta curta por pergunta;
- 17 tabelas `coluna | o que e | como interpretar`, uma antes de cada saida;
- 18 celulas que comecam com `**Leitura.**`, uma depois de cada saida, com os
  numeros da celula acima;
- contrato de leitura em codigo: `require_columns`, `assert_unique` antes de
  join e assert de contagem depois;
- as armadilhas documentadas na secao em que aparecem, e nao numa secao
  propria no fim.

## Alternativas consideradas
| Alternativa | A favor | Contra | Descartada porque |
|---|---|---|---|
| Manter o documento separado | ja estava no template | desatualiza no primeiro commit que muda uma celula, e quem abre o notebook nao o encontra | nenhum documento do corpus chegou a seguir o template |
| Documento separado gerado a partir do notebook | uma fonte so | precisa de gerador, e o que o leitor de negocio le e o notebook | resolve um problema que a documentacao dentro do notebook nao tem |
| Documentacao dentro do notebook, com o 30 como exemplar | descreve um notebook que ja passou por revisao de negocio | um exemplar so, e de analise, nao de pipeline | adotada |

## Decisao
Adotamos a documentacao de notebook dentro do proprio notebook, em celulas
markdown, com a estrutura de `templates/notebook-doc.md` e a voz de
`contracts/estilo-notebook.md`, os dois extraidos do notebook 30.

## Razao
O padrao foi extraido, e nao desenhado, como em ADR-0010. Cada regra do
contrato aponta para o que o notebook 30 faz.

As tres excecoes sao deliberadas e estao declaradas:

**A tabela de etapas para notebook de pipeline nao foi extraida.** O exemplar
e de analise, e responde perguntas. Notebook de pipeline nao tem pergunta, tem
etapa, e o template troca uma tabela pela outra. E extrapolacao ate existir um
notebook de pipeline no padrao.

**A tabela de saidas no cabecalho veio do template anterior.** O exemplar so
declara que nao grava nada. Notebook que grava precisa dizer o que, com grao e
consumidor, e a tabela de Saidas do template anterior ja fazia isso.

**Como executar saiu.** Os widgets com valor padrao cobrem os parametros, e o
exemplar nao registra cluster nem tempo. Fica o espaco para o primeiro
notebook que precisar dizer isso mostrar como.

O documento separado nao tem nenhum exemplo no corpus. O notebook 30 foi
escrito para um leitor que nao o rodou, a revisao de negocio, e por isso e o
exemplar.

## Consequencias
- `templates/notebook-doc.md` deixa de descrever um documento e passa a
  descrever a sequencia de celulas;
- `contracts/estilo-notebook.md` passa a existir, e `contracts/` passa a cobrir
  quatro dos seis padroes: card e comentario, sprint review e notebook;
- a secao Armadilhas conhecidas sai do template: armadilha vai na secao em que
  aparece, e vira assert quando da para verificar;
- `config/glossario.yaml` ganha `probabilidade de compra` e `fora do tempo`,
  que o notebook 30 define e que um leitor confundiria com
  `probabilidade de conversao` e com validacao comum;
- o revisor tecnico rastreia numero por celula do notebook, que ja era o
  formato previsto em `agent_instructions/papeis/revisor-tecnico.md`.

## Como falsificar
Se os proximos notebooks de pipeline nao conseguirem seguir o template sem
inventar secao, a extrapolacao da tabela de etapas estava errada, e o padrao
de pipeline precisa ser extraido de um notebook de pipeline real.

Se a leitura passar a repetir a tabela em prosa, linha por linha, ela virou
formalidade, e o ciclo de tres celulas precisa ser revisto para tabelas
pequenas.
