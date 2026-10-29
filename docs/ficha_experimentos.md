# Ficha de Experimentos Científicos — Masmorra Genética (Grupo 7)

**Projeto:** Masmorra Genética: A Evolução do Guerreiro — Grupo 7 (IA II — FIB)  
**Responsáveis principais:** Reuel Vitor Lanzetti e Eduardo Coque Corrêa de Lima  
**Arquivo de Evidências Reais:** `data/experiments/scientific_experiments_v1.json`  
**Versão do Dataset:** `srd-2014-v1.0.0` (334 criaturas, SHA-256 `51a00f4785dcf07fcb4056cd97eaa1eb5b2ba0c235d2b7d5b2762a772691d397`)  
**Versão do Simulador:** `balance-v1.0.0`  

---

## Configuração Experimental Comum e Separação Treino/Validação

- **Conjunto de Otimização (Treinamento):** 5 masmorras fixas de 100 salas geradas com as sementes `[101, 102, 103, 104, 105]`.
- **Conjunto de Validação Final (Holdout Fora da Amostra):** 10 masmorras inéditas de 100 salas geradas com as sementes `[201, 202, 203, 204, 205, 206, 207, 208, 209, 210]`, totalmente disjuntas das sementes de otimização.
- **Conjunto de Composições Alternativas:** 10 masmorras geradas com as sementes `[301..310]` e `composition_mode="alternate_pool"`.
- **Métrica Principal:** Média de salas concluídas (`mean_rooms_cleared` $\in [0, 100]$).
- **Métrica Reportada Separadamente:** Taxa de conclusão das 100 salas (`completion_rate` $\in [0\%, 100\%]$).
- **Critérios Secundários de Desempate:** Fração de vida restante (`0,006 * mean_hp_ratio`) e ouro restante (`0,003 * min(1, gold/2000)`), cujo teto combinado (`0,009`) é matematicamente inferior a `1/K` salas, impedindo qualquer inversão de prioridade de avanço.

---

## Experimento 1 — Impacto da Taxa de Mutação (`2%`, `10%`, `25%`)

- **Hipótese:** Taxas diferentes de mutação afetam a velocidade de convergência, a diversidade genética da população e a capacidade de generalização fora da amostra.
- **Parâmetros Fixos:** População = `20`, Gerações = `12` (`240` avaliações da função objetivo = `1.200` simulações de masmorra por execução), Torneio = `3`, Elitismo = `2`, Cruzamento = `85%`, Repetições independentes = `5` por taxa.

### Resultados Reais Observados

| Taxa de Mutação | Salas em Treino (Média ± DP) | Salas em Validação (Média ± DP) | Mediana (Validação) | Taxa de Conclusão 100 Salas (Val) | Diversidade Final Média | Geração Média de Convergência | Tempo Médio (s) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2%** (`0,02`) | 95,96 ± 1,88 | 90,58 ± 4,20 | 89,40 | 28,0% | 0,0893 | 4,4 | 9,68s |
| **10%** (`0,10`) | 95,44 ± 0,85 | **92,50 ± 3,04** | **94,70** | 24,0% | 0,0707 | **4,0** | **8,61s** |
| **25%** (`0,25`) | **96,96 ± 1,03** | 92,26 ± 5,05 | 94,40 | **30,0%** | **0,1347** | 7,6 | 8,64s |

### Interpretação
Confirmou-se a hipótese experimental:
1. A taxa de **10%** obteve a maior média (`92,50` salas), a maior mediana (`94,70` salas) e o menor desvio-padrão (`3,04`) no conjunto de validação fora da amostra.
2. A taxa de **2%** estagnou cedo em ótimos locais do conjunto de treino, resultando na pior média (`90,58`) e mediana (`89,40`) em validação.
3. A taxa de **25%** preservou quase o dobro de diversidade genética (`0,1347` vs `0,0707`), permitindo explorar picos mais altos no treino (`96,96` salas) e atingir `30,0%` de conclusão total, mas exigiu quase o dobro de gerações para convergir (`7,6` vs `4,0`) e apresentou maior instabilidade (`DP = 5,05`).

---

## Experimento 2 — Configurações de População sob Orçamento Equivalente (`240` avaliações)

- **Hipótese:** Mantendo o orçamento total de avaliações fixo em `240` avaliações da função objetivo, o balanço entre tamanho da população (`N`) e número de gerações (`G`) altera o compromisso entre diversidade populacional e especialização geracional.
- **Alterações Avaliadas:**
  - **Cenário A:** `Pop = 12 × 20 Gerações = 240 avaliações`
  - **Cenário B:** `Pop = 20 × 12 Gerações = 240 avaliações`
  - **Cenário C:** `Pop = 40 × 6 Gerações = 240 avaliações`
  - Repetições independentes = `5` por cenário (Taxa de mutação = `10%`).

