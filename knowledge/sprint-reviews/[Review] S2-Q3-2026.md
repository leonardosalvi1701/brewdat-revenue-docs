---
tipo: sprint-review
sprint: S2-Q3-2026
squad: Revenue
status: vigente
audiencia: squad
origem: Microsoft Loop, exportado em PDF
---

<!--
Extracao textual de `[Review] S2-Q3-2026.pdf`, o exemplar do padrao de escrita
da squad. Existe porque PDF nao e recuperavel: o curador precisa poder citar
trecho, e o escritor precisa poder comparar tom.

Nao e o documento original. Imagens, tabelas formatadas e trechos de codigo do
paper nao sobrevivem a extracao. Para qualquer duvida de formato, o PDF manda.
-->

Adicionar capa [Review] S2-Q3-2026 Índice Sumário
1. Objetivo do Paper
2. Descrição da Sprint
2.1. Objetivo
2.2. Duração da Sprint
3 Métricas da Sprint
4. Atividades desenvolvidas
4.1 Modelo de Volume Evolução das regras de contorno da quantidade mínima Consolidação da documentação e material da Sync Integração da nova política e produtização Adequação ao Databricks Runtime e correção de vulnerabilidades Interferência por descomissionamento da fonte de aderência Acompanhamento da solução em produção Proposta para evolução do modelo de desconto Estruturação da EDA do modelo de desconto dado a quantidade mínima Apoio ao desenvolvimento e seleção da amostra Cards validados Flexibilização da Quantidade Máxima no protótipo CMAB Design do Experimento e estimação da amostra para experimento BAR Outros Cards Complementares
4.2. Promo Por Objetivo - Arquitetura e Documentação
4.3. Promo Removal (Cerveja) - Ajustes e Bugs Bug 1 - Reason 12: Qtd. mínima do SKU > média semanal do PDV Bug 2 - Janela de histórico divergente entre modelo e regra manual Bug 3 - Reason 7 removendo a promoção com maior desconto Bug 4 - Cobertura de clientes estáveis não enviada para remoção Bug 5 - Cobertura com max_sku = 1 removida pelas Reasons 3 e 12
4.4. Promo CORA - Correção de recebimento e reprocessamento
4.5. Promo Removal de Combos - Discovery e Alinhamento
4.6. Promo Removal - Subir PR do Pedido Agendado
4.7. Promo Removal - Recadastro
4.8. Promo por Objetivo - Elegibilidade e Ranqueamento
4.8.1 Documentação Técnica de Elegibilidade e Ranqueamento Elegibilidade Construção da Base de Dados Atualização da Elegibilidade Ranqueamento
4.8.2 Criação de Dashboard para MVP com as GEOs
4.9. Otimizador de Cobertura - Monitoramento em Produção e Correção de BUG Monitoramento da Tabela de Orçamento Ajuste no Pipeline de Features do Modelo - Descomissionamento de Tabela
4.10 Revisão dos Indicadores de Share de Promoções
4.11 Migração de Inputs Manuais para BrewDat
4.12 Demais Atividades e Interferências
5 Reconhecimentos Ao time de engenharia, entramos em um TRI de geração de MUITO valor
1. Objetivo do Paper Visando dar clareza e tornar objetiva as cerimônias de encerramento de sprint, o paper em questão traz uma breve apresentação sobre os artefatos entregáveis ao final da sprint, trazendo imagens ilustrativas, trechos de código, e exemplos práticos.

Além de auxiliar sobre o que de fato é relevante ser trazido na review/retrospectiva, a escrita sobre uma entrega trás a oportunidade de refletir sobre como as atividades da sprint contribuem para o produto, e conectar algumas pontas soltas entre as entregas.
2. Descrição da Sprint
2.1. Objetivo Nessa sprint tivemos os seguintes objetivos:
Deliverable Descrição da Entrega Impacto Esperado
1
2
3
2.2. Duração da Sprint SX: seg., 20 de jul. de 2026 a sex., 7 de ago. de 2026
3 Métricas da Sprint Apresentar indicadores que ajudem a acompanhar o fluxo de trabalho e a saúde do delivery da squad.
KPI Valor da Sprint Observação
1 Story Points planejados
2 Story Points entregues
3 Taxa de entrega Planejado (%)
4 Bugs encontrados
5 Bugs resolvidos
6 Lead time médio
7 Cycle time médio
4. Atividades desenvolvidas
4.1 Modelo de Volume Responsável: Leonardo Salvi Evolução das regras de contorno da quantidade mínima Durante a sprint, foi concluída a etapa de validação da proposta de flexibilização da quantidade mínima do Otimizador de

