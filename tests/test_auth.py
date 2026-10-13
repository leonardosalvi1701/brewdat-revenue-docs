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


# ---------- Databricks ----------

def test_databricks_token_ganha_de_perfil(monkeypatch):
    monkeypatch.setattr(auth, "token_databricks", lambda *a, **k: pytest.fail("nao usar cli"))
    header, metodo = auth.cabecalho_databricks("dapi-segredo", "meu-perfil")
    assert header["Authorization"] == "Bearer dapi-segredo"
    assert "dapi-segredo" not in metodo


def test_databricks_sem_token_usa_perfil(monkeypatch):
    monkeypatch.setattr(auth, "token_databricks", lambda perfil, **_: f"tok-{perfil}")
    header, metodo = auth.cabecalho_databricks("", "meu-perfil")
    assert header["Authorization"] == "Bearer tok-meu-perfil"
    assert "meu-perfil" in metodo and "tok-" not in metodo


def test_databricks_sem_nada_diz_o_que_fazer():
    with pytest.raises(auth.SemCredencial) as exc:
        auth.cabecalho_databricks("", None)
    assert "databricks auth login" in str(exc.value)
    assert "DATABRICKS_CONFIG_PROFILE" in str(exc.value)
    assert "DATABRICKS_TOKEN" not in str(exc.value)


def test_databricks_sessao_expirada_manda_logar_no_perfil(monkeypatch):
    class Proc:
        returncode = 1
        stdout = ""
        stderr = "Error: refresh token is invalid"
    monkeypatch.setattr(auth.shutil, "which", lambda _: "/usr/bin/databricks")
    monkeypatch.setattr(auth.subprocess, "run", lambda *a, **k: Proc())
    with pytest.raises(auth.SemCredencial, match=r"auth login --host \S+ --profile meu-perfil"):
        auth.token_databricks("meu-perfil")


def test_databricks_le_access_token_da_cli(monkeypatch):
    class Proc:
        returncode = 0
        stdout = '{"access_token": "abc", "token_type": "Bearer"}'
        stderr = ""
    monkeypatch.setattr(auth.shutil, "which", lambda _: "/usr/bin/databricks")
    monkeypatch.setattr(auth.subprocess, "run", lambda *a, **k: Proc())
    assert auth.token_databricks("meu-perfil") == "abc"


# ---------- perfil e CLI ----------
#
# Os quatro casos de 08/10/2026: perfil com nome que nao existe, perfil
# azure-cli que a CLI da como valido e nao devolve token, CLI legada na frente
# da nova no PATH, e o segredo do arquivo que nao pode vazar para a tela.

def cfg(tmp_path, monkeypatch, texto):
    arquivo = tmp_path / "databrickscfg"
    arquivo.write_text(texto, encoding="utf-8")
    monkeypatch.setenv("DATABRICKS_CONFIG_FILE", str(arquivo))
    return arquivo


CFG = """
[DEFAULT]

[sso]
host      = https://adb-1.azuredatabricks.net/
auth_type = databricks-cli

[azcli]
host      = https://adb-1.azuredatabricks.net
auth_type = azure-cli

[pat]
host  = https://adb-1.azuredatabricks.net
token = dapi-nao-pode-vazar

[__settings__]
auth_storage = plaintext
"""


def test_le_perfis_sem_segredo(tmp_path, monkeypatch):
    cfg(tmp_path, monkeypatch, CFG)
    perfis = auth.ler_perfis()
    assert set(perfis) == {"sso", "azcli", "pat"}
    assert perfis["sso"] == {"host": "https://adb-1.azuredatabricks.net", "tipo": "databricks-cli"}
    assert perfis["pat"]["tipo"] == "pat"
    assert "dapi-nao-pode-vazar" not in repr(perfis)


def test_perfil_inexistente_lista_os_que_existem(tmp_path, monkeypatch):
    cfg(tmp_path, monkeypatch, CFG)
    monkeypatch.setattr(auth.subprocess, "run", lambda *a, **k: pytest.fail("nao chamar a CLI"))
    with pytest.raises(auth.SemCredencial) as exc:
        auth.checar_perfil("BRMIN197195@ab-inbev.com")
    assert "nao existe" in str(exc.value) and "sso, azcli, pat" in str(exc.value)


def test_perfil_azure_cli_nao_e_tratado_como_sessao_expirada(tmp_path, monkeypatch):
    cfg(tmp_path, monkeypatch, CFG)
    with pytest.raises(auth.SemCredencial) as exc:
        auth.checar_perfil("azcli")
    texto = str(exc.value)
    assert "auth_type=azure-cli" in texto and "expir" not in texto
    assert "--host https://adb-1.azuredatabricks.net --profile azcli-sso" in texto


def test_perfil_pat_nao_vaza_token_na_mensagem(tmp_path, monkeypatch):
    cfg(tmp_path, monkeypatch, CFG)
    with pytest.raises(auth.SemCredencial) as exc:
        auth.checar_perfil("pat")
    assert "dapi-nao-pode-vazar" not in str(exc.value)


def test_perfil_sso_passa(tmp_path, monkeypatch):
    cfg(tmp_path, monkeypatch, CFG)
    auth.checar_perfil("sso")


def escreve_cli(pasta, conteudo):
    pasta.mkdir(parents=True, exist_ok=True)
    cli = pasta / "databricks"
    cli.write_bytes(conteudo)
    cli.chmod(0o755)
    return str(cli)


def test_cli_legada_na_frente_e_pulada(tmp_path, monkeypatch):
    legada = escreve_cli(tmp_path / "venv", b"#!/home/x/.venv/bin/python\nimport sys\n")
    nova = escreve_cli(tmp_path / "usr", b"\x7fELF binario")
    monkeypatch.setenv("PATH", f"{tmp_path / 'venv'}:{tmp_path / 'usr'}")
    assert auth.cli_legada(legada) and not auth.cli_legada(nova)
    assert auth.clis_databricks() == [legada, nova]
    assert auth.cli_databricks() == nova


def test_so_cli_legada_manda_desinstalar(tmp_path, monkeypatch):
    escreve_cli(tmp_path / "venv", b"#!/usr/bin/env python3\n")
    monkeypatch.setenv("PATH", str(tmp_path / "venv"))
    with pytest.raises(auth.SemCredencial, match="pip uninstall databricks-cli"):
        auth.cli_databricks()
