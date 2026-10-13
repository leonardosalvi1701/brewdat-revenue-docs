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
Um humano aprova e se identifica, num de dois lugares: na janela de permissão
da ferramenta de IA, quando o agente pede `docs approve`, ou no
`docs decidir`, num terminal dele. Um executor separado aplica apenas o que
está em `proposals/approved/`. Ver ADR-0015.

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
  `import`, `delete`, `mkdirs`, `sync`, `update`, `create`, `comment`,
  `assign`, nem requisição HTTP que não seja `GET`. Escrita só passa por
  proposta;
- nunca executar código nem SQL em compute do Databricks. SQL escreve tanto
  quanto lê, e execução custa dinheiro da squad;
- nunca exibir, registrar nem gravar token. Se um comando imprime credencial,
  não repassar a saída;
- nunca importar nem instanciar `docsquad.gate.executor.Executor`;
- rodar `docs propose ...` é permitido, porque só cria arquivo em `pending/`;
- pedir `docs approve <id> --aplicar` ou `docs reject <id> --reason "..."` é
  permitido só nas condições da seção abaixo. A ferramenta pergunta à pessoa
  antes de executar, sempre, e o clique dela é a aprovação;
- nunca rodar `docs decidir` nem `docs apply`. O primeiro é o caminho do
  terminal da pessoa; o segundo já vem junto do `approve --aplicar`;
- nunca contornar a janela de permissão: nada de chamar `ProposalStore` em
  Python, mover ou editar JSON em `proposals/`, juntar vários `approve` num
  comando composto, ou mexer em `.claude/settings.json`, `.codex/rules/`,
  `.github/hooks/`, `agent_instructions/aprovacao.yaml` ou
  `scripts/hooks/`. Se um `approve` rodar sem a ferramenta ter perguntado,
  avisar a pessoa na hora: a configuração está quebrada.

Na escrita, a separação depende da janela de permissão da ferramenta, gerada
por `scripts/sync_agent_files.py`. Se você se comportar mal, o pior resultado
possível é uma pergunta que a pessoa recusa. Manter assim.
A leitura é liberada por contrato, e só a leitura: a credencial da pessoa
permite escrever, e o que impede é esta seção.

## Como responder a um pedido de escrita

A pessoa vai pedir mudança em card sem saber, ou sem lembrar, que a escrita
passa por proposta. "Comenta isso no card", "muda pra Waiting-Development",
"atribui a mim", "põe a tag X" são todos pedido de escrita, qualquer que seja
o verbo usado. Nesses casos, sempre:

1. gerar a proposta com `docs propose ...`, nunca pular direto pra explicar;
2. rodar `docs show <id>`, para o conteúdo exato que vai ser publicado
   aparecer na conversa. É o que a pessoa confere antes de aprovar;
3. se ela pediu para publicar, e não só para rascunhar, pedir
   `docs approve <id> --aplicar`, um comando por proposta. Avisar antes que a
   ferramenta vai perguntar, e que aprovar ali publica o que o `show`
   mostrou;
4. se ela recusar na janela, ou pedir ajuste, não tentar de novo: ajustar e
   gerar proposta nova, ou recusar a antiga com `docs reject` se ela pedir;
5. se ela só pediu rascunho, parar na proposta e dizer que ela aprova quando
   quiser, pedindo no chat ou com `docs decidir` num terminal dela.

Isso vale pra toda proposta, não só card: comentário, transição, atribuição,
tag, criação de card e escrita de notebook seguem o mesmo aviso.

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
- `proposals/approved/`, `rejected/` e `applied/`, que são decisão humana;
- `agent_instructions/aprovacao.yaml` e `scripts/hooks/`, que definem quando
  a ferramenta pergunta antes de decidir proposta.

Você nunca edita, em nenhuma hipótese, porque são gerados: `AGENTS.md`,
`.claude/`, `.codex/` e `.github/`. Alterar a fonte em `agent_instructions/` e rodar o
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
  card e comentário de card, sprint review e notebook;
- documentação de notebook mora no próprio notebook, em células markdown, e
  não em arquivo separado. Ver `contracts/estilo-notebook.md` e ADR-0014;
- toda afirmação com número cita a fonte, com data;
- incerteza declarada como incerteza, nunca omitida.