Volume 1.0. A alteração parte da remoção da barreira fixa de três caixas e da revisão das regras de contorno utilizadas para definir os limites das recomendações geradas pelo modelo.
As alterações haviam sido inicialmente desenvolvidas por Eduardo e, nesta etapa, o trabalho foi direcionado à validação da implementação e de sua aderência aos resultados observados no experimento. Para isso, foram retomados os códigos utilizados na construção das novas regras e reconstruídas as análises necessárias para avaliar tanto o comportamento das recomendações quanto seus impactos de negócio.
Durante essa validação, foi necessário revisar também a forma como algumas análises anteriores estavam sendo calculadas. Na construção dos boxplots, por exemplo, a tabela final do Otimizador continha previsões históricas para diferentes combinações de PDV e produto ao longo de aproximadamente dois anos. A utilização de todo esse histórico distorcia a leitura do cenário atual.
Dessa forma, a análise foi ajustada para considerar somente a previsão mais recente de cada combinação PDV × produto.
Adicionalmente, durante a investigação de valores negativos de lifting observados inicialmente, foi identificada uma inconsistência entre a variável de média utilizada para aplicar as regras de correção e aquela utilizada posteriormente para gerar as visualizações. A utilização de variáveis distintas produzia uma distorção gráfica que indicava um comportamento negativo inexistente na aplicação efetiva da regra. Após a padronização da variável utilizada nas duas etapas, essa inconsistência foi eliminada.
As análises foram progressivamente complementadas a partir das discussões com as lideranças técnica e de negócio. Foram incorporadas avaliações da distribuição de descontos cadastrados e convertidos, comparação do comportamento por categoria, análise por porte de PDV e exemplos comparando as recomendações antes e depois da aplicação da nova regra. Também foram consideradas, na avaliação da quantidade mínima, tanto a média quanto a mediana das recomendações, buscando caracterizar de forma mais robusta a mudança na distribuição.
Os resultados obtidos foram apresentados e discutidos com os stakeholders e utilizados para suportar a decisão de continuidade da nova política. A etapa consolidou, portanto, não apenas a implementação da flexibilização da quantidade mínima, mas também sua validação experimental e de negócio antes do avanço para o fluxo de produção.
Pontos Positivos
• A nova política foi validada a partir dos resultados experimentais e discutida com os stakeholders.
• Inconsistências identificadas nas análises anteriores foram corrigidas antes do avanço da solução para o fluxo de produção.
Consolidação da documentação e material da Sync Em paralelo à validação, os resultados foram consolidados em uma documentação técnica e de negócios sobre a evolução das regras de quantidade mínima. O objetivo foi produzir um material único contendo o racional da alteração, a experimentação realizada, as limitações identificadas, as análises financeiras e de negócio e os resultados das avaliações realizadas ao longo do desenvolvimento.
A documentação foi construída de forma mais abrangente, servindo como material de referência para a solução. Essa decisão permitiu também otimizar o esforço necessário para a preparação do material da Sync do Volume 1.0. Como ambos os materiais tratavam da mesma evolução, o conteúdo já estruturado no paper técnico e de negócio foi utilizado como base para uma versão mais condensada e direcionada à apresentação.
Dessa forma, o material da Sync priorizou os principais resultados e decisões, enquanto a documentação completa permaneceu como referência para o aprofundamento metodológico e técnico. Essa organização evitou a reconstrução das mesmas análises em dois materiais independentes e garantiu maior consistência na comunicação dos resultados.
Pontos Positivos O conteúdo produzido na documentação técnica e de negócios foi reaproveitado na construção do material da Sync, reduzindo a duplicação de esforço entre as duas entregas.
Integração da nova política e produtização Após a conclusão das validações, a alteração avançou para a etapa de integração no fluxo do modelo. As DAGs relacionadas ao

Otimizador de Volume foram executadas em ambiente de desenvolvimento considerando a nova política, permitindo verificar o funcionamento do pipeline de ponta a ponta antes da disponibilização em produção.
Ao todo, as cinco DAGs previstas para a validação foram executadas, e o resultado da previsão final foi conferido com sucesso.
Com a conclusão dos testes, foi aberto o Pull Request contendo as alterações necessárias para a evolução das regras do modelo.
Entretanto, o processo de integração coincidiu com uma série de intercorrências técnicas externas ao desenvolvimento originalmente planejado, aumentando o esforço necessário para conclusão da entrega.
Adequação ao Databricks Runtime e correção de vulnerabilidades Durante o processo de produtização, foram recebidas duas demandas obrigatórias de plataforma. A primeira estava relacionada à identificação, pelo Snyk, de vulnerabilidades críticas em dependências utilizadas pelo projeto. A segunda decorreu da migração compulsória dos produtos de Machine Learning para o Databricks Runtime 16.4 LTS.
Para adequação do projeto, foram atualizadas as dependências vulneráveis e revisadas as configurações dos clusters e pipelines que ainda utilizavam versões anteriores do runtime. As alterações precisaram ser aplicadas tanto no fluxo principal do modelo quanto nos códigos e pipelines relacionados, seguidas por uma nova rodada de validações.
Esse trabalho ocorreu simultaneamente à abertura do Pull Request da flexibilização da quantidade mínima e passou a fazer parte do mesmo fluxo de integração, uma vez que o modelo precisava estar compatível com a nova infraestrutura antes do merge.
Além das alterações de código, houve uma intercorrência adicional na esteira de CI. Mesmo com o Pull Request aprovado, os checks obrigatórios não foram iniciados após uma atualização da branch, mantendo o PR bloqueado sem que houvesse propriamente uma reprovação dos testes. A análise apontou que o evento responsável por disparar os workflows não havia sido gerado.
Após uma nova atualização da branch, as validações foram reacionadas, permitindo a continuidade da esteira. Posteriormente, a falha foi caracterizada em conjunto com a arquitetura como um problema da própria esteira, e, as validações foram reacionadas, permitindo a continuidade da esteira. Posteriormente, a falha foi caracterizada em conjunto com a arquitetura como um problema da própria esteira, e não do repositório ou das alterações desenvolvidas.
Com a regularização do CI e a conclusão das validações, o Pull Request foi finalmente mergeado.
Pontos Negativos
• A necessidade de correção das vulnerabilidades e adequação ao novo Databricks Runtime surgiu durante o processo de integração e aumentou o esforço necessário para conclusão da entrega.
• Uma falha na esteira de CI manteve temporariamente o Pull Request bloqueado mesmo após sua aprovação.
Interferência por descomissionamento da fonte de aderência Outra interferência ocorrida durante o mesmo período foi o descomissionamento do path utilizado para consumo da tabela AderenciaTtv. A fonte anteriormente disponível na Iris foi removida pelo time responsável e migrada para o Unity Catalog, impactando diretamente o notebook de geração das features de volume.
Foi necessário comparar as estruturas das bases antiga e nova para avaliar o impacto da migração. O contrato permaneceu majoritariamente compatível, mas duas colunas consumidas pelo código tiveram seus nomes alterados. O pipeline foi então ajustado para consumir o novo path e a nova nomenclatura, garantindo a continuidade da geração das features.
Essa alteração não fazia parte do planejamento inicial da evolução da quantidade mínima, mas precisou ser incorporada ao mesmo Pull Request para que o fluxo pudesse continuar operacional após o descomissionamento da fonte anterior.
Pontos de atenção O descomissionamento de uma fonte utilizada pelo pipeline exigiu uma adequação não prevista durante o processo de integração.
Acompanhamento da solução em produção Após o merge, foi realizado o acompanhamento das DAGs do Otimizador em produção, com o objetivo de verificar a estabilidade do fluxo e comparar os resultados gerados com aqueles previamente validados em desenvolvimento.

