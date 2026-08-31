#!/usr/bin/env python3
"""Regenera os arquivos de configuracao derivados dos agentes de IA.

Cada ferramenta procura instrucao num caminho fixo, que ela nao deixa
configurar. Duplicar o conteudo a mao nesses caminhos faria as copias
divergirem em uma semana, e o repo passaria a se comportar diferente conforme
quem estivesse na cadeira. Por isso toda instrucao mora em
`agent_instructions/` e os caminhos que as ferramentas exigem sao gerados.

Fontes de verdade, editadas a mao, todas em `agent_instructions/`:

- `contrato.md`, o contrato de trabalho no repositorio;
- `papeis/*.md`, os papeis de agente;
- `ferramentas/*.md`, o que muda de uma ferramenta para outra.

Derivados, nunca editados a mao:

- `AGENTS.md`, ponteiro para o contrato, para Codex e afins;
- `.claude/CLAUDE.md`, ponteiro com import `@`, para o Claude Code;
- `.claude/commands/*.md`, slash commands do Claude Code;
- `.github/copilot-instructions.md`, copia do contrato para o Copilot;
- `.github/prompts/*.prompt.md`, prompt files do Copilot Chat.

O Copilot recebe copia, e nao ponteiro, porque injeta o conteudo do arquivo
direto no contexto e nao se pode contar com ele para abrir o alvo do ponteiro.

Rodar apos qualquer alteracao em `agent_instructions/`. Em CI, `--check`.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
FONTE_DIR = ROOT / "agent_instructions"
CONTRATO = FONTE_DIR / "contrato.md"
PAPEIS_DIR = FONTE_DIR / "papeis"
FERRAMENTAS_DIR = FONTE_DIR / "ferramentas"

AVISO = "<!-- GERADO POR scripts/sync_agent_files.py. NAO EDITAR A MAO. -->"
FONTE = "<!-- Fonte: agent_instructions/. Alterar la, depois rodar o script. -->"


def papeis() -> list[Path]:
    return sorted(PAPEIS_DIR.glob("*.md"))


def rel(caminho: Path) -> str:
    """Caminho a partir da raiz do repo. Serve para o texto que a pessoa le."""
    return caminho.relative_to(ROOT).as_posix()


def rel_de(origem: Path, alvo: Path) -> str:
    """Caminho de `alvo` visto de dentro da pasta de `origem`.

    O import `@` do Claude Code resolve a partir da pasta do arquivo que
    importa, e nao da raiz do repo. Como `CLAUDE.md` mora em `.claude/`, um
    `@agent_instructions/...` apontaria para `.claude/agent_instructions/...`,
    que nao existe, e o import falharia calado.
    """
    return os.path.relpath(alvo, origem.parent).replace(os.sep, "/")


def descricao(caminho: Path) -> str:
    """Primeira frase do primeiro paragrafo, ou o titulo se nao houver corpo.

    O paragrafo e reunido antes do corte porque os arquivos de papel quebram
    linha em 79 colunas: cortar na quebra produziria descricao pela metade.
    """
    linhas = [l.strip() for l in caminho.read_text(encoding="utf-8").splitlines()]
    titulo = next((l[2:].strip() for l in linhas if l.startswith("# ")), caminho.stem)

    paragrafo: list[str] = []
    for linha in linhas:
        if linha.startswith("#"):
            continue
        if linha:
            paragrafo.append(linha)
        elif paragrafo:
            break

    texto = " ".join(paragrafo)
    if not texto:
        return titulo
    frase, ponto, _ = texto.partition(". ")
    return (frase + ".") if ponto else texto


def lista_papeis() -> list[str]:
    return [f"- `/{p.stem}`: {descricao(p)}" for p in papeis()]


def agents_md() -> tuple[Path, str]:
    """Ponteiro generico. Codex e qualquer outro agente que leia AGENTS.md."""
    linhas = [
        AVISO,
        "",
        FONTE,
        "",
        "# Instrucoes do repositorio",
        "",
        f"O contrato de trabalho esta em `{rel(CONTRATO)}`, e vale",
        "para todo agente de IA. Abrir e ler o arquivo inteiro antes de",
        "qualquer alteracao. Nao e opcional: este ponteiro nao contem o",
        "contrato, so aponta para ele.",
        "",
        "Depois, ler a particularidade da ferramenta que voce esta usando:",
        "",
    ]
    linhas += [f"- `{rel(f)}`" for f in sorted(FERRAMENTAS_DIR.glob("*.md"))]
    linhas += [
        "",
        f"Os papeis de agente estao em `{rel(PAPEIS_DIR)}/`, com as rubricas em",
        f"`{rel(FONTE_DIR / 'rubricas')}/`:",
        "",
    ]
    linhas += lista_papeis()
    linhas.append("")
    return ROOT / "AGENTS.md", "\n".join(linhas)


def claude_md() -> tuple[Path, str]:
    """Ponteiro com import `@`: o Claude Code resolve sozinho na leitura.

    Mora em `.claude/`, e nao na raiz, porque o carregador de memoria empilha
    `CLAUDE.md` e `.claude/CLAUDE.md` com o mesmo escopo de projeto. Ver
    ADR-0008.
    """
    destino = ROOT / ".claude" / "CLAUDE.md"
    ferramenta = FERRAMENTAS_DIR / "claude.md"
    linhas = [
        AVISO,
        "",
        FONTE,
        "",
        "# Instrucoes do repositorio",
        "",
        f"O contrato deste repositorio esta em `{rel(CONTRATO)}`, e",
        "vale para todos os agentes de IA. Ler antes de qualquer alteracao.",
        "",
        f"@{rel_de(destino, CONTRATO)}",
        f"@{rel_de(destino, ferramenta)}",
        "",
        "## Papeis disponiveis como slash command",
        "",
    ]
    linhas += lista_papeis()
    linhas.append("")
    return destino, "\n".join(linhas)


def copilot_instructions() -> tuple[Path, str]:
    """Copia, nao ponteiro. Ver o docstring do modulo."""
    contrato = CONTRATO.read_text(encoding="utf-8")
    ferramenta = (FERRAMENTAS_DIR / "copilot.md").read_text(encoding="utf-8")
    cabecalho = "\n".join([AVISO, "", FONTE, "", ""])
    corpo = contrato.rstrip("\n") + "\n\n---\n\n" + ferramenta
    return ROOT / ".github" / "copilot-instructions.md", cabecalho + corpo


def wrappers() -> list[tuple[Path, str]]:
    """Wrappers de uma linha. Nenhuma instrucao propria, para nao divergir."""
    saida: list[tuple[Path, str]] = []
    for papel in papeis():
        alvo = rel(papel)
        corpo = [
            AVISO,
            "",
            f"Assuma o papel descrito em `{alvo}`. Leia o arquivo inteiro e siga",
            "todos os criterios dele, mais a rubrica correspondente em",
            f"`{rel(FONTE_DIR / 'rubricas')}/`, se houver.",
            "",
            f"Vale o contrato de `{rel(CONTRATO)}`: voce nao escreve em sistema",
            "externo. Toda escrita externa e proposta, e um humano aprova.",
            "",
        ]

        saida.append(
            (
                ROOT / ".claude" / "commands" / papel.name,
                "\n".join(
                    ["---", f"description: {descricao(papel)}", "---", "", *corpo,
                     "Argumentos da invocacao, se houver: $ARGUMENTS", ""]
                ),
            )
        )
        saida.append(
            (
                ROOT / ".github" / "prompts" / f"{papel.stem}.prompt.md",
                "\n".join(
                    ["---", "mode: agent", f"description: {descricao(papel)}", "---",
                     "", *corpo]
                ),
            )
        )
    return saida


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="nao escreve; falha se algum derivado estiver desatualizado.",
    )
    args = parser.parse_args()

    alvos = [agents_md(), claude_md(), copilot_instructions(), *wrappers()]

    desatualizados: list[Path] = []
    for caminho, conteudo in alvos:
        atual = caminho.read_text(encoding="utf-8") if caminho.exists() else None
        if atual == conteudo:
            continue
        desatualizados.append(caminho)
        if not args.check:
            caminho.parent.mkdir(parents=True, exist_ok=True)
            caminho.write_text(conteudo, encoding="utf-8")

    if args.check:
        if desatualizados:
            print("Derivados desatualizados:", file=sys.stderr)
            for caminho in desatualizados:
                print(f"  {caminho.relative_to(ROOT)}", file=sys.stderr)
            print("Rodar: python scripts/sync_agent_files.py", file=sys.stderr)
            return 1
        print("Derivados em dia.")
        return 0

    for caminho in desatualizados:
        print(f"atualizado: {caminho.relative_to(ROOT)}")
    if not desatualizados:
        print("Nada a fazer.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
