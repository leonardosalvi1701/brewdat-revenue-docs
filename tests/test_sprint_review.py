"""O rascunho da review nao pode afirmar nada que o snapshot nao diga.

Esses testes cobrem o compromisso do ADR-0009. Eles nao substituem
`test_gate.py`, que continua sendo a garantia estrutural do repo: aqui o pior
resultado possivel e um arquivo em `outputs/` mal montado, e nao uma escrita
externa indevida.
"""
import pytest

from docsquad import sprint_review as sr
from docsquad.connectors import FRENTE_INDEFINIDA, e_de, filtrar_por_pessoa, frente

EU = "leonardo.salvi@ab-inbev.com"
OUTRO = "nicolas.braga@ab-inbev.com"


def card(cid, titulo="Titulo", estado="Done", email=EU, nome="Leonardo Salvi",
         grupo="pai:99", commits=(), comments=(), **fields):
    return {
        "id": cid,
        "fields": {"System.Title": titulo, "System.WorkItemType": "Technical Story",
                   "System.State": estado,
                   "System.AssignedTo": {"displayName": nome, "uniqueName": email},
                   **fields},
        "_responsavel": {"nome": nome, "email": email},
        "_frente": {"chave": grupo, "dica": f"card pai de {grupo}"},
        "_commits": [{"sha": s, "message": m} for s, m in commits],
        "_comments": [{"text": c} for c in comments],
    }


def snapshot(concluidos=(), validacao=(), ativos=(), outros=(), commits_erro=None):
    return {"sprint": "S3-Q3-2026", "squad": "Revenue",
            "_arquivo": "knowledge/cards/snap.json", "commits_erro": commits_erro,
            "board": {"iteration": {"name": "S3-Q3-2026"},
                      "concluidos": list(concluidos),
                      "aguardando_validacao": list(validacao),
                      "ativos": list(ativos), "outros": list(outros)}}


# ---------- identidade ----------

def test_casa_por_email_e_por_nome():
    wi = card(1)
    assert e_de(wi, EU)
    assert e_de(wi, "leonardo salvi")      # nome, caixa diferente
    assert not e_de(wi, OUTRO)


def test_pessoa_vazia_nao_casa_com_ninguem():
    """Senao um `--de ''` traria o board inteiro como se fosse de uma pessoa."""
    assert filtrar_por_pessoa([card(1), card(2)], "") == []


def test_card_sem_responsavel_nao_vaza_para_ninguem():
    wi = card(1)
    wi["fields"]["System.AssignedTo"] = None
    assert not e_de(wi, EU)


# ---------- frente ----------

def test_card_pai_agrupa_mas_nao_nomeia():
    """O pai da squad e um OKR do trimestre. Ele agrupa bem e batiza mal."""
    wi = card(1, **{"System.Parent": 2613936})
    f = frente(wi, {2613936: "Ter ate 7% de NP no Q3-26"})
    assert f["chave"] == "pai:2613936"
    assert "Ter ate 7% de NP no Q3-26" in f["dica"]


def test_cards_do_mesmo_pai_caem_no_mesmo_grupo():
    a = frente(card(1, **{"System.Parent": 42}), {})
    b = frente(card(2, **{"System.Parent": 42}), {})
    assert a["chave"] == b["chave"]


def test_sem_pai_agrupa_pela_area():
    f = frente(card(1, **{"System.AreaPath": "AMBEV\\Squad Revenue"}))
    assert f["chave"] == "area:Squad Revenue"


def test_sem_pai_e_sem_area_ainda_tem_chave():
    assert frente(card(1))["chave"] == "sem-grupo"


def test_nenhuma_secao_e_batizada_pelo_board():
    """Nenhum titulo de frente sai do board: todos saem em branco, para nomear."""
    snap = snapshot(concluidos=[card(1, "A", grupo="pai:2613936")])
    texto = sr.rascunho(snap, EU)
    assert f"### 4.1 {FRENTE_INDEFINIDA}" in texto
    assert "card pai de pai:2613936" in texto   # a dica, em comentario


