"""Diagnostico do ambiente, para o `docs config-check`.

Cada verificacao devolve achados com nivel, assunto e texto, e o texto de uma
falha diz o que fazer. A saida e feita para ser colada inteira num pedido de
ajuda: quem le precisa achar a causa sem pedir um segundo comando.

Tudo aqui e leitura. O `git fetch` atualiza so as referencias locais do
remoto, e nao mexe na branch de ninguem.
"""
from __future__ import annotations

import os
import posixpath
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import requests
from . import auth
from .config import ROOT, perfil_databricks

OK, AVISO, FALHA = "ok", "aviso", "falha"


@dataclass
class Achado:
    nivel: str
    assunto: str
    texto: str


def comparar_identidade(assunto: str, esperado: str,
                        observado: str) -> Achado:
    if observado.strip().casefold() == esperado.strip().casefold():
        return Achado(OK, assunto, f"{observado} (conforme config/settings.yaml)")
    if not observado.strip():
        return Achado(FALHA, assunto,
                      f"nao consegui ler a identidade autenticada; esperado {esperado}.")
    return Achado(FALHA, assunto,
                  f"autenticado como {observado}, mas config/settings.yaml espera {esperado}.")


def checar_identidades_locais(cfg: dict) -> list[Achado]:
    """Confere a conta Azure e o email de commit contra a identidade declarada."""
    usuarios = cfg.get("usuarios", {})
    achados = []
    try:
        r = subprocess.run(["az", "account", "show", "--query", "user.name", "-o", "tsv"],
                           capture_output=True, text=True, timeout=20, check=False)
        atual = r.stdout.strip() if r.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        atual = ""
    achados.append(comparar_identidade("Azure", usuarios.get("azure", ""), atual))

    email_git = subprocess.run(["git", "-C", str(ROOT), "config", "--local", "user.email"],
                               capture_output=True, text=True, timeout=20, check=False)
    atual_git = email_git.stdout.strip() if email_git.returncode == 0 else ""
    achados.append(comparar_identidade("Git", usuarios.get("git_email", ""), atual_git))
    return achados


def checar_identidade_github(cfg: dict) -> list[Achado]:
    """Confere os logins da CLI e do token GitHub usado pelo conector."""
    esperado = cfg.get("usuarios", {}).get("github", "")
    achados: list[Achado] = []

    gh = shutil.which("gh")
    if gh:
        status = subprocess.run([gh, "auth", "status", "--hostname", "github.com"],
                                capture_output=True, text=True, timeout=20,
                                check=False)
        if status.returncode == 0:
            r = subprocess.run([gh, "api", "user", "--jq", ".login"],
                               capture_output=True, text=True, timeout=20,
                               check=False)
            achados.append(comparar_identidade(
                "GitHub CLI", esperado, r.stdout.strip() if r.returncode == 0 else ""))
        else:
            achados.append(Achado(AVISO, "GitHub CLI",
                                  "sem sessao ativa; use gh auth login --web se precisar do gh."))

    token = os.getenv("GITHUB_TOKEN", "").strip()
    if not token:
        achados.append(Achado(AVISO, "GitHub API",
                              "GITHUB_TOKEN nao configurado; evidencia GitHub continua opcional."))
        return achados
    try:
        r = requests.get("https://api.github.com/user",
                         headers={"Authorization": f"Bearer {token}",
                                  "Accept": "application/vnd.github+json"},
                         timeout=20)
        r.raise_for_status()
        atual = r.json().get("login", "")
    except Exception as exc:
        achados.append(Achado(FALHA, "GitHub API",
                              f"nao consegui confirmar a conta do token: {exc}"))
        return achados
    achados.append(comparar_identidade("GitHub API", esperado, atual))
    return achados


# ---------- CLI do Databricks ----------

