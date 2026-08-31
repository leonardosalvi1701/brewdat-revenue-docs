"""Coleta unificada: junta sprint, commits e notebooks num unico snapshot.

Esse snapshot e o insumo de todos os agentes. Ele e salvo em knowledge/ para
que a geracao de documento seja reproduzivel: o mesmo snapshot gera o mesmo
texto, e da para auditar depois de onde cada afirmacao veio.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .config import path, settings
from .connectors import (DatabricksClient, DevOpsClient, GitHubClient,
                         frente, responsavel)


def snapshot(janela_dias: int | None = None, com_databricks: bool = True) -> dict:
    cfg = settings()
    devops = DevOpsClient()
    board = devops.sprint_board()

    # O DevOps e o unico insumo obrigatorio: sem ele nao ha sprint para
    # descrever. GitHub e Databricks sao evidencia, e boa parte da squad nao
    # tem token dos dois. Fazer o snapshot inteiro falhar por falta de um token
    # de leitura de commits deixaria essas pessoas sem acesso aos proprios
    # cards, entao a ausencia vira registro no snapshot, e nao excecao.
    por_card: dict[str, list[dict]] = {}
    commits_erro = None
    try:
        commits = GitHubClient().commits_all_repos(since_days=janela_dias)
        por_card = GitHubClient.group_by_card(commits)
    except Exception as exc:
        commits_erro = str(exc)

    notebooks = []
    notebooks_erro = None
    if com_databricks:
        try:
            notebooks = DatabricksClient().inventory()
        except Exception as exc:  # workspace pode estar indisponivel
            notebooks_erro = str(exc)

    # anexa responsavel, frente, commits e comentarios a cada card
    todos = (board["concluidos"] + board["aguardando_validacao"]
             + board["ativos"] + board["outros"])

    # A frente vem do card pai, entao os titulos dos pais sao resolvidos num
    # batch so. Um GET por card multiplicaria as chamadas pelo tamanho da
    # sprint sem nenhum ganho.
    pais = [wi["fields"]["System.Parent"] for wi in todos
            if wi.get("fields", {}).get("System.Parent")]
    try:
        titulos_pai = devops.titulos(pais) if pais else {}
    except Exception:
        titulos_pai = {}

    for wi in todos:
        cid = str(wi["id"])
        wi["_responsavel"] = responsavel(wi)
        wi["_frente"] = frente(wi, titulos_pai)
        wi["_commits"] = por_card.get(cid, [])
        try:
            wi["_comments"] = devops.comments(wi["id"])
        except Exception:
            wi["_comments"] = []

    return {
        "gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sprint": board["iteration"].get("name"),
        "iteration_id": board["iteration"].get("id"),
        "squad": cfg["squad"]["nome"],
        "board": board,
        "commits_sem_card": por_card.get("_sem_card", []),
        "commits_erro": commits_erro,
        "notebooks": notebooks,
        "notebooks_erro": notebooks_erro,
    }


def carregar(caminho: str | None = None) -> dict:
    """Le um snapshot salvo. Sem caminho, o mais recente de knowledge/cards/.

    A sprint review se escreve a partir de um snapshot nomeado, e nao de uma
    consulta nova ao DevOps: duas pessoas escrevendo a review da mesma sprint
    precisam estar olhando o mesmo estado do board, e o texto precisa continuar
    auditavel depois que os cards andarem.
    """
    if caminho:
        alvo = Path(caminho)
    else:
        candidatos = sorted(path("knowledge", "cards").glob("snapshot-*.json"))
        if not candidatos:
            raise FileNotFoundError(
                "Nenhum snapshot em knowledge/cards/. Rode antes: docs collect")
        alvo = candidatos[-1]
    snap = json.loads(alvo.read_text(encoding="utf-8"))
    # relativo a raiz do repo: o caminho vai para o frontmatter do rascunho, e
    # um caminho absoluto ali vaza o home de quem gerou e nao serve para mais
    # ninguem abrir.
    try:
        referencia = str(alvo.resolve().relative_to(path()))
    except ValueError:
        referencia = str(alvo)
    return snap | {"_arquivo": referencia}


def save(snap: dict) -> str:
    nome = f"snapshot-{snap.get('sprint', 'sprint')}-{snap['gerado_em'][:10]}.json"
    nome = nome.replace("/", "-").replace(" ", "_")
    destino = path("knowledge", "cards", nome)
    destino.write_text(json.dumps(snap, ensure_ascii=False, indent=2, default=str),
                       encoding="utf-8")
    return str(destino)
