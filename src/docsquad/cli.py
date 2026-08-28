"""CLI do docsquad.

Fluxo tipico de uma sprint:

    docs sprint                      # o que esta em aberto e o que aguarda validacao
    docs collect                     # snapshot de cards + commits + notebooks
    docs propose comment 2680725 --from-snapshot
    docs review                      # lista propostas pendentes
    docs show <id>                   # ve o texto exato que sera publicado
    docs approve <id> --by "Leo"
    docs apply --all                 # executor aplica so o que foi aprovado
"""
from __future__ import annotations

import json

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import collect as collect_mod
from .config import path, settings
from .connectors import DatabricksClient, DevOpsClient
from .gate import Executor, Proposal, ProposalKind, ProposalStore

app = typer.Typer(help="Documentacao assistida da squad Revenue.", no_args_is_help=True)
console = Console()
store = ProposalStore()


# ---------------- leitura ----------------

@app.command()
def sprint(iteration: str = typer.Option(None, help="Id da iteracao. Vazio = corrente.")):
    """Mostra o board da sprint, separando o que aguarda validacao."""
    board = DevOpsClient().sprint_board(iteration)
    console.print(Panel(f"[bold]{board['iteration'].get('name')}[/] "
                        f"- {board['total']} itens"))
    for titulo, chave in [("Aguardando validacao", "aguardando_validacao"),
                          ("Ativos", "ativos"), ("Outros", "outros")]:
        itens = board[chave]
        if not itens:
            continue
        t = Table(title=titulo, show_lines=False)
        t.add_column("Id", style="cyan")
        t.add_column("Tipo")
        t.add_column("Estado")
        t.add_column("Titulo", overflow="fold")
        for wi in itens:
            f = wi["fields"]
            t.add_row(str(wi["id"]), f.get("System.WorkItemType", ""),
                      f.get("System.State", ""), f.get("System.Title", ""))
        console.print(t)


@app.command()
def collect(janela: int = typer.Option(None, help="Janela de commits em dias."),
            sem_databricks: bool = typer.Option(False)):
    """Gera o snapshot que alimenta os agentes."""
    snap = collect_mod.snapshot(janela_dias=janela, com_databricks=not sem_databricks)
    destino = collect_mod.save(snap)
    console.print(f"[green]Snapshot salvo:[/] {destino}")
    console.print(f"  sprint: {snap['sprint']}")
    console.print(f"  cards: {snap['board']['total']}")
    console.print(f"  commits sem card: {len(snap['commits_sem_card'])}")
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
    for nome, fn in [("Azure DevOps", lambda: DevOpsClient().current_iteration()),
                     ("Databricks", lambda: DatabricksClient().list_path(
                         cfg["databricks"]["paths"][0]))]:
        try:
            fn()
            console.print(f"[green]ok[/] {nome}")
        except Exception as exc:
            console.print(f"[red]falha[/] {nome}: {exc}")


if __name__ == "__main__":
    app()
