#!/usr/bin/env python3
"""Regenera os arquivos de configuracao derivados dos agentes de IA.

Cada agente procura instrucao num arquivo diferente. Duplicar o conteudo a mao
faria as copias divergirem em uma semana, e o repo passaria a se comportar
diferente conforme quem estivesse na cadeira. Por isso ha uma fonte unica e o
resto e gerado.

Fontes de verdade, editadas a mao:

- `AGENTS.md`, o contrato de trabalho no repositorio;
- `agents/*.md`, os papeis de agente.

Derivados, nunca editados a mao:

- `CLAUDE.md`, ponteiro para AGENTS.md;
- `.github/copilot-instructions.md`, copia do contrato para o Copilot;
- `.claude/commands/*.md`, slash commands do Claude Code;
- `.github/prompts/*.prompt.md`, prompt files do Copilot Chat.

Codex le `AGENTS.md` direto e nao precisa de derivado.

Rodar apos qualquer alteracao em `AGENTS.md` ou em `agents/`. Em CI, `--check`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
AVISO = "<!-- GERADO POR scripts/sync_agent_files.py. NAO EDITAR A MAO. -->"
FONTE = "<!-- Fonte: AGENTS.md e agents/. Alterar la, depois rodar o script. -->"


def papeis() -> list[Path]:
    return sorted((ROOT / "agents").glob("*.md"))


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


def claude_md() -> tuple[Path, str]:
    linhas = [
        AVISO,
        "",
        FONTE,
        "",
        "# Instrucoes do repositorio",
        "",
        "O contrato deste repositorio esta em `AGENTS.md` e vale para todos os",
        "agentes de IA. Ler antes de qualquer alteracao.",
        "",
        "@AGENTS.md",
        "",
        "## Papeis disponiveis como slash command",
        "",
    ]
    linhas += [f"- `/{p.stem}`: {descricao(p)}" for p in papeis()]
    linhas.append("")
    return ROOT / "CLAUDE.md", "\n".join(linhas)


def copilot_instructions() -> tuple[Path, str]:
    contrato = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    cabecalho = "\n".join([AVISO, "", FONTE, "", ""])
    return ROOT / ".github" / "copilot-instructions.md", cabecalho + contrato


def wrappers() -> list[tuple[Path, str]]:
    """Wrappers de uma linha. Nenhuma instrucao propria, para nao divergir."""
    saida: list[tuple[Path, str]] = []
    for papel in papeis():
        alvo = f"agents/{papel.name}"
        corpo = [
            AVISO,
            "",
            f"Assuma o papel descrito em `{alvo}`. Leia o arquivo inteiro e siga",
            "todos os criterios dele, mais a rubrica correspondente em",
            "`agents/rubricas/`, se houver.",
            "",
            "Vale o contrato de `AGENTS.md`: voce nao escreve em sistema externo.",
            "Toda escrita externa e proposta, e um humano aprova.",
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

    alvos = [claude_md(), copilot_instructions(), *wrappers()]

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
