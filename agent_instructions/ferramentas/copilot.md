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
