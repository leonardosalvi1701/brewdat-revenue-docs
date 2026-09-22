---
id: ADR-0013
titulo: Tag de card entra como novo tipo de proposta
status: vigente
data: 2026-09-22
projeto: docsquad
autor: Leonardo Salvi
substitui:
substituida_por:
impacta: [contrato, docsquad-cli, docsquad-gate]
---

# ADR-0013: Tag de card entra como novo tipo de proposta

## Contexto
Depois do ADR-0012 (atribuicao de responsavel como proposta), apareceu a
mesma lacuna para `System.Tags`: nao ha `docs propose tag`, nem metodo de
escrita para tags em `DevOpsClient`. Em 22/09/2026, ao revisar os tres cards
do epico #2613941 (#2718847, #2748628, #2748621), so o primeiro tinha tags
("Mudanca de Escopo", "Otimizacao", "Transbordo"); os outros dois estavam sem
nenhuma.

`System.Tags` e uma string unica separada por `;`, nao uma lista no sentido
da API. Escrever a tag exige saber o valor atual, senao a escrita apaga
qualquer tag que ja exista — diferente de `AssignedTo`, que e valor unico e
pode ser sobrescrito direto.

## Alternativas consideradas
| Alternativa | A favor | Contra | Descartada porque |
|---|---|---|---|
| Sem caminho para tag, edicao manual no DevOps | menor superficie de escrita | mesma friccao ja resolvida para atribuicao volta a existir para tag | inconsistente ter um campo de metadado coberto e outro nao |
| Executor le o card e funde a tag no momento de aplicar | proposta fica simples de gerar | `docs show` deixaria de mostrar o conteudo exato que sera publicado, porque o valor final so existe na hora da aplicacao | contraria o proposito de `show`, que e exibir "o conteudo exato que sera publicado" |
| `docs propose tag` le o card no momento de propor, calcula a string final (tags atuais + nova, sem duplicar) e guarda o valor final no payload; executor so sobrescreve | `docs show` mostra o valor final de verdade, antes da aprovacao; execucao vira so escrita, como as demais | proposta fica "desatualizada" se o card mudar de tag entre propor e aplicar | risco aceito: o mesmo existe hoje para `card_transition`, que guarda `from_state` fixo, e o executor nao le o estado atual antes de aplicar |

## Decisao
Adotamos `card_tag` como novo tipo de proposta. `docs propose tag` le as tags
atuais do card, calcula a string final (atuais + nova, sem duplicar) e grava
esse valor final no payload. O executor so sobrescreve `System.Tags` com o
valor gravado, sem reler o card.

## Razao
Calcular o valor final no momento de propor mantem `docs show` fiel ao seu
proposito — mostrar exatamente o que vai ser publicado — e evita que o
executor precise de uma leitura extra so para aplicar uma escrita, o que
inverteria a regra de que leitura e escrita passam por caminhos diferentes.
O risco de a proposta ficar desatualizada entre propor e aplicar ja existe
para `card_transition` e nunca foi tratado como bloqueador.

## Consequencias
- novo subcomando `docs propose tag <card_id> <tag>`, que le
  `System.Tags` do card, monta a lista final sem duplicar e gera proposta do
  tipo `card_tag` com o valor final no payload;
- `DevOpsClient` ganha `set_tags(work_item_id, tags)` na secao ESCRITA (so
  chamada pelo Executor), ao lado de `set_assigned_to` e `set_state`;
- `src/docsquad/gate/executor.py` passa a reconhecer `card_tag`, sem
  checagem de politica propria — tag nao muda estado nem cria item, mesmo
  raciocinio ja aplicado a `card_comment` e `card_assign`;
- `tests/test_gate.py` ganha cobertura de `card_tag` no mesmo padrao dos
  outros tipos;
- nao introduz lista de tags permitidas nem bloqueadas — tag e rotulo, nao
  aciona transicao nem fecha card.

## Como falsificar
Se `docs propose tag` gerar uma proposta cujo `docs show` nao bate com o
que de fato aparece no card depois de aplicada (por exemplo, apagando tag
que ja existia), a decisao falhou. Nesse caso o caminho de sobrescrita
simples deve virar leitura-e-fusao no momento da aplicacao, mesmo com o
custo de inverter a regra de leitura separada de escrita.
