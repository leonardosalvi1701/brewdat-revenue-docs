---
id: ADR-0018
titulo: Validacao, titulo com tema e conferencia de sprint no padrao de card
status: proposta
data: 2026-11-09
projeto: docsquad
autor: Leonardo Salvi
substitui:
substituida_por:
impacta: [templates-card, contracts-estilo-card]
---

# ADR-0018: Validacao, titulo com tema e conferencia de sprint no padrao de card

## Contexto
Os cards da S3-Q4-26 chegaram ao time com titulo generico ("Implementacao de
Melhoria 1", "Implementacao de Melhoria 2") e sem sprint: o campo
`System.IterationPath` estava na raiz do projeto, e eles nao apareciam no
quadro mesmo com a sprint configurada no time. Ao preencher os cinco cards do
Leonardo em 09/11/2026, tres lacunas do `templates/card.md` apareceram:

- o template nao diz como escrever o titulo;
- o DoD diz quando o trabalho acabou, mas nao como provar que funcionou. O
  processo ja tem o campo `Evidencias da Validacao`, e o template nao fala dele;
- nada lembra de conferir sprint, tag e esforco, que ficam fora do corpo.

## Alternativas consideradas
| Alternativa | A favor | Contra | Descartada porque |
|---|---|---|---|
| Manter o template | padrao extraido dos cards reais (ADR-0010) | as tres lacunas se repetem a cada sprint | os cards de 09/11 sairam errados nos tres pontos |
| Colocar validacao como bloco do DoD | um lugar so | o DoD tem quatro blocos por natureza do trabalho, e validacao vale para todos | misturaria o criterio de pronto com a prova de resultado |
| Validacao na descricao, evidencia no campo proprio, e conferencia antes de salvar | cada coisa no lugar que o processo ja tem | um item a mais no corpo | proposta |

## Decisao
Propomos acrescentar ao padrao de card o titulo `{Tema} | {acao no contexto}`,
uma secao `Validacao` no fim da descricao, e a conferencia de sprint, tag e
esforco antes de salvar.

## Razao
A validacao escrita no inicio diz o numero que vai confirmar o trabalho, com o
valor de hoje, e o campo `Evidencias da Validacao` recebe o valor medido na
entrega. A conferencia de sprint evita card invisivel no quadro, que foi o
sintoma da S3-Q4-26.

## Consequencias
- `templates/card.md` ganha as secoes Titulo, Validacao e Antes de salvar;
- `contracts/estilo-card.md` ganha as regras de titulo, validacao e
  referencia (pasta do workspace, tabela, Loop ou monorepo, nunca repositorio
  pessoal);
- vira vigente depois de uma sprint em que os cards novos sigam o padrao.

## Como falsificar
Conferir no snapshot de `knowledge/cards/` do fim da S3-Q4-26: se os cards
com `Validacao` na descricao nao tiverem `Evidencias da Validacao` preenchido
mais do que os sem a secao, a secao nao muda a pratica e sai do template.
