# Ficha de experimentos — Masmorra Genética (Grupo 7)

Os resultados abaixo documentam as avaliações empíricas do projeto. As versões originais estão registradas em `data/experiments/scientific_experiments_v2.json` e o experimento adicional pré-registrado em `data/experiments/extra_mutation_e5_v1.json`. O snapshot de criaturas é `srd-2014-v1.0.0` e as regras de combate são `balance-v1.0.0`. Os gráficos gerados estão em `results/finalizacao/graficos/`.

Orçamento: todas as buscas (AG e busca aleatória) usam contagem estrita de **avaliações efetivas da função objetivo** (indivíduos preservados pelo elitismo não são reavaliados e não consomem orçamento).

---

## Tabela Resumo dos Experimentos

| Exp. | Hipótese | Alteração / Configuração | Métrica / Resultado Principal | Interpretação Científica |
| :--- | :--- | :--- | :--- | :--- |
| **E1** | Taxas de mutação afetam o equilíbrio entre exploração e diversidade genética. | Mutação a 2%, 10% e 25%. População 20, 12 gerações (240 avaliações efetivas), 5 repetições. Validação nas sementes 201–210. | Média de salas concluídas: <br>• 2%: 91,28 ± 3,31 (conclusão 28%)<br>• 10%: 92,12 ± 3,42 (conclusão 20%)<br>• 25%: 95,06 ± 2,02 (conclusão 36%) | Taxa de 25% manteve maior diversidade (0,110 vs 0,035) e obteve maior média de validação neste conjunto. Populações pequenas sob mutação baixa sofrem perda rápida de diversidade. |
| **E2** | Com orçamento equivalente (240 avaliações), variar o tamanho da população altera a profundidade da busca. | Populações de 12 (24 ger.), 20 (14 ger.) e 40 (7 ger.). Mutação 10%, 5 repetições. Validação nas sementes 201–210. | Média de salas concluídas: <br>• Pop 12: 86,28 ± 5,63 (conclusão 18%)<br>• Pop 20: 86,82 ± 3,58 (conclusão 20%)<br>• Pop 40: 89,56 ± 3,43 (conclusão 20%) | A população de 40 teve a maior média nas configurações testadas. O experimento não estabelece a causa da diferença. |
| **E3** | O algoritmo genético supera a heurística fixa e compete com a busca aleatória com mesmo orçamento. | Estratégia fixa vs. Busca Aleatória (240 avaliações) vs. AG (240 avaliações, mut 10%). 7 repetições independentes. Validação 201–210. | Média de salas na validação: <br>• Fixa: 69,00 (0% conclusão)<br>• Busca Aleatória: 92,27 ± 4,16 (25,71% conclusão)<br>• AG: 91,27 ± 4,11 (28,57% conclusão)<br>Mann-Whitney AG vs Aleatória: **p = 0,748** | As duas buscas tiveram médias maiores que a regra fixa. Não houve evidência suficiente de diferença entre AG e busca aleatória; isso não prova equivalência entre os métodos. |
| **E4** | A estratégia campeã do AG sofre degradação de desempenho quando as regras do ambiente são alteradas. | Estratégia campeã do treino avaliada em 5 cenários: Treino (101–105), Validação padrão (201–210), Pool alternativo (301–310), Dificuldade +15%, Sem baús. | Média de salas do AG: <br>• Treino: 98,2 (60% conclusão)<br>• Validação: 96,9 (40% conclusão)<br>• Pool alternativo: 94,4 (20% conclusão)<br>• Dificuldade +15%: 73,4 (10% conclusão)<br>• Sem baús: 80,0 (20% conclusão) | Generalização razoável em novas sementes e monstros (+16,9 salas sobre fixa sem baús), mas sensível a aumentos globais de dificuldade (-23,5 salas) e privação econômica (-16,9 salas). |
| **E5** *(Adicional pré-registrado)* | Comparar AG (10%), AG (25%) e Busca Aleatória em **20 sementes virgens** (401–420) com 10 repetições. | Treino nas sementes 101–105. Validação nas sementes 401–420 (nunca vistas em nenhum experimento). Orçamento: 240 avaliações. 10 repetições por método. | Média de salas concluídas: <br>• AG (10%): 90,38 ± 3,83 (conclusão 14,5%)<br>• AG (25%): 92,49 ± 2,80 (conclusão 19,0%)<br>• Busca Aleatória: 94,56 ± 2,42 (conclusão 20,0%)<br>Mann-Whitney: AG25 vs AG10 p=0,241; AG10 vs Aleatória p=0,021; AG25 vs Aleatória p=0,121. | A média do AG com 25% foi 2,11 salas maior que com 10%, mas a diferença não foi conclusiva. A busca aleatória teve média maior que o AG com 10%; os dados não estabelecem a causa da diferença. |

