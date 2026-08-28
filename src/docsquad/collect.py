"""Coleta unificada: junta sprint, commits e notebooks num unico snapshot.

Esse snapshot e o insumo de todos os agentes. Ele e salvo em knowledge/ para
que a geracao de documento seja reproduzivel: o mesmo snapshot gera o mesmo
texto, e da para auditar depois de onde cada afirmacao veio.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from .config import path, settings
from .connectors import DatabricksClient, DevOpsClient, GitHubClient


def snapshot(janela_dias: int | None = None, com_databricks: bool = True) -> dict:
    cfg = settings()
    devops = DevOpsClient()
    board = devops.sprint_board()

    gh = GitHubClient()
    commits = gh.commits_all_repos(since_days=janela_dias)
    por_card = GitHubClient.group_by_card(commits)

    notebooks = []
    if com_databricks:
        try:
            notebooks = DatabricksClient().inventory()
        except Exception as exc:  # workspace pode estar indisponivel
            notebooks = [{"error": str(exc)}]

    # anexa commits e comentarios a cada card
    todos = (board["aguardando_validacao"] + board["ativos"] + board["outros"])
    for wi in todos:
        cid = str(wi["id"])
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
        "notebooks": notebooks,
    }


def save(snap: dict) -> str:
    nome = f"snapshot-{snap.get('sprint', 'sprint')}-{snap['gerado_em'][:10]}.json"
    nome = nome.replace("/", "-").replace(" ", "_")
    destino = path("knowledge", "cards", nome)
    destino.write_text(json.dumps(snap, ensure_ascii=False, indent=2, default=str),
                       encoding="utf-8")
    return str(destino)
