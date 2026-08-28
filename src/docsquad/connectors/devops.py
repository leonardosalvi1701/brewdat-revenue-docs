"""Azure DevOps: leitura de sprint e cards, escrita apenas via Executor."""
from __future__ import annotations

import base64
from typing import Any

import requests

from ..config import env, settings

API = "7.1"


class DevOpsClient:
    def __init__(self, org_url: str | None = None, project: str | None = None,
                 team: str | None = None, pat: str | None = None):
        self.org_url = (org_url or env("AZDO_ORG_URL")).rstrip("/")
        self.project = project or env("AZDO_PROJECT")
        self.team = team or env("AZDO_TEAM", required=False) or self.project
        pat = pat or env("AZDO_PAT")
        token = base64.b64encode(f":{pat}".encode()).decode()
        self.s = requests.Session()
        self.s.headers.update({"Authorization": f"Basic {token}"})

    # ---------- helpers ----------

    def _get(self, url: str, **params) -> dict:
        params.setdefault("api-version", API)
        r = self.s.get(url, params=params, timeout=60)
        r.raise_for_status()
        return r.json()

    def _post(self, url: str, body: Any, content_type: str = "application/json",
              **params) -> dict:
        params.setdefault("api-version", API)
        r = self.s.post(url, json=body, params=params,
                        headers={"Content-Type": content_type}, timeout=60)
        r.raise_for_status()
        return r.json()

    def _patch(self, url: str, body: Any, **params) -> dict:
        params.setdefault("api-version", API)
        r = self.s.patch(url, json=body, params=params,
                         headers={"Content-Type": "application/json-patch+json"},
                         timeout=60)
        r.raise_for_status()
        return r.json()

    # ---------- LEITURA ----------

    def current_iteration(self) -> dict:
        url = f"{self.org_url}/{self.project}/{self.team}/_apis/work/teamsettings/iterations"
        data = self._get(url, **{"$timeframe": "current"})
        values = data.get("value", [])
        if not values:
            raise RuntimeError("Nenhuma iteracao corrente encontrada para o time.")
        return values[0]

    def iterations(self) -> list[dict]:
        url = f"{self.org_url}/{self.project}/{self.team}/_apis/work/teamsettings/iterations"
        return self._get(url).get("value", [])

    def iteration_work_item_ids(self, iteration_id: str) -> list[int]:
        url = (f"{self.org_url}/{self.project}/{self.team}/_apis/work/teamsettings/"
               f"iterations/{iteration_id}/workitems")
        data = self._get(url)
        return [rel["target"]["id"] for rel in data.get("workItemRelations", [])
                if rel.get("target")]

    def work_items(self, ids: list[int], fields: list[str] | None = None) -> list[dict]:
        """Batch de ate 200 por chamada."""
        if not ids:
            return []
        fields = fields or [
            "System.Id", "System.Title", "System.WorkItemType", "System.State",
            "System.AssignedTo", "System.IterationPath", "System.Tags",
            "System.ChangedDate", "System.Description",
            "Microsoft.VSTS.Common.AcceptanceCriteria",
        ]
        out: list[dict] = []
        url = f"{self.org_url}/{self.project}/_apis/wit/workitemsbatch"
        for i in range(0, len(ids), 200):
            body = {"ids": ids[i:i + 200], "fields": fields}
            out.extend(self._post(url, body).get("value", []))
        return out

    def sprint_board(self, iteration_id: str | None = None) -> dict:
        """Cards da sprint agrupados por situacao, com a fatia de validacao separada."""
        cfg = settings()["devops"]
        it = self.current_iteration() if iteration_id is None else {"id": iteration_id}
        ids = self.iteration_work_item_ids(it["id"])
        items = self.work_items(ids)

        def state(wi):
            return wi["fields"].get("System.State", "")

        validacao = [w for w in items if state(w) in cfg["estados_validacao"]]
        ativos = [w for w in items if state(w) in cfg["estados_ativos"]
                  and w not in validacao]
        outros = [w for w in items if w not in validacao and w not in ativos]
        return {
            "iteration": it,
            "total": len(items),
            "aguardando_validacao": validacao,
            "ativos": ativos,
            "outros": outros,
        }

    def comments(self, work_item_id: int) -> list[dict]:
        url = f"{self.org_url}/{self.project}/_apis/wit/workItems/{work_item_id}/comments"
        return self._get(url, **{"api-version": "7.1-preview.3"}).get("comments", [])

    def updates(self, work_item_id: int) -> list[dict]:
        """Historico de mudancas. Util para reconstruir o que aconteceu na sprint."""
        url = f"{self.org_url}/{self.project}/_apis/wit/workItems/{work_item_id}/updates"
        return self._get(url).get("value", [])

    # ---------- ESCRITA (so chamada pelo Executor) ----------

    def add_comment(self, work_item_id: int, text: str) -> dict:
        url = f"{self.org_url}/{self.project}/_apis/wit/workItems/{work_item_id}/comments"
        return self._post(url, {"text": text}, **{"api-version": "7.1-preview.3"})

    def set_state(self, work_item_id: int, new_state: str) -> dict:
        url = f"{self.org_url}/{self.project}/_apis/wit/workitems/{work_item_id}"
        patch = [{"op": "add", "path": "/fields/System.State", "value": new_state}]
        return self._patch(url, patch)

    def create_work_item(self, item_type: str, title: str, description: str = "",
                         parent_id: int | None = None,
                         iteration: str | None = None) -> dict:
        url = f"{self.org_url}/{self.project}/_apis/wit/workitems/${item_type}"
        patch = [
            {"op": "add", "path": "/fields/System.Title", "value": title},
            {"op": "add", "path": "/fields/System.Description", "value": description},
        ]
        if iteration:
            patch.append({"op": "add", "path": "/fields/System.IterationPath",
                          "value": iteration})
        if parent_id:
            patch.append({
                "op": "add", "path": "/relations/-",
                "value": {"rel": "System.LinkTypes.Hierarchy-Reverse",
                          "url": f"{self.org_url}/_apis/wit/workItems/{parent_id}"},
            })
        return self._patch(url, patch)
