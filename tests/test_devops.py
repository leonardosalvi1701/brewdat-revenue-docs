"""Montagem de url do Azure DevOps.

O time da squad se chama "Squad Revenue DI", com espacos, e o nome vai no
caminho da url. Interpolado cru, o resultado e um 404 generico, que se parece
com time inexistente e manda quem esta depurando para o lado errado.
"""
import pytest

from docsquad.connectors import DevOpsClient

ORG = "https://dev.azure.com/AMBEV-SA"
PROJETO = "AMBEV-ANALYTICS-DATA-CHAPTER-SALES"
TIME = "Squad Revenue DI"


@pytest.fixture
def client():
    return DevOpsClient(org_url=ORG, project=PROJETO, team=TIME, pat="fake")


def test_espaco_no_nome_do_time_e_codificado(client):
    assert client._team == "Squad%20Revenue%20DI"
    assert " " not in f"{client.org_url}/{client._project}/{client._team}"


def test_nome_cru_continua_disponivel_para_exibicao(client):
    """A url e codificada; o que aparece para a pessoa nao."""
    assert client.team == TIME


def test_barra_no_segmento_nao_inventa_caminho(client):
    """`safe=''` garante que um nome com barra nao vire dois segmentos de url."""
    c = DevOpsClient(org_url=ORG, project=PROJETO, team="A/B", pat="fake")
    assert c._team == "A%2FB"


def test_org_url_sem_barra_final():
    c = DevOpsClient(org_url=ORG + "/", project=PROJETO, team=TIME, pat="fake")
    assert c.org_url == ORG


def test_time_ausente_cai_para_o_projeto():
    c = DevOpsClient(org_url=ORG, project=PROJETO, team=None, pat="fake")
    assert c.team == PROJETO
