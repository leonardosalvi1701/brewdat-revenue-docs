#!/usr/bin/env bash
# Prepara o ambiente do docsquad do zero, e pode ser rodado de novo sem estrago.
#
# O que faz, nesta ordem:
#   1. confere o Python e instala requirements.txt num .venv;
#   2. instala o Azure CLI, ou atualiza se estiver abaixo da versao minima;
#   3. exige `az login`. Sem sessao valida no Azure, o script para aqui;
#   4. instala ou atualiza a CLI do Databricks;
#   5. exige o perfil SSO definido em databricks.perfil no settings.yaml, faz
#      o login nele se preciso e cria a pasta revenue-docs no workspace;
#   6. roda `docs config-check`, que sai com erro se algum item falhar.
#
# Tambem corrige o que travou gente da squad em 08/10/2026: remove a CLI
# legada do Databricks (pacote `databricks-cli` do pip) do .venv, tira o fim
# de linha do Windows do .env, valida o perfil SSO definido no settings e
# avisa quando o repo esta atras do GitHub.
#
# Uso:
#   scripts/preparar_ambiente.sh                  # caminho normal
#   scripts/preparar_ambiente.sh --atualizar      # forca atualizar as CLIs
#   scripts/preparar_ambiente.sh --device-code    # login por codigo, sem navegador
#   scripts/preparar_ambiente.sh --perfil revenue # valida o perfil do settings
#   scripts/preparar_ambiente.sh --sem-databricks # pula os passos 4 e 5
#
# No WSL, rodar dentro do Linux, e nao no PowerShell: o `docs` so enxerga as
# CLIs instaladas no mesmo ambiente em que ele roda. No WSL o login por codigo
# e o padrao, porque o navegador costuma nao abrir. Se o `az` do Windows
# aparecer no PATH do WSL (instalacao antiga, ou perfil que herda o PATH do
# Windows), o script detecta e instala o nativo do Linux por cima, porque o
# `az` do Windows chama `cmd.exe`, que nao entende o caminho UNC da pasta
# atual dentro do WSL e falha em qualquer comando.
#
# Pede sudo so para instalar ou atualizar CLI. Nao guarda token em lugar
# nenhum: as duas CLIs mantem a sessao no proprio cache.

set -euo pipefail

# ---------- requisitos minimos ----------
PYTHON_MIN="3.10"
AZ_MIN="2.60.0"
DATABRICKS_MIN="1.0.0"
DATABRICKS_HOST_PADRAO="https://adb-1820723078635205.5.azuredatabricks.net"
PASTA_PRODUTO="revenue-docs"

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$RAIZ/.env"
SETTINGS_FILE="$RAIZ/config/settings.yaml"

ATUALIZAR=0
SEM_DATABRICKS=0
PERFIL=""
DEVICE_CODE=0
EM_WSL=0
grep -qi microsoft /proc/version 2>/dev/null && { DEVICE_CODE=1; EM_WSL=1; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --atualizar) ATUALIZAR=1 ;;
    --device-code) DEVICE_CODE=1 ;;
    --sem-databricks) SEM_DATABRICKS=1 ;;
    --perfil) PERFIL="${2:?--perfil precisa de um nome}"; shift ;;
    -h|--help) sed -n '2,26p' "$0"; exit 0 ;;
    *) echo "Opcao desconhecida: $1" >&2; exit 2 ;;
  esac
  shift
done

passo() { printf '\n\033[1m==> %s\033[0m\n' "$*"; }
ok()    { printf '    \033[32mok\033[0m %s\n' "$*"; }
aviso() { printf '    \033[33m!\033[0m %s\n' "$*"; }
falha() { printf '\n\033[31mERRO:\033[0m %s\n' "$*" >&2; exit 1; }

# A configuracao pessoal e validada antes de instalar pacotes ou iniciar
# logins. A leitura simples evita depender de PyYAML antes da criacao do .venv.
ler_config() {
  local secao="$1" campo="$2"
  sed -n "/^${secao}:[[:space:]]*$/,/^[^[:space:]#]/p" "$SETTINGS_FILE" \
    | sed -nE "s/^[[:space:]]+${campo}:[[:space:]]*[\"']?([^\"'#]+)[\"']?[[:space:]]*(#.*)?$/\1/p" \
    | head -n1 | xargs
}
ler_usuario() { ler_config usuarios "$1"; }

