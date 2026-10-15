"""CLI do docsquad.

Fluxo tipico de uma sprint:

    docs sprint --meus               # os cards que sao seus, agrupados
    docs collect                     # snapshot de cards + commits + notebooks
    docs sprint-review               # rascunho da sua review, a partir do snapshot
    docs propose comment 2680725 --from-snapshot
    docs decidir                     # humano: revisa, aprova ou recusa, e aplica
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

import requests
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import collect as collect_mod
from . import diagnostico as diag
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


@propose.command("assign")
def propose_assign(card_id: int, pessoa: str):
    """Propoe atribuir um card a alguem. `pessoa` e nome ou email."""
    p = Proposal(kind=ProposalKind.CARD_ASSIGN, target=str(card_id),
                 summary=f"Card {card_id}: atribuir a {pessoa}",
                 payload={"pessoa": pessoa})
    store.save(p)
    console.print(f"[yellow]Proposta {p.id} criada em pending.[/] "
                  f"Revise com: docs show {p.id}")


@propose.command("tag")
def propose_tag(card_id: int, tag: str):
    """Propoe adicionar uma tag a um card, sem apagar as que ja existem."""
    devops = DevOpsClient()
    atual = devops.work_items([card_id], fields=["System.Id", "System.Tags"])
    tags_atuais = [t.strip() for t in
                   (atual[0]["fields"].get("System.Tags", "") if atual else "").split(";")
                   if t.strip()]
    if tag.strip() in tags_atuais:
        console.print(f"[yellow]Card {card_id} ja tem a tag '{tag}'. Nada a propor.[/]")
        raise typer.Exit()
    tags_final = "; ".join(tags_atuais + [tag.strip()])
    p = Proposal(kind=ProposalKind.CARD_TAG, target=str(card_id),
                 summary=f"Card {card_id}: tags -> {tags_final}",
                 payload={"tags": tags_final})
    store.save(p)
    console.print(f"[yellow]Proposta {p.id} criada em pending.[/] "
                  f"Revise com: docs show {p.id}")


@propose.command("notebook")
def propose_notebook(caminho: str, arquivo: str):
    """Propoe escrita de notebook no Databricks."""
    erro = diag.checar_caminho_escrita(
        caminho, settings()["databricks"].get("escrita_permitida", []))
    if erro:
        console.print(f"[red]Proposta nao criada.[/] {erro}")
        raise typer.Exit(1)
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


def _mostrar(p: Proposal) -> None:
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
def show(pid: str):
    """Mostra o conteudo exato que sera publicado."""
    _mostrar(store.load(pid))


def _interativo() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def _exigir_humano(comando: str) -> None:
    """Aprovar e decisao humana, e so roda num terminal de verdade.

    O shell de um agente de IA nao tem terminal interativo, entao esta e uma
    barreira a mais alem do contrato. Nao e garantia absoluta: quem quiser
    burlar consegue simular um terminal. O portao continua sendo o Executor.
    """
    if not _interativo():
        console.print(f"[red]`docs {comando}` so roda num terminal interativo.[/] "
                      "Aprovar e decisao humana: rode voce mesmo, num terminal seu.")
        raise typer.Exit(1)


def _recusar_sem_pessoa(comando: str) -> None:
    """Em CI e no agente de nuvem do Copilot nao ha ninguem para clicar.

    Ali a janela de permissao nao existe, entao decidir proposta nao roda.
    """
    if any(os.getenv(v) for v in ("CI", "GITHUB_ACTIONS")):
        console.print(f"[red]`docs {comando}` nao roda em CI.[/] Decidir proposta "
                      "exige uma pessoa aprovando na janela de permissao. Ver ADR-0015.")
        raise typer.Exit(1)


def _identidade() -> tuple[str, str]:
    """Quem esta aprovando, e de onde veio: a conta do `az login`, ou o git."""
    for comando, origem in [(["az", "account", "show", "--query", "user.name", "-o", "tsv"], "az login"),
                            (["git", "config", "user.email"], "git config")]:
        try:
            r = subprocess.run(comando, capture_output=True, text=True, timeout=20, check=False)
        except (OSError, subprocess.TimeoutExpired):
            continue
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip(), origem
    return "", ""


def _aplicar(alvos: list[Proposal], dry_run: bool = False) -> None:
    ex = Executor(devops=DevOpsClient(), databricks=None)
    for p in alvos:
        if p.kind is ProposalKind.NOTEBOOK_WRITE and ex.databricks is None:
            ex.databricks = DatabricksClient()
        try:
            res = ex.apply(p, dry_run=dry_run)
            console.print(f"  [green]OK[/] {p.id}: {res}")
        except Exception as exc:
            console.print(f"  [red]BLOQUEADA[/] {p.id}: {exc}")


@app.command()
def decidir(como: str = typer.Option(None, "--como",
                                     help="Quem aprova. Vazio = a conta do az login.")):
    """Percorre as propostas pendentes: aprovar, recusar ou pular, e aplicar no fim."""
    _recusar_sem_pessoa("decidir")
    _exigir_humano("decidir")
    # Da mais antiga para a mais nova: e a ordem em que o trabalho aconteceu.
    pendentes = sorted(store.list("pending"), key=lambda p: p.created_at)
    if not pendentes:
        console.print("Nenhuma proposta pendente.")
        return

    quem, origem = (como, "--como") if como else _identidade()
    if not quem:
        quem = typer.prompt("Quem esta aprovando").strip()
        origem = "digitado"
    console.print(f"Aprovando como [bold]{quem}[/] ({origem})")

    aprovadas = []
    for i, p in enumerate(pendentes, 1):
        console.print(f"\n[bold][{i}/{len(pendentes)}][/] {p.kind.value}  {p.target}")
        _mostrar(p)
        escolha = ""
        while escolha not in ("a", "r", "p", "s"):
            escolha = typer.prompt("(a)provar  (r)ecusar  (p)ular  (s)air").strip().lower()[:1]
        if escolha == "s":
            break
        if escolha == "a":
            aprovadas.append(store.approve(p.id, quem))
            console.print("  [green]aprovada[/]")
        elif escolha == "r":
            motivo = ""
            while not motivo.strip():
                motivo = typer.prompt("  motivo")
            store.reject(p.id, motivo.strip())
            console.print("  [red]recusada[/]")

    restantes = len(store.list("pending"))
    if restantes:
        console.print(f"\n{restantes} pendente(s) ficaram para depois.")
    if not aprovadas:
        return
    resposta = typer.prompt(f"\n{len(aprovadas)} aprovada(s). Aplicar agora? [s/N]",
                            default="n", show_default=False)
    if resposta.strip().lower() in ("s", "sim"):
        _aplicar(aprovadas)
    else:
        console.print("Ficam em proposals/approved/. Aplique depois com: docs apply --all")


@app.command()
def approve(pid: str,
            by: str = typer.Option(None, "--by", help="Quem aprova. Vazio = a conta do az login."),
            aplicar: bool = typer.Option(False, "--aplicar", help="Aplica logo depois de aprovar.")):
    """Aprova uma proposta, e aplica com --aplicar.

    Pelo agente de IA, so roda depois que a pessoa aprova na janela de
    permissao da ferramenta, que pergunta sempre neste comando. Ver ADR-0015.
    """
    _recusar_sem_pessoa("approve")
    quem = by or _identidade()[0]
    if not quem:
        console.print("[red]Sem identidade.[/] Rode `az login` ou passe --by \"Seu Nome\".")
        raise typer.Exit(1)
    try:
        p = store.approve(pid, quem)
    except (FileNotFoundError, ValueError) as exc:
        console.print(f"[red]Nao aprovada.[/] {exc}")
        raise typer.Exit(1)
    console.print(f"[green]Aprovada[/] {p.id} por {p.approved_by}.")
    if aplicar:
        _aplicar([p])
    else:
        console.print(f"Aplique com: docs apply --id {p.id}")


@app.command()
def reject(pid: str, reason: str = typer.Option(..., "--reason")):
    """Recusa uma proposta, registrando o motivo."""
    _recusar_sem_pessoa("reject")
    store.reject(pid, reason)
    console.print(f"[red]Recusada[/] {pid}")


@app.command()
def apply(pid: str = typer.Option(None, "--id"),
          todas: bool = typer.Option(False, "--all"),
          dry_run: bool = typer.Option(False, "--dry-run")):
    """Aplica propostas aprovadas. Unico comando que escreve fora."""
    _recusar_sem_pessoa("apply")
    alvos = [store.load(pid)] if pid else store.list("approved")
    if not alvos:
        console.print("Nada aprovado para aplicar.")
        return
    if not (pid or todas):
        console.print("Use --id <id> ou --all.")
        raise typer.Exit(1)
    _aplicar(alvos, dry_run=dry_run)


ESTILO = {diag.OK: "[green]ok[/]", diag.AVISO: "[yellow]aviso[/]", diag.FALHA: "[red]falha[/]"}


def _pasta_databricks(cfg: dict) -> list[diag.Achado]:
    """Credencial, login e pasta pessoal, nessa ordem: cada um depende do anterior."""
    try:
        cliente = DatabricksClient()
        login = cliente.usuario()
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "?"
        dica = (" A requisicao chegou sem credencial aceita: confira DATABRICKS_HOST "
                "acima." if status == 401 else "")
        return [diag.Achado(diag.FALHA, "Databricks", f"HTTP {status} ao ler o login.{dica}")]
    except Exception as exc:
        return [diag.Achado(diag.FALHA, "Databricks", str(exc))]

    identidade = diag.comparar_identidade(
        "Identidade Databricks", cfg.get("usuarios", {}).get("databricks", ""), login)
    achados = [diag.Achado(diag.OK, "Databricks", f"{cliente.metodo_auth}, login {login}"),
               identidade]
    if identidade.nivel == diag.FALHA:
        return achados
    for bruto in cfg["databricks"]["paths"]:
        caminho = cliente.resolver(bruto)
        try:
            cliente.list_path(bruto)
            achados.append(diag.Achado(diag.OK, "pasta", caminho))
        except requests.HTTPError as exc:
            if exc.response is None or exc.response.status_code != 404:
                achados.append(diag.Achado(diag.FALHA, "pasta", f"{caminho}: {exc}"))
            elif "{usuario}" not in bruto:
                achados.append(diag.Achado(
                    diag.FALHA, "pasta",
                    f"{caminho} nao existe, e o caminho fixo e de config antiga. "
                    "Rode `git pull`."))
            else:
                achados.append(diag.Achado(
                    diag.FALHA, "pasta",
                    f"{caminho} nao existe. Rode scripts/preparar_ambiente.sh, que "
                    "cria, ou crie pela interface do Databricks."))
    return achados


@app.command()
def config_check():
    """Diagnostica credenciais, CLIs, perfil e repo, sem escrever nada.

    A saida e feita para ser colada inteira num pedido de ajuda. Sai com
    codigo 1 se algum item falhar.
    """
    cfg = settings()
    console.print(Panel(json.dumps(cfg["gate"], indent=2), title="Politica do portao"))

    achados = (diag.checar_repo() + diag.checar_env_file()
               + diag.checar_identidades_locais(cfg)
               + diag.checar_identidade_github(cfg))
    try:
        devops = DevOpsClient()
        devops.current_iteration()
        achados.append(diag.Achado(diag.OK, "Azure DevOps", devops.metodo_auth))
        identidade_devops = devops.me().get("email", "")
        achados.append(diag.comparar_identidade(
            "Identidade DevOps", cfg.get("usuarios", {}).get("devops_email", ""),
            identidade_devops))
    except Exception as exc:
        achados.append(diag.Achado(diag.FALHA, "Azure DevOps", str(exc)))

    nome, origem, no_terminal, host = diag.contexto_perfil()
    achados += diag.checar_clis()
    achados += diag.checar_host(host)
    achados += diag.checar_perfil(nome, origem, no_terminal,
                                  diag.auth.ler_perfis(), host)
    # Sem perfil utilizavel, a chamada ao workspace so repetiria a falha.
    if not any(a.nivel == diag.FALHA for a in achados
               if a.assunto in ("perfil", "DATABRICKS_HOST", "CLI do Databricks")):
        achados += _pasta_databricks(cfg)

    for a in achados:
        console.print(f"{ESTILO[a.nivel]} [bold]{a.assunto}[/]: {a.texto}", highlight=False)
    if any(a.nivel == diag.FALHA for a in achados):
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
