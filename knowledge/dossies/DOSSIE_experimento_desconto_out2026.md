# Dossiê do experimento de desconto de outubro de 2026
### Fonte consolidada para quem documenta, revisa ou desenha o próximo experimento

**Origem:** paper "Experimento de desconto de outubro: resultados e melhorias", publicado no Loop
em novembro de 2026 ([link](https://loop.cloud.microsoft/p/eyJ3Ijp7InUiOiJodHRwczovL2FuaGV1c2VyYnVzY2hpbmJldi5zaGFyZXBvaW50LmNvbS8_bmF2PWN6MGxNa1ltWkQxaUlXeEVaMlZFV0ZjNVpFVXRSVEJoWTFGVVVtTkJiSEJyU2s5c1VEWTBiMnhCY2w5a1RVSnpka1V4T1ZkUFdUSndYMlpPTVZCVVdsSlhjbDlNY0ZoaFdVUW1aajB3TVRWRFQweERVazVPVTFjM1NWbERWMHMxVWtOYVJUWlhNbEUzV1ZkR1VrWklKbU05Sm1ac2RXbGtQVEUlM0QiLCJyIjpmYWxzZX0sInAiOnsidSI6Imh0dHBzOi8vYW5oZXVzZXJidXNjaGluYmV2LnNoYXJlcG9pbnQuY29tLzpmbDovci9jb250ZW50c3RvcmFnZS9DU1BfMGQxZTM4OTQtYmQ3NS00Zjc0LTg0ZDEtYTcxMDRkMTcwMDk2L0RvY3VtZW50JTIwTGlicmFyeS9Mb29wQXBwRGF0YS9TZW0lMjB0JUMzJUFEdHVsbyUyMDkubG9vcD9kPXdlY2NiMWVjNDFkMmI0MTQyYjA4MmIzYmJiMTM4YjIxNSZjc2Y9MSZ3ZWI9MSZuYXY9Y3owbE1rWmpiMjUwWlc1MGMzUnZjbUZuWlNVeVJrTlRVRjh3WkRGbE16ZzVOQzFpWkRjMUxUUm1OelF0T0RSa01TMWhOekV3TkdReE56QXdPVFltWkQxaUlXeEVaMlZFV0ZjNVpFVXRSVEJoWTFGVVVtTkJiSEJyU2s5c1VEWTBiMnhCY2w5a1RVSnpka1V4T1ZkUFdUSndYMlpPTVZCVVdsSlhjbDlNY0ZoaFdVUW1aajB3TVRWRFQweERVazlGUkROR05sbExXVFZKU2tFelFrRldWRmhQV1ZSU1RWRldKbU05SlRKR0ptWnNkV2xrUFRFbVlUMU1iMjl3UVhCd0puQTlKVFF3Wm14MWFXUjRKVEpHYkc5dmNDMXdZV2RsTFdOdmJuUmhhVzVsY2laNFBTVTNRaVV5TW5jbE1qSWxNMEVsTWpKVU1GSlVWVWg0YUdKdGFHeGtXRTVzWTIxS01XTXlUbTloVnpWcFdsaFpkV015YUdoamJWWjNZakpzZFdSRE5XcGlNakU0V1dsR2MxSkhaR3hTUm1oWVQxZFNSa3hWVlhkWlYwNVNWa1pLYWxGWGVIZGhNSEJRWWtaQk1rNUhPWE5SV0VwbVdrVXhRMk16V2taTlZHeFlWREZyZVdOR09XMVVha1pSVmtad1UxWXpTbVpVU0VKWldWWnNSV1pFUVhoT1ZVNVFWRVZPVTFSck5WUldlbVJLVjFWT1dGTjZWbE5STVhCR1RteGplVlZVWkZwV01GcFRVbXRuSlRORUpUSXlKVEpESlRJeWFTVXlNaVV6UVNVeU1qWXpaakl4WkdNNExUSTFNRFV0TkRNek9DMWlZekEyTFROalpEUXpZV1JpTkdKaU5DVXlNaVUzUkElM0QlM0QiLCJyIjpmYWxzZX0sImkiOnsiaSI6IjYzZjIxZGM4LTI1MDUtNDMzOC1iYzA2LTNjZDQzYWRiNGJiNCJ9fQ)), e os notebooks 07, 08, 09b e 33 da pasta `brewopt-modelagem`
do workspace de dev. Este dossiê referencia o resultado e não copia a modelagem.

**Uso:** anexar no lugar do paper quando o texto precisar só dos números e das decisões. Todo
número traz a data de leitura, porque a aderência recebe notas atrasadas e os números mudam entre
execuções. A régua de leitura está no ADR-0016 e as lições de desenho no ADR-0017.

---

## 1. O desenho

- **População:** 6.000 PDVs pequenos e médios, sorteados dentro de estratos entre grupo de
  tratamento (desconto do modelo) e grupo de controle (prática).
- **Cesta:** 4 pares por PDV, 2 de cerveja, 1 de NAB e 1 de MATCH. 24.000 pares planejados, 23.612
  cadastrados na Cora.
- **Orçamentos:** INI-76901 (controle, cerveja), INI-76903 (tratamento, cerveja), INI-77095
  (controle, NAB e MATCH), INI-77096 (tratamento, NAB e MATCH).
- **Vigência:** planejada de 05/10 a 01/11/2026, início efetivo em 07/10.
- **Leituras:** parcial em 27/10 (notas até 22/10, 16 dias) e final em 06/11 (notas até 01/11,
  26 dias).
- **Modelo testado:** `logit P(d) = eta_base + S1·min(d, nó) + S2·max(d − nó, 0)`, objetivo
  `P(d) × Qmin × [1 − λ × d/100 × preço]`, com λ = 0,12 calibrado para neutralidade de gasto, piso
  de 0,5 p.p. e teto duro de 25 p.p.

## 2. Leitura final, 06/11/2026

| Cesta | Grupo | Uplift de faturamento | Gasto | Custo por conversão | ROI técnico ajustado | ROI técnico de Revenue | ROI do dashboard |
|---|---|---|---|---|---|---|---|
| Cerveja | Controle | +R$ 367,1 mil (+10,6%) | R$ 52,3 mil | R$ 31,30 | | 7,02 | 5,67 |
| | Tratamento | +R$ 371,2 mil (+10,8%) | R$ 93,7 mil | R$ 48,88 | | 3,96 | 5,28 |
| | **Tratamento − controle** | **+R$ 4,2 mil** | **R$ 41,3 mil** | **+R$ 17,58** | **1,49** | **0,07** | **−0,38** |
| NAB + MATCH | Controle | −R$ 26,2 mil (−5,4%) | R$ 11,2 mil | R$ 19,10 | | −2,33 | 2,24 |
| | Tratamento | +R$ 5,7 mil (+1,2%) | R$ 14,8 mil | R$ 23,64 | | 0,39 | 2,97 |
| | **Tratamento − controle** | **+R$ 31,9 mil** | **R$ 3,6 mil** | **+R$ 4,54** | **6,94** | **9,06** | **+0,72** |

- **Cerveja:** conversão de 32,4% no tratamento contra 28,4% no controle, +4,1 p.p., diferença
  detectável. Gasto 1,79 vez o do controle. O ROI técnico ajustado de 1,49 não tem significância.
- **O uplift negativo do controle de NAB e MATCH não é efeito do desconto.** A cesta saiu das 4
  semanas antes do sorteio, só com pares que compraram, e essa janela está dentro da linha de base
  de 12 semanas do ROI técnico de Revenue.
- **O nível do ROI do dashboard não é efeito.** O placebo, nas semanas antes do início, também sai
  alto; só a diferença entre os grupos se compara. A réplica foi validada na INI-74798 (setembro de
  2026): 4,86 contra 4,88 do dashboard.

## 3. Para onde foi a verba a mais, leitura parcial de 27/10/2026

Na cerveja, a verba a mais do tratamento se divide em gasto a mais em desconto, 66%, pago a
conversões que aconteceriam de qualquer forma, e conversões novas, 34%. As fórmulas estão no
ADR-0016 e no glossário.

## 4. Onde o modelo se afasta do observado, leitura parcial de 27/10/2026

- conversão realizada em 0,82 a 0,86 da prevista, na cerveja;
- ganho de conversão com a subida em 69% do previsto na cerveja e 59% em NAB;
- 83% dos pares de cerveja no piso ou no teto do desconto;
- no HIGH END, descer o desconto custou R$ 39,8 mil de faturamento para R$ 1,8 mil economizados;
- o λ único gasta de 0,4 a 2,4 vezes a prática conforme o segmento.

## 5. O que foi decidido

Das 13 melhorias mapeadas, 8 foram selecionadas, com 12 pontos de esforço, divididas em três cards
de implementação:

| Card | Sprint | Melhorias |
|---|---|---|
| Melhoria 1, regras de política do desconto | S3-Q4-26 | transições mais lentas entre a prática e o ótimo; λ por segmento e categoria; verificação de canibalização |
| Melhoria 2, resposta ao desconto corrigida com o experimento | S3-Q4-26 | dados do experimento no treino; reestimar a resposta ao desconto com os pares sorteados |
| Melhoria 3 | S4-Q4-26 | ganho por faixa de chance e esforço; features de recência e estoque; recalibração do nível da conversão |

A validação em campo das melhorias vai para um experimento numa geo, sem orçamento dedicado, com
discovery e desenho na S3-Q4-26 (ADR-0017).
