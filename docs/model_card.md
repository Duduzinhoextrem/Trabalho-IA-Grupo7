# Model Card — Masmorra Genética

**Solução:** busca de estratégias de evolução para um guerreiro em uma masmorra simulada de 100 salas.

**Objetivo e público:** demonstrar algoritmos genéticos para estudantes e visitantes, além de apoiar a investigação acadêmica do Grupo 7. Não é um modelo preditivo treinado com partidas de jogadores.

**Técnica:** algoritmo genético próprio com cromossomos de 16 valores, seleção por torneio, cruzamento, mutação, elitismo e controle de diversidade. Cada política é testada por um motor de combate compartilhado.

**Dados:** 334 registros de criaturas fictícias da D&D 5e SRD API, coletados em 29/10/2026 e congelados como `srd-2014-v1.0.0`. O manifesto contém origem, licença, atribuição e hash. Os combates são simulações criadas pelo projeto.

**Preparação:** validação de campos, normalização de estruturas aninhadas e cálculo de estimativas de dano. Quatro formas passivas são retiradas do pool de combate. Quando o dano não é identificado, aplica-se uma estimativa própria. As fórmulas estão em `src/game/monsters.py` e `config/balance.json`.

**Variáveis:** distribuição de atributos, prioridade de aliados, evolução dos aliados e decisões de compra e reserva. As criaturas são selecionadas considerando, entre outros dados, nível de desafio e atributos adaptados.

**Métricas:** média de salas concluídas e taxa de conclusão de 100 salas. Vida e ouro são usados como critérios secundários.

**Busca interativa:** além dos experimentos científicos, a aplicação pode procurar uma estratégia que vença as 100 salas de uma masmorra escolhida. Essa masmorra participa da otimização, portanto o resultado nela não é uma avaliação independente; as rodadas têm limite e podem ser continuadas.

**Resultados `v2`:** em sete repetições, o AG obteve média de 91,27 salas na validação e taxa média de conclusão de 28,57%; a busca aleatória obteve 92,27 e 25,71%; a regra fixa obteve 69,00 e 0%. Cada repetição dos métodos de busca teve 240 avaliações efetivas. O resultado individual da estratégia selecionada no treino foi 96,9 salas e 40% de conclusão nas dez sementes de validação. Consulte a ficha para detalhes e limites.

**Limitações e vieses:** os dados, as fórmulas de adaptação, os custos e as regras do simulador influenciam as estratégias; cinco sementes de treino e dez de validação não representam todos os cenários. A validação é reutilizada entre experimentos. A maior frequência de uma classe nas prioridades não prova que ela seja universalmente melhor ou que tenha sido contratada em todas as partidas.

**Quando não usar:** não usar os resultados para prever partidas reais, tirar conclusões sobre jogadores, afirmar que existe uma estratégia ótima universal ou substituir testes em outro jogo ou sistema de regras.
