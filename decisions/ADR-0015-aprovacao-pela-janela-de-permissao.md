---
id: ADR-0015
titulo: Aprovacao de proposta pela janela de permissao da ferramenta de IA
status: proposta
data: 2026-10-09
projeto: docsquad
autor: Leonardo Salvi
substitui:
substituida_por:
impacta: [cli, contrato, sync-agent-files, claude-settings, codex-rules, copilot-hooks]
---

# ADR-0015: Aprovacao de proposta pela janela de permissao da ferramenta de IA

## Contexto
Ate 09/10/2026, aprovar uma proposta exigia sair da conversa com o agente,
abrir outro terminal e rodar tres comandos, `docs show`, `docs approve <id>
--by "Nome"` e `docs apply --id <id>`, copiando o id da conversa. O
`docs decidir` juntou os tres num comando interativo, mas continuou exigindo
o segundo terminal, porque o chat das ferramentas de IA nao e terminal
interativo.

A squad usa tres ferramentas, e as tres tem uma janela de permissao que para
antes de executar um comando, configuravel por repositorio:

- Claude Code: regra `ask` em `.claude/settings.json`. Pergunta inclusive no
  modo automatico, e ganha de regra `allow`;
- Codex: `prefix_rule` com `decision = "prompt"` em `.codex/rules/`. So
  carrega com o projeto confiavel; com aprovacao desligada, o comando e
  recusado;
- Copilot: hook `preToolUse` em `.github/hooks/`, que responde `ask`. Vale
  no Copilot CLI e no modo agente do VS Code. No agente de nuvem, `ask` vira
  recusa.

## Alternativas consideradas
| Alternativa | A favor | Contra | Descartada porque |
|---|---|---|---|
| Manter so o terminal, com atalho do VS Code | nao muda o modelo de seguranca | continua fora da conversa | a squad pediu aprovar sem sair do chat |
| Painel web local | visual | servidor local que o agente alcanca por shell | separacao mais fraca que a janela da ferramenta, e dependencia nova |
| Janela de permissao, configurada por ferramenta | um clique, dentro da conversa | a garantia passa a depender da configuracao da ferramenta | adotada |

## Decisao
Adotamos a janela de permissao da ferramenta de IA como lugar de aprovacao.
O agente pede `docs approve <id> --aplicar` depois de mostrar o conteudo com
`docs show`, e a ferramenta pergunta antes de executar. `docs decidir` fica
como o caminho do terminal.

As tres configuracoes sao geradas de uma fonte so,
`agent_instructions/aprovacao.yaml`, por `scripts/sync_agent_files.py`.

## Razao
O clique na janela e uma acao humana que o agente nao consegue produzir, e
acontece com o comando exato na tela, depois do conteudo exato na conversa.
Isso preserva o que importa no portao: so o que a pessoa viu e aceitou e
aplicado, e o Executor continua revalidando a politica.

A separacao deixa de ser fisica no sentido de antes. Antes, o pior resultado
de um agente se comportando mal era um JSON que ninguem aprovou. Agora e uma
pergunta que a pessoa recusa, desde que a configuracao da ferramenta esteja
no lugar. Por isso:

- a configuracao e gerada e conferida no `--check`, e coberta por teste;
- cada ferramenta falha fechada onde da: o Codex recusa com aprovacao
  desligada, o hook do Copilot sai com erro se nao conseguir rodar, e o
  `docs` recusa decidir proposta em CI;
- o contrato proibe contornar a janela, e manda avisar a pessoa se um
  `approve` rodar sem pergunta.

## Consequencias
- `docs approve` aceita `--aplicar`, e `--by` passa a ser opcional, com a
  identidade do `az login`;
- `docs approve`, `apply`, `reject` e `decidir` recusam rodar com `CI` ou
  `GITHUB_ACTIONS` definido;
- passam a ser gerados `.claude/settings.json`, `.codex/rules/docsquad.rules`
  e `.github/hooks/aprovacao-humana.json`, e `.codex/` entra na lista de
  derivados que ninguem edita a mao;
- o contrato troca "nunca rodar `docs approve`" por "pedir `docs approve`
  so depois do `docs show`, um por comando, e nunca contornar a janela";
- quem usa Copilot nao pode usar "Allow all", "Autopilot" ou
  `--allow-all-tools` neste repo, porque a documentacao nao garante que eles
  respeitem o `ask`.

## Como falsificar
Se um `docs approve` rodar sem a ferramenta perguntar, em qualquer das tres,
a garantia quebrou naquela ferramenta. O caminho e voltar aquela ferramenta
para o `docs decidir` ate a configuracao ser corrigida, e registrar o caso em
`review-log/`.

Se as aprovacoes pela janela passarem a sair sem que ninguem leia o
`docs show`, por cliques automaticos, o clique deixou de ser revisao. Ai a
janela nao serve como portao, e o `decidir` volta a ser o unico caminho.
