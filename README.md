# brewdat-revenue-docs

Repositorio de documentacao assistida da squad Revenue. Conecta Azure DevOps,
GitHub e Databricks para ajudar o time a documentar o que foi feito em outros
ambientes, sempre sob validacao humana explicita.

Este repo nao contem modelagem. A modelagem vive em
`brewdat-saz-saz-sales-revenue-promophoenix-volume-mlp`. A ligacao entre os
dois se faz por referencia, nunca por copia de codigo.

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

## Roda em qualquer agente de IA

O contrato de trabalho esta em `AGENTS.md`, fonte unica. Cada agente procura
instrucao num arquivo diferente, entao os demais sao gerados:

| Agente | Le | Origem |
|---|---|---|
| Codex | `AGENTS.md` | fonte |
| Claude Code | `CLAUDE.md`, `.claude/commands/` | gerado |
| Copilot | `.github/copilot-instructions.md`, `.github/prompts/` | gerado |

```bash
python scripts/sync_agent_files.py           # regenera os derivados
python scripts/sync_agent_files.py --check   # falha se algum estiver atrasado
```

Os papeis de `agents/` viram slash command em todos eles: `/curador`,
`/revisor-negocio`, `/revisor-tecnico`. Os wrappers nao contem instrucao
propria, so apontam para o arquivo do papel, para nao divergir.

---

## Instalacao

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env    # preencher PATs
docs config-check       # valida credenciais sem escrever nada
```

---

## Fluxo de uma sprint

```bash
docs sprint                        # o que esta aberto, o que aguarda validacao
docs collect                       # snapshot: cards + commits + notebooks
docs notebooks                     # inventario, quais nao tem cabecalho documentado

docs propose comment 2680725 --file rascunho.md
docs review                        # propostas pendentes
docs show a3f9c210                 # o texto exato que sera publicado
docs approve a3f9c210 --by "Leo"
docs apply --all --dry-run         # confere antes
docs apply --all
```

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
| `agents/` | prompts e rubricas dos agentes |
| `review-log/` | comentarios de revisores humanos, transcritos |
| `knowledge/` | corpus recuperavel: snapshots, dossies, papers |
| `proposals/` | o portao. Auditavel via historico do git |

---

## Os cinco padroes de documento

1. **Paper tecnico** (`templates/paper-tecnico.md`) - engenharia ou ciencia de dados
2. **Paper de negocio** (`templates/paper-negocio.md`) - teto de 10 paginas
3. **Comentario de card** (`templates/card-comment.md`) - formato 📌 da squad
4. **Documentacao de notebook** (`templates/notebook-doc.md`)
5. **Sprint review** (`templates/sprint-review.md`)

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