Na primeira execução, a DAG de features apresentou falha durante a instalação de uma dependência. O mesmo código executava normalmente em desenvolvimento, e foi identificado que outras pipelines de Machine Learning apresentavam o mesmo comportamento em produção naquele período. A ocorrência estava relacionada ao ambiente de plataforma, que se encontrava em processo de correção.
Após a regularização do ambiente, a DAG de features voltou a executar normalmente sem necessidade de alterações adicionais no código do modelo. As etapas seguintes também foram acompanhadas. Houve ainda uma falha pontual na DAG de serving associada à disponibilidade de recursos, porém uma nova execução foi concluída com sucesso.
Ao final do acompanhamento, as DAGs necessárias foram executadas com sucesso em produção e os resultados finais foram conferidos por meio de um notebook específico de validação, concluindo a etapa de disponibilização das alterações.
Pontos Positivos
• Após a regularização do ambiente, as DAGs necessárias foram executadas com sucesso em produção.
• Os resultados foram conferidos por meio de um notebook específico de validação.
• A falha da DAG de features não exigiu alteração adicional no código do modelo.
Proposta para evolução do modelo de desconto Em paralelo à consolidação do Volume 1.0, avançou-se na definição da abordagem metodológica para a próxima evolução do Otimizador, voltada à otimização conjunta entre quantidade mínima e desconto.
A discussão partiu da comparação entre diferentes abordagens de elasticidade já estudadas pelo time, incluindo soluções existentes de elasticidade de desconto e pontos, além da possibilidade inicialmente considerada de utilização de regressão logística. O objetivo foi estruturar uma proposta capaz de combinar resposta ao desconto, previsão de demanda e características dos PDVs em uma mesma lógica de decisão.
A proposta inicial foi apresentada às lideranças e aos pares de Data Science e passou por rodadas de discussão e revisão. Entre os pontos levantados estiveram a incorporação de variáveis relacionadas a sazonalidade, potencial de faturamento, perfil e nível de digitalização do PDV, além da necessidade de avaliar adequadamente o nível em que uma eventual clusterização deverá ocorrer.
Também foi levantada uma questão metodológica central: se a otimização individual de cada combinação PDV × SKU necessariamente produz o melhor resultado global. Essa discussão motivou a avaliação de alternativas multinível e passou a compor as premissas a serem estudadas antes da definição final do modelo.
Após a incorporação das críticas e respostas às questões levantadas nas apresentações, a proposta foi aprovada pelos pares. A partir dessa definição, foi estruturado o cronograma e o desenho da EDA que deverá sustentar as etapas seguintes de modelagem.
Estruturação da EDA do modelo de desconto dado a quantidade mínima Com a definição da proposta metodológica, iniciou-se a Análise Exploratória de Dados que dará suporte ao modelo de desconto dado a quantidade mínima.
O planejamento inicial previa a realização da EDA antes da construção das features do modelo. Entretanto, ao iniciar a investigação, foi identificado que não existia uma base analítica consolidada ligando a promoção cadastrada ao seu respectivo desfecho. As informações necessárias estavam distribuídas entre diferentes fontes, incluindo Smart Promo, informações de behavior, aderência e conversão.
Dessa forma, a ordem originalmente planejada precisou ser readequada. Antes de avançar nas análises exploratórias propriamente ditas, tornou-se necessário estruturar as features e construir uma base capaz de representar, de forma consistente, a relação entre PDV × SKU × campanha e seu resultado observado.
A primeira etapa foi, portanto, direcionada à reconciliação das fontes e à definição do rótulo de conversão. A construção parte das promoções otimizadas pelo Smart Promo, restringe-se às promoções ativas na janela de referência e posteriormente enriquece o desfecho utilizando os sinais disponíveis nas bases de aderência, conversão e comportamento.
Um ponto importante dessa construção foi a utilização conjunta dos diferentes sinais de interação e conversão. A presença de uma conversão é considerada como evidência positiva mesmo quando determinados registros de comportamento não estão disponíveis, evitando que promoções efetivamente convertidas sejam classificadas incorretamente como negativas.
Além da construção do rótulo, foram iniciadas as avaliações referentes à chave de junção entre as diferentes fontes, à taxa efetiva

