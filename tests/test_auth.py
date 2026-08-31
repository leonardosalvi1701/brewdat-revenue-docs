"""Escolha de credencial.

Sem rede e sem `az`: o que se testa aqui e a decisao entre PAT e Entra ID, e a
qualidade da mensagem quando nao ha nenhum dos dois. Uma mensagem ruim aqui
custa uma pessoa travada no primeiro dia.
"""
import base64

import pytest

from docsquad import auth


def test_pat_ganha_de_az_quando_preenchido(monkeypatch):
    """Escolha explicita nao perde para implicita."""
    monkeypatch.setattr(auth, "token_entra", lambda **_: pytest.fail("nao usar az"))
    header, metodo = auth.cabecalho("segredo")
    assert header["Authorization"] == "Basic " + base64.b64encode(b":segredo").decode()
    assert "PAT" in metodo


def test_sem_pat_usa_entra(monkeypatch):
    monkeypatch.setattr(auth, "token_entra", lambda **_: "tok123")
    header, metodo = auth.cabecalho("")
    assert header["Authorization"] == "Bearer tok123"
    assert "az login" in metodo


def test_sem_az_instalado_diz_o_que_fazer(monkeypatch):
    monkeypatch.setattr(auth.shutil, "which", lambda _: None)
    with pytest.raises(auth.SemCredencial) as exc:
        auth.token_entra()
    assert "az login" in str(exc.value) and "AZDO_PAT" in str(exc.value)


def test_sessao_expirada_manda_rodar_az_login(monkeypatch):
    class Proc:
        returncode = 1
        stdout = ""
        stderr = "ERROR: Please run 'az login' to setup account."
    monkeypatch.setattr(auth.shutil, "which", lambda _: "/usr/bin/az")
    monkeypatch.setattr(auth.subprocess, "run", lambda *a, **k: Proc())
    with pytest.raises(auth.SemCredencial, match="az login"):
        auth.token_entra()


def test_resposta_sem_token_nao_passa_silenciosa(monkeypatch):
    class Proc:
        returncode = 0
        stdout = '{"expiresOn": "2026-08-31"}'
        stderr = ""
    monkeypatch.setattr(auth.shutil, "which", lambda _: "/usr/bin/az")
    monkeypatch.setattr(auth.subprocess, "run", lambda *a, **k: Proc())
    with pytest.raises(auth.SemCredencial, match="accessToken"):
        auth.token_entra()


def test_token_nao_aparece_no_nome_do_metodo(monkeypatch):
    """O metodo vai para a tela. O segredo nao pode ir junto."""
    monkeypatch.setattr(auth, "token_entra", lambda **_: "tok-secreto")
    _, metodo = auth.cabecalho("")
    assert "tok-secreto" not in metodo
    _, metodo_pat = auth.cabecalho("pat-secreto")
    assert "pat-secreto" not in metodo_pat
