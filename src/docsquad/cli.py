"""CLI do docsquad.

Fluxo tipico de uma sprint:

    docs sprint --meus               # os cards que sao seus, agrupados
    docs collect                     # snapshot de cards + commits + notebooks
    docs sprint-review               # rascunho da sua review, a partir do snapshot
    docs propose comment 2680725 --from-snapshot
    docs review                      # lista propostas pendentes
    docs show <id>                   # ve o texto exato que sera publicado
    docs approve <id> --by "Leo"
    docs apply --all                 # executor aplica so o que foi aprovado
"""
from __future__ import annotations

import json

import requests
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import collect as collect_mod
from . import sprint_review as review_mod
from .config import env, path, settings
from .connectors import (DatabricksClient, DevOpsClient, filtrar_por_pessoa,
                         responsavel)
from .gate import Executor, Proposal, ProposalKind, ProposalStore

app = typer.Typer(help="Documentacao assistida da squad Revenue.", no_args_is_help=True)
console = Console()
store = ProposalStore()


# ---------------- leitura ----------------

# Os grupos do board na ordem em que a sprint review os apresenta. A mesma
# ordem nas duas pontas evita que a tela e o documento contem historias
# diferentes da mesma sprint.
GRUPOS = [("Entregue", "concluidos"),
          ("Em validacao", "aguardando_validacao"),
          ("Ativos", "ativos"),
          ("Outros", "outros")]


def _resolver_pessoa(devops: DevOpsClient, de: str | None, meus: bool) -> str | None:
    """Quem filtrar, em ordem de precedencia.

    `--de` manda, porque e explicito na chamada. Depois `AZDO_USER_EMAIL`, que
    existe para quem o `me()` nao consegue resolver. Por ultimo o proprio PAT,
    que e o caminho normal e nao exige configuracao nenhuma.
    """
    if de:
        return de
    if not meus:
        return None
    configurado = env("AZDO_USER_EMAIL", required=False)
    if configurado:
        return configurado
    eu = devops.me()
    pessoa = eu.get("email") or eu.get("nome")
    if not pessoa:
        raise typer.BadParameter(
            "Nao consegui identificar voce pela credencial. Preencha "
            "AZDO_USER_EMAIL no .env ou use --de \"Seu Nome\".")
    return pessoa


@app.command()
def sprint(iteration: str = typer.Option(None, help="Id da iteracao. Vazio = corrente."),
           meus: bool = typer.Option(False, "--meus",
                                     help="So os cards atribuidos a voce."),
           de: str = typer.Option(None, "--de",
                                  help="Cards de outra pessoa: nome ou email.")):
    """Mostra o board da sprint, nos mesmos grupos da sprint review."""
    devops = DevOpsClient()
    pessoa = _resolver_pessoa(devops, de, meus)
    board = devops.sprint_board(iteration)

    cabecalho = f"[bold]{board['iteration'].get('name')}[/] - {board['total']} itens"
    if pessoa:
        cabecalho += f"   filtro: {pessoa}"
    console.print(Panel(cabecalho))

    vazio = True
    for titulo, chave in GRUPOS:
        itens = board[chave]
        if pessoa:
            itens = filtrar_por_pessoa(itens, pessoa)
        if not itens:
            continue
        vazio = False
        t = Table(title=titulo, show_lines=False)
        t.add_column("Id", style="cyan")
        t.add_column("Tipo")
        t.add_column("Estado")
        t.add_column("Titulo", overflow="fold")
        if not pessoa:
            t.add_column("Responsavel", overflow="fold")
        for wi in itens:
            f = wi["fields"]
            linha = [str(wi["id"]), f.get("System.WorkItemType", ""),
                     f.get("System.State", ""), f.get("System.Title", "")]
            if not pessoa:
                linha.append(responsavel(wi)["nome"] or "[dim]sem responsavel[/]")
            t.add_row(*linha)
        console.print(t)

    if vazio and pessoa:
        console.print(f"Nenhum card de '{pessoa}' nesta sprint. "
                      "Confira o nome com: docs quem-sou-eu")


@app.command("quem-sou-eu")
def quem_sou_eu():
    """Mostra por qual identidade voce esta lendo o board."""
    c = DevOpsClient()
    eu = c.me()
    console.print(Panel(f"nome: {eu.get('nome') or '[dim]nao informado[/]'}\n"
                        f"email: {eu.get('email') or '[dim]nao informado[/]'}\n"
                        f"auth: {c.metodo_auth}",
                        title="Sua identidade no DevOps"))
    console.print("E este email que `--meus` usa para filtrar os cards.")


