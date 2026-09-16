# Ferramenta: Claude Code

## Onde ele acha instrucao
`.claude/CLAUDE.md`, e nao a raiz. O carregador de memoria empilha
`<raiz>/CLAUDE.md` e `<raiz>/.claude/CLAUDE.md` com o mesmo escopo de projeto,
entao o segundo funciona sozinho e deixa a raiz limpa.

E um ponteiro gerado que importa o contrato e este arquivo por `@`. Os imports
sao `@../agent_instructions/...`, com `../`, porque o `@` resolve a partir da
pasta do arquivo que importa, nao da raiz do repo. Sem o `../` o import falha
calado.

## Papeis
Vem como slash command, gerados em `.claude/commands/`: `/curador`,
`/revisor-negocio`, `/revisor-tecnico`. O wrapper nao contem instrucao propria,
so manda ler o arquivo do papel em `agent_instructions/papeis/`. Se o wrapper
comecar a divergir do papel, o errado e o wrapper.

## Autoria de commit
Esta e a unica pegadinha especifica desta ferramenta. O harness acrescenta
`Co-Authored-By:` e uma linha de sessao por padrao. Omitir as duas ativamente
ao montar a mensagem, conforme o contrato.

## Sistema externo
O contrato vale integralmente, e a ferramenta tem shell. Leitura pelas CLIs
(`databricks`, `az`, `gh`) e pelos comandos de leitura do `docs` e permitida,
sempre com `--profile` explicito no Databricks, escolhido pela pessoa. Escrita
nunca: nada de subcomando que cria, altera ou apaga, nada de SQL ou codigo em
compute, e nada de `docs apply`, `docs approve` ou `docs reject`.
`docs propose` e permitido.
