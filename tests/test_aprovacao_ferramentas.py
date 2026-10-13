"""Janela de permissao das tres ferramentas (ADR-0015).

A garantia de que o agente nao decide proposta sozinho mora na configuracao de
cada ferramenta, gerada de `agent_instructions/aprovacao.yaml`. O que se testa
e que as tres cobrem todo comando da fonte, e que o hook do Copilot pede
aprovacao no comando e so no comando.
"""
import importlib.util
import json
import sys
from pathlib import Path

import pytest
import yaml

RAIZ = Path(__file__).resolve().parents[1]
FONTE = yaml.safe_load((RAIZ / "agent_instructions" / "aprovacao.yaml").read_text(encoding="utf-8"))


def carregar(nome, caminho):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    modulo = importlib.util.module_from_spec(spec)
    sys.modules[nome] = modulo
    spec.loader.exec_module(modulo)
    return modulo


hook = carregar("exigir_aprovacao", RAIZ / "scripts" / "hooks" / "exigir_aprovacao.py")
sync = carregar("sync_agent_files", RAIZ / "scripts" / "sync_agent_files.py")


def test_fonte_cobre_os_comandos_que_decidem():
    assert set(FONTE["comandos"]) >= {"approve", "apply", "reject", "decidir"}


def test_hook_le_os_mesmos_comandos_que_o_yaml():
    """O hook roda fora do .venv e le o yaml sem pyyaml. Nao pode divergir."""
    assert hook._comandos() == FONTE["comandos"]


@pytest.mark.parametrize("comando", FONTE["comandos"])
@pytest.mark.parametrize("prefixo", [" ".join(p) for p in FONTE["prefixos"]])
def test_hook_pede_aprovacao_em_toda_forma(comando, prefixo):
    linha = f"cd /repo && {prefixo} {comando} abc123"
    cli = {"toolName": "bash", "toolArgs": json.dumps({"command": linha})}
    vscode = {"tool_name": "run_in_terminal", "tool_input": {"command": linha}}
    for entrada in (cli, vscode):
        resposta = hook.decidir(entrada)
        assert resposta["permissionDecision"] == "ask"
        assert resposta["hookSpecificOutput"]["permissionDecision"] == "ask"


@pytest.mark.parametrize("entrada", [
    {"toolName": "bash", "toolArgs": {"command": "docs propose comment 1 --file r.md"}},
    {"toolName": "bash", "toolArgs": {"command": "docs show abc123"}},
    {"toolName": "bash", "toolArgs": {"command": "mkdocs apply"}},
    {"toolName": "edit", "toolArgs": {"path": "README.md", "new_str": "docs approve abc"}},
    {},
])
def test_hook_nao_pergunta_no_resto(entrada):
    assert hook.decidir(entrada) is None


def test_claude_pergunta_em_todo_comando():
    _, texto = sync.claude_settings()
    ask = json.loads(texto)["permissions"]["ask"]
    for comando in FONTE["comandos"]:
        assert f"Bash(*docs {comando}*)" in ask


def test_codex_tem_prompt_em_todo_prefixo():
    _, texto = sync.codex_rules()
    assert texto.count('decision = "prompt"') == len(FONTE["prefixos"])
    assert "allow" not in texto
    for prefixo in FONTE["prefixos"]:
        assert json.dumps([*prefixo, FONTE["comandos"]]) in texto


def test_copilot_chama_o_hook():
    _, texto = sync.copilot_hooks()
    entrada = json.loads(texto)["hooks"]["preToolUse"][0]
    assert "scripts/hooks/exigir_aprovacao.py" in entrada["bash"]
    assert "scripts/hooks/exigir_aprovacao.py" in entrada["powershell"]
