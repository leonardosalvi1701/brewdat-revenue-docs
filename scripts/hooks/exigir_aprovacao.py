#!/usr/bin/env python3
"""Hook `preToolUse` do Copilot: pede aprovacao humana para decidir proposta.

Lido pelo Copilot CLI e pelo VS Code em `.github/hooks/aprovacao-humana.json`.
Recebe a chamada de ferramenta em JSON pela entrada padrao e, quando ela roda
`docs approve`, `apply`, `reject` ou `decidir`, responde `ask`: a ferramenta
para e pergunta a pessoa antes de executar. Ver ADR-0015.

Os dois formatos de entrada e de saida convivem, porque o Copilot CLI e o VS
Code nao concordam nos nomes: `toolArgs` contra `tool_input`, e
`permissionDecision` na raiz contra dentro de `hookSpecificOutput`. A
resposta leva os dois, e cada um le o seu.

So o campo de comando conta. Editar um arquivo que cita `docs approve`, como
este, nao e rodar o comando.

Sem saida, a ferramenta segue o fluxo normal dela. Erro aqui sai com codigo
diferente de zero, que as duas leem como recusa: falha fechada.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
CHAVES_DE_COMANDO = {"command", "cmd", "commandLine", "command_line"}


def _comandos() -> list[str]:
    texto = (RAIZ / "agent_instructions" / "aprovacao.yaml").read_text(encoding="utf-8")
    bloco = texto.split("comandos:", 1)[1].split("\n\n", 1)[0]
    return re.findall(r"^\s*-\s*(\w+)\s*$", bloco, flags=re.M)


def padrao() -> re.Pattern:
    alternativas = "|".join(map(re.escape, _comandos()))
    return re.compile(rf"(?<![\w.-])(docs|docsquad\.cli)\s+({alternativas})\b")


def _textos_de_comando(valor) -> list[str]:
    """Todo valor de chave de comando, em qualquer profundidade.

    `toolArgs` pode chegar como objeto ou como texto JSON, conforme a versao.
    """
    if isinstance(valor, str):
        try:
            valor = json.loads(valor)
        except ValueError:
            return []
    achados: list[str] = []
    if isinstance(valor, dict):
        for chave, item in valor.items():
            if chave in CHAVES_DE_COMANDO and isinstance(item, str):
                achados.append(item)
            else:
                achados += _textos_de_comando(item)
    elif isinstance(valor, list):
        for item in valor:
            achados += _textos_de_comando(item)
    return achados


def decidir(entrada: dict) -> dict | None:
    argumentos = [entrada.get(k) for k in ("toolArgs", "tool_input", "input")]
    regex = padrao()
    for texto in (t for a in argumentos for t in _textos_de_comando(a)):
        achado = regex.search(texto)
        if achado:
            motivo = (f"`docs {achado.group(2)}` decide proposta de escrita em sistema "
                      "externo. Confira o conteudo mostrado no `docs show` antes de "
                      "aprovar. Ver ADR-0015.")
            return {
                "permissionDecision": "ask",
                "permissionDecisionReason": motivo,
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "ask",
                    "permissionDecisionReason": motivo,
                },
            }
    return None


def main() -> int:
    bruto = sys.stdin.read()
    entrada = json.loads(bruto) if bruto.strip() else {}
    resposta = decidir(entrada)
    if resposta:
        print(json.dumps(resposta, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
