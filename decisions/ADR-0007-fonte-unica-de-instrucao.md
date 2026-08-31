---
id: ADR-0007
titulo: AGENTS.md como fonte unica de instrucao de agente
status: superseded
substituida_por: ADR-0008
data: 2026-08-28
projeto: docsquad
autor: Leonardo Salvi
impacta: [agents, claude-md, copilot-instructions, scripts-sync]
---

# ADR-0007: AGENTS.md como fonte unica de instrucao de agente

## Contexto
O repo precisa funcionar com qualquer agente de IA que a squad use hoje ou
venha a usar: Claude Code, Codex e Copilot, no minimo. Cada um procura
instrucao num arquivo diferente. Codex le `AGENTS.md`, Claude Code le
`CLAUDE.md`, Copilot le `.github/copilot-instructions.md`.

Na versao inicial nao havia nenhum desses arquivos. Os papeis em `agents/`
existiam, mas nenhum agente os encontrava sozinho: dependiam de alguem copiar e
colar o prompt no chat certo. Na pratica, a regra central do repo, que nenhum
agente escreve em sistema externo, nao chegava ao agente.

## Alternativas consideradas
| Alternativa | A favor | Contra | Descartada porque |
|---|---|---|---|
| Um arquivo por agente, escrito a mao | simples de comecar | tres copias divergem em semanas | o repo passaria a se comportar diferente conforme quem estivesse na cadeira |
| Plugin de Claude Code | integracao mais rica | so funciona no Claude | viola o requisito de rodar em qualquer agente |
| Fonte unica com derivados gerados | uma copia so, verificavel em CI | exige rodar um script | adotada |

## Decisao
`AGENTS.md` e a fonte unica do contrato. `agents/*.md` sao a fonte unica dos
papeis. `scripts/sync_agent_files.py` gera `CLAUDE.md`,
`.github/copilot-instructions.md`, `.claude/commands/*.md` e
`.github/prompts/*.prompt.md`.

Os wrappers de comando nao contem instrucao propria: apontam para o arquivo do
papel. Toda mudanca de comportamento acontece na fonte, uma vez, e vale para
todos os agentes.

## Razao
Instrucao duplicada a mao diverge. Quando diverge, o agente que le a copia
desatualizada e justamente o que nao sabe da regra nova, e a regra que mais
importa aqui e a que impede escrita em sistema externo.

## Consequencias
- `python scripts/sync_agent_files.py --check` entra na verificacao de qualquer
  alteracao, ao lado dos testes;
- os derivados sao versionados, para que o agente os encontre em clone limpo;
- um agente novo custa uma funcao no script, nao uma copia do contrato.

## Como falsificar
Se surgir agente cuja instrucao nao possa ser derivada mecanicamente de
`AGENTS.md`, por exigir formato incompativel, a fonte unica deixa de bastar e o
caso vira excecao declarada, nao copia silenciosa.