passo "Identificacao pessoal"
for campo in azure databricks github devops_email git_email; do
  valor="$(ler_usuario "$campo")"
  case "$valor" in
    ""|PREENCHER*|\<*\>)
      falha "Preencha usuarios.$campo em config/settings.yaml antes de preparar o ambiente."
      ;;
  esac
done
PERFIL_CONFIG="$(ler_config databricks perfil)"
case "$PERFIL_CONFIG" in
  ""|PREENCHER*|\<*\>)
    falha "Defina databricks.perfil em config/settings.yaml antes de preparar o ambiente."
    ;;
esac
if [[ -n "$PERFIL" && "$PERFIL" != "$PERFIL_CONFIG" ]]; then
  falha "--perfil '$PERFIL' diverge de databricks.perfil='$PERFIL_CONFIG' em config/settings.yaml. Altere a configuracao e rode o setup novamente."
fi
PERFIL="$PERFIL_CONFIG"
USUARIO_AZURE="$(ler_usuario azure)"
USUARIO_DATABRICKS="$(ler_usuario databricks)"
USUARIO_GITHUB="$(ler_usuario github)"
EMAIL_DEVOPS="$(ler_usuario devops_email)"
EMAIL_GIT="$(ler_usuario git_email)"
ok "identificadores pessoais preenchidos"

# O email usado por commits neste clone vem da mesma fonte de identidade.
git -C "$RAIZ" config --local user.email "$EMAIL_GIT"
ok "git user.email=$EMAIL_GIT neste clone"

# versao_ok ATUAL MINIMA -> verdadeiro se ATUAL >= MINIMA
versao_ok() { [[ "$(printf '%s\n%s\n' "$2" "$1" | sort -V | head -n1)" == "$2" ]]; }

SO="$(uname -s)"
tem_brew() { command -v brew >/dev/null 2>&1; }
tem_apt()  { command -v apt-get >/dev/null 2>&1; }

env_get() { [[ -f "$ENV_FILE" ]] && grep -E "^$1=" "$ENV_FILE" | tail -n1 | cut -d= -f2- || true; }
env_set() {
  "$PY" - "$ENV_FILE" "$1" "$2" <<'EOF'
import re, sys
caminho, chave, valor = sys.argv[1:]
texto = open(caminho, encoding="utf-8").read()
linha = f"{chave}={valor}"
if re.search(rf"^{chave}=.*$", texto, flags=re.M):
    texto = re.sub(rf"^{chave}=.*$", linha, texto, count=1, flags=re.M)
else:
    texto = texto.rstrip("\n") + "\n" + linha + "\n"
open(caminho, "w", encoding="utf-8").write(texto)
EOF
}

MUDOU_CLI=0

# A CLI legada do Databricks e script Python; a nova e binario.
cli_legada() { head -n1 "$1" 2>/dev/null | grep -q '^#!.*python'; }
databricks_nova() {
  local c
  while IFS= read -r c; do
    cli_legada "$c" || { echo "$c"; return 0; }
  done < <(type -ap databricks)
  return 1
}

# ---------- 1. Python ----------
passo "Python e dependencias"
PY=""
for candidato in python3.12 python3 python; do
  if command -v "$candidato" >/dev/null 2>&1; then PY="$(command -v "$candidato")"; break; fi
done
[[ -n "$PY" ]] || falha "Python nao encontrado. Instale Python $PYTHON_MIN ou mais novo."
PY_VER="$("$PY" -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"
versao_ok "$PY_VER" "$PYTHON_MIN" || falha "Python $PY_VER encontrado, o minimo e $PYTHON_MIN."
ok "Python $PY_VER ($PY)"

if [[ ! -d "$RAIZ/.venv" ]]; then
  "$PY" -m venv "$RAIZ/.venv" || falha "Nao consegui criar o .venv. No Ubuntu: sudo apt install python3-venv"
fi
# shellcheck disable=SC1091
source "$RAIZ/.venv/bin/activate"
PY="$RAIZ/.venv/bin/python"
"$PY" -m pip install --quiet --upgrade pip
"$PY" -m pip install --quiet -r "$RAIZ/requirements.txt"
ok "requirements.txt instalado em .venv"

# Instalada a mao em algum momento, ela entra no PATH na frente da nova sempre
# que o .venv esta ativo, e repassa cada comando com aviso no meio da saida.
if "$PY" -m pip show databricks-cli >/dev/null 2>&1; then
  aviso "CLI legada do Databricks (pacote databricks-cli) no .venv, removendo"
  "$PY" -m pip uninstall --quiet -y databricks-cli
  hash -r
  MUDOU_CLI=1
