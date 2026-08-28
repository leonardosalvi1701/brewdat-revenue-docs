---
id: ADR-0006
titulo: Politica do portao no processo real, testes num processo ficticio
status: vigente
data: 2026-08-28
projeto: docsquad
autor: Leonardo Salvi
impacta: [config-settings, gate-executor, tests-gate]
---

# ADR-0006: Politica do portao no processo real, testes num processo ficticio

## Contexto
`config/settings.yaml` nasceu com os estados do processo Scrum padrao do Azure
DevOps: `New`, `Approved`, `Committed`, `In Progress`, `Ready for Validation`.
A squad usa processo customizado da Ambev. Conferindo contra 23 cards reais das
sprints S2 e S3 do Q3/26, os estados observados sao `In-Refinement`,
`Waiting-Development`, `Developing` e `Done`, e os tipos sao `Technical Story`,
`Analysis Activity`, `Business Story`, `Bug` e `Action`.

Nenhum estado configurado existia. Consequencia: `sprint_board` classificava
todo card como "outros", e toda proposta de transicao caia na recusa por lista
branca. A falha era segura, mas a funcionalidade nascia morta.

Corrigir o arquivo, sozinho, cria um segundo problema. Os testes do portao liam
`config/settings.yaml` diretamente, entao passariam a depender do processo
vigente da squad. Uma mudanca legitima de processo quebraria a garantia central
do repo, e a saida mais facil seria afrouxar o teste.

## Alternativas consideradas
| Alternativa | A favor | Contra | Descartada porque |
|---|---|---|---|
| So corrigir o settings | uma linha de diff | teste continua acoplado ao processo | adia o problema para a proxima mudanca de processo |
| Congelar os estados no codigo do executor | teste estavel | politica deixa de ser configuravel | o processo muda e o codigo nao deveria |
| Settings real + fixture de teste separada | teste estavel e politica configuravel | dois arquivos para manter | adotada |

## Decisao
`config/settings.yaml` descreve o processo real da squad. O caminho e
sobrescrivel por `DOCSQUAD_SETTINGS`, e `tests/conftest.py` aponta os testes
para `tests/fixtures/settings.yaml`, um processo ficticio e estavel.

`estados_validacao` fica vazio: este processo nao tem estado de validacao
explicito. Preencher com um estado inventado faria o board mentir.

As transicoes permitidas cobrem so o avanco natural do refinamento ate o
desenvolvimento. O grafo oficial do processo ainda nao foi confirmado com o time
de processo, entao o que estiver fora continua bloqueado por omissao.

## Razao
O portao e a unica garantia estrutural do repo. Ele precisa ser testavel sem
depender de como a squad organiza o board hoje. Acoplar as duas coisas
transforma manutencao de processo em risco de seguranca.

## Consequencias
- mudanca de processo altera `config/settings.yaml` e nao toca em teste nenhum;
- a fixture nao deve refletir o processo real, de proposito;
- `devops.tipos` passou a ser lida pelo executor, ao restringir criacao de card,
  e deixou de ser configuracao morta;
- o grafo de transicoes continua incompleto e assumido, nao verificado.

## Como falsificar
Se o time de processo confirmar transicoes legitimas fora da lista branca, a
lista esta errada e deve crescer. Se aparecer um estado de validacao explicito,
`estados_validacao` deixa de ser vazio e o board volta a separar essa fatia.
