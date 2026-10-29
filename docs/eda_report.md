# Relatório de Análise Exploratória de Dados (EDA) — D&D 5e SRD API (2014)

**Projeto:** Masmorra Genética: A Evolução do Guerreiro — Grupo 7 (IA II — FIB)  
**Responsável principal pela frente de Dados/EDA:** Matheus Alcântara Pereira (com validação de toda a equipe)  
**Versão do Snapshot:** `srd-2014-v1.0.0`  
**SHA-256 do Arquivo Bruto (`data/raw/monsters_raw_srd2014.json`):** `51a00f4785dcf07fcb4056cd97eaa1eb5b2ba0c235d2b7d5b2762a772691d397`  

---

## 1. Fonte de Dados, Proveniência e Licenciamento

- **Endpoint de listagem consultado:** `https://www.dnd5eapi.co/api/2014/monsters`
- **Exemplo de registro individual:** `https://www.dnd5eapi.co/api/2014/monsters/goblin`
- **Repositório de origem:** `https://github.com/5e-bits/5e-database`
- **Fonte secundária documentada (contingência):** Open5e API V2 (`https://api.open5e.com/v2/creatures/?document__slug=wotc-srd`)
- **Licenciamento e Atribuição:** Os dados das criaturas pertencem ao *System Reference Document 5.1 (SRD 5.1)* da Wizards of the Coast LLC, distribuído sob licença **Creative Commons Attribution 4.0 International (CC-BY-4.0)** e **Open Game License (OGL) v1.0a**. O código de serviço da API (`5e-bits`) é distribuído sob licença **MIT**.

### Diferenciação Estrita de Proveniência
1. **Dados externos originais (`data/raw/monsters_raw_srd2014.json`):** JSON bruto exato retornado pelos 334 endpoints da API.
2. **Dados externos tratados (`data/processed/monsters_srd2014_processed.parquet` e `.csv`):** Colunas normalizadas (ex.: extração do inteiro `armor_class` a partir da lista aninhada `[{"type": ..., "value": ...}]`, contagem de resistências e cálculo do valor esperado matemático de expressões de dados `NdS+M`).
3. **Atributos derivados por fórmulas (`src/game/monsters.py` + `config/balance.json`):** Parâmetros de combate do simulador (ataque, defesa, dano físico, dano mágico, mitigação e ouro), calculados em tempo de instanciação sem sobrescrever o dataset original.

---

## 2. Quantidade de Criaturas, Validação e Valores Ausentes

- **Registros esperados na listagem da API:** `334`
- **Registros coletados com sucesso:** `334` (`0` falhas HTTP, `0` duplicatas, `0` registros inválidos)
- **Campos obrigatórios (`index`, `name`, `size`, `type`, `armor_class`, `hit_points`, `challenge_rating`, `xp`, `strength`, `dexterity`, `constitution`, `intelligence`, `wisdom`, `charisma`):** **100% preenchidos** (0 nulos nos 334 registros).
- **Campos opcionais ou listas frequentemente vazias:**
  - `subtype`: nulo em **258 de 334** registros (77,25%).
  - `damage_vulnerabilities`: lista vazia em **319 de 334** registros (95,51%).
  - `damage_resistances`: lista vazia em **264 de 334** registros (79,04%).
  - `damage_immunities`: lista vazia em **198 de 334** registros (59,28%).
  - `legendary_actions`: lista vazia em **302 de 334** registros (90,42%).
  - `actions`: lista vazia em **4 de 334** registros (`frog`, `sea-horse`, `shrieker`, `vampire-mist`).

---

## 3. Estatísticas Descritivas Observadas (`n = 334`)