fi

if [[ ! -f "$ENV_FILE" ]]; then
  cp "$RAIZ/.env.example" "$ENV_FILE"
  ok ".env criado a partir do .env.example"
fi
env_set AZDO_USER_EMAIL "$EMAIL_DEVOPS"
# .env editado no Windows deixa \r no fim de cada valor, e o perfil
# "revenue\r" nao existe.
if grep -q $'\r' "$ENV_FILE"; then
  "$PY" - "$ENV_FILE" <<'EOF'
import sys
caminho = sys.argv[1]
dados = open(caminho, "rb").read().replace(b"\r\n", b"\n")
open(caminho, "wb").write(dados)
EOF
  ok "fim de linha do Windows removido do .env"
fi

# Repo atrasado le config antiga, e o erro aparece la na frente, como pasta
# inexistente. So avisa: puxar e decisao de quem tem alteracao local.
if git -C "$RAIZ" rev-parse --abbrev-ref '@{u}' >/dev/null 2>&1; then
  if GIT_TERMINAL_PROMPT=0 timeout 20 git -C "$RAIZ" fetch --quiet 2>/dev/null; then
    ATRAS="$(git -C "$RAIZ" rev-list --count 'HEAD..@{u}')"
    [[ "$ATRAS" == "0" ]] && ok "repo em dia com o GitHub" \
      || aviso "repo $ATRAS commit(s) atras do GitHub. Rode: git pull"
  else
    aviso "nao consegui consultar o GitHub para conferir se o repo esta em dia"
  fi
fi

# ---------- 2. Azure CLI ----------
passo "Azure CLI (minimo $AZ_MIN)"
instalar_az() {
  if [[ "$SO" == "Darwin" ]] && tem_brew; then
    brew install azure-cli
  elif tem_apt; then
    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
  else
    falha "Nao sei instalar o az neste sistema. Siga https://learn.microsoft.com/cli/azure/install-azure-cli e rode de novo."
  fi
}

AZ_PATH="$(command -v az || true)"
if [[ -z "$AZ_PATH" ]]; then
  aviso "az nao encontrado, instalando"
  instalar_az
  hash -r
