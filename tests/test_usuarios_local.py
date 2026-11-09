"""A identidade pessoal mora em config/usuarios.local.yaml, fora do git.

O settings.yaml e versionado e vale para a squad inteira; o arquivo local e
juntado a ele na leitura. Os testes garantem a juncao, e que o arquivo da
maquina de quem roda os testes nunca entra quando DOCSQUAD_SETTINGS aponta
para a fixture.
"""
from __future__ import annotations

from docsquad import config
from docsquad import diagnostico as diag

CHEIO = """usuarios:
  azure: "a@x.com"
  databricks: "d@x.com"
  github: "login"
  devops_email: "o@x.com"
  git_email: "g@x.com"
"""


def _escrever(tmp_path, nome, texto):
    caminho = tmp_path / nome
    caminho.write_text(texto, encoding="utf-8")
    return caminho


def test_arquivo_local_entra_por_cima_do_settings(tmp_path, monkeypatch):
    base = _escrever(tmp_path, "settings.yaml",
                     'squad:\n  nome: X\nusuarios:\n  azure: "velho@x.com"\n')
    local = _escrever(tmp_path, "usuarios.local.yaml", CHEIO)
    monkeypatch.setenv("DOCSQUAD_SETTINGS", str(base))
    monkeypatch.setenv("DOCSQUAD_USUARIOS", str(local))
    cfg = config.settings()
    assert cfg["squad"]["nome"] == "X"
    assert cfg["usuarios"]["azure"] == "a@x.com"
    assert cfg["usuarios"]["git_email"] == "g@x.com"


def test_com_fixture_o_arquivo_da_maquina_nao_entra(monkeypatch):
    monkeypatch.delenv("DOCSQUAD_USUARIOS", raising=False)
    assert config._caminho_usuarios() is None


def test_sem_arquivo_local_falha_e_diz_o_que_fazer(tmp_path):
    achados = diag.checar_usuarios({}, arquivo=tmp_path / "nao-existe.yaml",
                                   settings_versionado=tmp_path / "nao-existe-2.yaml")
    assert achados[0].nivel == diag.FALHA
    assert "preparar_ambiente.sh" in achados[0].texto


def test_campo_com_preencher_falha_nomeando_o_campo(tmp_path):
    local = _escrever(tmp_path, "usuarios.local.yaml",
                      CHEIO.replace('"login"', '"PREENCHER_LOGIN_DO_GITHUB"'))
    cfg = {"usuarios": {"azure": "a@x.com", "databricks": "d@x.com",
                        "github": "PREENCHER_LOGIN_DO_GITHUB",
                        "devops_email": "o@x.com", "git_email": "g@x.com"}}
    achados = diag.checar_usuarios(cfg, arquivo=local,
                                   settings_versionado=tmp_path / "nao-existe.yaml")
    assert achados[0].nivel == diag.FALHA
    assert "usuarios.github" in achados[0].texto


def test_identidade_esquecida_no_settings_versionado_gera_aviso(tmp_path):
    local = _escrever(tmp_path, "usuarios.local.yaml", CHEIO)
    versionado = _escrever(tmp_path, "settings.yaml", CHEIO)
    cfg = {"usuarios": {c: "x@x.com" for c in diag.CAMPOS_USUARIO}}
    achados = diag.checar_usuarios(cfg, arquivo=local, settings_versionado=versionado)
    assert [a.nivel for a in achados] == [diag.OK, diag.AVISO]
    assert "git checkout config/settings.yaml" in achados[1].texto
