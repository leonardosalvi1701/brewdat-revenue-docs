"""Azure DevOps: leitura de sprint e cards, escrita apenas via Executor."""
from __future__ import annotations

import os
from typing import Any
from urllib.parse import quote

import requests

from ..auth import cabecalho
from ..config import env, settings

API = "7.1"


def _conexao(var: str, cfg: dict, chave: str) -> str:
    """Onde o board vive: variavel de ambiente primeiro, settings.yaml depois.

    O endereco do board nao e segredo e e o mesmo para a squad inteira, entao
    o padrao fica versionado e ninguem precisa de `.env` para comecar. A
    variavel continua vencendo, para apontar para outro time sem editar
    arquivo que vai para o git.
    """
    valor = os.getenv(var) or cfg.get(chave)
    if not valor:
        raise RuntimeError(
            f"Sem {var}: nao esta no ambiente nem em config/settings.yaml "
            f"({chave}).")
    return valor


class DevOpsClient:
    def __init__(self, org_url: str | None = None, project: str | None = None,
                 team: str | None = None, pat: str | None = None):
        cfg = settings()["devops"]
        self.org_url = (org_url or _conexao("AZDO_ORG_URL", cfg, "org_url")).rstrip("/")
        self.project = project or _conexao("AZDO_PROJECT", cfg, "project")
        self.team = (team or os.getenv("AZDO_TEAM") or cfg.get("team")
                     or self.project)

        # Nome de time no Azure DevOps costuma ter espaco, como "Squad Revenue
        # DI", e projeto tambem pode ter. Interpolar cru numa f-string produz
        # URL invalida, e o erro que volta e um 404 generico, que se confunde
        # com time inexistente. Codificar aqui, uma vez, evita a caca ao erro
        # errado. `safe=""` porque estes sao segmentos, e nao caminhos.
        self._project = quote(self.project, safe="")
        self._team = quote(self.team, safe="")

        # `required=False`: sem PAT nao e erro, e o caminho normal. A
        # autenticacao cai para o Entra ID, e o erro, se vier, vem de la com a
        # instrucao do que fazer.
        pat = pat if pat is not None else env("AZDO_PAT", required=False)
        header, self.metodo_auth = cabecalho(pat)
        self.s = requests.Session()
        self.s.headers.update(header)

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
        url = f"{self.org_url}/{self._project}/{self._team}/_apis/work/teamsettings/iterations"
        data = self._get(url, **{"$timeframe": "current"})
        values = data.get("value", [])
        if not values:
            raise RuntimeError("Nenhuma iteracao corrente encontrada para o time.")
        return values[0]

    def iteration(self, iteration_id: str | None = None) -> dict:
        """A iteracao inteira, e nao so o id.

        Nome e datas de inicio e fim entram no cabecalho da sprint review, e um
        board devolvido so com o id fazia a review sair com `sprint: None`.
        """
        if iteration_id is None:
            return self.current_iteration()
        achada = next((i for i in self.iterations() if i["id"] == iteration_id), None)
        return achada or {"id": iteration_id}

    def iterations(self) -> list[dict]:
        url = f"{self.org_url}/{self._project}/{self._team}/_apis/work/teamsettings/iterations"
        return self._get(url).get("value", [])

    def iteration_work_item_ids(self, iteration_id: str) -> list[int]:
        url = (f"{self.org_url}/{self._project}/{self._team}/_apis/work/teamsettings/"
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
            "System.AssignedTo", "System.IterationPath", "System.AreaPath",
            "System.Parent", "System.Tags", "System.ChangedDate",
            "System.Description",
            "Microsoft.VSTS.Common.AcceptanceCriteria",
        ]
        out: list[dict] = []
        url = f"{self.org_url}/{self._project}/_apis/wit/workitemsbatch"
        for i in range(0, len(ids), 200):
            body = {"ids": ids[i:i + 200], "fields": fields}
            out.extend(self._post(url, body).get("value", []))
        return out

    def sprint_board(self, iteration_id: str | None = None) -> dict:
        """Cards da sprint agrupados pelas secoes da sprint review.

        Os grupos existem para casar com `templates/sprint-review.md`, e nao
        por comodidade de exibicao: `concluidos` alimenta "Entregue",
        `aguardando_validacao` alimenta "Em validacao", e o resto e o que a
        secao "Nao entregue" precisa explicar. Um card cai em exatamente um
        grupo, senao a review contaria a mesma entrega duas vezes.

        `estados_concluidos` e lido com `.get` porque a fixture de teste do
        portao descreve um processo ficticio que nao tem esse conceito.
        """
        cfg = settings()["devops"]
        it = self.iteration(iteration_id)
        ids = self.iteration_work_item_ids(it["id"])
        items = self.work_items(ids)

        def state(wi):
            return wi["fields"].get("System.State", "")

        concluidos = [w for w in items if state(w) in cfg.get("estados_concluidos", [])]
        validacao = [w for w in items if state(w) in cfg["estados_validacao"]
                     and w not in concluidos]
        ativos = [w for w in items if state(w) in cfg["estados_ativos"]
                  and w not in concluidos and w not in validacao]
        outros = [w for w in items if w not in concluidos and w not in validacao
                  and w not in ativos]
        return {
            "iteration": it,
            "total": len(items),
            "concluidos": concluidos,
            "aguardando_validacao": validacao,
            "ativos": ativos,
            "outros": outros,
        }

    def titulos(self, ids: list[int]) -> dict[int, str]:
        """Titulo de cada id, num batch so. Usado para nomear a frente pelo pai."""
        itens = self.work_items(sorted(set(ids)), fields=["System.Id", "System.Title"])
        return {i["id"]: i["fields"].get("System.Title", "") for i in itens}

    def me(self) -> dict:
        """Quem e o dono do PAT em uso.

        Cada pessoa da squad usa a propria credencial, entao a identidade sai
        dela: perguntar o nome ao usuario abriria espaco para alguem listar os
        cards de outro por engano de digitacao.

        Tenta `connectionData`, que responde no mesmo host da org. Se a org
        estiver num tenant que nao expoe esse endpoint, cai para o perfil em
        `vssps`, que e o caminho documentado.
        """
        try:
            user = self._get(f"{self.org_url}/_apis/connectionData").get(
                "authenticatedUser", {})
            email = (user.get("properties", {})
                     .get("Account", {}).get("$value", ""))
            nome = user.get("providerDisplayName") or user.get("customDisplayName")
            if nome or email:
                return {"nome": nome or "", "email": email or ""}
        except requests.HTTPError:
            pass

        org = self.org_url.rstrip("/").rsplit("/", 1)[-1]
        perfil = self._get(
            f"https://vssps.dev.azure.com/{org}/_apis/profile/profiles/me")
        return {"nome": perfil.get("displayName", ""),
                "email": perfil.get("emailAddress", "")}

    def comments(self, work_item_id: int) -> list[dict]:
        url = f"{self.org_url}/{self._project}/_apis/wit/workItems/{work_item_id}/comments"
        return self._get(url, **{"api-version": "7.1-preview.3"}).get("comments", [])

    def updates(self, work_item_id: int) -> list[dict]:
        """Historico de mudancas. Util para reconstruir o que aconteceu na sprint."""
        url = f"{self.org_url}/{self._project}/_apis/wit/workItems/{work_item_id}/updates"
        return self._get(url).get("value", [])

    # ---------- ESCRITA (so chamada pelo Executor) ----------

    def add_comment(self, work_item_id: int, text: str) -> dict:
        url = f"{self.org_url}/{self._project}/_apis/wit/workItems/{work_item_id}/comments"
        return self._post(url, {"text": text}, **{"api-version": "7.1-preview.3"})

    def set_state(self, work_item_id: int, new_state: str) -> dict:
        url = f"{self.org_url}/{self._project}/_apis/wit/workitems/{work_item_id}"
        patch = [{"op": "add", "path": "/fields/System.State", "value": new_state}]
        return self._patch(url, patch)

    def create_work_item(self, item_type: str, title: str, description: str = "",
                         parent_id: int | None = None,
                         iteration: str | None = None) -> dict:
        url = f"{self.org_url}/{self._project}/_apis/wit/workitems/${item_type}"
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


