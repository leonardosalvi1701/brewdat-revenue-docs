# brewdat-revenue-docs

Contrato de trabalho neste repositório. Vale para qualquer agente de IA: Claude
Code, Codex, Copilot, ou outro. Ler antes de qualquer alteração.

Este arquivo é a fonte única. `CLAUDE.md` e `.github/copilot-instructions.md`
são derivados, gerados por `scripts/sync_agent_files.py`. Não editar os
derivados.

## O que este repositório é

Documentação assistida da squad Revenue. Conecta Azure DevOps, GitHub e
Databricks para ajudar o time a documentar o que foi feito em outros ambientes,
sempre sob validação humana explícita.

Não contém modelagem. A modelagem vive em outro repositório, e a ligação entre
os dois se faz por referência, nunca por cópia de código.

## A regra que não se negocia

**Nenhum agente escreve em sistema externo.**

Um agente produz uma proposta, que é um arquivo JSON em `proposals/pending/`.
Um humano aprova e se identifica. Um executor separado aplica apenas o que está
em `proposals/approved/`.

Consequências práticas para você, agente:

- nunca chamar a API do Azure DevOps, do GitHub ou do Databricks diretamente;
- nunca importar nem instanciar `docsquad.gate.executor.Executor`;
- nunca rodar `docs apply`, `docs approve` ou `docs reject`. Esses comandos são
  do humano;
- rodar `docs propose ...` é permitido, porque só cria arquivo em `pending/`.

A separação é física, não contratual. Se você se comportar mal, o pior
resultado possível é um arquivo JSON que ninguém aprovou. Manter assim.

## Onde escrever

Você pode editar livremente:

- `decisions/`, os ADRs;
- `knowledge/dossies/`, o corpus de referência;
- `review-log/`, transcrição de revisão humana;
- `outputs/`, rascunhos de documento;
- `proposals/pending/`, via `docs propose`.

Você não edita sem pedido explícito:

- `src/docsquad/gate/`, o núcleo de segurança;
- `tests/test_gate.py` e `tests/fixtures/`, a garantia desse núcleo;
- `config/settings.yaml`, que descreve o processo real da squad;
- `proposals/approved/`, `rejected/` e `applied/`, que são decisão humana.

## Antes de fechar qualquer alteração

```bash
PYTHONPATH=src pytest tests/ -q
python scripts/sync_agent_files.py --check
```

Se `tests/test_gate.py` quebrar, pare tudo e conserte antes de qualquer outra
coisa. Os testes do portão usam um processo fictício em `tests/fixtures/`, de
propósito: mudança no processo real da squad nunca pode mascarar uma regressão
de segurança.

## Autoria de commit

Não incluir `Co-Authored-By: Claude ...`, `Claude-Session: ...`, nem qualquer
variante que atribua autoria ou coautoria a ferramenta de IA. A mensagem termina
no corpo, sem trailer de autoria.

Autoria de commit é atribuição de trabalho a pessoas, e a política do time não
permite essa referência. O harness do Claude Code adiciona esses trailers por
padrão, então é preciso omiti-los ativamente ao montar a mensagem.

## Vocabulário

`config/glossario.yaml` é canônico. Um conceito, um termo. Não introduzir
sinônimo, nem em texto gerado, nem em nome de variável.

## Cards e decisões não se misturam

O card registra que algo foi feito. O ADR registra por que uma alternativa foi
escolhida sobre outra, e sobrevive ao card. Cards vêm automaticamente do DevOps
para `knowledge/cards/`. ADRs são escritos à mão, e é o único lugar do repo com
escrita manual deliberada.

## Os papéis de agente

`agents/` contém os prompts dos papéis. Ao assumir um papel, ler o arquivo
inteiro e seguir a rubrica correspondente em `agents/rubricas/`:

- `curador.md`: decide o que entra no contexto dos demais;
- `revisor-negocio.md`: otimiza compreensão, com `rubrica-negocio.yaml`;
- `revisor-tecnico.md`: otimiza lastro, com `rubrica-tecnico.yaml`.

As duas rubricas se opõem de propósito em pontos concretos. O sistema não
resolve esse conflito sozinho, e nem deveria. O autor arbitra.

## Estilo de texto gerado

- português do Brasil;
- o template manda: `templates/` define os cinco padrões de documento, e
  `contracts/estilo-card.md` define o formato de comentário de card;
- toda afirmação com número cita a fonte, com data;
- incerteza declarada como incerteza, nunca omitida.
