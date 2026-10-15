"""Databricks: leitura de notebooks do workspace, escrita apenas via Executor."""
from __future__ import annotations

import base64
import posixpath
from typing import Iterator

import requests

from ..auth import cabecalho_databricks
from ..config import env, perfil_databricks, settings


class DatabricksClient:
    def __init__(self, host: str | None = None, token: str | None = None,
                 perfil: str | None = None):
        self.host = (host or env("DATABRICKS_HOST")).rstrip("/")
        # O caminho normal e o perfil SSO da CLI; o token so existe para
        # automacao. O token do SSO dura cerca de uma hora, o que cobre uma
        # coleta com folga.
        token = token if token is not None else env("DATABRICKS_TOKEN", required=False)
        perfil = perfil or perfil_databricks()[0]
        header, self.metodo_auth = cabecalho_databricks(token, perfil)
        self.s = requests.Session()
        self.s.headers.update(header)

    def _get(self, endpoint: str, **params):
        r = self.s.get(f"{self.host}{endpoint}", params=params, timeout=120)
        r.raise_for_status()
        return r.json()

    def _post(self, endpoint: str, body: dict):
        r = self.s.post(f"{self.host}{endpoint}", json=body, timeout=120)
        r.raise_for_status()
        return r.json() if r.content else {}

    # ---------- LEITURA ----------

    def usuario(self) -> str:
        """Login de quem esta autenticado, como o workspace o conhece."""
        if not hasattr(self, "_usuario"):
            self._usuario = self._get("/api/2.0/preview/scim/v2/Me")["userName"]
        return self._usuario

    def resolver(self, path: str) -> str:
        """Troca `{usuario}` pelo login atual. So consulta a API se precisar."""
        if "{usuario}" not in path:
            return path
        return path.replace("{usuario}", self.usuario())

    def list_path(self, path: str) -> list[dict]:
        return self._get("/api/2.0/workspace/list",
                         path=self.resolver(path)).get("objects", [])

    def walk(self, path: str) -> Iterator[dict]:
        """Percorre recursivamente, devolvendo apenas notebooks."""
        for obj in self.list_path(path):
            if obj["object_type"] == "DIRECTORY":
                yield from self.walk(obj["path"])
            elif obj["object_type"] == "NOTEBOOK":
                yield obj

    def export_notebook(self, path: str, fmt: str = "SOURCE") -> str:
        """fmt: SOURCE, HTML, JUPYTER, DBC. HTML e o mais confiavel no workspace."""
        data = self._get("/api/2.0/workspace/export", path=path, format=fmt,
                         direct_download="false")
        return base64.b64decode(data["content"]).decode("utf-8", errors="replace")

    def notebook_status(self, path: str) -> dict:
        return self._get("/api/2.0/workspace/get-status", path=path)

    def inventory(self, paths: list[str] | None = None) -> list[dict]:
        """Inventario de notebooks com tamanho e contagem de celulas de codigo.

        Serve de insumo para o agente de documentacao de notebook saber o que
        mudou e o que ainda nao tem docstring de cabecalho.
        """
        paths = paths or settings()["databricks"]["paths"]
        out = []
        for root in map(self.resolver, paths):
            for nb in self.walk(root):
                try:
                    src = self.export_notebook(nb["path"], "SOURCE")
                except requests.HTTPError as exc:
                    out.append({"path": nb["path"], "error": str(exc)})
                    continue
                cells = src.split("# COMMAND ----------")
                header = cells[0] if cells else ""
                out.append({
                    "path": nb["path"],
                    "language": nb.get("language"),
                    "object_id": nb.get("object_id"),
                    "n_cells": len(cells),
                    "n_linhas": src.count("\n"),
                    "tem_cabecalho_documentado": "MAGIC %md" in header,
                    "primeiras_linhas": "\n".join(src.splitlines()[:15]),
                })
        return out

    # ---------- ESCRITA (so chamada pelo Executor) ----------

    def import_notebook(self, path: str, content: str, language: str = "PYTHON",
                        overwrite: bool = False) -> dict:
        # A API de import nao cria os diretorios pais. mkdirs e idempotente e
        # cria a hierarquia necessaria quando ela ainda nao existe.
        self._post("/api/2.0/workspace/mkdirs",
                   {"path": posixpath.dirname(path)})
        body = {
            "path": path,
            "format": "SOURCE",
            "language": language,
            "overwrite": overwrite,
            "content": base64.b64encode(content.encode("utf-8")).decode(),
        }
        self._post("/api/2.0/workspace/import", body)
        return {"path": path, "bytes": len(content), "overwrite": overwrite}
