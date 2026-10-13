# Ferramenta: GitHub Copilot

## Onde ele acha instrucao
`.github/copilot-instructions.md`, que e copia gerada do contrato inteiro, e
nao ponteiro. O Copilot injeta o conteudo do arquivo direto no contexto e nao
se pode contar com ele para seguir um ponteiro, entao aqui a copia e o formato
que funciona. Ela e gerada e verificada em CI, entao nao diverge.

## Papeis
Prompt files em `.github/prompts/*.prompt.md`, com `mode: agent`. Invocar por
`/curador`, `/revisor-negocio` ou `/revisor-tecnico` no Copilot Chat.

## Autoria de commit
A mensagem de commit sugerida pelo Copilot as vezes traz trailer de coautoria.
Remover antes de commitar, conforme o contrato.

## Aprovacao
`.github/hooks/aprovacao-humana.json`, gerado, chama
`scripts/hooks/exigir_aprovacao.py` antes de cada ferramenta. Quando a
chamada roda `docs approve`, `apply`, `reject` ou `decidir`, o hook responde
`ask` e o Copilot pergunta antes de executar. O mesmo arquivo vale para o
Copilot CLI e para o modo agente do VS Code.

O que precisa estar ligado:

- no VS Code, a pasta marcada como confiavel (Workspace Trust) e os hooks
  ligados (`chat.useHooks`, ligado por padrao). A organizacao pode desligar
  hooks; nesse caso, aprovar so pelo `docs decidir`;
- nao usar os niveis "Allow all" ou "Autopilot" neste repo, nem
  `--allow-all-tools` no CLI: a documentacao nao garante que eles respeitem
  o `ask`.

No agente de nuvem do Copilot nao ha ninguem para clicar: o hook vira recusa,
e o proprio `docs` recusa decidir proposta quando `CI` ou `GITHUB_ACTIONS`
esta definido.