de casamento dos registros, à comparação da taxa de conversão reconstruída com os números acompanhados pelo negócio, ao tratamento de promoções removidas e à ocorrência de duplicidades relacionadas ao recadastro.
A mudança de planejamento permitiu transformar a EDA em uma análise apoiada por uma estrutura de dados reprodutível, em vez de realizar investigações sobre bases ainda não reconciliadas. Nesta sprint foram concluídas a definição inicial das features e as análises previstas nos Blocos 1 a 3 do desenho da EDA.
Essa etapa também evidenciou a necessidade de manter o desenho analítico adaptável durante o desenvolvimento. À medida que as fontes foram reconciliadas e suas limitações se tornaram mais claras, foi necessário reavaliar a sequência das análises e a própria estrutura da base. Essas mudanças passaram a fazer parte do processo de construção da solução, buscando evitar que decisões metodológicas posteriores sejam baseadas em relações de conversão ou exposição ainda não corretamente identificadas.
Pontos de atenção O planejamento inicial precisou ser readequado porque não havia uma base analítica consolidada para realização da EDA. Foi necessário antecipar a estruturação das features e a reconciliação das fontes antes de avançar nas análises.
Apoio ao desenvolvimento e seleção da amostra Durante a sprint, também foi realizado apoio ao desenvolvimento do desenho amostral conduzido por Ayrton Farias, incluindo a revisão do algoritmo de seleção utilizado nos novos experimentos.
A análise conjunta identificou que a amostra utilizada anteriormente não contornava adequadamente PDVs já empregados em outro experimento, fazendo com que uma parcela relevante dos estabelecimentos disponíveis fosse absorvida e gerando desequilíbrio na seleção restante. Além disso, foram revisados pesos e critérios utilizados na estratificação.
A lógica de geração da amostra foi reestruturada e foram propostas melhorias na distribuição dos descontos, buscando reduzir a concentração de gastos acima da média. O trabalho também contemplou apoio e validação do processo amostral associado aos experimentos de flexibilização das quantidades mínima e máxima.
Cards validados Além das atividades diretamente relacionadas ao desenvolvimento do Otimizador de Volume, foram realizadas validações técnicas de entregas conduzidas por outros integrantes do time durante a sprint. O objetivo dessas validações foi revisar a consistência das soluções desenvolvidas, documentação, critérios experimentais e adequação das implementações antes de sua conclusão.
• Implementação do ranqueamento dos PDVs-SKUs elegíveis Responsável: Alice Adativa Ferreira Menezes. QA realizado.
• Documentação técnica da elegibilidade desenvolvida e apresentação para stakeholders Responsável: Alice Adativa Ferreira Menezes. Documento revisado, com discussão de sugestões de alteração no paper e alinhamento de dúvidas.
• Design do Experimento Responsável: Ayrton Farias. Design validado.
• Atualização dos notebooks de outros experimentos Responsável: Ayrton Farias. Validação realizada, com apontamentos de ajustes relacionados a parâmetros, duplicidades, limpeza dos notebooks e definição dos novos valores utilizados para quantidade máxima.
Flexibilização da Quantidade Máxima no protótipo CMAB Responsável: Ayrton Farias Esta atividade estendeu o protótipo CMAB do otimizador de volume para introduzir uma terceira dimensão no braço promocional: a quantidade máxima flexível. Até então, cada PDV x SKU do grupo de tratamento recebia um desconto e uma quantidade mínima com Qmax = Qmin, ou seja, um envelope rígido, sem folga de compra acima do piso.
O que foi realizado: o objetivo principal dessa atividade foi redefinir o braço de (desconto, volume) para (desconto,

volume, k_qmax), onde k_qmaxé um multiplicador que define o teto de compra baseado no paper de referência produzido pelo Gabriel. Isso expandiu o espaço de decisão de 30 para 90 braços por segmento. Com essa atividade, foram entregues dois notebooks: um para gerar a primeira base e outro para o recadastro semanal usadopara as iterações semanais - além do documento de Desing do experimento.
Por que foi realizado: essa tarefa foi realizada com o objetivo de investigar a hipótese de que o envelope rígido corta compra incremental que o PDV faria se tivesse um teto maior. Abrir uma folga de volume controlada por segmento permite capturar esse incremental e avaliar se ele é suficiente para não deteriorar o ROI, mantendo intactos o motor de decisão e a função de recompensa.
Como foi realizado: o nível de flexibilização (k_qmax) foi incorporado ao braço redefinindo a métrica de dificuldade que guia a migração. Dessa forma, passou-se a usar o ponto médio entre Qmine Qmax fazendo a dificuldade crescer com o teto. A capacidade logistica por SKU é incorporada como um teto limite e é derivada diretamento do volume do SKU. A primeira semana aplica a flexibilização via semeadura balanceada (1/3 dos PDVs por nível de k_qmaxem cada porte), mantendo a dificuldade da semana anterior para isolar o efeito do teto; a partir da segunda semana, a política de iteração migra os braços compondo a partir da semana anterior (baseline).
Pontos positivos
• A mudança continua preservando o motor original de decisão e a função de recompensa, sendo assim, a nova dimensão foi acoplada por cima do mecanismo já existente.
• As verificações de integridade e coerência do Qmax foram executadas e validadas com sucesso e os níveis entre porte foram recalibrados junto com Leonardo Salvi.
Pontos de atenção A atualização dos notebooks e documentação das alterações já estão prontos e validados, porém a liberação do orçamento ainda não foi disponibilizada, o que impede o go-live do experimento.
Design do Experimento e estimação da amostra para experimento BAR Responsável: Ayrton Farias Nesta atividade foi construído o desenho de um experimento aleatorizado (teste A/B) e estimada a amostra de PDVs para investigar, de forma causal, a hipótese de que descontos maiores seriam mais atrativos para bares do que descontos baixos. Uma hipótese que foi levantada na apresentação da análise do Leonardo Salvi.
O que foi realizado:Desenhou-se um experimento de desconto para o canal BAR, com dois grupos (controle e tratamento) definidos por faixa de desconto, e estimou-se uma amostra de aproximadamente 10 mil PDVs estratificada e balanceada. O experimento define a atribuição de desconto por grupo, a quantidade mínima (via Smart Promo) e um teto flexível de quantidade. O conjunto de métricas-alvo definidas foram: conversão e volume como primárias, com faturamento e ROI como complementares. A entrega inclui o paper de design, o notebook de estimação da amostra e as validações de balanceamento.
Por que foi realizado: Uma análise de backtest observacional sugeriu que bares com desconto acima de 5% compravam mais volume e apresentavam maior faturamento, mantendo eficiência. Porém, por se tratar de uma análise com dados observacionais, onde o desconto não foi atribuído aleatoriamente, os resultados eram frágeis para cravar causa e efeito. Assim, esse experimento foi desenhado para responder a essa hipótese, aleatorizando os descontos e eliminando o viés de seleção do backtest.
Como foi realizado: A amostra foi restrita a bares, portes Pequeno e Médio, cerveja ON, PDVs com pelo menos 80% de compra em SKUs RGB, excluindo todos os PDVs de outros experimentos, PDVs de histórico muito curto e de faturamento global muito alto (para remover sub/atacado). Os grupos foram formados por randomização estratificada e pareada em que os PDVs foram organizados em estratos (GEO x segmento x porte x faixa de desconto percentual x mês-ano) e, dentro de cada estrato, pareados dois a dois por desconto histórico, com um PDV de cada par indo para cada grupo, garantindo grupos disjuntos, de tamanho igual e pareados no perfil de desconto. A atribuição de desconto parte da distribuição empírica dos descontos cadastrados, preservando a forma e deslocando a faixa entre grupos, de modo que a única dimensão seja o nível de desconto. O balanceamento foi validado comparando volume, faturamento e desconto histórico entre os grupos, no agregado e por GEO/segmento/porte, além da verificação de independência entre desconto atribuído e quantidade mínima.

