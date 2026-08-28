# Dossiê Summer (engine `ambev_pricing`)
### Fonte única consolidada para o paper de Otimização de Desconto dado Qmin

**Origem:** destilado de quatro fontes do projeto do Eduardo (repositório em 2026-08-11):
Relatório de Handoff integral (73 pág.), Resumo Executivo, Guia Operacional e o repositório
`Python_Ambev_Pricing_Specialist` (890 arquivos, incluindo `models/specifications/` e
`project_brief/`, camadas conceituais que não aparecem nos PDFs).

**Uso:** anexar este arquivo em vez dos quatro originais. Referências no formato `arquivo.py:linha`
e `§N` remetem às fontes originais, para quem precisar auditar.

**Nota de tom (fixa):** nada aqui deve ser redigido como crítica à viabilidade ou ao impacto do
Summer. O enquadramento é: o Summer estabeleceu a fundação; ao construir sobre ela identificamos
limitações naturais de escopo, quase todas declaradas pelo próprio sistema, e desenvolvemos
estratégias de contorno para que não se propagassem.

---

## 1. O que o Summer é, em uma frase

Um sistema que mede quanto volume de sell-in a mais um PDV pede quando recebe desconto, por
recorte (marca, embalagem, geografia, canal, categoria), e transforma isso em um teto de desconto
defensável por loja e um plano de campanha com custo em R$.

Seis camadas: ingestão com contratos rígidos, estimador econométrico, malha de grãos (lattice),
barreiras de recusa, publicação governada e governança (ADRs, tiers de rigor, red-team).

A propriedade que o próprio documento declara como mais valiosa não é o número produzido, e sim a
disciplina com que o sistema se recusa a produzir número quando a evidência não existe.

---

## 2. A fronteira declarada: sell-in não é demanda

Este é o ponto mais importante para a nossa comparação, e é declaração deles, não avaliação nossa.

`project_brief/measurement_reality.md` abre dizendo que é o documento conceitual mais importante do
sistema e que sell-in é uma mistura de pelo menos quatro coisas:

1. demanda incremental real do consumidor;
2. carregamento / antecipação de compra (efeito chicote);
3. target-chasing (PDV ou representante puxando volume para bater meta);
4. captura de margem: em On Trade o dono do bar define o preço de menu e ele é rígido, então o
   desconto de sell-in vira margem do PDV e não chega ao consumidor.

Conclusão textual deles: uma elasticidade promocional estimada sobre sell-in é um **limite superior
contaminado por carregamento e captura de margem**, e tratá-la como elasticidade de consumo
superestima sistematicamente a responsividade.

O mesmo documento lista o que tornaria aquilo evidência de demanda real: reconciliação com sell-out,
ausência de queda pós-promoção, ou desenho causal (DiD, controle sintético, holdout regional).

**Quatro consequências que atravessam o sistema inteiro (§3 do handoff):**

- o que se mede é associação de pedido, não elasticidade de demanda;
- o sinal é contaminado por carregamento;
- nenhum número autoriza orçamento sozinho: `authorizes_budget = FALSE` em toda superfície;
- o estimando é de **margem intensiva** (`estimand_grain = line_intensive`): mede quanto foi pedido
  dado que houve pedido. **Se a promoção fez mais PDVs pedirem, isso é invisível ali.**

O exemplo canônico do carregamento, que aparece nas duas fontes: PDV compra 10 HL/mês; em março,
com 15% de desconto, compra 25 HL; em abril, sem desconto, compra 2 HL. O sistema vê +150% em
março. O trimestre fecha em 37 HL contra 30 de baseline, ou seja, incremento real de 7 HL e não 15.
Superestimação de mais de 2x.

---

## 3. O estimador

```
log_volume_hl ~ i(discount_band, ref = 'none') | customer_id + period + product_id
```

- **Bandas saturadas:** a profundidade não entra contínua, entra discretizada em faixas de 1 p.p.
  (2 p.p. em baixa escala), borda superior 40%, 42 rótulos na grade de 1 p.p. Cada faixa ganha seu
  próprio coeficiente contra a faixa `none`. Nenhuma forma funcional é imposta: a saturação aparece.
  Sem a banda `none` no recorte, o ajuste é recusado.