@app.command()
def collect(janela: int = typer.Option(None, help="Janela de commits em dias."),
            sem_databricks: bool = typer.Option(False)):
    """Gera o snapshot que alimenta os agentes."""
    snap = collect_mod.snapshot(janela_dias=janela, com_databricks=not sem_databricks)
    destino = collect_mod.save(snap)
    console.print(f"[green]Snapshot salvo:[/] {destino}")
    console.print(f"  sprint: {snap['sprint']}")
    console.print(f"  cards: {snap['board']['total']}")
    if snap.get("commits_erro"):
        console.print(f"  [yellow]commits: nao coletados[/] ({snap['commits_erro']})")
    else:
        console.print(f"  commits sem card: {len(snap['commits_sem_card'])}")
    if snap.get("notebooks_erro"):
        console.print(f"  [yellow]notebooks: nao coletados[/] ({snap['notebooks_erro']})")
    else:
        console.print(f"  notebooks: {len(snap['notebooks'])}")


@app.command()
def notebooks():
    """Inventario de notebooks do Databricks."""
    inv = DatabricksClient().inventory()
    t = Table(title="Notebooks")
    t.add_column("Caminho", overflow="fold")
    t.add_column("Celulas", justify="right")
    t.add_column("Linhas", justify="right")
    t.add_column("Cabecalho?", justify="center")
    for nb in inv:
        if "error" in nb:
            t.add_row(nb.get("path", "?"), "-", "-", "[red]erro[/]")
            continue
        t.add_row(nb["path"], str(nb["n_cells"]), str(nb["n_linhas"]),
                  "sim" if nb["tem_cabecalho_documentado"] else "[yellow]nao[/]")
    console.print(t)


@app.command("sprint-review")
def sprint_review(
        de: str = typer.Option(None, "--de", help="Review de outra pessoa."),
        snapshot: str = typer.Option(None, "--snapshot",
                                     help="Caminho do snapshot. Vazio = o mais recente."),
        saida: str = typer.Option(None, "--saida", help="Arquivo de destino.")):
    """Gera o rascunho da sua sprint review no padrao de `templates/sprint-review.md`.

    Preenche so o que sai do board: quais cards, em que estado, com que
    evidencia. Objetivo, decisoes, aprendizados e proxima sprint ficam em
    branco de proposito, porque nao estao no DevOps.
    """
    snap = collect_mod.carregar(snapshot)
    pessoa = de or _resolver_pessoa(DevOpsClient(), None, meus=True)

    texto = review_mod.rascunho(snap, pessoa)
    destino = saida or review_mod.salvar(texto, snap, pessoa)
    if saida:
        open(saida, "w", encoding="utf-8").write(texto)

    console.print(f"[green]Rascunho salvo:[/] {destino}")
    console.print(f"  sprint: {snap.get('sprint')}   autor: {pessoa}")
    console.print(f"  snapshot: {snap.get('_arquivo')}")
    console.print("As secoes 1, 5, 6 e 7 estao em branco: elas nao saem do board.")
    console.print("Depois de escrever, revise com: /revisor-negocio ou /revisor-tecnico")


# ---------------- propostas ----------------

propose = typer.Typer(help="Gera propostas. Nunca escreve em sistema externo.")
app.add_typer(propose, name="propose")


@propose.command("comment")
def propose_comment(card_id: int, arquivo: str = typer.Option(
        None, "--file", help="Arquivo markdown com o texto do comentario.")):
    """Propoe um comentario num card. Texto vem de arquivo ou do editor."""
    texto = (open(arquivo, encoding="utf-8").read() if arquivo
             else typer.edit("\n") or "")
    if not texto.strip():
        raise typer.BadParameter("Comentario vazio.")
    p = Proposal(kind=ProposalKind.CARD_COMMENT, target=str(card_id),
                 summary=f"Comentario no card {card_id}",
                 payload={"text": texto})
    store.save(p)
    console.print(f"[yellow]Proposta {p.id} criada em pending.[/] "
                  f"Revise com: docs show {p.id}")


@propose.command("transition")
def propose_transition(card_id: int, to_state: str,
                       from_state: str = typer.Option(..., "--from")):
    """Propoe mudanca de estado de um card."""
    p = Proposal(kind=ProposalKind.CARD_TRANSITION, target=str(card_id),
                 summary=f"Card {card_id}: {from_state} -> {to_state}",
                 payload={"from_state": from_state, "to_state": to_state})
    store.save(p)
    console.print(f"[yellow]Proposta {p.id} criada em pending.[/]")


