"""Rascunho de sprint review a partir de um snapshot.

O padrao e o de `templates/sprint-review.md`, que reproduz o paper real da
squad. O exemplar vive em `knowledge/sprint-reviews/`.

Este modulo faz so o trabalho mecanico: descobrir quais cards sao da pessoa,
agrupa-los por frente e montar o esqueleto da secao 4 com um bloco por
atividade, ja com a materia-prima de cada bloco em comentario. Prosa nenhuma
sai daqui.

A escolha e deliberada. Um gerador que escrevesse a narrativa produziria texto
plausivel sobre trabalho que ele nao viu, e a review e justamente o lugar onde
a squad afirma o que fez. O rascunho entrega estrutura e evidencia; a
afirmacao continua sendo de quem viveu a sprint.
"""
from __future__ import annotations

import re
from datetime import date
from html import unescape

from .config import path, settings
from .connectors import FRENTE_INDEFINIDA, filtrar_por_pessoa

# Cabecalho do bloco de uma atividade. O titulo do card vira titulo da
# atividade porque e o que a pessoa reconhece; o id fica ao lado para auditoria.
ATIVIDADE = "#### {titulo}"


def _campo(wi: dict, nome: str, padrao: str = "") -> str:
    return wi.get("fields", {}).get(nome, padrao) or padrao


def _materia_prima(wi: dict, commits_disponiveis: bool) -> list[str]:
    """O que o snapshot sabe sobre o card, em comentario HTML.

    Fica em comentario, e nao no corpo, para nao virar texto por inercia:
    quem escreve le, usa e apaga. Se virasse prosa, a review passaria a
    afirmar o que o board registrou, e nao o que a pessoa fez.
    """
    linhas = [f"<!-- Card {wi['id']} | {_campo(wi, 'System.WorkItemType')} "
              f"| {_campo(wi, 'System.State')}"]

    commits = wi.get("_commits") or []
    if commits:
        linhas.append("     Commits:")
        linhas += [f"       {c['sha']} {c['message']}" for c in commits]
    elif commits_disponiveis:
        linhas.append("     Commits: nenhum commit referencia este card.")
    else:
        linhas.append("     Commits: nao coletados neste snapshot.")

    comentarios = wi.get("_comments") or []
    if comentarios:
        linhas.append(f"     Comentarios no card: {len(comentarios)}. "
                      "O ultimo costuma trazer o desfecho.")
        # O comentario vem como html do editor do DevOps: tag para tirar, e
        # entidade para converter, senao o emoji do padrao 📌 da squad chega
        # aqui como `&#128204;` e polui a materia-prima.
        ultimo = re.sub(r"<[^>]+>", " ", str(comentarios[-1].get("text", "")))
        ultimo = re.sub(r"\s+", " ", unescape(ultimo)).strip()
        if ultimo:
            linhas.append(f"       {ultimo[:400]}")
    linhas.append("-->")
    return linhas


def _bloco(wi: dict, commits_disponiveis: bool) -> list[str]:
    return ([ATIVIDADE.format(titulo=_campo(wi, "System.Title", f"Card {wi['id']}")),
             ""]
            + _materia_prima(wi, commits_disponiveis)
            + ["",
               "O que foi feito, por que foi feito e o que ficou decidido.",
               ""])


def _validados() -> list[str]:
    """Esqueleto de "Cards validados", que o gerador nao tem como preencher.

    O QA que uma pessoa faz no card de outra nao fica em campo nenhum do work
    item: o card continua atribuido a quem desenvolveu. Da para adivinhar pelo
    autor dos comentarios, mas comentar um card nao e valida-lo, e a review
    passaria a creditar validacao que nao houve. Entao o bloco vem vazio e
    nomeado, que e o pedido honesto.
    """
    return ["#### Cards validados", "",
            "<!-- O board nao registra quem validou o card de quem: preencher a mao.",
            "     Um bullet por entrega validada, com quem conduziu e o que a",
            "     validacao apontou. Sem validacao na sprint, apagar o bloco. -->",
            "",
            "- {entrega validada}",
            "  Responsavel: {quem conduziu}. {o que a validacao apontou}.",
            ""]


def _secao_4(cards: list[dict], pessoa: str, commits_disponiveis: bool) -> list[str]:
    """Secao 4 agrupada, mas nao batizada.

    O grupo vem do board; o nome da frente vem da pessoa. Ver o comentario de
    `connectors.devops.frente`: o campo que agrupa nao e o campo que nomeia, e
    escrever um titulo plausivel aqui seria o mesmo erro que o ADR-0009 evita
    no corpo do texto, so que no cabecalho.
    """
    por_grupo: dict[str, list[dict]] = {}
    dicas: dict[str, str] = {}
    for wi in cards:
        f = wi.get("_frente") or {}
        chave = f.get("chave", "sem-grupo")
        por_grupo.setdefault(chave, []).append(wi)
        dicas.setdefault(chave, f.get("dica", ""))

    ordem = sorted(por_grupo, key=lambda c: (-len(por_grupo[c]), c))

    linhas: list[str] = []
    for i, chave in enumerate(ordem, 1):
        linhas += [f"### 4.{i} {FRENTE_INDEFINIDA}", f"Responsavel: {pessoa}", ""]
        if dicas.get(chave):
            linhas += [f"<!-- Estes {len(por_grupo[chave])} cards andam juntos no "
                       f"board: {dicas[chave]}.",
                       "     Isso agrupa, mas nao nomeia: o card pai da squad e um OKR "
                       "do trimestre.",
                       "     De o nome da frente como ela aparece no paper, por exemplo "
                       '"Modelo de Volume",',
                       '     "Promo Removal" ou "Otimizador de Cobertura". -->',
                       ""]
        for wi in por_grupo[chave]:
            linhas += _bloco(wi, commits_disponiveis)
    return linhas