- **Ponderação por `volume_hl`.**
- **Erros-padrão agrupados por PDV (CRV1).** É por isso que os pisos de admissão são contados em
  PDVs e não em linhas.
- **Escada de efeitos fixos**, tentada nesta ordem: `customer_id + period + product_id` →
  `customer_id + period` → `period`. Se só o último sobrevive, o status é `unidentified` e nada é
  publicado. O degrau efetivo viaja na coluna `fe_used`.

**Evidência empírica registrada sobre o FE de produto:** numa execução real, `customer_id+period+product`
e `customer_id+period`, ambos com FE de loja, devolveram **+0,17057971** e **−0,07014202** na mesma
banda 4%-5%, mesmos dados, sem descarte por colinearidade. Causa: `product_id = marca|embalagem`;
sem esse FE o coeficiente absorve mix de produto, e descontos profundos assentados em SKUs de baixo
volume puxam a inclinação *entre* produtos para negativo enquanto a inclinação *dentro* do produto
segue positiva. Teste construído isola o efeito: +0,182322 com FE contra −0,298251 sem, e a resposta
intra-produto recupera o uplift desenhado de +20% até a sexta casa (log 1,2 = 0,182322).

Observação importante: `brand`, `pack`, `channel` e `region` **não** são efeitos fixos do modelo.
São eixos de recorte.

---

## 4. A âncora e a matemática da elasticidade

**Âncora (SABS-10):** a profundidade em que a elasticidade de manchete de cada recorte é lida.
Referência global 7,5%, janela de busca ±3 p.p. (4,5% a 10,5%), mínimo de 42 PDVs na faixa, faixa
admissível [0%, 20%]. Dentro da janela o seletor escolhe a faixa **melhor suportada**, não a mais
próxima de 7,5%. A âncora é adaptativa mas compartilhada entre recortes, para que as células sejam
comparáveis; âncora estática é proibida.

**Transformação:**

```
E = (exp(β) − 1) / (−profundidade)          # profundidade sempre positiva
```

Convenção de sinal: resposta normal tem β > 0 e E negativo. **E positivo é violação de sinal**, não
elasticidade fraca, e o valor é retido com a causa em `response_sign`. E publicado com 3 casas.

### ⚠️ E e r são números DIFERENTES da mesma célula

```
E = ( e^(r·d) − 1 ) / d
```

| Símbolo | O que é | Onde aparece |
|---|---|---|
| `E` | elasticidade-**arco**, média sobre o trecho de 0% até a âncora | matriz, mapa, lente Per-PDV (`E_at_anchor`) |
| `r` | **taxa de resposta**, que projeta volume | é o que o planner multiplica |

No exemplo canônico do documento, a mesma célula tem **E = 2,95 e r = 2,67**. Não é arredondamento,
são grandezas distintas, e trocá-las numa projeção erra o volume.

Leitura correta de E = −2,952: a banda ancorada 7%-8% mostra ~22,1% mais volume de sell-in que a
banda `none`; como elasticidade-arco sobre o intervalo inteiro, isso é ~2,95% mais volume por 1% de
preço líquido a menos, **em média de 0% a 7,5%**. A resposta marginal *em* 7,5% é ~2,70%.

**Três armadilhas declaradas:** (1) elasticidade não agrega, média de elasticidades de células não é
a elasticidade do agregado (Jensen mais composição); (2) ranquear usa |E| na âncora, dimensionar usa
a resposta marginal da banda relevante; (3) |E| sazonal difere do |E| do mês.

**Rótulos de banda não são comparáveis entre grades.** Um recorte com desconto médio de 7,4% cai em
"7%-8%" na grade de 1 p.p. e em "6%-8%" na de 2 p.p. Compare em profundidades de referência, nunca
em rótulos.

---

## 5. Grãos, pisos e status

**Lattice:** eixos `(subchannel, brand, sub_brand, pack, region, uf)`, todos os subconjuntos não
vazios = **2⁶ − 1 = 63 grãos**. `uf` é filho de `region` e `sub_brand` é filho de `brand`, com
canonicalização quando o filho determina o pai. `category` (High End / Mainstream) **não** é eixo,
é função da marca, e entraria degenerada; existe uma lista explícita de grãos de categoria.

