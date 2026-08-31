---
id: ADR-0009
titulo: Sprint review gerada como estrutura e evidencia, nunca como prosa
status: vigente
data: 2026-08-31
projeto: docsquad
autor: Leonardo Salvi
substitui:
substituida_por:
impacta: [templates-sprint-review, contracts-estilo-sprint-review, sprint-review-py, settings-yaml, papeis]
---

# ADR-0009: Sprint review gerada como estrutura e evidencia, nunca como prosa

## Contexto
A squad ja tinha um padrao de sprint review, escrito e apresentado, num paper
mantido no Microsoft Loop. O repo tinha um `templates/sprint-review.md` que nao
era esse padrao: sete secoes organizadas por estado de card, com tabelas de
entregue, em validacao e nao entregue. O paper real se organiza por frente de
trabalho, com prosa corrida, e nao tem nenhuma dessas tres tabelas.

Duas definicoes concorrentes do mesmo documento, e a que valia na cerimonia era
a que nao estava no repo.

Ao mesmo tempo, cada pessoa da squad precisa escrever a sua parte da review, e
nao tinha como chegar aos proprios cards: `docs sprint` imprimia o board
inteiro sem filtro por responsavel, e `docs collect` falhava por completo para
quem nao tivesse token do GitHub, que a maior parte do time nao tem.

O board tambem nao devolvia grupo nenhum que casasse com o documento. O
processo da squad tem `Waiting for QA` e `Done` como estados de saida, e
`config/settings.yaml` declarava `estados_validacao: []` afirmando que nao
existia estado de validacao.

## Alternativas consideradas
| Alternativa | A favor | Contra | Descartada porque |
|---|---|---|---|
| Manter o template do repo e pedir que a squad adote | consistente com o resto do repo | ignora um padrao ja em uso e ja aprovado | o padrao nao e do repo, e da squad |
| Gerador escreve a narrativa a partir de card e commit | entrega review quase pronta | afirma o que nao foi observado | ver Razao |
| Gerador so lista cards, sem estrutura | simples, nao mente | deixa o trabalho todo de formatacao | nao resolve o problema que existia |
| Gerador monta estrutura e anexa evidencia em comentario | nao afirma nada, e poupa o trabalho mecanico | exige que a pessoa escreva | adotada |

## Decisao
Adotamos o paper real da squad como padrao: `templates/sprint-review.md`
reproduz a estrutura dele, `contracts/estilo-sprint-review.md` descreve a voz,
e `knowledge/sprint-reviews/` guarda os exemplares.

`docs sprint-review` gera um rascunho com a estrutura preenchida e os cards da
pessoa distribuidos por frente, com a materia-prima de cada card em comentario
HTML. Nenhuma frase de narrativa e gerada.

## Razao
O card registra o que foi feito. Por que foi feito e o que ficou decidido nao
estao em campo nenhum do Azure DevOps, e sao exatamente as duas coisas que
fazem a review valer a leitura.

Um gerador que preenchesse essas duas por inferencia produziria paragrafos
plausiveis sobre trabalho que ele nao viu. E o pior resultado possivel para
este documento especifico, porque a review e onde a squad afirma o que fez, na
frente de quem decide prioridade. Uma lacuna visivel alguem preenche; um
paragrafo plausivel alguem aprova.

A materia-prima vai em comentario, e nao no corpo, pelo mesmo motivo: texto no
corpo vira texto final por inercia.

## Consequencias
- `config/settings.yaml` passa a declarar `estados_validacao: [Waiting for QA]`
  e `estados_concluidos: [Done]`, e `sprint_board` devolve o grupo
  `concluidos`. O comentario que afirmava a inexistencia de estado de
  validacao era falso e foi corrigido;
- `Waiting for QA -> Done` entra em `transicoes_bloqueadas`, pela mesma regra
  que ja bloqueava as outras transicoes para `Done`;
- `docs sprint` ganha `--meus` e `--de`, e `docs quem-sou-eu` resolve a
  identidade pelo proprio PAT. Ninguem digita o nome de outra pessoa por
  engano;
- `docs collect` degrada em vez de falhar quando GitHub ou Databricks nao
  respondem, e registra a ausencia no snapshot. A ausencia de coleta aparece no
  rascunho como ausencia de coleta, e nunca como ausencia de trabalho;
- a frente e inferida do card pai, com area path como segunda opcao. Quando
  nao da para inferir, o rascunho diz `Frente a definir` em vez de escolher;
- existe o papel `escritor-sprint-review`, cujo limite declarado e o mesmo:
  onde falta material, ele deixa a pergunta, nao o paragrafo.

## Como falsificar
Se, ao longo de duas ou tres sprints, as pessoas passarem a escrever a review
fora do repo e usar o rascunho so como checklist de cards, entao a estrutura
nao era o gargalo e o gerador esta resolvendo o problema errado. O sinal a
observar e o numero de arquivos em `outputs/` que chegam a ter prosa.

Se, ao contrario, os blocos comecarem a ser preenchidos com paragrafos vagos e
intercambiaveis, a lacuna visivel nao estara funcionando como pedido, e o
caminho passa a ser a entrevista guiada, e nao a geracao.