def _fatiar(texto: str) -> tuple[list[str], list[tuple[str, list[str]]]]:
    """Separa frontmatter e secoes `## `, preservando o corpo de cada uma."""
    linhas = texto.splitlines()
    frontmatter: list[str] = []
    if linhas and linhas[0].strip() == "---":
        fim = linhas.index("---", 1)
        frontmatter, linhas = linhas[:fim + 1], linhas[fim + 1:]

    secoes: list[tuple[str, list[str]]] = []
    titulo, atual = "", []
    for linha in linhas:
        if linha.startswith("## "):
            secoes.append((titulo, atual))
            titulo, atual = linha, []
        else:
            atual.append(linha)
    secoes.append((titulo, atual))
    return frontmatter, secoes


def _preencher_frontmatter(linhas: list[str], valores: dict) -> list[str]:
    saida = list(linhas)
    for i, linha in enumerate(saida):
        chave = linha.split(":", 1)[0].strip()
        if chave in valores and linha.rstrip().endswith(":"):
            saida[i] = f"{chave}: {valores[chave]}"
    return saida


def _periodo(snap: dict) -> tuple[str, str]:
    """Inicio e fim da iteracao, como o DevOps informa. Vazio quando nao informa."""
    attrs = (snap.get("board", {}).get("iteration", {}) or {}).get("attributes", {})
    fmt = settings()["formato"]["data"]

    def dia(valor: str) -> str:
        if not valor:
            return ""
        try:
            return date.fromisoformat(valor[:10]).strftime(fmt)
        except ValueError:
            return ""

    return dia(attrs.get("startDate", "")), dia(attrs.get("finishDate", ""))


def _nome_de(pessoa: str, cards: list[dict]) -> str:
    """Nome de exibicao da pessoa, quando algum card dela souber dizer.

    `--meus` resolve a identidade pelo email do PAT, mas o paper assina com
    nome. Puxar do proprio card evita uma segunda tabela de nomes para manter.
    """
    for wi in cards:
        nome = (wi.get("_responsavel") or {}).get("nome")
        if nome:
            return nome
    return pessoa


def rascunho(snap: dict, pessoa: str) -> str:
    """Monta o rascunho da parte de `pessoa` na review da sprint do snapshot."""
    board = snap["board"]
    commits_disponiveis = snap.get("commits_erro") is None

    meus = filtrar_por_pessoa(board.get("concluidos", []), pessoa)
    meus += filtrar_por_pessoa(board.get("aguardando_validacao", []), pessoa)
    em_aberto = (filtrar_por_pessoa(board.get("ativos", []), pessoa)
                 + filtrar_por_pessoa(board.get("outros", []), pessoa))

    nome = _nome_de(pessoa, meus + em_aberto)
    sprint = str(snap.get("sprint", ""))
    inicio, fim = _periodo(snap)

    frontmatter, secoes = _fatiar(
        path("templates", "sprint-review.md").read_text(encoding="utf-8"))
    frontmatter = _preencher_frontmatter(frontmatter, {
        "sprint": sprint,
        "periodo": f"{inicio} a {fim}" if inicio and fim else "",
        "squad": snap.get("squad", settings()["squad"]["nome"]),
        "autor": nome,
        "data": date.today().strftime(settings()["formato"]["data"]),
        "snapshot": snap.get("_arquivo", ""),
    })

    partes = ["\n".join(frontmatter)]
    for titulo, corpo in secoes:
        if titulo.startswith("## 4."):
            corpo = ([""] + _secao_4(meus, nome, commits_disponiveis)
                     + _validados() + _em_aberto(em_aberto))
        partes.append("\n".join(([titulo] if titulo else []) + corpo))

    texto = "\n".join(partes).rstrip() + "\n"

    # Os marcadores do template so viram texto quando o snapshot sabe o valor.
    # Deixar `{inicio}` visivel e melhor que inventar uma data: quem le o
    # rascunho enxerga o buraco em vez de confiar num numero inventado.
    for marcador, valor in (("{sprint}", sprint), ("{inicio}", inicio),
                            ("{fim}", fim)):
        if valor:
            texto = texto.replace(marcador, valor)
    if not commits_disponiveis:
        texto += (f"\n<!-- Commits nao coletados neste snapshot: "
                  f"{snap['commits_erro']}. Nenhum bloco cita evidencia de "
                  f"codigo, e isso e ausencia de coleta, nao ausencia de "
                  f"trabalho. -->\n")
    return texto


def _em_aberto(cards: list[dict]) -> list[str]:
    """O que ficou em aberto. No paper isso vira interferencia ou proximo passo.

    Nao aparece como secao propria de status: o padrao da squad nao tem uma.
    Aparece como lembrete, para quem escreve decidir onde cada um entra.
    """
    if not cards:
        return []
    linhas = ["<!-- Ainda em aberto no fim da sprint, seus:"]
    for wi in cards:
        linhas.append(f"     {wi['id']} [{_campo(wi, 'System.State')}] "
                      f"{_campo(wi, 'System.Title')}")
    linhas += ["     O que atrasou entra em 'Demais atividades e interferencias';",
               "     o que continua entra em 'Proximos Passos' da frente. -->", ""]
    return linhas


def salvar(texto: str, snap: dict, pessoa: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", pessoa.split("@")[0].casefold()).strip("-")
    sprint = re.sub(r"[^A-Za-z0-9]+", "-", str(snap.get("sprint", "sprint"))).strip("-")
    destino = path("outputs", f"sprint-review-{sprint}-{slug}.md")
    destino.write_text(texto, encoding="utf-8")
    return str(destino)
