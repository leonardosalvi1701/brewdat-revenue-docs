# brewdat-revenue-docs

Contrato de trabalho neste repositório. Vale para qualquer agente de IA, seja
qual for a ferramenta. Ler antes de qualquer alteração.

Toda instrução de agente mora em `agent_instructions/`, e este arquivo é a
fonte única do contrato. Os arquivos que cada ferramenta procura na raiz e em
`.github/` são derivados, gerados por `scripts/sync_agent_files.py`, e não se
editam à mão. Particularidades de cada ferramenta ficam em
`agent_instructions/ferramentas/`.

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

- ler do Azure DevOps, do GitHub e do Databricks é permitido, pelas
  credenciais que a pessoa já configurou: comandos de leitura do `docs`
  (`collect`, `sprint`, `notebooks`, `quem-sou-eu`, `config-check`) e
  subcomandos de leitura das CLIs, como `databricks workspace list`,
  `databricks workspace export`, `databricks workspace export-dir`,
  `az boards work-item show`, `az boards query` e `gh api` com `GET`.
  Exportação vai para `knowledge/notebooks/`, que está fora do git. Ver
  ADR-0011;
- nunca escrever nesses sistemas diretamente, por nenhum caminho: nada de
  `import`, `delete`, `mkdirs`, `sync`, `update`, `create`, `comment`, nem
  requisição HTTP que não seja `GET`. Escrita só passa por proposta;
- nunca executar código nem SQL em compute do Databricks. SQL escreve tanto
  quanto lê, e execução custa dinheiro da squad;
- nunca exibir, registrar nem gravar token. Se um comando imprime credencial,
  não repassar a saída;
- nunca importar nem instanciar `docsquad.gate.executor.Executor`;
- nunca rodar `docs apply`, `docs approve` ou `docs reject`. Esses comandos são
  do humano;
- rodar `docs propose ...` é permitido, porque só cria arquivo em `pending/`.

Na escrita, a separação é física, não contratual. Se você se comportar mal,
o pior resultado possível é um arquivo JSON que ninguém aprovou. Manter assim.
A leitura é liberada por contrato, e só a leitura: a credencial da pessoa
permite escrever, e o que impede é esta seção.

## Onde escrever

Você pode editar livremente:

- `decisions/`, os ADRs;
- `knowledge/dossies/`, o corpus de referência;
- `knowledge/sprint-reviews/`, as reviews já apresentadas, que são o exemplar
  do padrão de escrita;
- `review-log/`, transcrição de revisão humana;
- `outputs/`, rascunhos de documento;
- `proposals/pending/`, via `docs propose`.

Você não edita sem pedido explícito:

- `src/docsquad/gate/`, o núcleo de segurança;
- `tests/test_gate.py` e `tests/fixtures/`, a garantia desse núcleo;
- `config/settings.yaml`, que descreve o processo real da squad;
- `proposals/approved/`, `rejected/` e `applied/`, que são decisão humana.

Você nunca edita, em nenhuma hipótese, porque são gerados: `AGENTS.md`,
`.claude/` e `.github/`. Alterar a fonte em `agent_instructions/` e rodar o
script.

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

A mensagem termina no corpo, sem trailer de autoria. Não incluir
`Co-Authored-By:`, nem linha de sessão, nem qualquer outra variante que atribua
autoria ou coautoria a ferramenta de IA, qualquer que seja o nome dela.

Autoria de commit é atribuição de trabalho a pessoas, e a política do time não
permite essa referência. Vários assistentes acrescentam esses trailers por
padrão, então é preciso omiti-los ativamente ao montar a mensagem.

## Vocabulário

`config/glossario.yaml` é canônico. Um conceito, um termo. Não introduzir
sinônimo, nem em texto gerado, nem em nome de variável.

## A sprint review

A review é o documento que a squad apresenta no encerramento da sprint, e o
padrão dela não é invenção deste repo: está em `knowledge/sprint-reviews/`,
que guarda as reviews já apresentadas. `templates/sprint-review.md` reproduz
esse padrão, e `contracts/estilo-sprint-review.md` descreve a voz.

O fluxo é `docs collect`, depois `docs sprint-review`, que gera em `outputs/`
um rascunho com a estrutura e os cards da pessoa, e nada mais. A prosa é de
quem viveu a sprint, ou do papel `escritor-sprint-review` a partir da
transcrição dela.

O gerador não escreve narrativa de propósito. O card registra o que foi feito;
por que foi feito e o que ficou decidido não estão em campo nenhum do DevOps.
Texto plausível sobre trabalho que ninguém descreveu é pior que uma lacuna
visível, porque a lacuna alguém preenche.

## O padrão de card

`templates/card.md` define o corpo do card: Descrição, DoR, DoD e lista de
tarefas. `templates/card-comment.md` define o comentário de atualização, e
`contracts/estilo-card.md` descreve a voz dos dois.

O padrão foi extraído dos cards reais da S3-Q3-26, e não desenhado. Ao alterá-lo,
conferir contra o snapshot em `knowledge/cards/` antes de assumir que o
contrato está certo. Ver ADR-0010.

O DoD tem quatro blocos e se escolhe um, pela natureza do trabalho. O card só
vai para `Done` com o bloco marcado e o QA registrado em comentário.

## Cards e decisões não se misturam

O card registra que algo foi feito. O ADR registra por que uma alternativa foi
escolhida sobre outra, e sobrevive ao card. Cards vêm automaticamente do DevOps
para `knowledge/cards/`. ADRs são escritos à mão, e é o único lugar do repo com
escrita manual deliberada.

## Os papéis de agente

`agent_instructions/papeis/` contém os prompts dos papéis. Ao assumir um papel,
ler o arquivo inteiro e seguir a rubrica correspondente em
`agent_instructions/rubricas/`:

- `curador.md`: decide o que entra no contexto dos demais;
- `escritor-sprint-review.md`: escreve a review a partir do rascunho gerado,
  com `contracts/estilo-sprint-review.md`;
- `revisor-negocio.md`: otimiza compreensão, com `rubrica-negocio.yaml`;
- `revisor-tecnico.md`: otimiza lastro, com `rubrica-tecnico.yaml`.

As duas rubricas se opõem de propósito em pontos concretos. O sistema não
resolve esse conflito sozinho, e nem deveria. O autor arbitra.

## Estilo de texto gerado

- português do Brasil;
- o template manda: `templates/` define os seis padrões de documento, e
  `contracts/` define o estilo de cada um que já tem contrato escrito, hoje
  comentário de card e sprint review;
- toda afirmação com número cita a fonte, com data;
- incerteza declarada como incerteza, nunca omitida.