# ---------- identidade de pessoa ----------
#
# O DevOps devolve o responsavel como objeto, com nome de exibicao e email, e
# nem sempre com os dois preenchidos. Comparar por string crua espalharia essa
# irregularidade por todo lugar que precisa filtrar por pessoa.


def responsavel(wi: dict) -> dict:
    """Nome e email de quem responde pelo card. Vazio quando nao ha ninguem."""
    pessoa = wi.get("fields", {}).get("System.AssignedTo") or {}
    return {"nome": pessoa.get("displayName", ""),
            "email": pessoa.get("uniqueName", "")}


def e_de(wi: dict, pessoa: str) -> bool:
    """Se o card e de `pessoa`, casando por email ou por nome, sem diferenciar caixa."""
    alvo = pessoa.strip().casefold()
    if not alvo:
        return False
    r = responsavel(wi)
    return alvo in (r["nome"].casefold(), r["email"].casefold())


def filtrar_por_pessoa(items: list[dict], pessoa: str) -> list[dict]:
    return [w for w in items if e_de(w, pessoa)]


# ---------- frente de trabalho ----------
#
# A sprint review se organiza por frente, que e o produto ou a solucao que o
# leitor reconhece, e nao por card. O board nao tem esse campo, e conferindo
# contra a sprint S3-Q3-26 em 31/08/2026 nenhum campo serve de substituto:
# `System.AreaPath` e identico nos 43 cards da sprint, `System.Tags` carrega
# rotulo de processo ("Nao Planejado", "Bloqueado", "Otimizacao"), e o card
# pai e um OKR do trimestre, do tipo "Ter ate 7% de NP no Q3-26".
#
# O pai agrupa bem, e nomeia mal. Entao ele vira chave de agrupamento e nunca
# titulo de secao: uma secao chamada "Ter ate 7% de NP no Q3-26" estaria
# errada com cara de certa, e o titulo errado sobrevive a revisao. O titulo
# fica em branco e o que o board sabe vai como dica, para a pessoa nomear.

FRENTE_INDEFINIDA = "Frente a definir"


def frente(wi: dict, titulos_pai: dict[int, str] | None = None) -> dict:
    """Como agrupar o card na secao 4, e o que o board sabe sobre o grupo.

    `chave` agrupa e nao aparece no documento. `dica` aparece em comentario,
    para quem escreve reconhecer o grupo e dar o nome de verdade.
    """
    f = wi.get("fields", {})
    pai = f.get("System.Parent")
    if pai:
        titulo = (titulos_pai or {}).get(pai, "")
        dica = f'card pai {pai}' + (f': "{titulo}"' if titulo else "")
        return {"chave": f"pai:{pai}", "dica": dica}

    area = f.get("System.AreaPath", "")
    folha = area.rsplit("\\", 1)[-1] if area else ""
    if folha:
        return {"chave": f"area:{folha}", "dica": f"sem card pai, area {folha}"}
    return {"chave": "sem-grupo", "dica": "sem card pai e sem area"}