elif [[ $EM_WSL -eq 1 && "$AZ_PATH" == /mnt/* ]]; then
  # No WSL, o PATH do Windows entra depois do PATH do Linux, e sem az nativo
  # `az` resolve pro .cmd do Windows. Esse binario chama cmd.exe, que nao
  # entende o caminho UNC `\\wsl.localhost\...` da pasta atual, e falha em
  # qualquer coisa que precise atualizar ou logar. Nao e "az desatualizado",
  # e "az errado": instalar o nativo, nao tentar atualizar o do Windows.
  aviso "az encontrado em $AZ_PATH e o do Windows via interop do WSL, nao o do Linux"
  aviso "instalando a versao nativa, que passa a vencer no PATH"
  instalar_az
  hash -r
fi
AZ_VER="$(az version --query '"azure-cli"' -o tsv 2>/dev/null || echo 0)"
if [[ $ATUALIZAR -eq 1 ]] || ! versao_ok "$AZ_VER" "$AZ_MIN"; then
  aviso "atualizando az $AZ_VER"
  az upgrade --yes --all --only-show-errors || aviso "az upgrade falhou; confira manualmente com: az upgrade"
  AZ_VER="$(az version --query '"azure-cli"' -o tsv)"
fi
versao_ok "$AZ_VER" "$AZ_MIN" || falha "az $AZ_VER continua abaixo de $AZ_MIN."
ok "az $AZ_VER"

# ---------- 3. az login (obrigatorio) ----------
passo "Login no Azure (obrigatorio)"
if ! az account show --only-show-errors >/dev/null 2>&1; then
  aviso "na tela do Azure, autentique como $USUARIO_AZURE"
  if [[ $DEVICE_CODE -eq 1 ]]; then
    aviso "abra https://microsoft.com/devicelogin e digite o codigo abaixo"
    az login --use-device-code --only-show-errors >/dev/null
  else
    az login --only-show-errors >/dev/null
  fi
fi
az account show --only-show-errors >/dev/null 2>&1 \
  || falha "Sem sessao no Azure. Rode scripts/preparar_ambiente.sh para autenticar com usuarios.azure (no WSL, use --device-code)."
AZURE_ATUAL="$(az account show --query user.name -o tsv)"
if [[ "${AZURE_ATUAL,,}" != "${USUARIO_AZURE,,}" ]]; then
  falha "Azure autenticou como '$AZURE_ATUAL', mas config/settings.yaml espera '$USUARIO_AZURE'. Rode az logout --username '$AZURE_ATUAL' e depois scripts/preparar_ambiente.sh; na tela de login, escolha '$USUARIO_AZURE'."
fi
ok "logado como $AZURE_ATUAL, conforme config/settings.yaml"

# A CLI do GitHub aceita selecionar um usuario ja autenticado, mas nao
# preseleciona uma conta durante o OAuth. Se houver sessao, ativa a conta
# indicada no settings; se ela nao estiver cadastrada, falha com a instrucao.
if command -v gh >/dev/null 2>&1 && gh auth status --hostname github.com >/dev/null 2>&1; then
  GH_ATUAL="$(gh api user --jq .login 2>/dev/null || true)"
  if [[ "${GH_ATUAL,,}" != "${USUARIO_GITHUB,,}" ]]; then
    if ! gh auth switch --hostname github.com --user "$USUARIO_GITHUB" >/dev/null 2>&1; then
      falha "GitHub esta autenticado como '$GH_ATUAL'; '$USUARIO_GITHUB' (config/settings.yaml) nao esta autenticado na CLI. Rode gh auth login --hostname github.com --web com essa conta e tente novamente."
    fi
    GH_ATUAL="$(gh api user --jq .login 2>/dev/null || true)"
  fi
  if [[ "${GH_ATUAL,,}" != "${USUARIO_GITHUB,,}" ]]; then
    falha "GitHub autenticou como '$GH_ATUAL', mas config/settings.yaml espera '$USUARIO_GITHUB'."
  fi
  ok "GitHub CLI usa $GH_ATUAL, conforme config/settings.yaml"
fi

if [[ -n "$(env_get AZDO_PAT)" ]]; then
  aviso "AZDO_PAT esta preenchido no .env e tem precedencia sobre o az login."
  aviso "Apague o valor se quiser usar a sessao do Azure."
fi

# ---------- 4. CLI do Databricks ----------
if [[ $SEM_DATABRICKS -eq 0 ]]; then
  passo "CLI do Databricks (minimo $DATABRICKS_MIN)"
  instalar_databricks() {
    if [[ "$SO" == "Darwin" ]] && tem_brew; then
      brew tap databricks/tap && brew install databricks
    else
      curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sudo sh
    fi
  }
  atualizar_databricks() {
    if [[ "$SO" == "Darwin" ]] && tem_brew; then
      brew upgrade databricks
    elif [[ "$DBX" == "/usr/local/bin/databricks" ]]; then
      # O instalador oficial recusa sobrescrever; a atualizacao e remover e
      # instalar de novo, no mesmo caminho.
      sudo rm -f /usr/local/bin/databricks
      instalar_databricks
    else
      falha "databricks em $DBX, fora do caminho padrao. Atualize pelo gerenciador que o instalou."
    fi
  }

  # Daqui em diante toda chamada usa o caminho da CLI nova, e nao `databricks`
  # solto, que pode resolver para uma legada fora do .venv.
  if ! DBX="$(databricks_nova)"; then
    aviso "CLI nova do Databricks nao encontrada, instalando"
    instalar_databricks
    hash -r
    MUDOU_CLI=1
    DBX="$(databricks_nova)" || falha "Instalei a CLI do Databricks e ela nao aparece no PATH."
  fi
  DBX_VER="$("$DBX" -v 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1 || echo 0)"
  if [[ $ATUALIZAR -eq 1 ]] || ! versao_ok "$DBX_VER" "$DATABRICKS_MIN"; then
    aviso "atualizando databricks $DBX_VER"
    atualizar_databricks
    hash -r
    MUDOU_CLI=1
    DBX="$(databricks_nova)"
    DBX_VER="$("$DBX" -v | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1)"
  fi
  versao_ok "$DBX_VER" "$DATABRICKS_MIN" || falha "databricks $DBX_VER continua abaixo de $DATABRICKS_MIN."
  ok "databricks $DBX_VER ($DBX)"
  while IFS= read -r c; do
    if cli_legada "$c"; then
      aviso "CLI legada do Databricks em $c. Remova com pip uninstall databricks-cli no ambiente dela."
    fi
  done < <(type -ap databricks)

  # ---------- 5. perfil SSO (obrigatorio) ----------
  passo "Perfil SSO do Databricks (obrigatorio)"
  HOST="$(env_get DATABRICKS_HOST)"
  [[ -n "$HOST" ]] || { HOST="$DATABRICKS_HOST_PADRAO"; env_set DATABRICKS_HOST "$HOST"; }
  ok "perfil selecionado em config/settings.yaml: $PERFIL"

  # Tipo e host do perfil, lidos pelo mesmo codigo que o docs usa. Perfil de
  # outro tipo (azure-cli, PAT) aparece como valido na CLI e nao da token ao
  # docs; nao se mexe nele, cria-se outro, SSO, ao lado.
  perfil_info() {
    "$PY" - "$1" <<'EOF'
import sys
from docsquad.auth import ler_perfis
p = (ler_perfis() or {}).get(sys.argv[1])
print(f"{p['tipo']} {p['host']}" if p else "ausente -")
EOF
  }
  read -r TIPO HOST_PERFIL < <(perfil_info "$PERFIL")
  if [[ "$TIPO" != "ausente" && "$TIPO" != "databricks-cli" && "$TIPO" != "desconhecido" ]]; then
    falha "O perfil configurado '$PERFIL' usa auth_type=$TIPO, e o docs precisa de login SSO. Escolha outro nome em databricks.perfil no settings.yaml."
  fi
  if [[ "$TIPO" != "ausente" && "${HOST_PERFIL%/}" != "${HOST%/}" ]]; then
    falha "O perfil '$PERFIL' aponta para $HOST_PERFIL, e o workspace da squad e $HOST. Defina outro nome em databricks.perfil no settings.yaml."
  fi

  # `auth token` so responde com sessao valida. A saida vai para o lixo porque
  # contem o token.
  if ! "$DBX" auth token --profile "$PERFIL" >/dev/null 2>&1; then
    aviso "sem sessao valida no perfil $PERFIL, abrindo o login SSO"
    aviso "se o navegador nao abrir, copie a URL que aparecer para o navegador do Windows"
    "$DBX" auth login --host "$HOST" --profile "$PERFIL"
  fi
  "$DBX" auth token --profile "$PERFIL" >/dev/null 2>&1 \
    || falha "Login no perfil $PERFIL nao concluiu. Rode: databricks auth login --host $HOST --profile $PERFIL"
  ok "perfil $PERFIL autenticado em $HOST"

  # Pasta do produto, lida pelo inventario e unica onde proposta aprovada
  # escreve notebook. Espelha databricks.paths em config/settings.yaml.
  LOGIN="$("$DBX" current-user me --profile "$PERFIL" -o json | "$PY" -c 'import json,sys; print(json.load(sys.stdin)["userName"])')"
  if [[ "${LOGIN,,}" != "${USUARIO_DATABRICKS,,}" ]]; then
    aviso "Databricks autenticou como '$LOGIN'; selecione '$USUARIO_DATABRICKS' no novo login SSO"
    "$DBX" auth login --host "$HOST" --profile "$PERFIL"
    LOGIN="$("$DBX" current-user me --profile "$PERFIL" -o json | "$PY" -c 'import json,sys; print(json.load(sys.stdin)["userName"])')"
    if [[ "${LOGIN,,}" != "${USUARIO_DATABRICKS,,}" ]]; then
      falha "Databricks autenticou como '$LOGIN', mas config/settings.yaml espera '$USUARIO_DATABRICKS'."
    fi
  fi
  ok "Databricks autenticado como $LOGIN, conforme config/settings.yaml"
  PASTA="/Workspace/Users/$LOGIN/$PASTA_PRODUTO"
  if "$DBX" workspace get-status "$PASTA" --profile "$PERFIL" >/dev/null 2>&1; then
    ok "pasta $PASTA ja existe"
  else
    "$DBX" workspace mkdirs "$PASTA" --profile "$PERFIL"
    ok "pasta $PASTA criada"
  fi
fi

# ---------- 6. conferencia ----------
passo "Conferencia final"
docs config-check || falha "A conferencia achou problema. Corrija o item marcado como falha acima e rode o script de novo."

printf '\n\033[32mAmbiente pronto.\033[0m Em cada terminal novo: source .venv/bin/activate\n'
if [[ $MUDOU_CLI -eq 1 ]]; then
  printf 'Uma CLI foi instalada ou removida: nos terminais ja abertos, rode hash -r ou abra um novo.\n'
fi
