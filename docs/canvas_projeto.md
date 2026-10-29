# Canvas do Projeto — Masmorra Genética: A Evolução do Guerreiro

**Disciplina:** Inteligência Artificial II — Faculdades Integradas de Bauru (FIB)  
**Grupo:** Grupo 7  
**Tema / Técnica:** Algoritmos Genéticos (Computação Evolutiva) — Evoluindo o Personagem Perfeito  
**Data de Referência:** 29/10/2026  

---

## 1. Problema
Jogos de RPG táticos com progressão longa (100 salas consecutivas) apresentam um espaço combinatório complexo de decisões sequenciais: como distribuir pontos irreversíveis de atributos a cada nível, quando economizar ouro ou comprar equipamentos (considerando depreciação de 60% na revenda por 40% do valor-base), quais classes de aliados contratar nos níveis 5 e 15 e como evoluí-los. Estratégias manuais ou regras fixas estáticas frequentemente colapsam nas salas avançadas devido ao escalonamento de dano, múltiplos inimigos e resistências físicas/mágicas assimétricas.

## 2. Público-Alvo
- Estudantes, pesquisadores e docentes de Inteligência Artificial e Computação Evolutiva.
- Designers de jogos (*Game Designers*) interessados em balanceamento automatizado e teste de estratégias via meta-heurísticas.
- Jogadores entusiastas de RPGs táticos e sistemas baseados no *Dungeons & Dragons 5e SRD*.

## 3. Entradas (Inputs)
1. **Dataset Externo Oficial (D&D 5e SRD 2014 API):** 334 registros reais de monstros (`index`, `name`, `size`, `type`, `hit_points`, `armor_class`, `challenge_rating`, `xp`, `strength`, `dexterity`, `constitution`, `intelligence`, `wisdom`, `charisma`, `actions`, `damage_resistances`, `damage_immunities`, `damage_vulnerabilities`).
2. **Configuração Versionada de Balanceamento (`config/balance.json`):** Fórmulas de adaptação de combate, catálogo de 4 armas, 4 armaduras, 3 escudos e parâmetros das 5 classes de aliados.
3. **Hiperparâmetros Evolutivos e Sementes:** Tamanho da população, número de gerações, taxa de mutação, taxa de cruzamento, tamanho do torneio, elitismo e sementes pseudoaleatórias (`seed`).

## 4. Saídas (Outputs)
1. **Cromossomo Otimizado (16 genes):** Política completa de distribuição de atributos do guerreiro e aliados, prioridades das 5 classes de aliados, preferência ofensiva/defensiva de equipamentos, reserva mínima de ouro e limiares econômicos de compra/contratação.
2. **Métricas de Desempenho e Reprodutibilidade:** Média, mediana e desvio-padrão de salas concluídas (em treino e validação fora da amostra), taxa de conclusão das 100 salas (%), curvas de convergência e diversidade genética por geração.
3. **Logs Auditáveis Sala a Sala:** Simulação completa das 100 salas com referência individual à URL original de cada monstro na API D&D 5e SRD.

## 5. Dataset Externo e Fonte
- **Fonte Primária:** D&D 5e SRD API (`https://www.dnd5eapi.co/api/2014/monsters`)
- **Repositório de Origem:** `https://github.com/5e-bits/5e-database`
- **Fonte Secundária Documentada (Contingência):** Open5e API V2 (`https://open5e.com/api-docs`)
- **Licença:** *System Reference Document 5.1 (Wizards of the Coast LLC)* sob **CC-BY-4.0 / OGL v1.0a** (Código API: MIT).
- **Snapshot Versionado no Repositório:** `data/raw/monsters_raw_srd2014.json` (`334` registros, SHA-256 `51a00f4785dcf07fcb4056cd97eaa1eb5b2ba0c235d2b7d5b2762a772691d397`) e `data/processed/monsters_srd2014_processed.parquet`.

