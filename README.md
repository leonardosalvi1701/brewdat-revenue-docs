# brewdat-revenue-docs

Repositorio de documentacao assistida da squad Revenue, feito para generalizar:
cada pessoa do time liga as proprias credenciais e o agente de IA que ja usa, e
passa a interagir com os proprios cards de forma automatica e dinamica. O
agente le Azure DevOps, GitHub e Databricks, e ajuda a automatizar etapas de
documentacao e de validacao de tarefas, como escrever o rascunho da sprint
review ou o comentario de um card a partir do que de fato mudou. Sempre sob
validacao humana explicita: o agente nunca escreve nada sozinho, so propoe.

---

## O principio que organiza tudo

Nenhum agente escreve em sistema externo. Agentes produzem **propostas**, que
sao arquivos JSON em `proposals/pending/`. Um humano aprova. Um executor
separado aplica apenas o que esta em `proposals/approved/`.

A separacao e fisica, nao contratual: o codigo dos agentes nao importa o
`Executor`. Se um agente se comportar mal, o pior resultado possivel e um
arquivo JSON que ninguem aprovou.

O executor revalida a politica no momento de aplicar, nao so na geracao. Uma
transicao para `Done` continua bloqueada mesmo que tenha sido aprovada por
engano, porque fechar card e decisao humana feita na interface do DevOps.

---

## Como comecar

Passo a passo, do clone ao primeiro comentario publicado num card.

### 1. Clonar e instalar

```bash
git clone https://github.com/leonardosalvi1701/brewdat-revenue-docs.git
cd brewdat-revenue-docs
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

### 2. Autenticar nas fontes de dado

```bash
cp .env.example .env    # org, projeto e time ja vem preenchidos
```

#### 2.1 Azure DevOps (obrigatorio)

Duas formas, na ordem de preferencia do repo:

- `az login`, se voce tem o Azure CLI na maquina. Funciona sem tocar em
  `.env`.
- Sem Azure CLI, ou em sessao nao interativa: preencha `AZDO_PAT` no `.env`,
  um Personal Access Token seu com permissao de leitura de Work Items
  (gerado em `https://dev.azure.com/AMBEV-SA/_usersSettings/tokens`).

```bash
docs config-check       # valida credenciais sem escrever nada
docs quem-sou-eu        # confirma como o DevOps te identifica
```

#### 2.2 GitHub (opcional: evidencia de commit)

Sem isso, o snapshot sai sem evidencia de commit e registra a ausencia em
vez de falhar. Com isso, `docs collect` traz os commits de cada repo
configurado e os correlaciona ao card pela mensagem (`AB#2680725`,
`#2680725` ou `[2680725]`), e essa correlacao vira materia-prima para a
sprint review e para o comentario de card.

1. Gere um Personal Access Token no GitHub (Settings > Developer settings >
   Personal access tokens), com escopo de leitura de conteudo dos repos que
   voce quer acompanhar (`repo`, no classico; `Contents: Read-only`, no
   fine-grained). Se a org `BrewDat` usa SSO, autorize o token para ela logo
   depois de criar.
2. Preencha `GITHUB_TOKEN` no `.env`.
3. Confira se o repo que voce quer acompanhar esta em
   `config/settings.yaml`, em `github.repos`. E uma lista, nao um campo
   unico: se voce trabalha em mais de um repo (por exemplo o
   `BrewDat/brewtiful`, alem do repo do modelo de volume ja configurado),
   acrescente uma linha por repo:

   ```yaml
   github:
     repos:
       - BrewDat/brewdat-saz-saz-sales-revenue-promophoenix-volume-mlp
       - BrewDat/brewtiful
   ```

   Essa lista e compartilhada pela squad inteira, entao editar
   `config/settings.yaml` e igual a editar `estados_validacao` ou qualquer
   outro pedaco do processo real: vale para todo mundo, confira com o time
   antes de mudar.
4. Referencie o numero do card na mensagem de commit (`AB#2680725` ou
   `#2680725`) para a correlacao funcionar. Commit sem referencia cai em
   `commits_sem_card` no snapshot, visivel mas nao associado a nenhum card.

#### 2.3 Databricks (opcional: inventario de notebook)

Sem isso, o snapshot sai sem inventario de notebook. Com isso, o agente
sabe quais notebooks mudaram e quais ainda nao tem cabecalho documentado
(`docs notebooks`), o que tambem vira materia-prima para documentacao e
comentario de card.

