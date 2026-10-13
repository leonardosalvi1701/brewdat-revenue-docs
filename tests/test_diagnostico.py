"""Diagnostico do `docs config-check`.

Sem rede. Cada teste e um dos casos que travaram alguem da squad em
08/10/2026, e o que se confere e que o diagnostico aponta a causa, e nao o
sintoma.
"""
from docsquad import config, diagnostico as diag

PERFIS = {"sso": {"host": "https://adb-1.azuredatabricks.net", "tipo": "databricks-cli"},
          "azcli": {"host": "https://adb-1.azuredatabricks.net", "tipo": "azure-cli"}}
HOST = "https://adb-1.azuredatabricks.net"


def niveis(achados):
    return [a.nivel for a in achados]


def test_perfil_ok():
    assert niveis(diag.checar_perfil("sso", ".env", "", PERFIS, HOST)) == [diag.OK]


def test_terminal_divergente_avisa_mesmo_com_perfil_ok():
    achados = diag.checar_perfil("sso", ".env", "BRMIN197195@ab-inbev.com", PERFIS, HOST)
    assert niveis(achados) == [diag.AVISO, diag.OK]
    assert "unset DATABRICKS_CONFIG_PROFILE" in achados[0].texto


def test_perfil_inexistente_falha_com_a_origem():
    achados = diag.checar_perfil("BRMIN197195@ab-inbev.com", "terminal", "", PERFIS, HOST)
    assert niveis(achados) == [diag.FALHA]
    assert "do terminal" in achados[0].texto and "sso, azcli" in achados[0].texto


def test_perfil_azure_cli_falha_e_sugere_perfil_sso():
    achados = diag.checar_perfil("azcli", ".env", "", PERFIS, HOST)
    assert niveis(achados) == [diag.FALHA]
    assert "--perfil azcli-sso" in achados[0].texto


def test_host_do_perfil_diferente_do_env_falha():
    achados = diag.checar_perfil("sso", ".env", "", PERFIS, "https://adb-2.azuredatabricks.net")
    assert niveis(achados) == [diag.FALHA]


def test_sem_databrickscfg_falha():
    assert niveis(diag.checar_perfil("sso", ".env", "", None, HOST)) == [diag.FALHA]


def test_host_com_redirecionamento_falha():
    """Redirecionamento descarta o cabecalho, e o sintoma e um 401 enganoso."""
    for ruim in ["http://adb-1.azuredatabricks.net",
                 "https://adb-1.azuredatabricks.net/?o=1",
                 "https://adb-1.azuredatabricks.net/browse"]:
        assert niveis(diag.checar_host(ruim)) == [diag.FALHA], ruim
    assert niveis(diag.checar_host(HOST + "/")) == [diag.OK]


def test_cli_legada_na_frente_avisa(tmp_path):
    legada = tmp_path / "venv" / "databricks"
    nova = tmp_path / "usr" / "databricks"
    for arq, conteudo in [(legada, b"#!/x/python\n"), (nova, b"\x7fELF")]:
        arq.parent.mkdir()
        arq.write_bytes(conteudo)
    achados = diag.checar_clis([str(legada), str(nova)])
    assert niveis(achados) == [diag.OK, diag.AVISO]
    assert "na frente da nova" in achados[1].texto


def test_env_com_crlf_avisa(tmp_path):
    env = tmp_path / ".env"
    env.write_bytes(b"DATABRICKS_CONFIG_PROFILE=sso\r\n")
    assert niveis(diag.checar_env_file(env)) == [diag.AVISO]


def test_env_do_arquivo_ganha_do_terminal(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text("DATABRICKS_CONFIG_PROFILE=sso\r\n", encoding="utf-8")
    monkeypatch.setattr(config, "ROOT", tmp_path)
    monkeypatch.setenv("DATABRICKS_CONFIG_PROFILE", "BRMIN197195@ab-inbev.com")
    assert config.perfil_databricks() == ("sso", ".env")


def test_terminal_vale_com_env_em_branco(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text("DATABRICKS_CONFIG_PROFILE=\n", encoding="utf-8")
    monkeypatch.setattr(config, "ROOT", tmp_path)
    monkeypatch.setenv("DATABRICKS_CONFIG_PROFILE", "automacao")
    assert config.perfil_databricks() == ("automacao", "terminal")


# ---------- caminho de escrita ----------

PREFIXOS = ["/Workspace/Users/{usuario}/revenue-docs/escritos"]


def test_caminho_dentro_do_prefixo_passa():
    alvo = "/Workspace/Users/a@b.com/revenue-docs/escritos/nb"
    assert diag.checar_caminho_escrita(alvo, PREFIXOS) is None


def test_caminho_fora_do_prefixo_sugere_o_certo():
    alvo = "/Workspace/Users/brmin197195@ab-inbev.com/Volume Limit/00_Features_PDV_documentacao"
    erro = diag.checar_caminho_escrita(alvo, PREFIXOS)
    assert "fora dos prefixos" in erro
    assert ("/Workspace/Users/brmin197195@ab-inbev.com/revenue-docs/escritos/"
            "00_Features_PDV_documentacao") in erro


def test_prefixo_nao_libera_irmao_nem_escapa_com_ponto_ponto():
    assert diag.checar_caminho_escrita(
        "/Workspace/Users/a/revenue-docs/escritos-outro/nb", PREFIXOS) is not None
    assert diag.checar_caminho_escrita(
        "/Workspace/Users/a/revenue-docs/escritos/../../nb", PREFIXOS) is not None
    assert diag.checar_caminho_escrita(
        "/Workspace/Users/a/x/revenue-docs/escritos/nb", PREFIXOS) is not None