## 6. Baselines (Referências Comparativas Obrigatórias)
1. **Baseline Fixo (Regra Determinística Equilibrada):** Distribuição uniforme de atributos (`34% STR / 33% VIT / 33% DEF`), compra conservadora (`1,25x` custo + reserva de `40` ouro) e contratação ofensiva padrão (`Arqueiro` no nível 5 e `Mago` no nível 15).
2. **Busca Aleatória (Random Search):** Geração de cromossomos válidos aleatórios sob exatamente o **mesmo orçamento de avaliações da função objetivo (`240` avaliações)** que o Algoritmo Genético, selecionando a melhor política encontrada.

## 7. Hipóteses Científicas
- **H1 (Mutação):** Taxas de mutação muito baixas (`2%`) aceleram a perda de diversidade e convergem prematuramente para ótimos locais inferiores na validação, enquanto taxas moderadas (`10%`) maximizam a generalização fora da amostra e taxas altas (`25%`) mantêm alta diversidade ao custo de maior variância.
- **H2 (População vs. Gerações):** Sob orçamento fixo de avaliações (`240`), configurações com população excessivamente pequena (`12`) ou muitas gerações em poucas sementes sofrem maior deriva/sobreajuste do que populações mais amplas (`40`).
- **H3 (Superioridade sobre Regras Fixas e Descoberta de Sinergia):** O Algoritmo Genético supera significativamente o Baseline Fixo ($p < 0,001$) ao descobrir autonomamente a sinergia entre atributos de sobrevivência do guerreiro e classes de suporte/sustentação (Padre, Monge, Alquimista).
- **H4 (Generalização):** A política evoluída pelo AG mantém vantagem superior a `+18` salas sobre o Baseline Fixo mesmo em novas sementes, novas composições de espécies, dificuldade aumentada em `+15%` e economia estrita sem baús.

## 8. Experimentos Planejados e Executados
1. **Experimento 1 — Mutação:** Comparação de `2%`, `10%` e `25%` (`Pop=20, Ger=12`, 5 repetições independentes).
2. **Experimento 2 — População:** Comparação de `12×20`, `20×12` e `40×6` (todas com `240` avaliações da função objetivo, 5 repetições).
3. **Experimento 3 — Comparação com Baselines:** Baseline Fixo vs. Busca Aleatória (`240` aval) vs. Algoritmo Genético (`240` aval), com 7 repetições independentes avaliadas em treino (`5` sementes) e validação holdout (`10` sementes).
4. **Experimento 4 — Generalização e Análise de Falhas:** Avaliação em novas sementes, composições alternativas de monstros, dificuldade `+15%` e desligamento de baús (`enable_chests=False`).

## 9. Protótipo Web Publicável
Aplicação em **Streamlit (`app.py`)** estruturada em 6 páginas interativas:
1. *Sobre o projeto* | 2. *Dataset & EDA* | 3. *Masmorra (Simulador 100 Salas)* | 4. *Evolução Genética (Modo Científico + Modo Demonstração ao Vivo)* | 5. *Experimentos & Análise de Falhas* | 6. *Laboratório de Sensibilidade*.

## 10. Divisão de Responsabilidades (Grupo 7)
- **Eduardo Coque Corrêa de Lima:** Coordenação técnica, implementação do Algoritmo Genético (`src/genetic/`) e integração geral.
- **Matheus Alcântara Pereira:** Pipeline ETL da API D&D 5e SRD, validação de schema, normalização, snapshot e EDA (`src/dataset/`).
- **Fernando Eduardo Motta Mendes:** Simulador de 100 salas, motor de combate por turnos, aliados, mercado/economia (`src/game/`) e interface Streamlit (`app.py`).
- **Rogério Tiritan Marcone:** Canvas, fundamentação metodológica, Model Card e Resumo Expandido.
- **Reuel Vitor Lanzetti:** Execução e análise estatística dos experimentos (`src/experiments/`), ficha de experimentos, slides, roteiro de vídeo e materiais de divulgação.
