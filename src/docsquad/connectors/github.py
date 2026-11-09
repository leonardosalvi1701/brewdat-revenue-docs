"""GitHub: commits em multiplos repos, correlacionados com cards da sprint."""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

import requests

from ..config import env, settings

# Padroes usuais de referencia a card na mensagem de commit:
#   AB#2680725   #2680725   [2680725]
CARD_REF = re.compile(r"(?:AB#|#|\[)\s*(\d{5,8})")


class GitHubClient:
    def __init__(self, token: str | None = None):
        self.s = requests.Session()
        self.s.headers.update({
            "Authorization": f"Bearer {token or env('GITHUB_TOKEN')}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        })
        esperado = settings().get("usuarios", {}).get("github", "").strip()
        if esperado:
            atual = self._get("https://api.github.com/user").get("login", "").strip()
            if atual.casefold() != esperado.casefold():
                raise RuntimeError(
                    f"GitHub autenticado como '{atual or 'desconhecido'}', mas "
                    f"config/settings.yaml espera '{esperado}'. Confira "
                    "GITHUB_TOKEN.")

    def _get(self, url: str, **params):
        r = self.s.get(url, params=params, timeout=60)
        r.raise_for_status()
        return r.json()

    def commits(self, repo: str, since_days: int | None = None,
                author: str | None = None, branch: str | None = None) -> list[dict]:
        cfg = settings()["github"]
        days = since_days if since_days is not None else cfg.get("janela_dias", 14)
        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        params = {"since": since, "per_page": 100}
        if author:
            params["author"] = author
        if branch:
            params["sha"] = branch
        out, page = [], 1
        while True:
            batch = self._get(f"https://api.github.com/repos/{repo}/commits",
                              page=page, **params)
            if not batch:
                break
            out.extend(batch)
            if len(batch) < 100:
                break
            page += 1
        return [self._normalize(repo, c) for c in out]

    def _normalize(self, repo: str, c: dict) -> dict:
        msg = c["commit"]["message"]
        return {
            "repo": repo,
            "sha": c["sha"][:10],
            "author": (c["commit"]["author"] or {}).get("name"),
            "date": (c["commit"]["author"] or {}).get("date"),
            "message": msg.splitlines()[0],
            "body": "\n".join(msg.splitlines()[1:]).strip(),
            "url": c.get("html_url"),
            "cards": sorted(set(CARD_REF.findall(msg))),
        }

    def commits_all_repos(self, since_days: int | None = None) -> list[dict]:
        repos = settings()["github"]["repos"]
        out = []
        for repo in repos:
            try:
                out.extend(self.commits(repo, since_days=since_days))
            except requests.HTTPError as exc:
                out.append({"repo": repo, "error": str(exc)})
        return out

    @staticmethod
    def group_by_card(commits: list[dict]) -> dict[str, list[dict]]:
        """Correlaciona commits com cards. Commits sem referencia caem em '_sem_card'."""
        grouped: dict[str, list[dict]] = {}
        for c in commits:
            keys = c.get("cards") or ["_sem_card"]
            for k in keys:
                grouped.setdefault(k, []).append(c)
        return grouped

    def files_changed(self, repo: str, sha: str) -> list[str]:
        data = self._get(f"https://api.github.com/repos/{repo}/commits/{sha}")
        return [f["filename"] for f in data.get("files", [])]
