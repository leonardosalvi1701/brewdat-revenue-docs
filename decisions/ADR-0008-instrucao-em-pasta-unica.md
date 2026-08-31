---
id: ADR-0008
titulo: agent_instructions/ como unica casa de instrucao de agente
status: vigente
data: 2026-08-28
projeto: docsquad
autor: Leonardo Salvi
substitui: ADR-0007
impacta: [agent-instructions, agents-md, claude-md, copilot-instructions, scripts-sync]
---

# ADR-0008: agent_instructions/ como unica casa de instrucao de agente

## Contexto
O ADR-0007 escolheu `AGENTS.md` como fonte unica e gerou os demais a partir
dele. A escolha resolveu a divergencia, mas espalhou instrucao pela raiz do
repo: `AGENTS.md` e `CLAUDE.md` soltos no topo, `agents/` numa pasta, `.claude/`
noutra, `.github/` numa terceira. Quem abre o repo pela primeira vez nao
consegue dizer, olhando, o que e instrucao e o que e conteudo, nem o que e
fonte e o que e copia.

Alem disso, nao havia onde por particularidade de ferramenta. Como o contrato
era o unico lugar de instrucao, o que valia para uma so ferramenta acabava
dentro dele, e vazava para as outras. Foi o que aconteceu com a regra de
trailer de autoria, escrita em cima do harness do Claude Code e lida tambem
pelo Codex e pelo Copilot, para quem ela nao se aplicava daquele jeito.

Nenhuma das tres ferramentas deixa configurar onde procura instrucao. Codex le
`AGENTS.md`. Claude Code le `CLAUDE.md`, `.claude/CLAUDE.md` e
`.claude/commands/`. Copilot le `.github/copilot-instructions.md` e
`.github/prompts/`. Esse fato nao muda, e a secao de evidencia abaixo mostra
como foi levantado.

## Alternativas consideradas
| Alternativa | A favor | Contra | Descartada porque |
|---|---|---|---|
| Manter o ADR-0007 como esta | zero trabalho | instrucao continua espalhada pela raiz, e particularidade de ferramenta continua vazando para as outras | o custo aparece toda vez que entra alguem novo no repo |
| Mover tudo para `agent_instructions/` sem deixar nada nos caminhos fixos | raiz limpa de verdade | as tres ferramentas deixam de carregar instrucao sozinhas | a regra que impede escrita em sistema externo deixaria de chegar ao agente, que e exatamente a falha que o ADR-0007 corrigiu |
| Hook `SessionStart` injetando o contrato | tira o `CLAUDE.md` da raiz sem ponteiro | hook e comando de shell, exige confianca no projeto, e se for recusado o contrato nao chega | falha silenciosa: nada indica que o agente esta sem contrato |
| Symlink dos caminhos fixos para dentro da pasta | sem duplicacao no git | symlink no Windows depende de configuracao, e nao ha garantia de que o Copilot siga | a squad trabalha em Windows com WSL, e o modo de falha e silencioso |
| Pasta unica, com ponteiro gerado nos caminhos fixos | uma casa so, e nada para de funcionar | a raiz ainda mostra dois arquivos gerados | adotada |

## Decisao
Toda instrucao de agente mora em `agent_instructions/`: `contrato.md`,
`papeis/`, `rubricas/` e `ferramentas/`. Os caminhos que as ferramentas exigem
sao gerados por `scripts/sync_agent_files.py` e marcados como nao editaveis.

`AGENTS.md` vira ponteiro curto na raiz, porque o Codex so procura ali. O
ponteiro do Claude Code vai para `.claude/CLAUDE.md`, e nao para a raiz.
`.github/copilot-instructions.md`
continua copia do contrato inteiro, porque o Copilot injeta o conteudo do
arquivo no contexto e nao se pode contar com ele para abrir o alvo de um
ponteiro. A copia e gerada e verificada em CI, entao nao e o caso que o
ADR-0007 descartou, que era copia mantida a mao.

`ferramentas/*.md` passa a ser o lugar de tudo que vale para uma ferramenta e
nao para as outras. O contrato so contem regra que vale para todas.

## Razao
O ADR-0007 acertou o mecanismo e errou o endereco. Fonte unica com derivado
gerado continua sendo a resposta certa para divergencia; o que mudou e que a
fonte agora tem casa propria, e que particularidade de ferramenta tem onde
morar sem contaminar o contrato comum.

Sobre o unico ponteiro que sobra na raiz: o Codex nao le nada alem de
`AGENTS.md`, e nao ha como eliminar essa entrada sem perder o carregamento
automatico. Entre uma raiz com um arquivo gerado de quinze linhas e uma raiz
limpa onde o contrato so chega ao agente se um humano lembrar de pedir, o risco
esta todo do segundo lado.

## Evidencia sobre os caminhos das ferramentas
Levantada no binario do Claude Code v2.1.250 e por sonda, em 2026-08-28.

O carregador de memoria de projeto empilha `<raiz>/CLAUDE.md` e
`<raiz>/.claude/CLAUDE.md` incondicionalmente, os dois com escopo `Project`,
sob o mesmo gate. Sonda com um arquivo so em `.claude/CLAUDE.md`: o conteudo
chegou ao contexto. Por isso o ponteiro do Claude Code nao precisa da raiz.

O import `@` resolve a partir da pasta do arquivo que importa, e nao da raiz do
repo. Na mesma sonda, `@../agent_instructions/probe-rel.md` resolveu e
`@agent_instructions/probe-cwd.md` nao. Por isso o gerador emite `../`.

`AGENTS.md` nao aparece no carregador de memoria do Claude Code. As unicas
cinco ocorrencias no binario estao no importador de config do Codex, que
inclusive afirma em prosa que "Claude Code hardcodes CLAUDE.md / AGENTS.md
discovery". A prosa nao bate com o codigo, e vale o codigo: um ponteiro unico
na raiz servindo as duas ferramentas nao funciona.

Nao ha chave de settings nem variavel de ambiente que realoque esses caminhos.
As variaveis existentes so desligam, como `CLAUDE_CODE_DISABLE_CLAUDE_MDS`.

## Consequencias
- `python scripts/sync_agent_files.py --check` continua na verificacao de
  qualquer alteracao, ao lado dos testes;
- alteracao de instrucao acontece em `agent_instructions/`, nunca nos derivados;
- a raiz tem uma unica entrada de instrucao, `AGENTS.md`, e ela e gerada;
- ferramenta nova custa um arquivo em `ferramentas/` e uma funcao no script;
- o ADR-0007 fica superseded, mas segue valendo naquilo que esta decisao
  reafirma: fonte unica, derivado gerado, verificacao em CI.

## Como falsificar
Se uma das ferramentas passar a ignorar o ponteiro na pratica, isto e, se um
agente comecar a alterar o repo sem ter aberto `contrato.md`, o ponteiro nao
basta e aquele caminho precisa virar copia, como ja e o do Copilot. O sinal e
observavel: agente que viola regra do contrato tendo lido so a raiz.

A evidencia acima e de uma versao especifica da ferramenta. Se uma versao nova
do Claude Code parar de carregar `.claude/CLAUDE.md`, ou passar a resolver `@`
a partir da raiz, o gerador quebra calado. Repetir a sonda ao subir de versao e
o teste barato: um arquivo com uma palavra marcada, e perguntar por ela.
