#!/usr/bin/env bash
# Prepara o ambiente do docsquad do zero, e pode ser rodado de novo sem estrago.
#
# O que faz, nesta ordem:
#   1. confere o Python e instala requirements.txt num .venv;
#   2. instala o Azure CLI, ou atualiza se estiver abaixo da versao minima;
#   3. exige `az login`. Sem sessao valida no Azure, o script para aqui;
#   4. instala ou atualiza a CLI do Databricks;
#   5. exige um perfil SSO do Databricks definido em DATABRICKS_CONFIG_PROFILE
#      no .env, e faz o login nele se preciso;
#   6. roda `docs config-check`.
#
# Uso:
#   scripts/preparar_ambiente.sh                  # caminho normal
#   scripts/preparar_ambiente.sh --atualizar      # forca atualizar as CLIs
#   scripts/preparar_ambiente.sh --device-code    # login por codigo, sem navegador
#   scripts/preparar_ambiente.sh --perfil revenue # nome do perfil do Databricks
#   scripts/preparar_ambiente.sh --sem-databricks # pula os passos 4 e 5
#
# No WSL, rodar dentro do Linux, e nao no PowerShell: o `docs` so enxerga as
# CLIs instaladas no mesmo ambiente em que ele roda. No WSL o login por codigo
# e o padrao, porque o navegador costuma nao abrir.
#
# Pede sudo so para instalar ou atualizar CLI. Nao guarda token em lugar
# nenhum: as duas CLIs mantem a sessao no proprio cache.

set -euo pipefail

# ---------- requisitos minimos ----------
PYTHON_MIN="3.10"
AZ_MIN="2.60.0"
DATABRICKS_MIN="1.0.0"
DATABRICKS_HOST_PADRAO="https://adb-1820723078635205.5.azuredatabricks.net"
PERFIL_PADRAO="revenue"

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$RAIZ/.env"

ATUALIZAR=0
SEM_DATABRICKS=0
PERFIL=""
DEVICE_CODE=0
grep -qi microsoft /proc/version 2>/dev/null && DEVICE_CODE=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --atualizar) ATUALIZAR=1 ;;
    --device-code) DEVICE_CODE=1 ;;
    --sem-databricks) SEM_DATABRICKS=1 ;;
    --perfil) PERFIL="${2:?--perfil precisa de um nome}"; shift ;;
    -h|--help) sed -n '2,25p' "$0"; exit 0 ;;
    *) echo "Opcao desconhecida: $1" >&2; exit 2 ;;
  esac
  shift
done

passo() { printf '\n\033[1m==> %s\033[0m\n' "$*"; }
ok()    { printf '    \033[32mok\033[0m %s\n' "$*"; }
aviso() { printf '    \033[33m!\033[0m %s\n' "$*"; }
falha() { printf '\n\033[31mERRO:\033[0m %s\n' "$*" >&2; exit 1; }

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

if [[ ! -f "$ENV_FILE" ]]; then
  cp "$RAIZ/.env.example" "$ENV_FILE"
  ok ".env criado a partir do .env.example"
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

if ! command -v az >/dev/null 2>&1; then
  aviso "az nao encontrado, instalando"
  instalar_az
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
  if [[ $DEVICE_CODE -eq 1 ]]; then
    aviso "abra https://microsoft.com/devicelogin e digite o codigo abaixo"
    az login --use-device-code --only-show-errors >/dev/null
  else
    az login --only-show-errors >/dev/null
  fi
fi
az account show --only-show-errors >/dev/null 2>&1 \
  || falha "Sem sessao no Azure. Rode: az login   (no WSL: az login --use-device-code)"
ok "logado como $(az account show --query user.name -o tsv)"

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
    elif [[ "$(command -v databricks)" == "/usr/local/bin/databricks" ]]; then
      # O instalador oficial recusa sobrescrever; a atualizacao e remover e
      # instalar de novo, no mesmo caminho.
      sudo rm -f /usr/local/bin/databricks
      instalar_databricks
    else
      falha "databricks em $(command -v databricks), fora do caminho padrao. Atualize pelo gerenciador que o instalou."
    fi
  }

  if ! command -v databricks >/dev/null 2>&1; then
    aviso "databricks nao encontrado, instalando"
    instalar_databricks
  fi
  DBX_VER="$(databricks -v 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1 || echo 0)"
  if [[ $ATUALIZAR -eq 1 ]] || ! versao_ok "$DBX_VER" "$DATABRICKS_MIN"; then
    aviso "atualizando databricks $DBX_VER"
    atualizar_databricks
    DBX_VER="$(databricks -v | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1)"
  fi
  versao_ok "$DBX_VER" "$DATABRICKS_MIN" || falha "databricks $DBX_VER continua abaixo de $DATABRICKS_MIN."
  ok "databricks $DBX_VER"

  # ---------- 5. perfil SSO (obrigatorio) ----------
  passo "Perfil SSO do Databricks (obrigatorio)"
  HOST="$(env_get DATABRICKS_HOST)"
  [[ -n "$HOST" ]] || { HOST="$DATABRICKS_HOST_PADRAO"; env_set DATABRICKS_HOST "$HOST"; }

  PERFIL="${PERFIL:-$(env_get DATABRICKS_CONFIG_PROFILE)}"
  if [[ -z "$PERFIL" ]]; then
    read -r -p "    Nome do perfil do Databricks [$PERFIL_PADRAO]: " PERFIL
    PERFIL="${PERFIL:-$PERFIL_PADRAO}"
  fi
  env_set DATABRICKS_CONFIG_PROFILE "$PERFIL"
  ok "DATABRICKS_CONFIG_PROFILE=$PERFIL no .env"

  # `auth token` so responde com sessao valida. A saida vai para o lixo porque
  # contem o token.
  if ! databricks auth token --profile "$PERFIL" >/dev/null 2>&1; then
    aviso "sem sessao valida no perfil $PERFIL, abrindo o login SSO"
    aviso "se o navegador nao abrir, copie a URL que aparecer para o navegador do Windows"
    databricks auth login --host "$HOST" --profile "$PERFIL"
  fi
  databricks auth token --profile "$PERFIL" >/dev/null 2>&1 \
    || falha "Login no perfil $PERFIL nao concluiu. Rode: databricks auth login --host $HOST --profile $PERFIL"
  ok "perfil $PERFIL autenticado em $HOST"
fi

# ---------- 6. conferencia ----------
passo "Conferencia final"
docs config-check

printf '\n\033[32mAmbiente pronto.\033[0m Em cada terminal novo: source .venv/bin/activate\n'