| Variável | Média | Desvio-Padrão | Mínimo | Q25 | Mediana | Q75 | Máximo | Assimetria (Skew) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `challenge_rating` (CR) | 4,56 | 5,82 | 0,0 | 0,5 | 2,0 | 6,0 | 30,0 | +1,74 |
| `hit_points` (HP) | 81,86 | 98,04 | 1,0 | 19,0 | 45,0 | 117,75 | 676,0 | +2,56 |
| `armor_class` (AC) | 13,96 | 3,22 | 5,0 | 12,0 | 13,0 | 16,75 | 25,0 | +0,42 |
| `xp` (Experiência) | 4.149,15 | 12.146,33 | 10,0 | 100,0 | 450,0 | 2.300,0 | 155.000,0 | +7,33 |
| `strength` (Força) | 15,19 | 6,64 | 1,0 | 11,0 | 16,0 | 19,0 | 30,0 | -0,19 |
| `dexterity` (Destreza) | 12,66 | 3,20 | 1,0 | 10,0 | 13,0 | 15,0 | 28,0 | +0,05 |
| `constitution` (Constituição) | 15,09 | 4,44 | 8,0 | 12,0 | 14,0 | 17,75 | 30,0 | +0,85 |
| `intelligence` (Inteligência) | 7,89 | 5,66 | 1,0 | 2,0 | 7,0 | 12,0 | 25,0 | +0,47 |
| `wisdom` (Sabedoria) | 11,70 | 2,90 | 3,0 | 10,0 | 12,0 | 13,0 | 25,0 | +0,37 |
| `charisma` (Carisma) | 9,74 | 5,73 | 1,0 | 5,0 | 8,0 | 14,0 | 30,0 | +0,66 |
| `max_attack_bonus` | 5,96 | 3,37 | 0,0 | 4,0 | 5,0 | 7,0 | 19,0 | +1,20 |
| `best_action_damage` | 14,28 | 14,46 | 0,0 | 5,5 | 10,0 | 17,0 | 91,0 | +2,49 |
| `estimated_dpr_raw` | 28,77 | 42,38 | 0,0 | 6,5 | 13,0 | 31,13 | 273,0 | +3,10 |

### Distribuição por Tipo de Criatura (`type`)
- `beast`: 87 (26,05%)
- `humanoid`: 50 (14,97%)
- `dragon`: 43 (12,87%)
- `monstrosity`: 39 (11,68%)
- `fiend`: 23 (6,89%)
- `undead`: 20 (5,99%)
- `elemental`: 16 (4,79%)
- `giant`: 10 (2,99%) | `swarm of tiny beasts`: 10 (2,99%)
- `construct`: 9 (2,69%) | `plant`: 6 | `fey`: 6 | `celestial`: 6 | `aberration`: 5 | `ooze`: 4

---

## 4. Análise de Correlações Verificadas

| Par de Variáveis | Correlação Linear de Pearson ($r$) | Valor-$p$ (Pearson) | Correlação de Postos de Spearman ($\rho$) | Interpretação Empírica |
| :--- | :---: | :---: | :---: | :--- |
| `challenge_rating` vs `hit_points` | **+0,9404** | $1,52 \times 10^{-157}$ | **+0,9693** | Forte relação linear e monotônica |
| `challenge_rating` vs `max_attack_bonus` | **+0,9068** | $1,46 \times 10^{-126}$ | **+0,8711** | Escalonamento muito consistente de precisão |
| `constitution` vs `hit_points` | **+0,8808** | $7,88 \times 10^{-110}$ | **+0,8940** | Constituição determina diretamente a reserva de vida |
| `challenge_rating` vs `constitution` | **+0,8588** | $1,97 \times 10^{-98}$ | **+0,8611** | Monstros mais fortes possuem alta Constituição |
| `challenge_rating` vs `xp` | **+0,7830** | $1,95 \times 10^{-70}$ | **+0,9995** | Monotônica perfeita, mas fortemente não-linear (exponencial) |
| `challenge_rating` vs `armor_class` | **+0,7547** | $9,51 \times 10^{-63}$ | **+0,6799** | Moderada-alta; comprimida pela *Bounded Accuracy* (5 a 25) |
| `challenge_rating` vs `estimated_dpr_raw` | **+0,7373** | $1,68 \times 10^{-58}$ | **+0,8763** | Forte aumento de dano por turno com multiataques |
| `challenge_rating` vs `strength` | **+0,7207** | $9,27 \times 10^{-55}$ | **+0,8085** | Crescimento expressivo de Força física |
| `dexterity` vs `armor_class` | **+0,2267** | $2,88 \times 10^{-5}$ | **+0,1696** | Correlação fraca no bestiário global |
| `challenge_rating` vs `dexterity` | **-0,0100** | $0,8556$ (n.s.) | **-0,0777** | **Inexistente** ($p > 0,15$); Destreza não cresce com CR |

---

## 5. Quatro Descobertas Empíricas Fundamentais para o Projeto

1. **Descoberta 1 — Divergência entre o crescimento linear de HP ($r = 0,9404$) e o crescimento hiper-exponencial de XP ($\rho = 0,9995$, assimetria $+7,33$):**
   Enquanto o HP médio sobe de `12,5` (CR 0–0.5) para `395,25` (CR 18–30) — um fator de ~31,6x —, o XP médio salta de `49,25` para `46.250,0` — um fator de **939x**. Utilizar o XP bruto diretamente em uma curva linear de nível faria o guerreiro ganhar dezenas de níveis em uma única sala avançada. Por isso, a camada de adaptação do simulador deve comprimir a recompensa de experiência via transformação sublinear calibrada sobre o XP/CR real.
