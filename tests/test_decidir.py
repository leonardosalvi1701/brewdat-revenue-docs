"""`docs decidir`: o fluxo de aprovacao interativo.

Sem rede e sem Executor de verdade. O que se testa e a decisao de cada
proposta, quem fica registrado como aprovador, e que nada e aplicado sem a
confirmacao final.
"""
import pytest
from typer.testing import CliRunner

from docsquad import cli
from docsquad.gate import Proposal, ProposalKind, ProposalStore

runner = CliRunner()


@pytest.fixture
def ambiente(tmp_path, monkeypatch):
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    store = ProposalStore(tmp_path)
    for i, alvo in enumerate(("101", "102", "103")):
        store.save(Proposal(kind=ProposalKind.CARD_TAG, target=alvo,
                            summary=f"Card {alvo}: +Bloqueado", payload={"tag": "Bloqueado"},
                            created_at=f"2026-10-09T10:00:0{i}+00:00"))
    aplicadas = []
    monkeypatch.setattr(cli, "store", store)
    monkeypatch.setattr(cli, "_interativo", lambda: True)
    monkeypatch.setattr(cli, "_identidade", lambda: ("pessoa@exemplo.com", "az login"))
    monkeypatch.setattr(cli, "_aplicar", lambda alvos, dry_run=False: aplicadas.extend(alvos))
    return store, aplicadas


def test_fora_de_terminal_recusa_sem_tocar_em_nada(ambiente, monkeypatch):
    """O shell de um agente nao e terminal interativo."""
    store, aplicadas = ambiente
    monkeypatch.setattr(cli, "_interativo", lambda: False)
    r = runner.invoke(cli.app, ["decidir"], input="a\na\na\ns\n")
    assert r.exit_code == 1
    assert len(store.list("pending")) == 3 and not aplicadas


def test_aprova_recusa_pula_e_aplica_so_as_aprovadas(ambiente):
    store, aplicadas = ambiente
    r = runner.invoke(cli.app, ["decidir"], input="a\nr\ntag errada\np\ns\n")
    assert r.exit_code == 0, r.output
    aprovadas = store.list("approved")
    assert [p.target for p in aprovadas] == ["101"]
    assert aprovadas[0].approved_by == "pessoa@exemplo.com"
    assert store.list("rejected")[0].rejection_reason == "tag errada"
    assert [p.target for p in store.list("pending")] == ["103"]
    assert [p.target for p in aplicadas] == ["101"]


def test_sem_confirmacao_final_nada_e_aplicado(ambiente):
    store, aplicadas = ambiente
    r = runner.invoke(cli.app, ["decidir"], input="a\na\na\nn\n")
    assert r.exit_code == 0, r.output
    assert len(store.list("approved")) == 3 and not aplicadas
    assert "docs apply --all" in r.output


def test_recusa_exige_motivo(ambiente):
    store, _ = ambiente
    runner.invoke(cli.app, ["decidir"], input="r\n\n  \nduplicada\ns\n")
    assert store.list("rejected")[0].rejection_reason == "duplicada"


def test_tecla_invalida_pergunta_de_novo(ambiente):
    store, _ = ambiente
    runner.invoke(cli.app, ["decidir"], input="x\nsim\ns\n")
    assert len(store.list("pending")) == 3


def test_como_sobrescreve_a_identidade(ambiente):
    store, _ = ambiente
    runner.invoke(cli.app, ["decidir", "--como", "Leo"], input="a\ns\nn\n")
    assert store.list("approved")[0].approved_by == "Leo"


def test_sem_identidade_pergunta_quem_aprova(ambiente, monkeypatch):
    store, _ = ambiente
    monkeypatch.setattr(cli, "_identidade", lambda: ("", ""))
    runner.invoke(cli.app, ["decidir"], input="Fulano\na\ns\nn\n")
    assert store.list("approved")[0].approved_by == "Fulano"


# ---------- approve pela janela de permissao (ADR-0015) ----------

@pytest.fixture
def sem_ci(monkeypatch):
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)


def test_approve_sem_by_usa_a_identidade_do_az(ambiente, sem_ci, monkeypatch):
    """Pelo agente, o comando roda sem terminal, depois do clique da pessoa."""
    store, aplicadas = ambiente
    monkeypatch.setattr(cli, "_interativo", lambda: False)
    pid = sorted(store.list("pending"), key=lambda p: p.created_at)[0].id
    r = runner.invoke(cli.app, ["approve", pid])
    assert r.exit_code == 0, r.output
    assert store.load(pid).approved_by == "pessoa@exemplo.com" and not aplicadas


def test_approve_com_aplicar_aplica_so_aquela(ambiente, sem_ci):
    store, aplicadas = ambiente
    pid = store.list("pending")[0].id
    runner.invoke(cli.app, ["approve", pid, "--aplicar"])
    assert [p.id for p in aplicadas] == [pid]


def test_approve_sem_identidade_nao_aprova(ambiente, sem_ci, monkeypatch):
    store, _ = ambiente
    monkeypatch.setattr(cli, "_identidade", lambda: ("", ""))
    r = runner.invoke(cli.app, ["approve", store.list("pending")[0].id])
    assert r.exit_code == 1 and not store.list("approved")


@pytest.mark.parametrize("variavel", ["CI", "GITHUB_ACTIONS"])
@pytest.mark.parametrize("args", [["approve", "PID"], ["apply", "--all"],
                                  ["reject", "PID", "--reason", "x"], ["decidir"]])
def test_em_ci_nada_e_decidido(ambiente, monkeypatch, variavel, args):
    """No agente de nuvem nao existe janela de permissao, nem ninguem para clicar."""
    store, aplicadas = ambiente
    monkeypatch.setenv(variavel, "true")
    pid = store.list("pending")[0].id
    r = runner.invoke(cli.app, [pid if a == "PID" else a for a in args], input="a\ns\ns\n")
    assert r.exit_code == 1
    assert len(store.list("pending")) == 3 and not aplicadas
