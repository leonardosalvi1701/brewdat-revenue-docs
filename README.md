# brewdat-revenue-docs

Repositorio de documentacao assistida da squad Revenue, feito para generalizar:
cada pessoa do time liga as proprias credenciais e o agente de IA que ja usa, e
passa a interagir com os proprios cards de forma automatica e dinamica. O
agente le Azure DevOps, GitHub e Databricks, e ajuda a automatizar etapas de
documentacao e de validacao de tarefas, como escrever o rascunho da sprint
review ou o comentario de um card a partir do que de fato mudou. Sempre sob
validacao humana explicita: o agente nunca escreve nada sozinho, so propoe.

> **Depois de clonar, preencha primeiro `usuarios` e confira `databricks.perfil` em `config/settings.yaml`; so
> entao rode `scripts/preparar_ambiente.sh`, antes de usar qualquer comando
> `docs`.** O script instala o que falta, exige o login no Azure e cria o seu
> perfil SSO do Databricks. Sem ele o `docs` nao autentica. Ver
> [Preparacao do ambiente](#preparacao-do-ambiente).

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

### 1. Clonar, informar sua identidade e preparar o ambiente (obrigatorio)

```bash
git clone https://github.com/leonardosalvi1701/brewdat-revenue-docs.git
cd brewdat-revenue-docs
```

Antes de instalar ou autenticar, edite a secao `usuarios` de
`config/settings.yaml`: substitua os cinco valores `PREENCHER_...` pelos dados
da sua conta Azure, Databricks, GitHub, Azure DevOps e Git. A tabela em
[Primeiro passo](#primeiro-passo-informar-sua-identidade-depois-rodar-o-script-obrigatorio)
explica campo por campo. Confira tambem `databricks.perfil` (padrao: `revenue`).
Nao coloque tokens, senhas ou chaves nesses campos e nao inclua os valores
pessoais em commits. O script para se algum identificador estiver vazio ou
continuar com `PREENCHER_...`.

Depois de preencher a secao, prepare o ambiente:

```bash
scripts/preparar_ambiente.sh
source .venv/bin/activate
```

O script valida primeiro os identificadores pessoais; depois instala as
dependencias, instala ou atualiza o Azure CLI e a CLI do
Databricks, exige o `az login`, cria o `.env` e cria o seu perfil SSO do
Databricks. Os detalhes, as opcoes e o passo a passo manual estao em
[Preparacao do ambiente](#preparacao-do-ambiente). Em cada terminal novo:
`source .venv/bin/activate`.

Esses valores orientam e validam as conexoes: `usuarios.azure` e mostrado antes
do login e comparado com a conta autenticada; `usuarios.devops_email` preenche
`AZDO_USER_EMAIL`; `usuarios.git_email` configura o `user.email` local deste
clone; e o script seleciona a conta `usuarios.github` na CLI `gh` quando ela
ja estiver autenticada. O `GITHUB_TOKEN`, quando preenchido, e conferido com
o mesmo login. O login SSO do Databricks nao aceita um e-mail como argumento:
o navegador deve autenticar `usuarios.databricks`, e o script verifica
`databricks current-user me` antes de criar a pasta pessoal. `docs config-check`
repete as conferencias de identidade.

### 2. Autenticar nas fontes de dado

O script ja deixa DevOps e Databricks autenticados. Esta secao explica cada
fonte, e o que fazer para o GitHub, que o script nao configura.

#### 2.1 Azure DevOps (obrigatorio)

Pelo `az login` interativo. O script mostra `usuarios.azure` para orientar a
escolha no navegador e compara o valor com a conta autenticada. Nao precisa de
nada no `.env`. Quando a sessao expira, rode
`scripts/preparar_ambiente.sh` de novo (no WSL, com `--device-code`).

`az login` interativo nao recebe o e-mail como argumento. O parâmetro
`--username` e usado junto com senha e nao atende ao fluxo corporativo com MFA;
por isso, o script verifica a conta retornada e para se ela diferir de
`usuarios.azure`. Consulte a [documentacao de login interativo do Azure CLI](https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli-interactively).

`AZDO_USER_EMAIL` e preenchido a partir de `usuarios.devops_email` e usado pelo
`--meus`; `docs config-check` confirma o e-mail que o Azure DevOps devolve.
`AZDO_PAT` no `.env` fica so para execucao sem sessao interativa. Preenchido,
ele tem precedencia sobre o `az login`, e a identidade devolvida pelo DevOps
continua sendo comparada com o campo configurado.

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
2. Preencha `GITHUB_TOKEN` no `.env`. `docs config-check` consulta a identidade
   associada ao token e compara o login com `usuarios.github`.
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

O workspace nao permite gerar token pessoal: o acesso e por perfil SSO. O
comando SSO abre o fluxo do navegador e nao aceita o e-mail como argumento; o
script consulta `databricks current-user me` depois do login e para se a conta
nao corresponder a `usuarios.databricks`.

1. O nome do perfil e configurado em `databricks.perfil` no
   `config/settings.yaml`. O script cria ou autentica essa entrada em
   `~/.databrickscfg`. Para criar a mao, trocar ou recriar, ver
   [Criar o perfil do Databricks](#criar-o-perfil-do-databricks).
2. `DATABRICKS_HOST` ja vem preenchido no `.env.example` com o workspace da
   squad.
3. A pasta do produto no workspace e `/Workspace/Users/<seu login>/revenue-docs`,
   e cada pessoa tem a sua. E dela que o inventario le, e so nela que uma
   proposta aprovada pode escrever notebook. O script cria a pasta se ela
   nao existir. A mao:
   ```bash
   databricks workspace mkdirs "/Workspace/Users/<seu login>/revenue-docs" --profile revenue
   ```
   Troque `revenue` pelo valor de `databricks.perfil` se voce configurou outro
   nome.
   Em `config/settings.yaml` o caminho aparece como
   `/Workspace/Users/{usuario}/revenue-docs`: o `{usuario}` e trocado pelo
   login de quem esta autenticado, entao a mesma linha serve para a squad
   inteira.

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

Pelo chat, o caminho normal, voce so pede: "comenta isso no card 2680725".
O agente gera a proposta, mostra o texto exato com `docs show`, e pede para
rodar `docs approve <id> --aplicar`. A ferramenta para e pergunta se pode
executar: aprovar ali e a sua aprovacao, e publica. Recusar ali nao publica
nada, e a proposta continua pendente.

```bash
docs propose comment 2680725 --file rascunho.md   # agente: proposals/pending/*.json
docs show a3f9c210                                # agente: o texto exato, na conversa
docs approve a3f9c210 --aplicar                   # a ferramenta pergunta; voce aprova
```

A pergunta e garantida pela configuracao de cada ferramenta, gerada de
`agent_instructions/aprovacao.yaml` por `scripts/sync_agent_files.py`: regra
`ask` no Claude Code, regra `prompt` no Codex e hook no Copilot, no CLI e no
VS Code. O que precisa estar ligado em cada uma esta em
`agent_instructions/ferramentas/`. Ver ADR-0015.

Pelo terminal, para revisar varias de uma vez, `docs decidir` percorre as
pendentes da mais antiga para a mais nova, mostra cada uma e pergunta
`(a)provar  (r)ecusar  (p)ular  (s)air`. No fim, pergunta se aplica as
aprovadas. So roda em terminal interativo.

Nos dois caminhos a identidade de quem aprova sai do `az login`; `--by` ou
`--como` sobrescrevem. Nenhum dos comandos de decisao roda em CI.

`docs propose` e o unico comando de escrita que um agente roda sem perguntar.
Decidir e sempre seu, pela janela de permissao ou pelo terminal.

---

## Preparacao do ambiente

### Primeiro passo: informar sua identidade; depois rodar o script (obrigatorio)

Numa maquina nova, clone o repo e edite somente a secao `usuarios` de
`config/settings.yaml`. Substitua cada valor `PREENCHER_...` pelo identificador
da sua propria conta:

| Campo | O que informar |
|---|---|
| `usuarios.azure` | E-mail da conta com que voce entra no Azure (`az login`). |
| `usuarios.databricks` | E-mail/nome de usuario da conta Databricks que o perfil SSO vai autenticar. |
| `usuarios.github` | Seu login do GitHub, sem `@`. |
| `usuarios.devops_email` | E-mail associado a sua conta no Azure DevOps. |
| `usuarios.git_email` | Valor de `git config user.email`, usado nos seus commits. |

Os campos que representam e-mail podem ter o mesmo valor se voce usa o mesmo
endereco nesses servicos; `usuarios.github` continua sendo o login, nao o
e-mail. Use identificadores, nao tokens, senhas ou chaves. Esses dados sao
pessoais: nao os inclua em commits. O script recusa com uma mensagem indicando
o campo enquanto houver valor vazio ou `PREENCHER_...`; essa validacao acontece
antes de instalar dependencias ou iniciar logins.

Confira tambem `databricks.perfil`: ele deve ser o nome do perfil SSO que o
setup criara ou autenticara. O clone vem com `revenue`; mantenha esse valor se
nao tiver motivo para usar outro nome. Nao altere as demais secoes, que
descrevem a configuracao compartilhada da squad.

```bash
git clone https://github.com/leonardosalvi1701/brewdat-revenue-docs.git
cd brewdat-revenue-docs
# edite config/settings.yaml: substitua os cinco PREENCHER_... em usuarios
# e confira databricks.perfil (padrao: revenue)
scripts/preparar_ambiente.sh
```

Depois da validacao de identidade, o script faz, nesta ordem:

1. cria o `.venv` e instala `requirements.txt`;
2. instala o Azure CLI, ou atualiza se estiver abaixo do minimo;
3. **exige o `az login`**, e para se nao houver sessao valida;
4. instala ou atualiza a CLI do Databricks;
5. **usa `databricks.perfil` do `config/settings.yaml`** para criar ou
   autenticar o perfil SSO (ver
   [Criar o perfil do Databricks](#criar-o-perfil-do-databricks));
6. termina com `docs config-check`, que deve mostrar `ok Azure DevOps` e
   `ok Databricks`.

Pede `sudo` apenas para instalar ou atualizar CLI, e abre o navegador para os
dois logins. Pode ser rodado de novo sem estrago. **Rode de novo sempre que:**

- o `docs` reclamar de sessao expirada ou de credencial ausente;
- quiser trocar ou recriar o perfil do Databricks;
- quiser atualizar as CLIs (`--atualizar`);
- o `.venv` for apagado ou o `requirements.txt` mudar.

Em cada terminal novo, antes de usar o `docs`: `source .venv/bin/activate`.

| Opcao | Efeito |
|---|---|
| `--perfil revenue` | compatibilidade: valida que o nome coincide com `databricks.perfil`; configure o perfil no `settings.yaml` |
| `--atualizar` | forca atualizar `az` e `databricks` mesmo acima do minimo |
| `--device-code` | login por codigo, sem abrir navegador. Padrao no WSL |
| `--sem-databricks` | pula a instalacao e o login do Databricks durante o setup. A conferencia final ainda exige CLI e perfil Databricks validos; use se eles ja estiverem prontos. |

**No Windows, usar o WSL e rodar tudo dentro do Linux.** O `docs` so enxerga
as CLIs instaladas no mesmo ambiente em que ele roda: um `az` instalado no
Windows nao serve para o `docs` do WSL.

### Requisitos

O script garante todos. A tabela serve para conferir ou para quem prepara a
maquina a mao.

| Requisito | Versao minima | Para que serve |
|---|---|---|
| Python | 3.12 | exigido pelo projeto (`pyproject.toml`) e usado pelo `docs` |
| Azure CLI (`az`) | 2.60.0 | login no Azure, que autentica a leitura do Azure DevOps. **Obrigatorio** |
| CLI do Databricks (`databricks`) | 1.0.0 | login SSO no workspace, que autentica a leitura de notebooks |
| Sessao `az login` | valida | sem ela o `docs` nao le o board |
| Perfil SSO do Databricks | valido, com nome em `databricks.perfil` no `settings.yaml` | sem ele o snapshot sai sem inventario de notebook |

Nenhum dos dois logins usa segredo no `.env`. As CLIs guardam a sessao no
proprio cache e renovam o token sozinhas; quando a sessao expira, a mensagem de
erro diz qual login refazer.

### Criar o perfil do Databricks

O workspace nao permite gerar token pessoal, entao o `docs` acessa o
Databricks por um **perfil SSO**: uma entrada com nome no arquivo
`~/.databrickscfg`, autenticada com a sua conta corporativa. O nome e definido
em `databricks.perfil`; o clone usa `revenue`.

**Pelo script (recomendado).** Defina `databricks.perfil` em
`config/settings.yaml` (o clone vem com `revenue`) e rode
`scripts/preparar_ambiente.sh`. O script abre o login para esse perfil e
confere que `usuarios.databricks` corresponde a conta autenticada. O código do
repo sempre consulta o perfil configurado e passa `--profile` explicitamente
para a CLI.

**A mao.** Um comando cria o perfil, se ele nao existe, ou refaz o login, se
ele ja existe:

```bash
databricks auth login \
  --host https://adb-1820723078635205.5.azuredatabricks.net \
  --profile revenue
```

1. O navegador abre na tela de login da Microsoft. Entre com a conta
   corporativa. No WSL, se nao abrir, copie a URL que aparecer no terminal
   para o navegador do Windows; o login termina sozinho.
2. A CLI grava o perfil em `~/.databrickscfg`:
   ```ini
   [revenue]
   host      = https://adb-1820723078635205.5.azuredatabricks.net
   auth_type = databricks-cli
   ```
   O token nao vai para esse arquivo. Fica no cache da CLI, que o renova.
3. Confira: `databricks auth profiles` deve listar `revenue` com
   `Valid: YES`.
4. Aponte o repo para ele em `config/settings.yaml`:
   ```bash
   databricks:
     perfil: revenue
   ```
5. Confira no repo: `docs config-check` deve mostrar `ok Databricks`.

**Sessao expirada.** Rode o mesmo
`databricks auth login --host <DATABRICKS_HOST> --profile revenue`, ou o script
de novo.

**Trocar ou apagar.** Para usar outro perfil, mude somente
`databricks.perfil` no `config/settings.yaml` e rode o setup. `--perfil` e
aceito apenas como validação de compatibilidade e precisa coincidir com esse
valor. Para apagar uma entrada antiga, remova o bloco `[nome]` do
`~/.databrickscfg`.

A extensao do Databricks no VS Code usa o mesmo `~/.databrickscfg`, mas nem
todo perfil dela serve para o `docs`: so o de login SSO, com
`auth_type = databricks-cli`. Perfil `azure-cli` ou de PAT aparece como valido
em `databricks auth profiles`, mas nao atende a autenticacao SSO usada pelo
repo. Configure em `databricks.perfil` o nome de um perfil SSO.

O terminal integrado pode exportar `DATABRICKS_CONFIG_PROFILE`. O código do
repo continua usando o valor de `databricks.perfil` e passa `--profile`
explicitamente. Para comandos `databricks` digitados manualmente sem
`--profile`, essa variável ainda pode selecionar outro perfil.

### Passo a passo manual

O que o script faz, para quem prefere rodar cada etapa.

**1. Python e dependencias**

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt     # inclui o proprio repo, e cria o comando `docs`
cp .env.example .env
```

Em cada terminal novo: `source .venv/bin/activate`.

**2. Instalar o Azure CLI**

```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash    # Ubuntu, Debian e WSL
brew install azure-cli                                    # macOS
```

**3. Atualizar o Azure CLI**

```bash
az version          # confere a versao
az upgrade --yes    # atualiza pelo mesmo gerenciador que instalou
```

**4. Login no Azure (obrigatorio)**

```bash
az login                      # no navegador, escolha usuarios.azure
az login --use-device-code    # no WSL; escolha usuarios.azure no navegador
az account show               # confere quem esta logado
```

No login por codigo, abrir `https://microsoft.com/devicelogin` no navegador do
Windows e digitar o codigo que aparecer. Se a conta tiver mais de um tenant e o
login cair no errado: `az login --tenant <tenant>`.

O `docs` usa essa sessao direto, sem extensao `az devops`. Deixe `AZDO_PAT`
vazio no `.env`: preenchido, ele tem precedencia sobre o `az login`.

**5. Instalar a CLI do Databricks**

```bash
curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sudo sh   # Linux e WSL
brew tap databricks/tap && brew install databricks                                           # macOS
```

**6. Atualizar a CLI do Databricks**

```bash
databricks -v                                   # confere a versao
sudo rm /usr/local/bin/databricks               # o instalador nao sobrescreve,
curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sudo sh   # entao remove e instala de novo
brew upgrade databricks                         # macOS
```

**7. Perfil SSO do Databricks**

Seguir [Criar o perfil do Databricks](#criar-o-perfil-do-databricks), na
parte "A mao".

**8. Conferir**

```bash
docs config-check     # uma linha por item: repo, .env, DevOps, CLI, host, perfil, login, pasta
docs quem-sou-eu      # como o DevOps te identifica
```

### Quando algo falha

Primeiro rode `docs config-check`, e cole a saida inteira em qualquer pedido de
ajuda. Ele confere, em ordem, o repo contra o GitHub, o `.env`, o DevOps, a CLI
do Databricks, o host, o perfil e de onde veio o nome dele, o login e a pasta
pessoal. Cada falha diz o que fazer, e o comando sai com codigo 1 se houver
alguma. Rodar o script de novo corrige a maior parte sozinho.

| Sintoma | O que fazer |
|---|---|
| `docs: command not found` | `source .venv/bin/activate`; se nao existir `.venv`, rodar o script |
| `O az nao devolveu token` | sessao expirou: rode `scripts/preparar_ambiente.sh` para autenticar com `usuarios.azure` |
| `O perfil X nao existe` | confira `databricks.perfil` em `config/settings.yaml` e compare com `databricks auth profiles`; rode o script para autenticar |
| `O perfil X usa auth_type=azure-cli` | perfil que nao e SSO. Configure em `databricks.perfil` o nome de um perfil SSO e rode o setup |
| `A CLI do Databricks nao devolveu token` | perfil SSO com sessao expirada: o comando de login sai na mensagem |
| `CLI legada do Databricks` | pacote `databricks-cli` do pip, 0.x. O script remove do `.venv`; fora dele, `pip uninstall databricks-cli`. Depois `hash -r` |
| `bash: .../databricks: No such file or directory` | o shell lembrava de uma CLI removida: `hash -r` ou terminal novo |
| `401 Credential was not sent` | `DATABRICKS_HOST` com `http://`, `?o=` ou caminho: deixar so `https://<workspace>.azuredatabricks.net` |
| `pasta ... nao existe` | rodar o script, que cria a pasta pessoal; se o caminho for fixo, sem seu login, `git pull` |
| `repo N commit(s) atras` | `git pull` |
| `databricks.perfil nao esta definido` | defina o nome em `config/settings.yaml` e rode `scripts/preparar_ambiente.sh` |
| `autenticacao: PAT (AZDO_PAT)` sem querer | apagar o valor de `AZDO_PAT` no `.env` |
| navegador nao abre no WSL | `scripts/preparar_ambiente.sh --device-code`; no Databricks, copiar a URL |

O token de GitHub continua opcional: sem ele o snapshot sai sem evidencia de
commit, e registra a ausencia em vez de falhar. O mesmo vale para o Databricks
sem perfil.

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

| Pasta/arquivo | Papel |
|---|---|
| `src/docsquad/connectors/` | leitura dos tres sistemas. Escrita so via Executor |
| `src/docsquad/gate/` | propostas e executor. O nucleo de seguranca |
| `scripts/` | preparacao do ambiente, sincronizacao das instrucoes e hooks |
| `tests/` | testes automatizados e configuracao ficticia em `tests/fixtures/` |
| `config/glossario.yaml` | vocabulario canonico. Um conceito, um termo |
| `decisions/` | ADRs. A fonte da verdade do "por que" |
| `contracts/` | contratos de estilo. Nao vao para o indice de busca |
| `templates/` | os seis padroes de documento |
| `agent_instructions/` | contrato, papeis, rubricas e notas por ferramenta |
| `review-log/` | comentarios de revisores humanos, transcritos |
| `knowledge/` | cards, commits, notebooks, dossies e sprint reviews coletados ou de referencia |
| `outputs/` | rascunhos gerados para revisao e edicao humana |
| `proposals/` | propostas por estado (`pending`, `approved`, `rejected`, `applied`), auditaveis pelo git |

---

## Os seis padroes de documento

1. **Paper tecnico** (`templates/paper-tecnico.md`) - engenharia ou ciencia de dados
2. **Paper de negocio** (`templates/paper-negocio.md`) - teto de 10 paginas
3. **Card** (`templates/card.md`) - Descricao, DoR, DoD e lista de tarefas
4. **Comentario de card** (`templates/card-comment.md`) - formato 📌 da squad
5. **Documentacao de notebook** (`templates/notebook-doc.md`) - dentro do proprio notebook
6. **Sprint review** (`templates/sprint-review.md`)

Os padroes 3 e 4 foram extraidos dos 43 cards e 170 comentarios da S3-Q3-26,
e nao desenhados: cada item do DoD e um item que a squad ja usava. Ver
ADR-0010, que registra tambem as duas excecoes, o DoR e o portao de
`Waiting-QA`.

O padrao 5 foi extraido do notebook 30, do repositorio de modelagem, e a voz
esta em `contracts/estilo-notebook.md`. A documentacao apresenta o contexto e
os conceitos, descreve metodologia e variaveis, contextualiza cada secao,
interpreta as saidas e fecha com uma sintese. Ver ADR-0014.

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