2. **Descoberta 2 — Ausência de correlação entre Nível de Desafio e Destreza ($r = -0,0100, p = 0,856$) e compressão de AC (*Bounded Accuracy*):**
   Ao contrário do senso comum de RPGs eletrônicos em que todos os atributos crescem com o nível do inimigo, no dataset D&D 5e SRD a Destreza das criaturas de CR 18–30 é estatisticamente indistinguível da de criaturas de CR 0–1. Além disso, a Classe de Armadura (`armor_class`) fica restrita ao intervalo `[5, 25]`. Consequentemente, converter `armor_class` diretamente 1:1 em redução fixa de dano sem considerar o escalonamento de Constituição e CR tornaria os monstros de CR alto excessivamente frágeis contra ataques físicos escalados.
3. **Descoberta 3 — Anomalias funcionais no dataset oficial (5 criaturas sem ação de dano direto e conjuradores de baixa AC):**
   Cinco registros válidos da API possuem `attack_actions_count == 0`: `frog` (CR 0), `sea-horse` (CR 0), `shrieker` (CR 0), `rug-of-smothering` (CR 2, cujo dano ocorre via mecânica especial de sufocamento textual) e `vampire-mist` (CR 13, forma gasosa de vampiro). Adicionalmente, conjuradores de alto desafio como `mage` (CR 6, HP 40, AC 12) e `archmage` (CR 12, HP 99, AC 12) possuem poder ofensivo concentrado em magias (`special_abilities`). Sem tratamento explícito na montagem da masmorra, `vampire-mist` geraria um encontro de CR 13 inofensivo, e `archmage` teria dano subestimado se apenas ataques de arma fossem lidos.
4. **Descoberta 4 — Assimetria entre Resistências Físicas e Mágicas nos Encontros Avançados:**
   Exatamente `85` criaturas (25,4%) possuem resistência ou imunidade física (`bludgeoning`, `piercing`, `slashing`) e `133` (39,8%) possuem resistência/imunidade elemental/mágica. Essa heterogeneidade real do dataset cria uma pressão seletiva genuína para o Algoritmo Genético: estratégias que investem exclusivamente em dano físico sofrem penalidades severas contra mortos-vivos incorpóreos, golens e elementais, valorizando a contratação coordenada de aliados mágicos (Mago, Monge) e de suporte/debuff (Padre, Alquimista).

---

## 6. Campos Aproveitados vs. Campos Descartados na Simulação

| Campo / Grupo de Campos | Decisão | Justificativa Técnica |
| :--- | :---: | :--- |
| `index`, `name`, `source_url` | **Aproveitado** | Rastreabilidade obrigatória entre cada inimigo de sala e o registro oficial na API. |
| `challenge_rating`, `xp` | **Aproveitado** | Orçamento de dificuldade das 100 salas e cálculo de progressão de experiência e ouro. |
| `hit_points`, `constitution` | **Aproveitado** | Determinação dos pontos de vida e robustez defensiva da instância de combate. |
| `armor_class`, `dexterity` | **Aproveitado** | Cálculo da defesa física/mágica e da iniciativa de turno no motor de combate. |
| `strength`, `intelligence`, `wisdom`, `charisma` | **Aproveitado** | Escalonamento complementar de poder ofensivo físico (STR) e mágico/especial (INT/WIS/CHA). |
| `actions`, `max_attack_bonus`, `best_action_physical_damage`, `best_action_magical_damage`, `multiattack_count` | **Aproveitado** | Determinação direta do ataque, dano físico base e dano mágico base do monstro no simulador. |
| `has_physical_resistance`, `has_magical_resistance`, `resistances_count`, `immunities_count`, `vulnerabilities_count` | **Aproveitado** | Taxas percentuais de mitigação física e mágica de cada inimigo no combate. |
| `type`, `size` | **Aproveitado** | Posicionamento tático (linha de frente vs. retaguarda) e filtros de composição de encontros. |
| `languages`, `senses`, `alignment`, `speed` | **Descartado na simulação (mantido no dataset)** | O combate é em turnos discretos abstratos (frente/retaguarda) sem mapa espacial em grade ou diálogos. |
| `condition_immunities`, `reactions`, `forms` | **Descartado na simulação (mantido no dataset)** | Simplificação deliberada (Seção 6 e 7) para evitar explosão de estados e manter avaliação rápida no AG. |
| `Monsters com attack_actions_count == 0 e CR == 0` (`frog`, `sea-horse`, `shrieker`) e `vampire-mist` | **Filtrados do pool de combate ativo (mantidos na EDA)** | Registro documentado: formas puramente passivas/alternativas sem ataque direto não compõem encontros de combate para evitar salas triviais defeituosas. |
