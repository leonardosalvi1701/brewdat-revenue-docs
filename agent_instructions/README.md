# agent_instructions

Toda instrucao de agente de IA deste repositorio mora aqui. Nada de instrucao
solta na raiz.

## Fonte, editada a mao

| Arquivo | O que e |
|---|---|
| `contrato.md` | o contrato de trabalho. Vale para qualquer agente |
| `papeis/*.md` | os prompts dos papeis: curador, revisor de negocio, revisor tecnico |
| `rubricas/*.yaml` | as metricas de cada revisor |
| `ferramentas/*.md` | o que muda de uma ferramenta para outra, e so isso |

## Derivado, nunca editado a mao

Cada ferramenta procura instrucao num caminho fixo, que ela nao deixa
configurar. Por isso esses caminhos existem, e por isso sao gerados a partir
daqui por `scripts/sync_agent_files.py`:

| Caminho | Para quem | Formato |
|---|---|---|
| `AGENTS.md` | Codex, e qualquer agente que leia AGENTS.md | ponteiro |
| `.claude/CLAUDE.md` | Claude Code | ponteiro, com import `@` |
| `.claude/commands/*.md` | Claude Code | wrapper de slash command |
| `.github/copilot-instructions.md` | Copilot | copia do contrato |
| `.github/prompts/*.prompt.md` | Copilot Chat | wrapper de prompt file |

```bash
python scripts/sync_agent_files.py           # regenera
python scripts/sync_agent_files.py --check   # falha se algum estiver atrasado
```

## Para adicionar uma ferramenta nova

Um arquivo em `ferramentas/`, com o que aquela ferramenta tem de diferente, e
uma funcao no script gerando o caminho que ela procura. O contrato nao muda.
Se a instrucao da ferramenta nova nao puder ser derivada daqui, o caso vira
excecao declarada em ADR, nao copia silenciosa.