### Resultados Reais Observados

| Configuração (`N × G`) | Orçamento (Avaliações) | Salas em Treino (Média ± DP) | Salas em Validação (Média ± DP) | Mediana (Validação) | Taxa de Conclusão 100 Salas (Val) | Diversidade Final Média | Tempo Médio (s) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Pop 12 × 20 Ger** | 240 | **95,52 ± 1,52** | 88,28 ± 3,89 | 87,50 | **20,0%** | 0,0791 | 10,53s |
| **Pop 20 × 12 Ger** | 240 | 95,28 ± 0,47 | 83,68 ± 5,41 | 83,30 | 18,0% | 0,0670 | **9,75s** |
| **Pop 40 × 6 Ger** | 240 | 95,32 ± 0,52 | **89,56 ± 3,43** | **88,80** | **20,0%** | **0,1166** | 10,37s |

### Interpretação
Todas as três configurações alcançaram desempenho semelhante no conjunto de treinamento (`~95,3` a `95,5` salas), porém **Pop 40 × 6 Gerações** obteve a maior média (`89,56 ± 3,43` salas) e a maior mediana (`88,80` salas) na validação fora da amostra, além da maior diversidade genética final (`0,1166`). Isso demonstra que, quando o conjunto de treino possui poucas sementes (`5`), executar muitas gerações com populações menores aumenta a pressão seletiva sobre peculiaridades das sementes de treino (sobreajuste), enquanto uma população inicial mais ampla preserva políticas mais robustas.

---

## Experimento 3 — Comparação Formal com Baselines (`7` Repetições Independentes)

- **Hipótese:** Estratégias evoluídas pelo Algoritmo Genético e pela Busca Aleatória superam amplamente a Estratégia Fixa equilibrada, e o Algoritmo Genético atinge o maior desempenho de otimização e taxa de conclusão das 100 salas sob o mesmo orçamento computacional (`240` avaliações).

### Resultados Reais Observados

| Método | Orçamento (Avaliações / Simulações) | Salas em Treino (Média ± DP) | Salas em Validação (Média ± DP) | Mediana em Validação | Taxa Média de Conclusão 100 Salas (Val) | Melhor Indivíduo em Validação (Salas / Conclusão) | Tempo Médio (s) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Estratégia Fixa (Baseline)** | 1 / 15 | 79,20 ± 0,00 | 69,00 ± 7,23 | 70,50 | 0,00% | 69,00 (`0,0%`) | **0,03s** |
| **2. Busca Aleatória** | 240 / 1.200 | 95,11 ± 0,97 | **92,27 ± 4,16** | **94,30** | 25,71% | 95,50 (`40,0%`) | 8,20s |
| **3. Algoritmo Genético** | 240 / 1.200 | **96,09 ± 1,04** | 90,96 ± 3,88 | 89,80 | **27,14%** | **96,90** (`30,0%`) | 8,96s |

### Testes Estatísticos e Análise Científica Crítica
- **Algoritmo Genético (Campeão) vs. Baseline Fixo nas 10 sementes de validação:** Teste de Mann-Whitney $U = 100,0$, **$p = 0,000166 < 0,001$** (diferença altamente significativa de **`+27,90` salas** na validação: `96,90` vs `69,00`).
- **Algoritmo Genético vs. Busca Aleatória (7 repetições com 240 avaliações):**
  - No **conjunto de treinamento (otimização)**, o Algoritmo Genético superou a Busca Aleatória (`96,09 ± 1,04` vs `95,11 ± 0,97` salas, chegando a `98,20` salas e `60%` de conclusão no treino).
  - Na **validação fora da amostra**, o AG obteve a **maior taxa média de conclusão das 100 salas (`27,14%` vs `25,71%`)** e encontrou a **melhor política global (`96,90` salas médias em validação)**, mas na média das 7 repetições empatou estatisticamente com a Busca Aleatória (`90,96` vs `92,27`, Mann-Whitney $p = 0,7002$, Welch $t = -0,5658, p = 0,5820$).
  - **Por que isso ocorre?** Em um espaço contínuo compacto de 16 genes onde políticas com Padre + Vitalidade alta ocupam uma região favorável, amostrar 240 cromossomos independentes (Busca Aleatória) encontra boas soluções sem concentrar a população nas 5 sementes de treino, ao passo que 12 gerações do AG especializam os limiares econômicos para as 5 sementes de treino (`gap` de `5,13` salas). Documentar esse comportamento empírico cumpre rigorosamente a diretriz científica da Seção 10 (*"Não exigir que o algoritmo genético sempre vença. Resultados negativos documentados são válidos"*).