1. No workspace do Databricks, va em User Settings > Developer > Access
   tokens e gere um token novo. Ele so precisa do acesso padrao do seu
   usuario ao workspace, nenhum escopo de admin.
2. Preencha `DATABRICKS_HOST` (a URL do seu workspace, por exemplo
   `https://adb-1820723078635205.5.azuredatabricks.net`) e
   `DATABRICKS_TOKEN` no `.env`.
3. Confira se os caminhos que voce quer inventariar estao em
   `config/settings.yaml`, em `databricks.paths`. Mesma logica do GitHub:
   lista compartilhada, acrescente uma linha por caminho que faltar.

```bash
docs config-check       # valida DevOps e Databricks, nao checa GitHub
docs collect            # se o GitHub estiver certo, sai sem commits_erro
```

### 3. Ligar ao agente de IA que voce usa

O repo roda em qualquer agente que leia instrucao de arquivo. Toda instrucao
mora em `agent_instructions/`, e os caminhos que cada ferramenta espera
(`AGENTS.md`, `.claude/`, `.github/`, ver tabela abaixo) sao gerados a partir
dela.

```bash
python scripts/sync_agent_files.py           # regenera os derivados
python scripts/sync_agent_files.py --check   # falha se algum estiver atrasado
```

Depois disso o agente ja enxerga o contrato e os papeis — `/curador`,
`/escritor-sprint-review`, `/revisor-negocio`, `/revisor-tecnico`, ou o
equivalente da ferramenta que voce usa — sem configuracao extra.

### 4. Puxar a sprint e gerar o paper da review

```bash
docs collect                       # snapshot: cards + commits + notebooks
docs sprint --meus                 # conferir os seus cards, nos grupos da review
docs sprint-review                 # rascunho da sua parte, em outputs/
```

