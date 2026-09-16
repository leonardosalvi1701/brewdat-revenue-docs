"""Resolucao de caminho do Databricks.

Sem rede: o que se testa e a troca de `{usuario}` pelo login atual, que existe
porque o repo do modelo e uma pasta Git dentro da pasta de cada pessoa.
"""
from docsquad.connectors.databricks import DatabricksClient


def cliente(monkeypatch, chamadas):
    c = DatabricksClient(host="https://exemplo", token="t")

    def fake_get(endpoint, **params):
        chamadas.append((endpoint, params))
        if endpoint.endswith("/scim/v2/Me"):
            return {"userName": "pessoa@exemplo.com"}
        return {"objects": []}

    monkeypatch.setattr(c, "_get", fake_get)
    return c


def test_troca_usuario_pelo_login(monkeypatch):
    chamadas = []
    c = cliente(monkeypatch, chamadas)
    c.list_path("/Workspace/Users/{usuario}/repo")
    assert chamadas[-1] == ("/api/2.0/workspace/list",
                            {"path": "/Workspace/Users/pessoa@exemplo.com/repo"})


def test_caminho_fixo_nao_consulta_usuario(monkeypatch):
    chamadas = []
    c = cliente(monkeypatch, chamadas)
    c.list_path("/Workspace/Shared/x")
    assert [e for e, _ in chamadas] == ["/api/2.0/workspace/list"]


def test_usuario_consultado_uma_vez(monkeypatch):
    chamadas = []
    c = cliente(monkeypatch, chamadas)
    c.inventory(["/Workspace/Users/{usuario}/a", "/Workspace/Users/{usuario}/b"])
    assert sum(e.endswith("/scim/v2/Me") for e, _ in chamadas) == 1