**Existem DOIS pisos de PDVs, e só o menor recusa:**

| Piso | Valor | Abaixo dele |
|---|---|---|
| `minimum_clusters_bootstrap` | **10** | `unidentified`, nada é publicado |
| `minimum_clusters_crv` | **42** | `weakly_estimable`, publica marcado, IC anticonservador |
| `anchor.minimum_pdv` | 42 | uma banda só pode ser âncora da treliça com 42+ PDVs |

40.000 linhas vindas de 8 PDVs são recusadas; 900 linhas de 300 PDVs passam com folga.

**Exceção crítica:** as quatro famílias diretas `brand_region`, `brand_region_uf`,
`brand_pack_region` e `brand_pack_region_uf` ajustam com piso primitivo de **2 PDVs**
(`subset_min_pdvs = 2`). São justamente os recortes mais tentadores operacionalmente. A coluna
`n_clusters` é a única forma de saber em qual caso se está.

**Status de identificação:** `estimable` (publica), `weakly_estimable` (publica marcado),
`unidentified` / `not_identified` / `insufficient_evidence` (não publica).

**Marcadores de qualidade que viajam junto:** `thin_unstable`, `degenerate_ci` (erro-padrão
colapsado, que não é precisão perfeita e sim ajuste saturado ou colinear), `sign_stable`,
`ci_method`.

**Trim intra-loja:** só entram no ajuste lojas com mais de uma banda de desconto distinta. Uma loja
que nunca variou de profundidade não identifica nada. Consequência: `n_clusters` nunca reconcilia
com a contagem de PDVs do painel, e isso é esperado, não defeito.

---

## 6. O baseline

Sobre ele se apoia tudo: incremento, custo, R$/HL e qualquer ROI. Um erro de 10% no baseline é um
erro de 10% em tudo o que vem depois.

```
baseline da linha = volume observado × e^( − r × desconto praticado )
```

**Correção de mal-entendido comum:** o baseline **não** é média de períodos limpos. Cada linha,
inclusive as com desconto, é dividida pelo efeito modelado do desconto que ela própria carregou. Uma
loja que nunca vendeu sem desconto ainda assim tem baseline.

**A dependência que precisa estar na mesa:**

```
incremento(d) = observado × e^(−r·rdep) × ( e^(r·d) − 1 )
```

O mesmo `r` aparece duas vezes. O baseline **não é evidência independente da elasticidade**, é
derivado dela. Um erro em `r` contamina os dois lados ao mesmo tempo.

**Quatro linhagens de baseline, duas com o mesmo nome de coluna:**

| | `stages/baseline.py` | `stages/campaign.py` | `projection → pdv_lens` | `domain/waterfall.py` |
|---|---|---|---|---|
| Coluna | `baseline_volume_hl_0pct` | `baseline_hl_0pct` | `baseline_hl_0pct` | `wf_baseline_caixas` |
| Unidade | HL | HL | HL | caixas |
| Expoente | β(banda(d_linha)) | r × d_linha | r × d_corrente | mediana de pedidos limpos |
| Serve a | descritivo | o planner | aba Per-PDV | mínimos de caixas |

As duas colunas `baseline_hl_0pct` divergem por construção (Jensen), sempre que a profundidade
variar dentro da loja. Cruzar a aba Per-PDV com o plano num BI dá diferente, e não é defeito.

**Direção do viés, explicitamente carimbada no código:** `baseline_volume_hl_0pct` é limite
**inferior**; `uplift_hl_gross_upper` é limite **superior**. Canais: carry-over subestima;
carregamento e canibalização entre irmãs superestimam; seleção (só entram ofertas com resposta
positiva) descreve a subpopulação onde o desconto funcionou.

`netting_status = "gross_un_netted"`: **canibalização entre irmãs não é descontada.** Um plano pode
conter três ofertas irmãs na mesma loja, e somar o HL delas superestima.

---

## 7. O planner de campanha

**Escopo → coorte → oferta.** O escopo precisa nomear marca (e embalagem, salvo `pack_scope=any`);
curingas são recusados com "is a wildcard, not a scope". A coorte aceita curinga, porque ali "sem
filtro" é escolha real.