---

## Detalhamento dos Experimentos

### E1 — Efeito da Taxa de Mutação (2%, 10%, 25%)
- **Hipótese:** Taxa de 2% causa convergência prematura; 25% causa dispersão estocástica; 10% equilibraria exploração e explotação.
- **Configuração:** 5 repetições por taxa; População 20; 12 gerações; 240 avaliações efetivas. Sementes de treino: 101–105; Validação: 201–210.
- **Evidências:** Diversidade final média: 2% = 0,0346; 10% = 0,0510; 25% = 0,1104. Geração média de convergência: 2% = 5,0; 10% = 6,4; 25% = 7,6.
- **Interpretação:** A taxa de 25% preservou melhor a capacidade de busca no espaço contínuo/discreto com 240 avaliações, contrariando a intuição inicial de que causaria ruído destrutivo.

### E2 — Tamanho da População com Orçamento Equivalente (240 avaliações)
- **Hipótese:** Com orçamento fixo, populações menores (12 indivíduos / 24 gerações) permitiriam maior profundidade evolutiva, enquanto populações maiores (40 indivíduos / 7 gerações) cobririam melhor a diversidade inicial.
- **Configuração:** 5 repetições por configuração. Sementes de treino: 101–105; Validação: 201–210.
- **Evidências:** Pop 40 obteve média de 89,56 salas vs 86,28 da Pop 12. A diversidade final da Pop 40 foi 0,1063 vs 0,0573 da Pop 12.
- **Interpretação:** A população de 40 teve média e diversidade final maiores nessa comparação. Outras repetições ajudariam a avaliar a estabilidade da diferença.

### E3 — Comparação com Baselines (Fixa vs. Busca Aleatória vs. Algoritmo Genético)
- **Hipótese:** O Algoritmo Genético superará tanto a política fixa heurística quanto a busca aleatória de estratégias com mesmo orçamento de avaliações.
- **Configuração:** 7 repetições independentes para Busca Aleatória e AG (240 avaliações por repetição); estratégia fixa avaliada deterministicamente. Sementes de treino: 101–105; Validação: 201–210.
- **Evidências:**
  - Fixa: 69,00 salas (0% conclusão).
  - Busca Aleatória: 92,27 ± 4,16 salas (25,71% conclusão).
  - Algoritmo Genético: 91,27 ± 4,11 salas (28,57% conclusão).
  - Teste Mann-Whitney U = 21,5, **p = 0,748053**; teste Welch t = -0,4188, **p = 0,682779**.
- **Interpretação:** A média do AG foi maior que a da regra fixa. Na comparação entre AG e busca aleatória, não houve evidência suficiente de diferença (p > 0,05); isso não prova que os métodos sejam equivalentes.

### E4 — Robustez e Generalização Fora da Amostra
- **Hipótese:** A estratégia selecionada pelo AG apresentará sobreajuste moderado às sementes de treino e queda de rendimento em regras adversas.
- **Configuração:** A melhor estratégia do AG (obtida no E3: foco Vitalidade/Defesa, contratação prioritária de Padre, armadura prioritária) avaliada em 5 cenários.
- **Evidências:**
  - In-sample treino: 98,2 salas (60% conclusão).
  - Holdout sementes 201–210: 96,9 salas (40% conclusão) — gap de generalização de 1,3 salas para este indivíduo.
  - Pool alternativo de monstros (301–310): 94,4 salas (20% conclusão).
  - Dificuldade +15%: 73,4 salas (10% conclusão; fixa = 51,4 salas).
  - Sem baús (economia estrita): 80,0 salas (20% conclusão; fixa = 61,1 salas).
