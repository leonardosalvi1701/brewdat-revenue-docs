---
documento: outputs/sprint-review-S5-Q3-26-REVENUE-DI-leonardo-luis-machado-salvi.md
versao: revisao (sprint encerrada; cards transbordados consultados em S1-Q4)
data: 13/10/2026
revisores: [Leonardo Luis Machado Salvi]
rodada: 2
---

# Log de revisao

Revisao do paper da S5-Q3-26 a partir da correcao do autor e dos comentarios
dos cards consultados no snapshot da S1-Q4-26.

| # | Secao | Problema observado | Correcao aplicada | Aprendizado para os agentes |
|---|---|---|---|---|
| 1 | 4.1 e 4.2 | A produtizacao do modelo de desconto foi omitida, e sua continuidade foi confundida com o acompanhamento da migracao do modelo de quantidade. | Separadas as etapas de features/treino e predict/serving do modelo de desconto da migracao do modelo de quantidade ja existente. | Mesmo framework ou Monorepo nao significa mesma frente. Confirmar modelo e etapa em cada card e manter separados os resultados e bloqueios distintos. |
| 2 | 4 | Cards ativos no fechamento da S5 nao estavam no snapshot original porque foram transbordados para S1-Q4. | Consultado o snapshot seguinte e incluida a fonte adicional no frontmatter. O texto descreve o estado ate 02/10 e distingue o andamento posterior. | Para explicar transbordo, consultar a sprint seguinte e reconstruir o estado na data de fechamento. Comentario posterior nao prova conclusao na sprint anterior. |
| 3 | 4.2 | O acompanhamento da migracao do modelo de quantidade podia parecer autoria da migracao em si, em vez de validacao e suporte ao time responsavel. | Reenquadrada a atividade como acompanhamento e validacao; a execucao da DAG fica como evidencia do resultado. | Distinguir quem implementou/migrou de quem acompanhou, validou ou deu suporte, conforme o card e a memoria do autor. |
| 4 | 4.3 | O apoio a Ayrton para avaliar a R3 foi misturado com atividades rastreadas, embora nao houvesse card proprio e a demanda nao estivesse planejada. | Mantido como atividade separada, identificada como nao planejada e sem card dedicado, com a transcricao do autor como fonte do esforco. | Nao atribuir apoio sem card ao card de quem recebeu ajuda; diferenciar trabalho nao planejado de card transbordado. |
| 5 | 4.4 | O paper menos tecnico do modelo de desconto, concluido em S5, e o complemento feito apos a revisao de negocio ficaram indistintos. | Registrada a conclusao do paper em 29/09 e a complementacao posterior da secao de Q&A em 08/10. | Documentacao e entrega; registrar progresso na sprint e datar complementos posteriores sem atribui-los ao periodo anterior. |
| 6 | 4.2 | A imagem da DAG precisava permanecer ligada a migracao do modelo de quantidade, sem ser usada como evidencia da produtizacao do modelo de desconto. | Mantida a figura sob a atividade de acompanhamento da migracao do modelo de quantidade, com legenda especifica. | Conferir visualmente cada anexo contra a atividade, o produto e a data da legenda. |

## Decisoes incorporadas aos padroes

- `contracts/estilo-sprint-review.md`: separacao de frentes e etapas, tratamento
  de transbordo e trabalho sem card, documentacao como atividade, rastreio
  temporal e conferencia das imagens.
- `templates/sprint-review.md`: orientacao para descrever atividades
  transbordadas e trabalho nao planejado sem card.
- `agent_instructions/papeis/escritor-sprint-review.md`: consulta de snapshot
  posterior, separacao entre transbordo e nao planejado, rastreabilidade de
  imagem e documentacao.
- Rubricas dos revisores: criterios para detectar frentes fundidas, estado
  temporal impreciso e imagem associada a atividade errada.
