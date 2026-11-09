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

import configparser
import json
import os
import shutil
import subprocess
from pathlib import Path

from .config import settings

# Id de recurso do Azure DevOps no Entra ID. E publico e igual em qualquer
# tenant, e nao um identificador da Ambev.
RECURSO_DEVOPS = "499b84ac-1321-427f-aa17-267ca6975798"

INSTRUCAO = (
    "Autentique com uma das duas opcoes:\n"
    "  1. rode scripts/preparar_ambiente.sh; ele usa usuarios.azure de "
    "config/settings.yaml para conferir a conta apos o login interativo\n"
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

    esperado = settings().get("usuarios", {}).get("azure", "").strip()
    if esperado:
        identidade = subprocess.run(
            ["az", "account", "show", "--query", "user.name", "-o", "tsv"],
            capture_output=True, text=True, timeout=timeout, check=False)
        atual = identidade.stdout.strip() if identidade.returncode == 0 else ""
        if atual.casefold() != esperado.casefold():
            raise SemCredencial(
                f"Azure autenticado como '{atual or 'desconhecido'}', mas "
                f"config/settings.yaml espera '{esperado}'. Rode "
                "scripts/preparar_ambiente.sh e escolha a conta configurada.")

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
            "Normalmente e sessao expirada ou de outra conta. Rode "
            "scripts/preparar_ambiente.sh para autenticar com usuarios.azure.")

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

def instrucao_databricks() -> str:
    esperado = settings().get("usuarios", {}).get("databricks", "")
    return (
        "Autentique no Databricks pelo login SSO. A CLI nao aceita usuario no "
        "comando de login; escolha no navegador a conta configurada em "
        f"usuarios.databricks ({esperado}) e o script confirma o login.\n"
        "Rode scripts/preparar_ambiente.sh para usar databricks.perfil e o host "
        "definidos na configuracao."
    )

# `auth token` so le o cache do login SSO. Perfil de outro tipo autentica a
# CLI normalmente, aparece como valido em `databricks auth profiles`, e mesmo
# assim nao devolve token aqui. Desconhecido passa: perfil antigo sem
# auth_type ainda pode ter sessao SSO, e a propria CLI decide.
TIPOS_SSO = {"databricks-cli", "desconhecido"}


def arquivo_databrickscfg() -> Path:
    """O mesmo arquivo que a CLI le, inclusive quando sobrescrito por variavel."""
    return Path(os.getenv("DATABRICKS_CONFIG_FILE") or Path.home() / ".databrickscfg")


def _tipo_perfil(secao) -> str:
    if secao.get("auth_type"):
        return secao["auth_type"].strip()
    if "token" in secao:
        return "pat"
    if "client_secret" in secao:
        return "service principal"
    return "desconhecido"


def ler_perfis(caminho: Path | None = None) -> dict[str, dict] | None:
    """Perfis do ~/.databrickscfg, so com host e tipo de autenticacao.

    Devolve None quando o arquivo nao existe. Nenhum valor de credencial sai
    daqui: o arquivo pode ter token em texto puro, e o que este modulo devolve
    vai para a tela.
    """
    caminho = caminho or arquivo_databrickscfg()
    if not caminho.is_file():
        return None
    # DEFAULT vira secao comum, como a CLI trata. Sem isto o configparser o
    # espalharia como valor padrao em todos os perfis.
    cp = configparser.ConfigParser(default_section="__sem_padrao__",
                                   interpolation=None, strict=False)
    cp.read(caminho, encoding="utf-8")
    perfis = {}
    for nome in cp.sections():
        secao = cp[nome]
        if nome.startswith("__") or not secao.get("host"):
            continue
        perfis[nome] = {"host": secao["host"].strip().rstrip("/"),
                        "tipo": _tipo_perfil(secao)}
    return perfis