**Identidade da oferta:** `(customer_id, sub_brand, pack)`. Uma loja não é uma linha de plano; uma
**oferta** é. Sob `pack_scope=any` uma loja pode gerar três linhas (Brahma 600ml, Brahma Zero 600ml,
Brahma Lata 350ml) com três escadas distintas.

**Baseline sazonal, escada T1 → T4:** `campaign_baseline_hl = Σ (diária do mês × dias de campanha no
mês)`. T1 usa a própria diária da oferta no mês; T2 usa meses adjacentes; T2.5 usa a forma sazonal
da loja (≥6 meses) com nível dessazonalizado da oferta; T3 usa índice descritivo (≥42 PDVs); T4 é a
diária geral sem ajuste. **O tier carimbado é o do mês MAIS FRACO da janela**, e
`seasonal_tier_by_month` publica a composição inteira.

**Alocação:**

```
aplicada = clip(profundidade, 0, teto)
total    = baseline × e^(resposta × aplicada)
custo    = preço × aplicada × total
```

O custo incide sobre `total`, não sobre o incremento: o desconto é dado sobre todo o volume vendido.

**Solver:** `allocation_method = "continuous_floor_discrete_frontier"`. Fase 1, ótimo contínuo com
preço-sombra λ:

```
d*(λ) = clip( 1/(preço × λ) − 1/resposta , 0 , teto )
```

**O baseline não aparece nessa fórmula.** Duas ofertas com mesmo preço e mesma resposta recebem a
mesma profundidade, vendendo 100 HL ou 20 HL. O tamanho decide quanto do orçamento a loja consome,
nunca quão fundo ela desce. λ é um piso sobre a razão `r/preço`. Fase 2, fronteira discreta em
passos de 0,1 p.p., ordenada por custo marginal e desempatada por tier sazonal, tier de curva e
identificador da loja.

**Orçamento acima do corredor simplesmente não é gasto.** Dez vezes mais verba compra o mesmo plano.

**Duas escadas:**
- **Quantidade (caixas):** PROVIDED (cadastro do cliente, por variante) tem precedência sobre EARNED
  (quantis 0,50 / 0,65 / 0,80 dos pedidos limpos da própria loja, encolhidos por James-Stein).
  Regra de admissibilidade PROVIDED (`pmono`): cada degrau ≥ o primeiro; a ordem mútua não é exigida,
  então um feed 10 / 20 / 18 passa.
- **Profundidade:** paridade de custo marginal. `mc(d) = preço × (1/r + d)`,
  `a0(d) = preço × d × e^(r·d)/(e^(r·d) − 1)`. T2 exige `a0(d) ≤ 1,00 × mc(entrada)`; T3 aceita 1,25×.

**Taxa de conversão π:** declarada, jamais estimada. O solver mira `B/π`, então com π = 0,40 e
B = R$ 20.000 o plano emitido custa ≈ R$ 50.000 se todas as lojas aderirem. **Quem aprova verba deve
ler `spend_at_full_conversion_rs`, não `requested_budget_rs`.** O desconto dispara quando um pedido
cruza o limiar, não quando a loja "adere": quem ignora a campanha e pede normalmente ainda coleta o
desconto, com incremento zero, e esse vazamento não é medido.

---

## 8. Governança e contratos reaproveitáveis

- **Identidade canônica do PDV:** `customer_id = cod_pdv + \x1f + cod_unb`. O mesmo código de loja
  existe sob UNBs diferentes; fundi-los derruba a contagem de PDVs (que decide o piso) **e** estreita
  artificialmente o intervalo de confiança. O erro ataca as duas defesas ao mesmo tempo.
- **Geografia comercial, não IBGE:** 7 GEOs (SP, MG, RJ/ES, NO, NE, CO, SUL), 27 UFs, **28 relações
  de pertencimento** porque TO pertence a NO e CO. **CE pertence a NO, não a NE.** Contrato em
  `contracts/geography.py`; nenhum consumidor deve re-derivar a topologia.
- **Cascata de reconciliação GEO/UF** em quatro degraus (padrão da UF → fronteira → CEP arbitra →
  descarta), com `region_source` e `uf_source` para declarar procedência.
- **Correção só na raiz (`adapt`).** Corrigir a jusante espalha a correção por N estágios e cria
  divergência silenciosa entre telas que deveriam concordar.
