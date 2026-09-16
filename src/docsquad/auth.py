"""Credenciais de leitura: Azure DevOps e Databricks.

Para o Azure DevOps, dois caminhos, nesta ordem de preferencia:

1. **Entra ID, via `az login`.** E o padrao. A pessoa ja se autentica no tenant
   da Ambev para outras coisas, o token dura cerca de uma hora, e nao existe
   segredo para guardar, vazar ou revogar quando alguem sai do time.
2. **PAT**, se `AZDO_PAT` estiver preenchido. Fica como escape para quem nao
   tem `az` na maquina, ou para execucao automatizada sem sessao interativa.

O PAT ganha precedencia quando existe: quem se deu ao trabalho de preencher a
variavel quer usa-la, e uma escolha explicita perdendo para uma implicita seria
surpresa ruim.

O token nunca e escrito em disco nem em log. Ele vive no processo, e some com
ele.
"""
from __future__ import annotations

import json
import shutil
import subprocess

# Id de recurso do Azure DevOps no Entra ID. E publico e igual em qualquer
# tenant, e nao um identificador da Ambev.
RECURSO_DEVOPS = "499b84ac-1321-427f-aa17-267ca6975798"

INSTRUCAO = (
    "Autentique com uma das duas opcoes:\n"
    "  1. az login    (recomendado, nao exige segredo no .env)\n"
    "  2. preencha AZDO_PAT no .env, com permissao de leitura de Work Items"
)


class SemCredencial(RuntimeError):
    """Nao ha como autenticar no Azure DevOps ou no Databricks."""


def token_entra(timeout: int = 60) -> str:
    """Token de acesso do Entra ID para o Azure DevOps, via `az`.

    Levanta `SemCredencial` com o que fazer a seguir, e nunca com a saida crua
    do `az`, que e longa e enterra a acao no meio.
    """
    if shutil.which("az") is None:
        raise SemCredencial(
            "O comando `az` nao esta instalado, e nenhum AZDO_PAT foi definido.\n"
            + INSTRUCAO)

    try:
        proc = subprocess.run(
            ["az", "account", "get-access-token", "--resource", RECURSO_DEVOPS,
             "--output", "json"],
            capture_output=True, text=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired as exc:
        raise SemCredencial(
            f"`az account get-access-token` passou de {timeout}s sem responder."
        ) from exc

    if proc.returncode != 0:
        erro = (proc.stderr or "").strip().splitlines()
        detalhe = erro[-1] if erro else "sem detalhe"
        raise SemCredencial(
            f"O `az` nao devolveu token: {detalhe}\n"
            "Normalmente e sessao expirada. Rode: az login")

    try:
        return json.loads(proc.stdout)["accessToken"]
    except (json.JSONDecodeError, KeyError) as exc:
        raise SemCredencial(
            "O `az` respondeu num formato inesperado, sem accessToken.") from exc


def cabecalho(pat: str | None) -> tuple[dict, str]:
    """Header de autorizacao e o nome do metodo em uso, para exibir.

    O nome volta junto porque a pessoa precisa saber por qual identidade esta
    lendo o board: PAT de colega em `.env` copiado e um erro que so aparece
    quando os cards vem errados.
    """
    if pat:
        import base64
        token = base64.b64encode(f":{pat}".encode()).decode()
        return {"Authorization": f"Basic {token}"}, "PAT (AZDO_PAT)"
    return {"Authorization": f"Bearer {token_entra()}"}, "Entra ID (az login)"


# ---------- Databricks ----------
#
# O caminho documentado e o login SSO da CLI do Databricks, por perfil do
# ~/.databrickscfg: a squad nao tem permissao de gerar PAT no workspace.
# DATABRICKS_TOKEN continua aceito, com precedencia, so como escape para
# execucao automatizada com credencial de servico. Nao e para uso pessoal, e
# por isso nao aparece no .env.example nem nas mensagens.

INSTRUCAO_DATABRICKS = (
    "Autentique no Databricks pelo login SSO:\n"
    "  1. databricks auth login --host <DATABRICKS_HOST> --profile <nome>\n"
    "  2. preencha DATABRICKS_CONFIG_PROFILE=<nome> no .env\n"
    "Ou rode scripts/preparar_ambiente.sh, que faz os dois."
)


def token_databricks(perfil: str, timeout: int = 60) -> str:
    """Token OAuth do login SSO da CLI, renovado pela propria CLI se preciso."""
    if shutil.which("databricks") is None:
        raise SemCredencial(
            "O comando `databricks` nao esta instalado.\n" + INSTRUCAO_DATABRICKS)

    try:
        proc = subprocess.run(
            ["databricks", "auth", "token", "--profile", perfil,
             "--output", "json"],
            capture_output=True, text=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired as exc:
        raise SemCredencial(
            f"`databricks auth token` passou de {timeout}s sem responder."
        ) from exc

    if proc.returncode != 0:
        erro = (proc.stderr or "").strip().splitlines()
        detalhe = erro[-1] if erro else "sem detalhe"
        raise SemCredencial(
            f"A CLI do Databricks nao devolveu token: {detalhe}\n"
            f"Normalmente e sessao expirada. Rode: "
            f"databricks auth login --profile {perfil}")

    try:
        return json.loads(proc.stdout)["access_token"]
    except (json.JSONDecodeError, KeyError) as exc:
        raise SemCredencial(
            "A CLI do Databricks respondeu num formato inesperado, "
            "sem access_token.") from exc


def cabecalho_databricks(token: str | None, perfil: str | None) -> tuple[dict, str]:
    """Header de autorizacao do Databricks e o nome do metodo em uso."""
    if token:
        return {"Authorization": f"Bearer {token}"}, "PAT (DATABRICKS_TOKEN)"
    if perfil:
        return ({"Authorization": f"Bearer {token_databricks(perfil)}"},
                f"SSO (perfil {perfil})")
    raise SemCredencial(
        "DATABRICKS_CONFIG_PROFILE nao esta definido.\n"
        + INSTRUCAO_DATABRICKS)