def cli_legada(caminho: str) -> bool:
    """A CLI legada (pacote `databricks-cli` do pip, 0.x) e script Python.

    A nova e binario. Ler a primeira linha distingue as duas sem executar
    nada, e a legada repassa os comandos para a nova com aviso no meio da
    saida, o que nao se quer descobrir rodando.
    """
    try:
        with open(caminho, "rb") as fh:
            primeira = fh.readline(200)
    except OSError:
        return False
    return primeira.startswith(b"#!") and b"python" in primeira


def clis_databricks(path_env: str | None = None) -> list[str]:
    """Todo `databricks` executavel no PATH, na ordem em que o shell acha."""
    vistos, achados = set(), []
    for pasta in (path_env if path_env is not None else os.getenv("PATH", "")).split(os.pathsep):
        candidato = os.path.join(pasta, "databricks")
        real = os.path.realpath(candidato)
        if os.path.isfile(candidato) and os.access(candidato, os.X_OK) and real not in vistos:
            vistos.add(real)
            achados.append(candidato)
    return achados


def cli_databricks() -> str:
    """Caminho da CLI nova. Pula a legada, que pode estar na frente no PATH."""
    primeira = shutil.which("databricks")
    if primeira is None:
        raise SemCredencial(
            "O comando `databricks` nao esta instalado.\n" + instrucao_databricks())
    if not cli_legada(primeira):
        return primeira
    for caminho in clis_databricks():
        if not cli_legada(caminho):
            return caminho
    raise SemCredencial(
        f"So existe a CLI legada do Databricks, em {primeira}. Ela nao faz login "
        "SSO. Remova com `pip uninstall databricks-cli` e rode "
        "scripts/preparar_ambiente.sh, que instala a nova.")


def _comando_login(perfil: str, host: str | None) -> str:
    host = host or os.getenv("DATABRICKS_HOST") or "<DATABRICKS_HOST>"
    return f"databricks auth login --host {host} --profile {perfil}"


def checar_perfil(perfil: str) -> None:
    """Para antes de chamar a CLI quando o perfil nao tem como dar token.

    Sem o ~/.databrickscfg nao ha o que conferir, e a CLI responde por si.
    """
    perfis = ler_perfis()
    if perfis is None:
        return
    if perfil not in perfis:
        existentes = ", ".join(perfis) or "nenhum"
        raise SemCredencial(
            f"O perfil `{perfil}` nao existe em {arquivo_databrickscfg()}. "
            f"Perfis existentes: {existentes}.\n"
            "Confira databricks.perfil em config/settings.yaml, ou crie o perfil:\n"
            f"  {_comando_login(perfil, None)}")
    tipo = perfis[perfil]["tipo"]
    if tipo not in TIPOS_SSO:
        raise SemCredencial(
            f"O perfil `{perfil}` usa auth_type={tipo}, e o docs precisa de "
            "perfil de login SSO (auth_type=databricks-cli). Ele autentica a "
            "CLI, mas nao deixa token para o docs ler.\n"
            "Altere databricks.perfil em config/settings.yaml para um nome de "
            "perfil SSO e rode scripts/preparar_ambiente.sh.")


def token_databricks(perfil: str, timeout: int = 60) -> str:
    """Token OAuth do login SSO da CLI, renovado pela propria CLI se preciso."""
    cli = cli_databricks()
    checar_perfil(perfil)

    try:
        proc = subprocess.run(
            [cli, "auth", "token", "--profile", perfil, "--output", "json"],
            capture_output=True, text=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired as exc:
        raise SemCredencial(
            f"`databricks auth token` passou de {timeout}s sem responder."
        ) from exc

    if proc.returncode != 0:
        erro = (proc.stderr or "").strip().splitlines()
        detalhe = erro[-1] if erro else "sem detalhe"
        perfis = ler_perfis() or {}
        host = perfis.get(perfil, {}).get("host")
        raise SemCredencial(
            f"A CLI do Databricks nao devolveu token: {detalhe}\n"
            "O perfil existe e e SSO, entao a sessao expirou ou o login nao "
            f"terminou. Rode: {_comando_login(perfil, host)}")

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
        "databricks.perfil nao esta definido em config/settings.yaml.\n"
        + instrucao_databricks())