Pontos positivos
• Os grupos ficaram bem equilibrados por construção: as distribuições de volume, faturamento e desconto histórico se sobrepõem entre controle e tratamento em todos os recortes;
• A partir da discussão realizada na reunião, o desenho evoluiu ao permitir medir, além da conversão, o volume/uplift flexibilizando a quantidade máxima. Isso responde à pergunta de negócio de forma mais completa do que apenas 'quantos bares aceitam a oferta'.
• A independência entre o desconto atribuído e a quantidade mínima (Qmin) foi verificada e confirmada, garantindo que o efeito do desconto não fique confundido com o tamanho do pedido.
Pontos de atenção O desenho e amostra já está pronto e validado, porém a liberação do orçamento para subir o experimento ainda não foi disponibilizada. A execução dos próximos passos depende dessa liberação.
Outros Cards Complementares Além das atividades épicas entregues nessa sprint, outras atividades complementares foram realizadas e funcionaram como suporte:
• Análise de dados do segmento BAR (backtest): atividade que serviu como pré-requisito para a construção do design de experimento BAR e que foi apresentada para o time de Revenue.
• Atualizações de notebooks de outros experimentos: atividade que serviu para atualizar a adaptar o notebook para os experimentos atuais, onde foram entregues quatro notebooks: dois para cada um dos designs de experimento desenhados (Flexibilização do Qmaxe Desconto Bar).
4.2. Promo Por Objetivo - Arquitetura e Documentação Responsável: Nicolas De Oliveira Lopes Braga Foi criada a documentação do Promo Por Objetivo para propor a arquitetura ideal de comunicação entre os times, definindo formas de envio e processamento dos dados. A necessidade veio do grande volume de dados que o processo pode movimentar, o que exige um desenho de integração bem definido desde o início.
 Documentação: Documentação de Arquitetura - Promo por Objetivo.loop 📄

4.3. Promo Removal (Cerveja) - Ajustes e Bugs Responsável: Nicolas De Oliveira Lopes Braga Durante a sprint foram tratados bugs de remoção indevida e ajustes de regra no Promo Removal, a partir de apontamentos das GEOs e validações internas.
Bug 1 - Reason 12: Qtd. mínima do SKU > média semanal do PDV Problema: Promoção removida pela Reason 12 com mínimo de 95 cxs para um cliente com média semanal de 84 cxs (cliente
628662_10998, promoção UNT-27538589). A referência usada foi a sugestão 1 do modelo de Volume (106 cxs), sem o desconto de
80%, o que gerou a remoção.
Solução / encaminhamento:
• Alinhado aplicar os 80% também sobre a menor sugestão do modelo.
• Validada a hipótese de usar a média do PDV no lugar da sugestão do modelo, mas em conjunto pegar o menor valor entre a média e sugestão do modelo.
• Em avaliação: não aplicar a Reason 12 quando a promoção for Smart Promo, já que Smart Promo não deveria ser removido pelo Removal. Acompanhamento pós-PR definido como DoD.
Bug 2 - Janela de histórico divergente entre modelo e regra manual Problema: O modelo de Volume usa o histórico dos últimos 2 anos do PDV, enquanto a regra manual avalia apenas os últimos 91 dias, removendo indevidamente PDVs com comportamento recente diferente.
Solução: Usar o modelo de Volume como input principal para a remoção de quantidade mínima e recorrer à regra manual apenas quando não houver correspondência. As descrições das Reasons 3 e 12 e novos exemplos foram adicionados ao sumário de regras.
[23.06.2026] Promo Removal CERVEJA - Sumário das Regras de Ineficiências.loop 📄 Bug 3 - Reason 7 removendo a promoção com maior desconto Problema: Promoções de cobertura da GEO SP com desconto percentual mais atrativo estavam sendo removidas pela Reason 7 (duplicadas com menor desconto), mantendo no Bees a de menor desconto.
Solução: Ajuste para considerar o desconto percentual no ranking e correção do cast do valor, que estava como string e afetava o row number.
Bug 4 - Cobertura de clientes estáveis não enviada para remoção Problema: A partir de apontamento da EDR da GEO SP, promoções de cobertura de clientes estáveis não estavam sendo removidas. A causa foi o filtro não considerar todas as promoções com "coverage" na coluna tags, classificando-as como volume e deixando de aplicar a regra de estabilidade.
Solução: Substituição de "Business Rules Coverage V1" por "Coverage" no filtro.
Bug 5 - Cobertura com max_sku = 1 removida pelas Reasons 3 e 12 Problema: A promoção UNT-29611492 (unb_pdv 546_9245, SKU 18836, máx. 1 cx) foi removida pelas Reasons 3 e 12, que não se aplicam a cobertura. Mesma causa-raiz do Bug 4: classificação incorreta como volume por falha no filtro de tags.
Solução: Substituição de "Business Rules Coverage V1" por "Coverage" no filtro.
4.4. Promo CORA - Correção de recebimento e reprocessamento Responsável: Nicolas De Oliveira Lopes Braga Problema: As iniciativas INI-68451 e INI-68454 retornavam vazias na tabela cora_promocoes_hist_mensal. Identificou-se um gap de leitura das filas do ECO entre 23:50 e 00:00, em que promoções enviadas nesse intervalo não eram recebidas.
Solução:
• Ajuste do timer para reduzir o gap de leitura (pendente alinhar com a Brewdat a correção do conector, pois uma falha na

última execução do dia ainda pode gerar perda de dados).
• Resync das INIs faltantes em DEV e, após validação, merge para PROD.
• No deploy houve falha no CI/CD da Brewdat, que subiu o notebook novo mas manteve a escrita anterior (overwrite).
Corrigido com um PR recuperando versões anteriores ao problema e refazendo o merge das bases corretas.
4.5. Promo Removal de Combos - Discovery e Alinhamento Responsável: Nicolas De Oliveira Lopes Braga O planejado era o alinhamento e desenvolvimento da arquitetura com o CORA, mas como o time ainda não estava por dentro do processo, as tasks de desenvolvimento foram canceladas e repriorizadas para a próxima sprint. Nesta sprint foram feitos o discovery das bases e uma reunião de alinhamento de arquitetura e priorizações.
Definições da reunião com o CORA:
• Priorizada a evolução do Smart Promo (a remoção direta passa para o lado deles e atuaremos apenas nas duplicadas).
• Em paralelo, o CORA iniciará a sinalização e remoção direta também para o Cadastro Manual de Promos.
• Combos com arquitetura alinhada, mas o desenvolvimento pelo CORA segue travado por falta de capacity. Assim que a base de regras for desenvolvida, será compartilhada para darem noção do que vem.
• Promo Por Objetivo ainda será alinhado entre Yanca e Ellen.
Arquitetura acordada: enviar a base via ECO (avaliar volumetria) pela Brewdat, junto das bases auxiliares necessárias, permitindo tanto a sinalização quanto a remoção direta.
4.6. Promo Removal - Subir PR do Pedido Agendado Responsável: Nicolas De Oliveira Lopes Braga Problema: Por conta do freezing, a nova ineficiência de pedido agendado não havia sido deployada para PROD. Além disso, algumas bases passaram a ser recebidas via processo stream, alterando a estrutura da tabela e descontinuando colunas antes utilizadas.
Solução: Acesso a outras tabelas e ajuste do processo para a nova estrutura. O PR já está aberto e aguardando aprovação para validar o processo em PROD.
4.7. Promo Removal - Recadastro Responsável: Nicolas De Oliveira Lopes Braga Criação do fluxo de recadastro das promoções removidas, um notebook que define quais promoções devem ser recadastradas, adapta os dados para o modelo do Smart Promo (similar ao Promo Suggestion) e salva a base para leitura na etapa de otimização.
Status: Notebook criado e testado em DEV, gerando a base esperada, uma consolidação de tudo o que já foi removido, com informações da promoção (quantidade, desconto, título, vigência etc.) e o reason de cada remoção (já que o CORA não retorna esse campo na base de feedback).
Próxima etapa: Após a aprovação do PR, espelhar a base para uso dentro do processo do Smart Promo na otimização e cadastro, de forma similar ao Promo Suggestion.
4.8. Promo por Objetivo - Elegibilidade e Ranqueamento
4.8.1 Documentação Técnica de Elegibilidade e Ranqueamento Responsável:
[27.07.26] Elegibilidade e Ranqueamento (Cobertura) - Documentação Técnica https://anheuserbuschinbev.sharepoint.com O Promo por Objetivo de Cobertura tem como finalidade identificar oportunidades de expansão de mix nos PDVs por meio de Editado 2dias atrás por Alice Adativa Ferreira Menezes