- **Falha fechada.** Um estágio que não satisfaz seu contrato para a execução em vez de emitir
  artefato parcial. Hierarquia: `ConfigurationError`, `IntegrityError`, `PublicationError`,
  `FinalizationError`, cada um dizendo a quem devolver o problema.
- **Portões de motor (código, não prompt):** `contracts/input.py` (preflight do CSV bruto),
  `contracts/governance.py` (declaração obrigatória antes de qualquer emissão com dado real),
  `contracts/completion.py`, `contracts/parity.py` (paridade superfície a superfície, sem tolerância
  numérica global), `orchestration/golden.py` (15 controles **re-executados**, não lidos de arquivo),
  `dashboard/live_smoke.py`.
- **Reprodutibilidade:** fingerprints por estágio, somas exatas em ordem canônica e
  `domain/r_numeric.py`, emulação do binário64 do kernel R de referência.

**Colunas que devem viajar com qualquer número reaproveitado:** `identification_status`,
`n_clusters`, `authorizes_budget`, `basis`, `estimand_label`, `estimand_grain`, `netting_status`,
`fe_used`, `region_source` / `uf_source`, `anchor_depth_pct`, `sign_stable`, `thin_unstable`,
`degenerate_ci`.

Ressalva declarada pelo próprio documento: o CSV do plano de campanha carrega apenas 2 dessas 11, e
`elasticity_lattice.parquet` também não carrega todas. Enquanto não forem adicionadas, carregá-las é
obrigação de quem exporta.

---

## 9. Limites que o sistema declara sobre si mesmo

Lista textual do §47 / §21, útil porque nenhum item precisa ser afirmado por nós:

1. Não mede demanda do consumidor. Sell-in, com contaminação de carregamento.
2. Não autoriza orçamento. `authorizes_budget = FALSE` em toda superfície numérica.
3. **Não produz elasticidade causal por PDV.** A elasticidade é herdada do recorte; a loja é
   contexto, não unidade de estimação causal. O que é personalizado é apenas a **escala**.
4. **Não otimiza lucro.** Não existe função objetivo de margem nem hurdle de retorno próprio.
5. **Não enxerga frequência de pedido** (`line_intensive`).
6. Não permite comparar rótulos de banda entre escalas.
7. Elasticidade não agrega por média.
8. **A implementação Python não está provada equivalente à referência aprovada.** O contrato
   normativo a mantém não-autorizante até que os 15 controles golden e uma execução compare limpa
   passem, e nenhuma das duas condições foi declarada satisfeita. É o limite mais consequente da
   lista, segundo o próprio documento.
9. Não sabe se uma campanha está no ar.
10. `unconstrained` opera fora da faixa observada: contra uma lei saturante ancorada no mesmo
    coeficiente, superestima volume em 3,70x e incremento em 5,61x no teto.

**Estado de maturidade das superfícies:** famílias de categoria × geografia e de sub-marca foram
declaradas e ligadas, mas **nunca produziram uma linha populada em execução ponta a ponta**. Um
parquet vazio dessas famílias é o estado esperado hoje. A superfície está provada apenas no seu
estado de recusa.

**Lacuna de alocação declarada:** `models/specifications/optimization_logic.md` define o objetivo
preferido como `net_promo_value_rs = incremental_gross_margin_rs − discount_investment_rs −
execution_cost_rs`, mas abre com um aviso de que **o produtor de alocação não está construído no
engine governado** e que o Campaign Planner é superfície de planejamento, não o objeto de alocação
ranqueada. Ou seja, a função objetivo de valor existe como contrato, não como implementação.

---

## 10. Base para a comparação no paper

### 10.1 O que reaproveitamos

| Ativo | Por que serve |
|---|---|
| Elasticidade-arco por célula | âncora externa para o desconto de cluster e validação metodológica independente |
| Geografia comercial (7 GEOs, 28 pertencimentos, TO duplo, CE em NO) | evita divergência de recorte entre as duas soluções; é contrato, não convenção |
| Identidade composta do PDV (`cod_pdv + cod_unb`) | mesma razão, e o erro tem consequência dupla (piso e variância) |
| `product_id` = marca × embalagem como FE único | há evidência empírica registrada de inversão de sinal sem ele |
| Padrão de governança de recusa | pisos, `identification_status`, colunas de procedência, falha fechada |