Dai em diante e trabalho do papel `/escritor-sprint-review` (ver "A sprint
review" abaixo): ele le o rascunho e escreve a prosa a partir dele, nunca
inventando o que o board nao registra.

### 5. Comentar num card, sem escrever direto no DevOps

Nenhum agente chama a API do DevOps para comentar, por mais autonomia que a
ferramenta permita configurar: e a regra que nao se negocia deste repo, ver
acima. O caminho e sempre proposta, aprovacao, execucao, e so o ultimo passo
escreve de fato.

`rascunho.md`, abaixo, e onde a automacao acontece: e o agente que escreve
esse arquivo, no formato de `templates/card-comment.md` e no estilo de
`contracts/estilo-card.md`, usando como fonte o card, os commits que
referenciaram o card (se o GitHub estiver conectado) e o notebook que mudou
(se o Databricks estiver conectado). Voce so aponta o arquivo:

```bash
docs propose comment 2680725 --file rascunho.md   # agente: proposals/pending/*.json
docs review                                       # o que esta pendente
docs show a3f9c210                                # o texto exato que sera publicado
docs approve a3f9c210 --by "Seu Nome"              # humano: aprova e se identifica
docs apply --all --dry-run                        # confere antes
docs apply --all                                  # humano: so agora escreve no DevOps
```

`docs propose` e o unico comando de escrita que um agente roda por conta
propria. `approve` e `apply` sao sempre seus.

---

## Roda em qualquer agente de IA

Toda instrucao de agente mora em `agent_instructions/`, e nada de instrucao
fica solto na raiz. O contrato esta em `agent_instructions/contrato.md`, fonte
unica.

Cada ferramenta procura instrucao num caminho fixo, que ela nao deixa
configurar. Esses caminhos existem, mas sao gerados e nao se editam:

| Ferramenta | Caminho que ela procura | O que tem la |
|---|---|---|
| Codex | `AGENTS.md` | ponteiro |
| Claude Code | `.claude/CLAUDE.md`, `.claude/commands/` | ponteiro e wrappers |
| Copilot | `.github/copilot-instructions.md`, `.github/prompts/` | copia e wrappers |

O Copilot recebe copia, e nao ponteiro, porque injeta o conteudo do arquivo
direto no contexto e nao se pode contar com ele para abrir o alvo de um
ponteiro. A copia e gerada e verificada em CI, entao nao diverge. Como
regenerar e o passo 3 de "Como comecar", acima.

Os papeis de `agent_instructions/papeis/` viram slash command nas duas
ferramentas que suportam: `/curador`, `/escritor-sprint-review`,
`/revisor-negocio`, `/revisor-tecnico`.
Os wrappers nao contem instrucao propria, so apontam para o arquivo do papel,
para nao divergir. O que muda de uma ferramenta para outra, e so isso, esta em
`agent_instructions/ferramentas/`.

Alem de `docs collect`, `docs sprint` e `docs notebooks` (inventario de quais
notebooks nao tem cabecalho documentado) tambem ajudam a olhar o board antes
de escrever.

---

## A sprint review

O padrao nao e invencao deste repo. Ele vem do paper que a squad ja apresenta,
guardado em `knowledge/sprint-reviews/`: cinco secoes, atividades organizadas
por frente de trabalho e nao por card, prosa corrida em voz impessoal.
`templates/sprint-review.md` reproduz a estrutura e
`contracts/estilo-sprint-review.md` descreve a voz.

`docs sprint-review` monta o esqueleto da sua parte: pega os seus cards do
snapshot, agrupa por frente e abre um bloco por atividade, com os commits e o
ultimo comentario de cada card em comentario HTML, como materia-prima.

Ele nao escreve nenhuma frase de narrativa, e isso e deliberado. O card diz o
que foi feito; por que foi feito e o que ficou decidido nao estao em campo
nenhum do DevOps, e sao as duas coisas que fazem a review valer a leitura.
Onde falta material, o rascunho deixa a lacuna a vista. Ver ADR-0009.

---

## Estrutura

| Pasta | Papel |
|---|---|
| `src/docsquad/connectors/` | leitura dos tres sistemas. Escrita so via Executor |
| `src/docsquad/gate/` | propostas e executor. O nucleo de seguranca |
| `config/glossario.yaml` | vocabulario canonico. Um conceito, um termo |
| `decisions/` | ADRs. A fonte da verdade do "por que" |
| `contracts/` | contratos de estilo. Nao vao para o indice de busca |
| `templates/` | os cinco padroes de documento |
| `agent_instructions/` | contrato, papeis, rubricas e notas por ferramenta |
| `review-log/` | comentarios de revisores humanos, transcritos |
| `knowledge/` | corpus recuperavel: snapshots, dossies, papers, reviews |
| `proposals/` | o portao. Auditavel via historico do git |

---

## Os seis padroes de documento

1. **Paper tecnico** (`templates/paper-tecnico.md`) - engenharia ou ciencia de dados
2. **Paper de negocio** (`templates/paper-negocio.md`) - teto de 10 paginas
3. **Card** (`templates/card.md`) - Descricao, DoR, DoD e lista de tarefas
4. **Comentario de card** (`templates/card-comment.md`) - formato 📌 da squad
5. **Documentacao de notebook** (`templates/notebook-doc.md`)
6. **Sprint review** (`templates/sprint-review.md`)

Os padroes 3 e 4 foram extraidos dos 43 cards e 170 comentarios da S3-Q3-26,
e nao desenhados: cada item do DoD e um item que a squad ja usava. Ver
ADR-0010, que registra tambem as duas excecoes, o DoR e o portao de
`Waiting-QA`.

---

## Os dois revisores

Separados por objetivo e por custo do erro, nao por profundidade.

**Revisor de negocios** otimiza compreensao. Falha quando o leitor trava.
Prefere cortar precisao a manter o leitor perdido.

**Revisor tecnico** otimiza lastro. Falha quando algo e afirmado sem base ou
contradiz decisao vigente. Prefere manter precisao a facilitar leitura.

As duas rubricas se opoem de proposito em pontos concretos: um quer cortar a
formula, o outro exige. O sistema nao resolve esse conflito sozinho, e nem
deveria. O mesmo conteudo existe nas duas versoes com profundidade diferente,
e o autor arbitra o resto.

---

## Cards versus decisoes

Sao artefatos distintos e nao devem se misturar. O card registra que algo foi
feito. O ADR registra por que uma alternativa foi escolhida sobre outra, e
sobrevive ao card. Cards vem automaticamente do DevOps para `knowledge/cards/`.
ADRs sao escritos por voce. E o unico lugar do repo com escrita manual
deliberada, e e assim de proposito.

---

## Testes

```bash
PYTHONPATH=src pytest tests/ -q
python scripts/sync_agent_files.py --check
```

Os testes do portao sao a garantia central do repo. Se `tests/test_gate.py`
quebrar, pare tudo e conserte antes de qualquer outra coisa.

Eles rodam contra um processo ficticio em `tests/fixtures/settings.yaml`, nao
contra `config/settings.yaml`. E de proposito: mudanca no processo real da squad
nunca pode mascarar uma regressao de seguranca. Ver ADR-0006.