uma base de recomendações elegíveis e de um mecanismo de priorização capaz de direcionar investimentos promocionais para os casos de maior potencial. A solução é construída sobre as recomendações da General Rank (B2O), complementadas por atributos de produto, cliente e bases táticas, permitindo que as GEOs criem promoções direcionadas de forma escalável e orientada por dados.
Elegibilidade A elegibilidade representa a etapa inicial do processo e tem como objetivo garantir a seleção da melhor base de PDVs e SKUs para ações de cobertura. A construção dessa base combina recomendações da General Rank com filtros de segmentação de produto, cliente e informações táticas.
Na versão atual, o escopo contempla exclusivamente as categorias BEER e MATCH, considerando apenas produtos classificados como NEW ou UNSTABLE, uma vez que produtos estáveis já apresentam recorrência de compra e não contribuem diretamente para a expansão de portfólio.
Os usuários podem segmentar a elegibilidade por atributos como categoria, segmento, família, marca, embalagem, GEO, UF, UNB, perfil comercial, operação, dinâmica primária, score de digitalização, market share, faturamento potencial, disponibilidade de tasks e ofertas de pontos.
Construção da Base de Dados A General Rank constitui a principal fonte da solução, fornecendo recomendações mensais na granularidade PDV–Brand Pack.
Durante o processamento são realizados filtros de qualidade, remoção de duplicidades e tratamentos de dados ausentes, garantindo consistência e disponibilidade para os processos posteriores de priorização.
A base é enriquecida com:
• Informações de produtos, incluindo categoria, segmento, família, marca e atributos de embalagem.
• Informações de clientes, como GEO, perfil comercial, operação e dinâmica primária.
• Score de digitalização, que classifica o nível de engajamento digital dos PDVs.
• Bases táticas, incluindo Tasks de Cobertura, Ofertas de Pontos, Market Share e Faturamento Potencial.
Informação
• Para garantir robustez operacional, a solução possui mecanismos de contingência que utilizam a informação mais recente disponível quando alguma base tática está temporariamente defasada em relação à General Rank.
Após todos os enriquecimentos, os dados são consolidados em uma tabela única de elegibilidade na granularidade UNB–PDV– SKU, que serve simultaneamente como base para filtragem, criação de promoções e priorização das recomendações.
Atualização da Elegibilidade A tabela de elegibilidade é atualizada diariamente. Como mecanismo de proteção contra sobreposição de incentivos, promoções já convertidas e com consumo de orçamento são removidas automaticamente da base elegível durante o mês vigente. Dessa forma, um mesmo PDV-SKU deixa de ser recomendado até que novas oportunidades sejam identificadas pela General Rank em ciclos futuros.
Ranqueamento Após a aplicação dos filtros de elegibilidade, a solução executa um processo de ranqueamento para garantir tanto uma distribuição saudável de promoções por PDV quanto a melhor utilização do orçamento disponível. O mecanismo opera em duas camadas:
• Ranqueamento Intra PDV: Responsável por controlar o volume de promoções dentro de cada PDV. O corte é realizado utilizando as colunas pn_priority e pn_tasks, mantendo apenas recomendações cuja prioridade esteja dentro do limite ideal definido para aquele estabelecimento (pn_priority ≤ pn_tasks).
• Ranqueamento Inter PDV:Responsável pela priorização global das promoções elegíveis quando existe restrição orçamentária. A ordenação ocorre primeiramente por score_coverage_qualitye, em casos de empate, por