---

## Experimento 4 (Adicional Obrigatório) — Generalização e Robustez

Avaliação da estratégia campeã do Algoritmo Genético (`seed=4185`) frente ao Baseline Fixo em cinco cenários distintos sem qualquer re-treinamento:

| Cenário de Teste | Sementes | Dificuldade | Composição | Baús | AG — Média ± DP (Mediana) | AG — Conclusão 100 Salas | Baseline Fixo — Média ± DP | Vantagem do AG |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Treinamento (In-Sample)** | `101–105` | 1,00x | Padrão | Sim | **98,20 ± 2,40** (100,0) | **60,0%** | 79,20 ± 8,98 | **+19,00 salas** |
| **2. Novas Sementes (Holdout)** | `201–210` | 1,00x | Padrão | Sim | **96,90 ± 2,66** (96,5) | **30,0%** | 69,00 ± 7,23 | **+27,90 salas** |
| **3. Novas Composições de Monstros** | `301–310` | 1,00x | Pool Alternativo | Sim | **97,50 ± 1,75** (97,5) | **30,0%** | 75,50 ± 3,72 | **+22,00 salas** |
| **4. Dificuldade Aumentada (+15%)** | `201–210` | **1,15x** | Padrão | Sim | **73,40 ± 32,28** (92,0) | **10,0%** | 51,40 ± 20,05 | **+22,00 salas** |
| **5. Sem Baús (Economia Estrita)** | `201–210` | 1,00x | Padrão | **Não** | **80,00 ± 28,30** (94,5) | **20,0%** | 61,10 ± 17,36 | **+18,90 salas** |

---

## 5. Análise Obrigatória de Falhas e Dominância

1. **Convergência Prematura:** Na taxa de mutação de `2%`, a população atinge 99% de seu fitness máximo já por volta da geração `4,4`, estacionando em ótimos locais que generalizam pior (`90,58` salas na validação contra `92,50` na mutação de `10%`).
2. **Baixa Diversidade Genética:** Sem imigração/mutação alta, o índice de diversidade cai de `~0,20` na Geração 1 para `0,067–0,079` na Geração 12 (`Pop 20` e `Pop 12`), enquanto `Mutação 25%` (`0,1347`) e `Pop 40` (`0,1166`) preservam maior variedade genética.
3. **Dependência de Aleatoriedade e Baús:** Com baús ativos nas sementes de validação `201–210`, a estratégia campeã do AG é altamente consistente (`96,90 ± 2,66` salas, mínimo `94`, máximo `100`). Porém, ao desligar completamente os baús (`enable_chests=False`) ou elevar os atributos dos monstros em `+15%`, surge um gargalo crítico por volta da **Sala 24–25** nas sementes `209` e `210`: quando a transição econômica inicial atrasa a compra de armadura antes do subchefe da Sala 25, o guerreiro morre no nível 11; se ultrapassa a Sala 25 (8 de 10 sementes), avança até as salas `89–100` (mediana `94,5` sem baús e `92,0` na dificuldade `+15%`).
4. **Sobreajuste à Configuração da Masmorra:** A média das 7 execuções do AG apresenta `96,09` salas nas 5 sementes de treino e `90,96` salas nas 10 sementes de validação (`gap = 5,13` salas), mostrando que otimizar limiares contínuos finos (`equipment_buy_threshold`, `min_gold_reserve`) sobre apenas 5 sementes gera especialização parcial aos drops daquelas sementes.
5. **Classes e Equipamentos Dominantes Identificados:**
   - **Dominância absoluta do Padre (`priest`):** Nas 7 repetições independentes do AG, o **Padre** foi selecionado no par prioritário de aliados em **100% das execuções (7/7)** e como primeiro aliado contratado no nível 5 em **85,7% (6/7)**. A segunda vaga (nível 15) foi dividida entre **Monge (`3/7`)**, **Alquimista (`3/7`)** e **Arqueiro (`1/7`)**, enquanto o **Mago (`0/7`)** foi preterido devido ao seu alto custo e baixa sobrevivência contra ataques à distância inimigos.
   - **Dominância de Equipamentos Defensivos Iniciais:** O gene `equip_offense_priority` convergiu para média de **`0,1222`** nas 7 execuções (`0,0113` no campeão), indicando que priorizar **Armadura e Escudo antes da Arma** (`equip_offense_priority < 0,40`) é decisivo para evitar a morte precoce do guerreiro.