def checar_clis(clis: list[str] | None = None) -> list[Achado]:
    """A CLI legada na frente da nova faz cada comando passar por um repasse."""
    clis = auth.clis_databricks() if clis is None else clis
    if not clis:
        return [Achado(FALHA, "CLI do Databricks",
                       "nao instalada. Rode scripts/preparar_ambiente.sh.")]
    legadas = [c for c in clis if auth.cli_legada(c)]
    novas = [c for c in clis if not auth.cli_legada(c)]
    achados = []
    if not novas:
        achados.append(Achado(FALHA, "CLI do Databricks",
                              f"so a CLI legada, em {legadas[0]}. Rode "
                              "`pip uninstall databricks-cli` e "
                              "scripts/preparar_ambiente.sh."))
        return achados
    achados.append(Achado(OK, "CLI do Databricks", novas[0]))
    for c in legadas:
        frente = clis.index(c) < clis.index(novas[0])
        achados.append(Achado(
            AVISO, "CLI do Databricks",
            f"CLI legada em {c}{', na frente da nova no PATH' if frente else ''}. "
            "Remova com `pip uninstall databricks-cli` no ambiente em que ela "
            "esta, e depois `hash -r` ou um terminal novo."))
    return achados


# ---------- perfil ----------

def _host_normal(host: str) -> str:
    return host.strip().rstrip("/").lower()


def checar_host(host: str) -> list[Achado]:
    """Host com redirecionamento faz a requisicao chegar sem credencial.

    O `requests` descarta o cabecalho de autorizacao quando segue um
    redirecionamento, e o Databricks responde 401 dizendo que a credencial nao
    foi enviada. A causa fica longe do sintoma.
    """
    if not host:
        return [Achado(FALHA, "DATABRICKS_HOST", "em branco no .env.")]
    u = urlparse(host.strip())
    problemas = []
    if u.scheme != "https":
        problemas.append("nao comeca com https://")
    if u.path.strip("/") or u.query or u.fragment:
        problemas.append("tem caminho ou `?o=` depois do dominio")
    if problemas:
        return [Achado(FALHA, "DATABRICKS_HOST",
                       f"{host!r} {' e '.join(problemas)}. Use so "
                       "https://<workspace>.azuredatabricks.net")]
    return [Achado(OK, "DATABRICKS_HOST", host)]


def checar_perfil(nome: str, origem: str, no_terminal: str,
                  perfis: dict[str, dict] | None, host: str) -> list[Achado]:
    achados = []
    if no_terminal and no_terminal != nome:
        achados.append(Achado(
            AVISO, "perfil",
            f"o terminal exporta DATABRICKS_CONFIG_PROFILE={no_terminal}, mas o "
            f"docs usa databricks.perfil={nome} de {origem}. Comandos da CLI "
            "chamados sem `--profile` podem usar o perfil exportado; remova a "
            "variavel com `unset DATABRICKS_CONFIG_PROFILE`."))
    if not nome:
        achados.append(Achado(FALHA, "perfil",
                              "databricks.perfil em branco em config/settings.yaml. "
                              "Defina o nome do perfil e rode scripts/preparar_ambiente.sh."))
        return achados
    if perfis is None:
        achados.append(Achado(FALHA, "perfil",
                              f"{auth.arquivo_databrickscfg()} nao existe. "
                              "Rode scripts/preparar_ambiente.sh."))
        return achados
    if nome not in perfis:
        achados.append(Achado(
            FALHA, "perfil",
            f"`{nome}` (do {origem}) nao existe em {auth.arquivo_databrickscfg()}. "
            f"Existentes: {', '.join(perfis) or 'nenhum'}."))
        return achados
    p = perfis[nome]
    if p["tipo"] not in auth.TIPOS_SSO:
        achados.append(Achado(
            FALHA, "perfil",
            f"`{nome}` usa auth_type={p['tipo']}, e o docs precisa de login SSO. "
            "Defina outro nome em databricks.perfil no settings.yaml e rode "
            "scripts/preparar_ambiente.sh."))
        return achados
    if host and _host_normal(p["host"]) != _host_normal(host):
        achados.append(Achado(
            FALHA, "perfil",
            f"`{nome}` aponta para {p['host']}, e DATABRICKS_HOST para {host}. "
            "O token de um workspace nao vale no outro."))
        return achados
    achados.append(Achado(OK, "perfil", f"{nome} (do {origem}), SSO, {p['host']}"))
    return achados


# ---------- repositorio ----------

def _git(*args: str, timeout: int = 20) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args], capture_output=True, text=True,
        timeout=timeout, check=False, env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})