- **Interpretação:** A estratégia mantém robustez relativa (sempre superando a estratégia fixa), mas a falta de baús reduz em 16,9 salas o rendimento médio, evidenciando forte dependência do fluxo econômico de itens.

### E5 — Experimento Adicional Pré-Registrado (Mutação 10% vs 25% vs Aleatória em Sementes Virgens)
- **Hipótese pré-registrada:** H1: AG 25% ≥ AG 10%; H2: AG ≥ Busca Aleatória em 20 sementes virgens (401–420).
- **Configuração:** 10 repetições de 240 avaliações por método. Treino: 101–105; Validação: 401–420 (20 sementes inéditas).
- **Evidências:**
  - AG (10% mutação): 90,38 ± 3,83 salas (14,5% conclusão).
  - AG (25% mutação): 92,49 ± 2,80 salas (19,0% conclusão).
  - Busca Aleatória: 94,56 ± 2,42 salas (20,0% conclusão).
  - Mann-Whitney AG25 vs AG10: U = 66,0, **p = 0,241145**; IC95% bootstrap da diferença [-0,86, +5,13].
  - Mann-Whitney AG10 vs Aleatória: U = 19,0, **p = 0,021134**; IC95% bootstrap [-6,92, -1,31].
  - Mann-Whitney AG25 vs Aleatória: U = 29,0, **p = 0,120665**; IC95% bootstrap [-4,28, +0,33].
- **Interpretação:** Nas sementes avaliadas, a média com mutação de 25% foi 2,11 salas maior que com 10%, mas a diferença não foi conclusiva ao nível de 5%. A busca aleatória teve média maior que o AG com mutação de 10% (p = 0,021). O experimento não identifica por que houve essa diferença.

---

## Análise Obrigatória de Três Casos de Falha / Limite

1. **Semente 201, Dificuldade +15%:**
   - *Ocorrência:* O guerreiro com a estratégia campeã do AG foi derrotado na **Sala 25** contra `Black Pudding` (concluiu 24 salas).
   - *Comportamento do baseline:* A regra fixa concluiu 25 salas e caiu na Sala 26 no mesmo cenário.
   - *Diagnóstico técnico:* Contra o Black Pudding fortalecido (+15% HP e dano), a estratégia do AG demorou para comprar armas ofensivas (focou em defesa e reserva de ouro), sofrendo desgaste prolongado no combate corpo a corpo.

2. **Semente 209, Sem Baús (Economia Estrita):**
   - *Ocorrência:* Guerreiro derrotado na **Sala 26** contra `Succubus/Incubus` (concluiu 25 salas).
   - *Estado no momento da derrota:* Arma nível 2, Escudo nível 1, mas **sem armadura** (tier 0) e com apenas 38 moedas restantes.
   - *Diagnóstico técnico:* A política genética dependia dos drops de baús para equilibrar o inventário. Sem baús, a reserva mínima de ouro (38,8 moedas) travou a aquisição de armadura, deixando o guerreiro vulnerável a ataques mágicos.

3. **Semente 308, Composição Alternativa de Criaturas:**
   - *Ocorrência:* Guerreiro avançou até a **Sala 79**, sendo derrotado por `Adult Red Dragon` (concluiu 78 salas).
   - *Dinâmica de desgaste:* Nas salas 76, 77 e 78, o HP pós-combate caiu progressivamente (380 → 372 → 332) devido a uma sequência de 3 encontros duplos consecutivos com imunidades elementais. O guerreiro entrou na sala 79 com HP incompleto e sem turnos de cura suficientes do Padre.
   - *Diagnóstico técnico:* O limite de 40 turnos e a recarga fixa de 22% de vida entre salas geram vulnerabilidade cumulativa a cadeias de encontros de alto CR.