### 10.2 O que a nossa solução acrescenta

Enquadramento: diferenças de **propósito**, não de qualidade. Cinco delas são declaradas pelo próprio
Summer.

| Frente | Summer (declarado por ele) | Otimizador de Desconto dado Qmin |
|---|---|---|
| Margem medida | `estimand_grain = line_intensive`: quanto foi pedido **dado que houve pedido**; se a promoção fez mais PDVs pedirem, é invisível | modelamos exatamente P(conversão), a margem **extensiva** |
| Identificação | observacional sobre Nota Fiscal, com FE e bandas saturadas | β₁ estimado causalmente em experimentos randomizados com variação semanal de desconto |
| Grão da resposta | elasticidade herdada da célula; o PDV entra só como escala | mesma filosofia (inclinação compartilhada, nível personalizado), executada em PDV × SKU com β₁ como offset no estágio 2 |
| Função objetivo | maximiza volume sujeito a custo; objetivo de valor declarado como lacuna aberta | `max_d P(d)/d^γ`, γ calibrado por neutralidade de gasto, com teto de ROI `d ≤ u/(1+u)` |
| Consistência com Qmin | escada de caixas própria (EARNED / PROVIDED), independente do Qmin publicado | desconto decidido **condicionado ao Qmin já publicado** pelo Otimizador de Volume 1.0 |

### 10.3 Seção 3.1, "As duas elasticidades"

- **A do Summer:** resposta do **volume de sell-in** à profundidade de desconto, medida como
  elasticidade-arco de 0% até a âncora, sobre PDVs que já pediram, contaminada por carregamento e
  captura de margem.
- **A nossa:** resposta da **probabilidade de conversão** à profundidade de desconto, identificada em
  experimento randomizado, sobre a base alocada inteira.

São eixos diferentes do mesmo fenômeno. É por isso que uma **ancora** a outra em vez de substituí-la:
o Summer diz quanto o PDV compra a mais quando compra; nós dizemos se ele compra.

### 10.4 Dois avisos técnicos antes de citar número do Summer

1. **E não é r.** Usar E onde o cálculo pede r erra o volume (na célula de referência, E = 2,95 e
   r = 2,67). E qualquer E precisa viajar com `anchor_depth_pct`, porque comparar dois E lidos em
   profundidades diferentes compara coisas diferentes.
2. **`authorizes_budget = FALSE`** e a implementação ainda não foi provada equivalente à referência
   aprovada. Referência metodológica e validação externa: coberto. Número que autoriza verba: não.
   Isto é nota interna, não entra no paper de negócios.

---

## 11. Operação (do Guia Operacional, para referência rápida)

Modelo de três pastas: template canônico (nunca alterar), `Run_template` (hospeda o `.venv`, nunca
alterar) e uma pasta por rodada. Entrada obrigatoriamente chamada `nf_raw.csv` ou `nf_raw.tsv` em
`inputs/`. **Todo filtro de dado é feito na query**, no SQL Editor do Databricks / Aderência 2.0; o
sistema processa o que recebe e não filtra depois. Uma rodada, um chat, para permitir retomada. O
13º estágio costuma concluir sem emitir o selo, e basta re-executá-lo. Atualização de template desce
em cascata: canônico → `Run_template` → rodada.

---

## 12. Glossário mínimo

| Termo | Significado |
|---|---|
| Banda de desconto | faixa de profundidade com coeficiente próprio |
| Âncora / SABS-10 | profundidade em que o E de manchete é lido |
| Célula | uma combinação de valores num grão, uma unidade de ajuste |
| Grão (grain) | conjunto de eixos que define um recorte |
| Família de banda | artefato com a curva completa de profundidade |
| Lattice | a malha de todos os grãos e células |
| CRV1 | erro-padrão agrupado por PDV |
| Sell-in / sell-out | venda da Ambev para o PDV / do PDV para o consumidor (não observado) |
| `(all)` | sentinela de "cego para este eixo", nunca "pertence a esta categoria" |
| Trim intra-loja | filtro que remove lojas sem variação de profundidade |
