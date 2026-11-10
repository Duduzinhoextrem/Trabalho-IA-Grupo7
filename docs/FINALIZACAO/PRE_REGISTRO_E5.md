# Pré-registro do experimento adicional E5 (10 de novembro de 2026)

Este arquivo foi escrito **antes** de executar o E5. O objetivo é impedir que hipótese, métrica ou conjunto de sementes sejam escolhidos depois de ver o resultado.

## Motivo

Nos experimentos `v2`, o AG usou mutação de 10% na comparação principal com a busca aleatória (E3). No E1, a taxa de 25% obteve a maior média de validação. A diferença pode ser acaso: o E1 teve apenas cinco repetições por taxa, e o conjunto de validação 201–210 foi reutilizado em vários experimentos. O E5 testa essa dúvida em sementes que nunca foram usadas.

O E5 **não substitui nem altera** `scientific_experiments_v1.json` ou `scientific_experiments_v2.json`.

## Hipóteses

- **H1:** o AG com mutação de 25% terá média de salas igual ou maior que o AG com 10% em masmorras novas.
- **H2:** o AG (10% e 25%) terá média de salas igual ou maior que a busca aleatória com o mesmo orçamento.
- Nenhuma das hipóteses é dada como verdadeira. Se os dados não sustentarem, o resultado será registrado como negativo ou inconclusivo.

## Configuração (fixada antes da execução)

| Item | Valor |
| --- | --- |
| Métodos | AG com mutação 10%, AG com mutação 25%, busca aleatória |
| Orçamento | 240 avaliações efetivas por repetição, nos três métodos |
| População do AG | 20; elitismo 2; torneio 3; cruzamento 0,85 (parâmetros padrão do código) |
| Sementes de treino | 101–105 (as mesmas dos experimentos anteriores) |
| Sementes de validação | **401–420** (20 masmorras nunca usadas em nenhuma otimização, escolha ou análise) |
| Repetições | 10 por método |
| Sementes das repetições | AG 10%: 5100 + 41·i; AG 25%: 5200 + 41·i; busca aleatória: 5300 + 41·i, com i = 0…9 |
| Dados e regras | `srd-2014-v1.0.0` e `balance-v1.0.0` (sem alteração) |
| Métrica principal | média de salas concluídas nas 20 masmorras de validação (média por repetição) |
| Métricas secundárias | taxa de conclusão das 100 salas; média no treino |
| Testes | Mann-Whitney bilateral entre métodos; intervalo de confiança bootstrap (10 000 reamostragens) para a diferença de médias |
| Critério de interpretação | com 10 repetições, diferenças com p ≥ 0,05 ou intervalo que inclui zero serão descritas como **não conclusivas** |

## Como reproduzir

```bash
python scripts/run_extra_mutation_experiment.py
```

Saída: `data/experiments/extra_mutation_e5_v1.json`.

## O que o E5 não responde

Não indica o melhor hiperparâmetro em geral. Mede apenas 10 repetições de um orçamento pequeno (240 avaliações) em um simulador específico.