def _referencia_remota(branch: str) -> str | None:
    """O upstream da branch, ou `<remoto>/<branch>` quando nao ha upstream."""
    up = _git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    if up.returncode == 0 and up.stdout.strip():
        return up.stdout.strip()
    for remoto in _git("remote").stdout.split():
        ref = f"{remoto}/{branch}"
        if _git("rev-parse", "--verify", "--quiet", ref).returncode == 0:
            return ref
    return None


def checar_repo() -> list[Achado]:
    """Repo atrasado le config antiga, e o erro aparece longe da causa."""
    try:
        branch = _git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
        ref = _referencia_remota(branch) if branch else None
        if ref is None:
            return [Achado(AVISO, "repo", "sem branch remota para comparar.")]
        remoto, _, ramo = ref.partition("/")
        buscou = _git("fetch", "--quiet", remoto, ramo).returncode == 0
        atras = int(_git("rev-list", "--count", f"HEAD..{ref}").stdout.strip() or 0)
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return [Achado(AVISO, "repo", "nao consegui consultar o git.")]
    ressalva = "" if buscou else " (sem acesso ao remoto, comparado com a ultima busca)"
    if atras:
        config = _git("diff", "--name-only", f"HEAD...{ref}", "--", "config/").stdout.split()
        motivo = (f" A config mudou no remoto ({', '.join(config)}), e a local "
                  "pode apontar para caminho que nao existe mais." if config else "")
        return [Achado(AVISO, "repo",
                       f"{atras} commit(s) atras de {ref}{ressalva}. Rode `git pull`.{motivo}")]
    return [Achado(OK, "repo", f"em dia com {ref}{ressalva}")]


def checar_env_file(caminho: Path | None = None) -> list[Achado]:
    """`\\r` no fim da linha vira parte do valor quando o .env vem do Windows."""
    caminho = caminho or ROOT / ".env"
    if not caminho.is_file():
        return [Achado(FALHA, ".env", "nao existe. Rode scripts/preparar_ambiente.sh.")]
    if b"\r" in caminho.read_bytes():
        return [Achado(AVISO, ".env",
                       "tem fim de linha do Windows. Rode: sed -i 's/\\r$//' .env")]
    return []


def contexto_perfil() -> tuple[str, str, str, str]:
    """Perfil em uso, origem, valor exportado no terminal, e DATABRICKS_HOST."""
    nome, origem = perfil_databricks()
    no_ambiente = os.getenv("DATABRICKS_CONFIG_PROFILE", "").strip()
    no_terminal = no_ambiente if no_ambiente != nome else ""
    # O host e o que o cliente vai usar de fato, venha de onde vier.
    host = os.getenv("DATABRICKS_HOST", "").strip()
    return nome, origem, no_terminal, host


# ---------- caminho de escrita ----------

def checar_caminho_escrita(alvo: str, prefixos: list[str]) -> str | None:
    """Erro para `docs propose notebook`, ou None se o caminho passa.

    Antecipa o que o Executor barra no `apply`, para a proposta errada nao
    chegar a ser aprovada. Nao substitui o portao: aqui `{usuario}` aceita
    qualquer login, e so o Executor sabe quem esta aplicando.
    """
    if not alvo.startswith("/") or posixpath.normpath(alvo) != alvo:
        return f"Caminho '{alvo}' nao esta normalizado: sem `..`, sem barra dupla, sem barra no fim."
    for pref in prefixos:
        padrao = re.escape(posixpath.normpath(pref).rstrip("/")).replace(
            re.escape("{usuario}"), "[^/]+")
        if re.match(padrao + "/", alvo):
            return None
    login = re.match(r"^/Workspace/Users/([^/]+)/", alvo)
    nome = posixpath.basename(alvo)
    sugestoes = [p.replace("{usuario}", login.group(1) if login else "<seu login>")
                 .rstrip("/") + "/" + nome for p in prefixos]
    return (f"Caminho '{alvo}' fora dos prefixos de escrita permitida: {prefixos}.\n"
            "O executor recusaria no apply. Proponha dentro do prefixo, por exemplo:\n"
            + "\n".join(f"  {s}" for s in sugestoes))