# ---------- o rascunho ----------

def test_so_traz_os_cards_da_pessoa():
    snap = snapshot(concluidos=[card(111, "Meu card"),
                                card(222, "Card do outro", email=OUTRO,
                                     nome="Nicolas Braga")])
    texto = sr.rascunho(snap, EU)
    assert "Meu card" in texto
    assert "Card do outro" not in texto
    assert "222" not in texto


def test_agrupa_por_frente_e_nao_por_estado():
    """Um card em validacao entra na frente dele, e nao numa secao de status."""
    snap = snapshot(concluidos=[card(1, "Card A", grupo="pai:10"),
                                card(2, "Card B", grupo="pai:20")],
                    validacao=[card(3, "Card C", estado="Waiting-QA",
                                    grupo="pai:10")])
    texto = sr.rascunho(snap, EU)
    grupo_maior = texto.split("### 4.1")[1].split("### 4.2")[0]
    assert "Card A" in grupo_maior and "Card C" in grupo_maior
    assert "Card B" not in grupo_maior


def test_nao_inventa_narrativa():
    """O bloco vem com o pedido, nunca com a resposta ja escrita."""
    snap = snapshot(concluidos=[card(1, "Evolucao das regras de contorno",
                                     commits=[("a3f9c21", "fix: regra de qmin")])])
    texto = sr.rascunho(snap, EU)
    assert "O que foi feito, por que foi feito e o que ficou decidido." in texto
    # o commit e materia-prima em comentario, nao afirmacao no corpo
    linha = next(l for l in texto.splitlines() if "a3f9c21" in l)
    assert linha.strip().startswith(("<!--", "a3f9c21"))
    assert "fix: regra de qmin" not in texto.split("<!--")[0]


def test_ausencia_de_commit_distingue_nao_coletado_de_inexistente():
    """A diferenca importa: uma e falta de credencial, a outra e falta de codigo."""
    sem_token = sr.rascunho(snapshot(concluidos=[card(1)],
                                     commits_erro="GITHUB_TOKEN ausente"), EU)
    assert "nao coletados neste snapshot" in sem_token
    assert "GITHUB_TOKEN ausente" in sem_token

    com_token = sr.rascunho(snapshot(concluidos=[card(1)]), EU)
    assert "nenhum commit referencia este card" in com_token


def test_card_em_aberto_nao_entra_como_entrega():
    snap = snapshot(concluidos=[card(1, "Entregue")],
                    ativos=[card(2, "Ainda andando", estado="Developing")])
    texto = sr.rascunho(snap, EU)
    assert "#### Entregue" in texto
    assert "#### Ainda andando" not in texto
    assert "Ainda andando" in texto  # aparece no lembrete do que ficou em aberto


def test_assina_com_o_nome_e_nao_com_o_email():
    texto = sr.rascunho(snapshot(concluidos=[card(1)]), EU)
    assert "autor: Leonardo Salvi" in texto
    assert "Responsavel: Leonardo Salvi" in texto


def test_estrutura_do_paper_sobrevive_a_um_rascunho_vazio():
    """Quem nao teve card na sprint recebe o padrao, e nao um arquivo quebrado."""
    texto = sr.rascunho(snapshot(), EU)
    for secao in ("## 1. Objetivo do paper", "## 2. Descricao da sprint",
                  "## 3. Metricas da sprint", "## 4. Atividades desenvolvidas",
                  "## 5. Reconhecimentos"):
        assert secao in texto


def test_salvar_nomeia_por_sprint_e_pessoa(tmp_path, monkeypatch):
    monkeypatch.setattr(sr, "path", lambda *p: tmp_path.joinpath(*p[1:]))
    snap = snapshot()
    destino = sr.salvar("conteudo", snap, EU)
    assert destino.endswith("sprint-review-S3-Q3-2026-leonardo-salvi.md")
