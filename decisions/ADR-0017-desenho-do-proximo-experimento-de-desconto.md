---
id: ADR-0017
titulo: Licoes de desenho para o proximo experimento de desconto
status: proposta
data: 2026-11-09
projeto: desconto-qmin
autor: Leonardo Salvi
substitui:
substituida_por:
impacta: [cards-de-discovery-e-desenho-de-experimento, paper-resultado-experimento]
---

# ADR-0017: Licoes de desenho para o proximo experimento de desconto

## Contexto
A leitura do experimento de outubro de 2026 (ADR-0016) expos quatro pontos
do desenho que limitaram o que se pode concluir. A squad vai desenhar o
proximo experimento numa geo especifica, com um conjunto definido de PDVs e
sem orcamento dedicado, para validar as melhorias do modelo de desconto
(cards de discovery e de desenho de experimento da S3-Q4-26). Fonte dos
numeros: paper "Experimento de desconto de outubro: resultados e melhorias",
no Loop, leitura final de 06/11/2026.

1. **A cesta saiu de dentro da janela de comparacao.** Os pares foram
   escolhidos nas 4 semanas antes do sorteio entre os que compraram, e essa
   janela entrou na linha de base de 12 semanas. O controle de NAB e MATCH
   saiu com uplift de -5,4% sem relacao com o desconto.
2. **O orcamento usou a mesma conversao nos dois grupos.** Isso previu 1,50
   vez a pratica na cerveja. A pontuacao, com a conversao prevista de cada
   grupo, ja previa 1,83 vez, e o realizado foi 1,79 vez.
3. **A leitura dependia da data de execucao.** A aderencia registra compra com
   2 a 5 dias de atraso, e os numeros mudavam a cada execucao ate a data de
   leitura virar parametro fixo dos notebooks.
4. **O desconto so variou entre os grupos.** A resposta ao desconto so e
   identificada pela diferenca media entre tratamento e controle; a curva
   (quanto cada p.p. a mais converte) nao. O ganho realizado com a subida foi
   69% do previsto na cerveja e 59% em NAB, na leitura parcial de 27/10/2026.

## Alternativas consideradas
| Alternativa | A favor | Contra | Descartada porque |
|---|---|---|---|
| Repetir o desenho de outubro | operacao ja conhecida | repete os quatro limites acima | nao valida as melhorias que dependem da curva |
| Corrigir so a leitura, mantendo o desenho | sem custo de desenho | a linha de base contaminada e a falta de dose nao se corrigem depois | o vies esta no dado, nao na conta |
| Incorporar as quatro licoes no desenho | ataca a causa de cada limite | sortear dose exige mais PDVs por estrato | proposta |

## Decisao
Propomos que o proximo experimento de desconto escolha a cesta fora da janela
de comparacao, faca o orcamento com a conversao prevista de cada grupo, fixe a
data de leitura como parametro, e avalie sortear doses de desconto dentro de
cada estrato de categoria, esforco e chance.

## Razao
Cada licao corresponde a um numero medido em outubro. As tres primeiras nao
custam amostra. A quarta custa, e por isso fica como avaliacao: o card de
desenho calcula o efeito minimo detectavel com a variancia de outubro antes
de decidir.

## Consequencias
- o card de desenho de experimento documenta cada um dos quatro pontos, com a
  escolha feita e o calculo de amostra;
- a leitura usa a regua do ADR-0016;
- esta ADR passa a vigente quando o desenho for aprovado por PM, DM e pela
  geo, com as escolhas finais registradas aqui.

## Como falsificar
- se a cesta escolhida fora da janela tiver conversao tao baixa que o
  experimento perca poder, o ponto 1 volta a ser discutido;
- se o calculo de amostra mostrar que doses sorteadas nao sao detectaveis numa
  geo, o ponto 4 sai do desenho e a curva continua sem identificacao.
