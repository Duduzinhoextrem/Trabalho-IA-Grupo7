# Model Card — Otimizador Evolutivo de Políticas (Masmorra Genética — Grupo 7)

## 1. Identificação da Solução
- **Nome da Solução:** *Masmorra Genética: Otimizador Evolutivo de Políticas de Progressão (MG-GA v1.0)*
- **Instituição / Disciplina:** Faculdades Integradas de Bauru (FIB) — Inteligência Artificial II
- **Autores (Grupo 7):** Eduardo Coque Corrêa de Lima, Fernando Eduardo Motta Mendes, Matheus Alcântara Pereira, Reuel Vitor Lanzetti e Rogério Tiritan Marcone
- **Versão:** `1.0.0` (Snapshot `srd-2014-v1.0.0` / Balance `balance-v1.0.0`)

## 2. Objetivo e Escopo de Uso
- **Objetivo Principal:** Encontrar automaticamente estratégias (políticas parametrizadas por um cromossomo de 16 genes) capazes de maximizar a progressão de um guerreiro e até dois aliados ao longo de uma masmorra sequencial de 100 salas povoada por monstros reais do *Dungeons & Dragons 5e SRD*.
- **Natureza da Técnica:** **Otimização meta-heurística de políticas por Algoritmo Genético (Computação Evolutiva)**. Diferentemente de modelos preditivos supervisionados (como regressão ou redes neurais treinadas sobre pares entrada-rótulo), o MG-GA evolui vetores de decisão avaliados por simulação estocástica multi-semente sem acesso a informações futuras das salas.

## 3. Dataset Externo Utilizado
- **Fonte Oficial:** D&D 5e SRD REST API (`https://www.dnd5eapi.co/api/2014/monsters`), derivada de `https://github.com/5e-bits/5e-database`.
- **Licenciamento:** *System Reference Document 5.1 (Wizards of the Coast LLC)* — Creative Commons Attribution 4.0 International (**CC-BY-4.0**) e Open Game License (**OGL v1.0a**).
- **Tamanho e Integridade:** `334` registros de criaturas coletados e validados (`0` ausentes nos campos obrigatórios; SHA-256 bruto `51a00f4785dcf07fcb4056cd97eaa1eb5b2ba0c235d2b7d5b2762a772691d397`).

## 4. Pré-Processamento e Camada de Transformação
1. **Extração Tabular (`src/dataset/preprocessing.py`):** Desaninhamento de `armor_class`, contagem de resistências/imunidades/vulnerabilidades e cálculo do valor esperado matemático de dados de dano (`NdS+M`) separados em componentes físico (`bludgeoning`, `piercing`, `slashing`) e mágico/elemental.
2. **Filtro de Formas Passivas (`src/game/monsters.py`):** Exclusão documentada de 4 registros sem ação de ataque (`frog`, `sea-horse`, `shrieker`, `vampire-mist`) do pool de encontros ativos, mantendo 330 criaturas combatentes.
3. **Adaptação para Simulador (`config/balance.json`):** Conversão explícita para `max_hp`, `defense` (compensando a *Bounded Accuracy* verificada na EDA), `physical_damage`, `magical_damage`, `phys_resistance` e `mag_resistance` (limitadas a `55%` para impedir invulnerabilidade), `xp_reward` (compressão logarítmica do XP exponencial do SRD) e `gold_reward`.

## 5. Variáveis do Cromossomo (16 Genes)
| Índices | Variáveis (Genes) | Tipo / Domínio | Papel na Política Online |
| :---: | :--- | :---: | :--- |
| `0..2` | `w_weight_str`, `w_weight_vit`, `w_weight_def` | Contínuos $\in [0,01; 1,0]$, $\sum = 1$ | Distribuição irreversível dos 3 pontos por nível do Guerreiro |
| `3..7` | `ally_prio_mage..alchemist` | Contínuos $\in [0,0; 1,0]$ | Ordem de prioridade para contratação das 5 classes nos níveis 5 e 15 |
| `8..10` | `ally_weight_power`, `ally_weight_vit`, `ally_weight_def` | Contínuos $\in [0,01; 1,0]$, $\sum = 1$ | Distribuição irreversível dos pontos por nível dos Aliados |
| `11` | `equip_offense_priority` | Contínuo $\in [0,0; 1,0]$ | Ordem de compra no mercado (`<0,40` Defensiva: Armadura $\rightarrow$ Escudo $\rightarrow$ Arma; $\ge 0,55$ Ofensiva) |
| `12` | `hire_before_equip_discrete` | Discreto $\in \{0, 1\}$ | Define se prioriza contratar aliado antes de comprar equipamento |
| `13` | `min_gold_reserve` | Contínuo $\in [0,0; 120,0]$ | Reserva mínima de ouro intocável em compras |
| `14..15` | `equipment_buy_threshold`, `ally_hire_threshold` | Contínuos $\in [1,0; 1,8]$ | Limiares multiplicadores para decidir entre comprar agora ou economizar |

## 6. Métricas e Resultados Empíricos Verificados
- **Métrica Primária:** Média de salas concluídas (`mean_rooms_cleared`, de 0 a 100).
- **Métrica Secundária Reportada:** Taxa de conclusão das 100 salas (`completion_rate`, %).
- **Desempenho em Validação Fora da Amostra (Sementes Holdout `201–210`):**
  - **Baseline Fixo:** `69,00 ± 7,23` salas (Mediana `70,50`, Conclusão `0,0%`).
  - **Busca Aleatória (240 avaliações, 7 repetições):** `92,27 ± 4,16` salas (Mediana `94,30`, Conclusão média `25,71%`).
  - **Algoritmo Genético (240 avaliações, 7 repetições):** `90,96 ± 3,88` salas na média das repetições (Conclusão média **`27,14%`**) e **`96,90 ± 2,66` salas (`30,0%` conclusão)** com o cromossomo campeão (`p = 0,000166` vs. Baseline Fixo).
  - **Generalização em Novas Composições (`301–310`):** `97,50 ± 1,75` salas (`30,0%` conclusão) vs. `75,50` do Baseline Fixo (`+22,00` salas).

## 7. Limitações, Riscos e Vieses Conhecidos
1. **Sensibilidade ao Tamanho do Conjunto de Treinamento (Sobreajuste):** Otimizar por muitas gerações sobre apenas 5 sementes de masmorra introduz um *gap* médio de `5,13` salas entre treino (`96,09`) e validação (`90,96`), pois os limiares econômicos contínuos se ajustam aos baús daquelas sementes.
2. **Gargalo de Transição na Sala 25 em Ambientes Estritos:** Quando os baús são desligados (`enable_chests=False`) ou a dificuldade sobe `+15%`, políticas com limiar alto de economia (`equipment_buy_threshold = 1,453`, que economizam para pular o Tier 2) podem enfrentar o subchefe da Sala 25 ainda com equipamento Tier 1 em sementes específicas (`209` e `210`), sofrendo derrota precoce naquelas sementes (embora alcancem mediana de `94,5` salas nas demais).
3. **Viés de Dominância de Classe:** Sob as regras atuais de recuperação parcial entre salas (`22%`), a classe **Padre (`priest`)** apresenta dominância estrutural (`100%` de presença nas soluções ótimas do AG), enquanto o **Mago (`mage`)** é sistematicamente descartado pelo otimizador.
4. **Proveniência Sintética das Simulações:** Os logs de batalha e taxas de vitória gerados pelo sistema são resultados de simulação computacional e **jamais** devem ser interpretados como telemetria de jogadores humanos reais.