score_final, ambos em ordem decrescente.
Pontos Positivos
• A solução de Cobertura estabelece uma camada estruturada de seleção e priorização de oportunidades promocionais, combinando inteligência da General Rank, segmentação de clientes e produtos, sinais táticos de execução e mecanismos de ranqueamento em tempo real. O resultado é uma base elegível consistente, capaz de direcionar investimentos promocionais para os PDVs e SKUs com maior potencial de expansão de distribuição e geração de valor para o negócio.
Pontos de Atenção
• Dependência do time de desenvolvimento do CORA para criar o produto na plataforma oficial.
Próximos Passos
• Desenvolver a etapa de curva de orçamento e meta de distribuição.
• Integrar a solução das curvas com a elegibilidade.
• Integrar o produto final no CORA.
4.8.2 Criação de Dashboard para MVP com as GEOs Responsável:
A disponibilização da solução para as GEOs ocorre por meio de um dashboard que consome diretamente a tabela final de elegibilidade. Todos os filtros são carregados dinamicamente com base nos dados disponíveis, permitindo a construção de promoções altamente segmentadas e alinhadas às estratégias comerciais, operacionais e táticas da companhia.
O dashboard permite:
• Filtrar PDVs e produtos elegíveis.
• Aplicar restrições por perfil comercial.
• Utilizar atributos táticos como Tasks, Ofertas de Pontos, Market Share e Faturamento Potencial.
• Visualizar a base resultante já preparada para o processo de ranqueamento.
Databricks - Sign In https://adb-1820723078635205.5.azuredatabricks.net/dashboardsv3/01f185f5dacf1011b0dcf927af8b5b94/published?o=1820723078635205 Um glossário para cada filtro também foi criado para melhor entendimento dos stakeholders.
[05.08.2026] Glossário de Filtros do Dashboard.pdf https://anheuserbuschinbev-my.sharepoint.com/:b:/g/personal/alice_menezes_ambevtech_co… Próximos Passos Document last modified by Alice Adativa Ferreira Menezes at 8/5/2026 7:55:28 PM

• Acompanhar a utilização das GEOs e aplicar melhorias sob demanda.
4.9. Otimizador de Cobertura - Monitoramento em Produção e Correção de BUG Responsável:
Monitoramento da Tabela de Orçamento Após a ocorrência do BUG na tabela de orçamentos listada na review da S1-Q3-26 (seção 4.2), nessa sprint passamos a monitorar o otimizador de cobertura em produção para analisar a efetividade da correção. Inicialmente, foram analisados aleatoriamente cerca de 100 INIs e verificamos que a correção da tabela foi efetiva. Nessa análise, apenas cerca de 5 orçamentos estavam com divergência, mas o que acontecia em todos eles é que a INI não estava mais ativa, parava de ser atualizada na tabela, e depois faziam a retirada do valor e essa retirada não era persistida.Como o boosting atua em INIs ativas, essa questão não afeta a solução.
Ajuste no Pipeline de Features do Modelo - Descomissionamento de Tabela Foi atualizada a fonte de dados de IDs de usuários (tabela utilizada em conjunto com as tabelas de behavior). A fonte de informações do usuário vinha da brewdat_uc_saz_iris_prod (obsoleta/descontinuada). A partir de agora, a fonte de informações do usuário vem dabrewdat_uc_saz_prod.
https://github.com/BrewDat/brewtiful/pull/28954 https://github.com/BrewDat/brewtiful/pull/28954 Próximos Passos
• Manter o monitoramento em Agosto.
• Adicionar novo canal de notificações no pipeline.
4.10Revisão dos Indicadores de Share de Promoções Atividade – Correção e padronização dos indicadores de Share de Consumo e Share de Cadastro Responsável: Daniel Barreto Barboza Silva Após a identificação de inconsistências nos resultados apresentados pelos indicadores de Share de Promoções, foi realizada uma análise detalhada das regras de negócio, fontes de dados e classificações utilizadas nos processos de cálculo. No indicador de Share de Consumo, foram executadas adequações estruturais, incluindo a migração da fonte de aderência TTV do ambiente IRIS para a tabela br_aderencia_ttv, revisão da referência temporal utilizada nos cálculos, substituindo a data de emissão da nota pela data do pedido, além da atualização das regras de classificação das promoções e inteligências. Também foi realizada a inclusão da coluna unique_key para aumentar a assertividade das classificações e a padronização dos usuários e categorias utilizadas nos indicadores. Para o indicador de Share de Cadastro, foram efetuadas correções nas classificações históricas, remoção de identificadores obsoletos e atualização das regras de categorização utilizando a unique_key como referência principal para classificação das promoções de inteligência. Durante as validações foi identificado um volume de promoções sem classificação adequada. Para investigação da causa raiz, foi criado um grupo de trabalho envolvendo os times responsáveis, centralizando a análise da origem dos dados de aderência. As análises realizadas até o momento apontam que a inconsistência está relacionada ao arquivo de origem fornecido pelo GPRO, que está sendo tratado em conjunto com o time de Sales Lab.
Pontos Positivos
• Correção das regras de negócio dos indicadores de Share de Consumo e Share de Cadastro.
• Migração da fonte de aderência para estrutura mais atualizada e aderente ao processo.
• Melhoria da qualidade das classificações através da utilização da unique_key.

