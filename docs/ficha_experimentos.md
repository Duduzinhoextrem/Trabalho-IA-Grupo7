# Ficha de experimentos

Os resultados abaixo vêm de `data/experiments/scientific_experiments_v2.json`. O snapshot é `srd-2014-v1.0.0` e as regras são `balance-v1.0.0`. Os gráficos estão em `results/experiments_v2/`.

A versão anterior foi preservada, mas contabilizava incorretamente o orçamento: o AG preservava elites sem reavaliá-las e, com a configuração anunciada como 240 avaliações, realizou 218; na busca aleatória foram 240. A versão atual conta avaliações efetivas, permite uma última geração parcial e usa 240 avaliações em cada execução dos métodos de busca.

As sementes 101–105 são usadas na otimização; 201–210 são usadas na validação; 301–310 são usadas no cenário de composição alternativa. A estratégia individual apresentada no experimento 4 foi escolhida pelo desempenho no treino. O conjunto de validação é reutilizado entre experimentos: isso limita sua independência se ele orientar ajustes posteriores do grupo.

A métrica principal é a média de salas concluídas. A taxa de conclusão das 100 salas é mostrada à parte. Vida e ouro participam do desempate no fitness. Os desvios das tabelas de mutação e população são calculados sobre as médias das repetições; eles não são o desvio de todas as batalhas individuais.

## E1 — Taxa de mutação

**Hipótese:** taxas diferentes afetam diversidade, convergência e desempenho. A hipótese inicial de que 10% ofereceria o melhor equilíbrio precisa ser confrontada com os dados.

Foram realizadas cinco repetições para cada taxa, com população inicial de 20 e 240 avaliações efetivas por repetição. A última geração pode ser parcial.

| Mutação | Média de salas na validação | Taxa média de conclusão | Diversidade final média |
| --- | ---: | ---: | ---: |
| 2% | 91,28 ± 3,31 | 28% | 0,0346 |
| 10% | 92,12 ± 3,42 | 20% | 0,0510 |
| 25% | 95,06 ± 2,02 | 36% | 0,1104 |

**Interpretação:** nesta execução, 25% teve a maior média de salas e maior taxa média de conclusão entre as configurações testadas. Isso não comprova que 25% será melhor em outras regras ou sementes. A diversidade final considera apenas os indivíduos avaliados da última geração, que pode estar incompleta.

## E2 — Tamanho da população

**Hipótese:** com o mesmo orçamento, mudar a quantidade de estratégias por geração altera o comportamento da busca. Foram feitas cinco repetições por configuração e 240 avaliações efetivas por execução.

| População | Gerações avaliadas | Média de salas na validação | Taxa média de conclusão |
| --- | ---: | ---: | ---: |
| 12 | 24 | 86,28 ± 5,63 | 18% |
| 20 | 14 | 86,82 ± 3,58 | 20% |
| 40 | 7 | 89,56 ± 3,43 | 20% |

**Interpretação:** a população de 40 teve a maior média de validação entre as três configurações nesta amostra. As últimas gerações são parciais e a diversidade final reflete apenas os indivíduos avaliados; o resultado não demonstra que populações maiores sejam sempre melhores.

## E3 — Comparação com referências

**Hipótese:** a busca genética pode encontrar estratégias competitivas em relação à estratégia fixa e à busca aleatória. Busca aleatória e AG tiveram sete repetições de 240 avaliações; a regra fixa foi avaliada sem busca.

| Método | Média de salas no treino | Média de salas na validação | Taxa média de conclusão na validação |
| --- | ---: | ---: | ---: |
| Estratégia fixa | 79,20 | 69,00 | 0,00% |
| Busca aleatória | 95,11 ± 0,97 | 92,27 ± 4,16 | 25,71% |
| Algoritmo genético | 96,09 ± 1,04 | 91,27 ± 4,11 | 28,57% |

As médias e desvios da busca aleatória e do AG resumem as sete médias de cada repetição. Cada repetição foi avaliada nas mesmas dez sementes de validação; a estratégia fixa foi avaliada uma vez nessas dez sementes. As diferenças entre os métodos são observações desta configuração, não uma garantia de superioridade.

A estratégia do AG selecionada no treino obteve média de 98,2 salas no treino e 96,9 na validação. Nas dez sementes de validação ela concluiu 100 salas em **4 de 10 tentativas (40%)**. Essa estratégia individual não deve ser confundida com a média das sete repetições.

## E4 — Novos cenários

**Hipótese:** alterar a composição dos encontros, a dificuldade ou os baús pode reduzir o desempenho da estratégia selecionada. Não houve novo treino nos cenários.

| Cenário | Sementes | Média do AG | Média da regra fixa | Conclusão do AG |
| --- | --- | ---: | ---: | ---: |
| Treino | 101–105 | 98,2 | 79,2 | 60% |
| Validação padrão | 201–210 | 96,9 | 69,0 | 40% |
| Composição alternativa | 301–310 | 94,4 | 74,9 | 20% |
| Dificuldade +15% | 201–210 | 73,4 | 51,4 | 10% |
| Sem baús | 201–210 | 80,0 | 61,1 | 20% |

**Interpretação:** o desempenho da estratégia selecionada caiu nos cenários mais difíceis e sem baús. As comparações usam as mesmas sementes e regras de cenário, mas trajetórias diferentes podem consumir a sequência aleatória de forma diferente. Os resultados não isolam, por si só, uma causa única para cada diferença.

## Três situações para discutir na apresentação

Os casos abaixo foram reproduzidos com a estratégia selecionada do `v2` e a configuração de combate versionada. A sala indicada é a que encerrou a tentativa; o total de salas concluídas é uma unidade menor.

1. **Semente 201, dificuldade +15%:** o guerreiro concluiu 24 salas e morreu na sala 25 contra `Black Pudding`. A regra fixa concluiu 25 salas no mesmo cenário. É um caso em que a estratégia selecionada não foi a melhor das duas.
2. **Semente 209, sem baús:** concluiu 25 salas e morreu na sala 26 contra `Succubus/Incubus`. Nesse registro estava com arma nível 2, escudo nível 1 e sem armadura. Isso descreve o estado observado, sem provar que uma única compra teria mudado o resultado.
3. **Semente 308, composição alternativa:** concluiu 78 salas e morreu na sala 79 contra `Adult Red Dragon`. Nas salas 77 e 78 a vida após recuperação caiu de 372 para 332, antes do encontro final. Isso ilustra a influência do desgaste em uma sequência de combates.

Também é possível discutir a perda de diversidade, a diferença entre treino e validação, a dependência das regras e as prioridades de aliados registradas no JSON. Prioridade de contratação não é o mesmo que contratação efetiva em todas as partidas.