@propose.command("notebook")
def propose_notebook(caminho: str, arquivo: str):
    """Propoe escrita de notebook no Databricks."""
    content = open(arquivo, encoding="utf-8").read()
    p = Proposal(kind=ProposalKind.NOTEBOOK_WRITE, target=caminho,
                 summary=f"Escrever notebook {caminho} ({len(content)} bytes)",
                 payload={"content": content})
    store.save(p)
    console.print(f"[yellow]Proposta {p.id} criada em pending.[/]")


# ---------------- portao ----------------

@app.command()
def review(status: str = "pending"):
    """Lista propostas aguardando decisao."""
    props = store.list(status)
    if not props:
        console.print(f"Nenhuma proposta em '{status}'.")
        return
    t = Table(title=f"Propostas: {status}")
    t.add_column("Id", style="cyan")
    t.add_column("Tipo")
    t.add_column("Alvo")
    t.add_column("Resumo", overflow="fold")
    for p in props:
        t.add_row(p.id, p.kind.value, p.target, p.summary)
    console.print(t)


@app.command()
def show(pid: str):
    """Mostra o conteudo exato que sera publicado."""
    p = store.load(pid)
    console.print(Panel(f"[bold]{p.summary}[/]\n"
                        f"tipo: {p.kind.value}   alvo: {p.target}   status: {p.status}"))
    if p.rationale:
        console.print(Panel(p.rationale, title="Por que o agente propos"))
    if p.sources:
        console.print(Panel("\n".join(f"- {s}" for s in p.sources), title="Fontes"))
    corpo = p.payload.get("text") or p.payload.get("content") or json.dumps(
        p.payload, ensure_ascii=False, indent=2)
    console.print(Panel(corpo, title="Conteudo a publicar"))


@app.command()
def approve(pid: str, by: str = typer.Option(..., "--by", help="Quem aprova.")):
    """Aprova uma proposta. Exige identificacao."""
    p = store.approve(pid, by)
    console.print(f"[green]Aprovada[/] {p.id} por {p.approved_by}. "
                  f"Aplique com: docs apply --id {p.id}")


@app.command()
def reject(pid: str, reason: str = typer.Option(..., "--reason")):
    """Recusa uma proposta, registrando o motivo."""
    store.reject(pid, reason)
    console.print(f"[red]Recusada[/] {pid}")


@app.command()
def apply(pid: str = typer.Option(None, "--id"),
          todas: bool = typer.Option(False, "--all"),
          dry_run: bool = typer.Option(False, "--dry-run")):
    """Aplica propostas aprovadas. Unico comando que escreve fora."""
    ex = Executor(devops=DevOpsClient(), databricks=None)
    alvos = [store.load(pid)] if pid else store.list("approved")
    if not alvos:
        console.print("Nada aprovado para aplicar.")
        return
    if not (pid or todas):
        console.print("Use --id <id> ou --all.")
        raise typer.Exit(1)
    for p in alvos:
        if p.kind is ProposalKind.NOTEBOOK_WRITE:
            ex.databricks = DatabricksClient()
        try:
            res = ex.apply(p, dry_run=dry_run)
            console.print(f"[green]OK[/] {p.id}: {res}")
        except Exception as exc:
            console.print(f"[red]BLOQUEADA[/] {p.id}: {exc}")


@app.command()
def config_check():
    """Verifica credenciais e politica sem escrever nada."""
    cfg = settings()
    console.print(Panel(json.dumps(cfg["gate"], indent=2), title="Politica do portao"))

    try:
        console.print(f"autenticacao: [bold]{DevOpsClient().metodo_auth}[/]")
    except Exception as exc:
        console.print(f"[red]sem credencial[/]\n{exc}")
        raise typer.Exit(1)

    for nome, fn in [("Azure DevOps", lambda: DevOpsClient().current_iteration()),
                     ("Databricks", lambda: DatabricksClient().list_path(
                         cfg["databricks"]["paths"][0]))]:
        try:
            fn()
            console.print(f"[green]ok[/] {nome}")
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 404:
                console.print(
                    f"[yellow]autenticado, mas caminho inexistente[/] {nome}: "
                    f"{exc.request.url if exc.request else exc}\n"
                    "  Confira os caminhos em config/settings.yaml.")
            else:
                console.print(f"[red]falha[/] {nome}: {exc}")
        except Exception as exc:
            console.print(f"[red]falha[/] {nome}: {exc}")


if __name__ == "__main__":
    app()