• Padronização das categorias e usuários, reduzindo inconsistências nos relatórios.
• Criação de notebook para execução manual do Share de Consumo em períodos específicos.
• Identificação e direcionamento da causa raiz das promoções sem classificação.
Pontos de atenção
• Persistem registros de promoções sem classificação devido a inconsistências identificadas na origem dos dados do GPRO.
• Necessidade de acompanhamento contínuo junto ao time de Sales Lab para validação das correções na source de aderência.
Próximos Passos
• Concluir a investigação da origem das promoções não classificadas junto ao time de Sales Lab.
• Validar a correção dos arquivos de origem fornecidos pelo GPRO.
• Monitorar a estabilidade e consistência dos resultados dos indicadores nas próximas execuções.
4.11Migração de Inputs Manuais para BrewDat Atividade – Migração dos processos Smart Promo, Promo Sorting, Dados Climáticos e Coleta TTC Responsável: Daniel Barreto Barboza Silva Foi realizada a migração dos inputs manuais dos processos Smart Promo, Promo Sorting, Dados Climáticos e Coleta TTC para a BrewDat, incluindo preservação dos históricos, atualização dos processos consumidores e adequação dos caminhos de entrada.
As alterações foram validadas por meio de PRs e acompanhadas de comunicação aos times responsáveis sobre o descomissionamento das estruturas legadas. Também foi realizado alinhamento com o time de Sales Lab para definição do fluxo futuro de cargas manuais do processo Coleta TTC.
Pontos Positivos
• Migração dos inputs manuais concluída com sucesso para a BrewDat.
• Históricos preservados durante a transição dos processos.
• Processos e transformações atualizados para a nova estrutura.
• Comunicação de descomissionamento realizada com os times impactados.
• Definição do fluxo operacional para futuras cargas manuais.
Pontos de atenção
• Garantir a atualização dos paths e utilização exclusiva da nova estrutura pelos times consumidores.
Próximos Passos
• Concluir o descomissionamento das estruturas legadas.
4.12Demais Atividades e Interferências

Responsável: Daniel Barreto Barboza Silva Durante a sprint, foi realizado o envio manual da ordenação do Promo Sorting para a Rota Global, contemplando três PDVs da UNB 401 e promoções da categoria Beer. Para viabilizar a entrega, foi desenvolvido um notebook para processamento e envio dos dados, executando o fluxo com sucesso. O incidente foi reportado ao time responsável pelo BEES BR, que informou a disponibilização de uma nova versão da API no BEES Sync. Também foi investigada uma inconsistência nos indicadores do Promo Suggestion, sendo identificada uma regra incorreta na classificação da inteligência de promoções. A correção permitiu evitar que promoções de experimentos de volume fossem classificadas indevidamente como Suggestion. Adicionalmente, foi realizado o mapeamento das iniciativas de migração do Material Sync, com registro dos escopos, decisões e próximos passos no documento de acompanhamento da Sync. Por fim, foi executado o processamento do Promo Suggestion Q1 para validação do negócio.
Devido à indisponibilidade temporária do ambiente de desenvolvimento do Airflow, as validações foram realizadas via Workspace, com geração do path em desenvolvimento e encaminhamento para homologação da área responsável.
Próximos Passos
• Acompanhar a disponibilização da nova versão da API do BEES Sync para o Promo Sorting
5 Reconhecimentos Espaço para reconhecer contribuições relevantes de membros do time durante a sprint.
Pessoa Reconhecimento Contexto
1 Ingrid Rocha, Yan Melhoria no processo de criação de bugs Cards do Removal com todas as informações necessárias facilitando a investigação e solução do problema.
2 Leonardo Salvi Documentação dos cards e criação de assistente de escrita da review Aprimorou a documentação de atividades realizadas nos cards e criou um assistente para documentar a review com as atividades do desenvolvedor e os QAs realizados por ele.
3 Yanca Lima Parceria nas adversidades Com as férias do Gabriel e um número elevado de interferências e bugs, principalmente em engenharia, a parceria da Yanca foi essencial para que o time entregasse as atividades prioritárias e os deliverables.
4 Nicolas Braga, Daniel Barboza e Leonardo Salvi Resiliência em meio às interferências e bugs Ao longo da sprint, foram cadastrados 13 cards de interferências/não planejados e bugs, mas o time foi resiliente, resolveu os problemas e entregou os deliverables planejados.
5 Alice Nova DM suplente Alice recebeu o desafio de liderar a squad durante 20 dias, e está mandando super bem. Recebeu diversas demandas e "mensagens no teams" e ajudou muito.

6 Ayrton Sentimento de Dono Ayrton construiu a análise de desconto nos bares com muita excelência. Além do paper gabarito, a apresentação em 30min para os stakeholders foi muito positiva.
7 Jonathan Liderança por exemplo Jonathan toca todos alinhamentos e dúvidas e protagoniza nos produtos de preços Ao time de engenharia, entramos em um TRI de geração de MUITO valor Em Julho, aceleramos algumas frentes de melhorias nos produtos para exponenciar a usabilidade do usuário e implementar novas features, unindo as iniciativas de Digital Insights + CORA.
Área Produto Dono Área Status Observaçõ es
1 COMBOS COMBOS INTERCAMBIÁVEIS Daniel CORA + BEES :
: Concluí do Lançamento em Julho/26
2 COMBOS SORTING Daniel DIGITAL INSIGHTS + BEES :
: Concluí do Lançamento em Maio/26
3 COMBOS REMOVAL Nicolas DIGITAL INSIGHTS + REVENUE + BEES : : Em andamen to Lançamento Agosto/26
4 REMOVAL REMOVAL NAB e MATCH Nicolas DIGITAL INSIGHTS + BEYOND :
: Concluí do Lançamento Julho/26
5 REMOVAL HORÁRIO REMOVAL Nicolas / Daniel DIGITAL INSIGHTS :
: Concluí do De 1x para 3x ao dia
6 SORTING SORTING MKTPLACE Daniel DIGITAL INSIGHTS + BEES + AUDIENCE :
: Concluí do Despriorizaçã o do mktplace no sorting Ajuste em Julho/26
7 SORTING HORÁRIO SORTING Daniel DIGITAL INSIGHTS + REVENUE : : Em andamen to De 1x para 3x ao dia
8 SMART PROMO HORÁRIO Daniel e Nicolas DIGITAL INSIGHTS :
: Concluí do De 3x para 6x ao dia
