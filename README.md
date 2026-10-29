# ⚔️ Masmorra Genética: A Evolução do Guerreiro — Grupo 7 (IA II — FIB)

Aplicação web científica e interativa que utiliza **Algoritmos Genéticos (Computação Evolutiva)** para evoluir estratégias de progressão de atributos, contratação de aliados e decisões econômicas em uma masmorra de **100 salas** construída diretamente a partir dos **334 monstros reais da API oficial Dungeons & Dragons 5e SRD (2014)**.

---

## 👥 Integrantes do Grupo 7 (Inteligência Artificial II — FIB)

| Integrante | Frente Principal | Responsabilidades |
| :--- | :--- | :--- |
| **Eduardo Coque Corrêa de Lima** | Coordenação Técnica & AG | Arquitetura, implementação do Algoritmo Genético (`src/genetic/`) e integração |
| **Matheus Alcântara Pereira** | Dataset, ETL & EDA | Coleta D&D 5e SRD API, validação, pré-processamento, snapshot e EDA (`src/dataset/`) |
| **Fernando Eduardo Motta Mendes** | Simulador, Combate & UI | Masmorra de 100 salas, motor de combate por turnos, economia (`src/game/`) e Streamlit (`app.py`) |
| **Rogério Tiritan Marcone** | Documentação Acadêmica | Canvas Inicial, Metodologia, Model Card e Resumo Expandido (`docs/`) |
| **Reuel Vitor Lanzetti** | Experimentos & Divulgação | Execução dos experimentos (`src/experiments/`), análise estatística/falhas, slides e vídeo |

---

## 📂 Arquitetura do Projeto

```text
Trabalho-IA-Grupo7/
├── app.py                                      # Aplicação Web Interativa (6 páginas em Streamlit)
├── requirements.txt                            # Dependências para reprodução local e Streamlit Cloud
├── README.md                                   # Documentação principal do repositório
├── .streamlit/
│   └── config.toml                             # Configuração de tema e servidor Streamlit
├── .github/
│   └── workflows/
│       └── ci_and_experiments.yml              # Pipeline GitHub Actions (Testes + Experimentos Científicos)
├── config/
│   └── balance.json                            # Parâmetros versionados de adaptação e economia
├── data/
│   ├── raw/
│   │   └── monsters_raw_srd2014.json           # Snapshot bruto oficial (334 monstros da API D&D 5e SRD)
│   ├── processed/
│   │   ├── monsters_srd2014_processed.csv      # Dataset tratado e normalizado (CSV)
│   │   └── monsters_srd2014_processed.parquet  # Dataset tratado e normalizado (Parquet)
│   ├── metadata/
│   │   ├── collection_manifest.json            # Manifesto de coleta, versão, licença e SHA-256
│   │   └── validation_report.json              # Relatório de validação de tipos e campos
│   └── experiments/
│       └── scientific_experiments_v1.json      # Resultados auditáveis dos 4 experimentos científicos
├── src/
│   ├── dataset/
│   │   ├── collector.py                        # Coleta HTTP concorrente com retry/backoff e fallback
│   │   ├── validation.py                       # Validação de schema, limites e integridade
│   │   ├── preprocessing.py                    # Normalização explícita e parsing de dados (NdS+M)
│   │   └── exploration.py                      # Estatísticas, correlações (Pearson/Spearman) e gráficos
│   ├── game/
│   │   ├── monsters.py                         # Camada de transformação SRD -> Instância de Combate
│   │   ├── dungeon.py                          # Gerador reproduzível por semente das 100 salas
│   │   ├── characters.py                       # Guerreiro e 5 classes de aliados (Mago, Arqueiro, Monge, Padre, Alquimista)
│   │   ├── economy.py                          # Mercado (4 armas, 4 armaduras, 3 escudos, venda 40%, baús)
│   │   └── combat.py                           # Motor único de combate automático em turnos (headless)
│   ├── genetic/
│   │   ├── chromosome.py                       # Cromossomo de 16 genes, reparo e decodificação online
│   │   ├── fitness.py                          # Função fitness lexicográfica multi-semente
│   │   ├── operators.py                        # Torneio, BLX-alpha/uniforme, mutação, elitismo e diversidade
│   │   └── optimizer.py                        # Ciclo evolutivo e registro por geração
│   ├── experiments/
│   │   ├── baselines.py                        # Baseline Fixo e Busca Aleatória (orçamento equivalente)
│   │   ├── evaluation.py                       # Execução dos Experimentos 1, 2, 3, 4 e Análise de Falhas
│   │   └── reports.py                          # Geração dos gráficos científicos (PNG)
│   └── ui/
├── scripts/
│   ├── run_etl_and_eda.py                      # Script executável de coleta, validação, tratamento e EDA
│   └── run_scientific_experiments.py           # Script executável dos 4 experimentos científicos
├── tests/
│   └── test_masmorra_genetica.py               # Suíte automatizada cobrindo os 17 critérios de aceitação
├── docs/
│   ├── eda_report.md                           # Relatório completo da Análise Exploratória de Dados
│   ├── canvas_projeto.md                       # Canvas Inicial do Projeto
│   ├── ficha_experimentos.md                   # Ficha de Experimentos e Análise de Falhas
│   ├── model_card.md                           # Model Card da Solução
│   ├── resumo_expandido.md                     # Resumo Expandido acadêmico (2 páginas)
│   └── materiais_divulgacao_e_apresentacao.md  # Folder, Instagram, Roteiro de Vídeo, Slides (40 min) e Deploy
└── results/
    ├── eda/                                    # Gráficos reais da Análise Exploratória (PNG + JSON)
    └── experiments/                            # Gráficos reais dos Experimentos Científicos (PNG + JSON)
```

---

## 🌐 Fonte de Dados Externa, Proveniência e Licenciamento

- **Endpoint Oficial de Listagem:** `https://www.dnd5eapi.co/api/2014/monsters`
- **Exemplo de Registro Individual:** `https://www.dnd5eapi.co/api/2014/monsters/goblin`
- **Repositório de Origem:** `https://github.com/5e-bits/5e-database`
- **Licenciamento:** *System Reference Document 5.1 (Wizards of the Coast LLC)* — **Creative Commons Attribution 4.0 International (CC-BY-4.0)** / **OGL v1.0a**. Código da API sob licença **MIT**.
- **Snapshot Congelado e Verificado:** `334` criaturas válidas (`0` falhas HTTP, `0` registros inventados), SHA-256 bruto `51a00f4785dcf07fcb4056cd97eaa1eb5b2ba0c235d2b7d5b2762a772691d397`.

---

## 📊 Principais Resultados Verificados

### 1. Descobertas da Análise Exploratória (EDA — `n = 334` criaturas)
1. **Escalonamento Linear de HP vs. Exponencial de XP:** `challenge_rating` possui correlação linear fortíssima com `hit_points` ($r = 0,9404, p < 10^{-156}$) e `max_attack_bonus` ($r = 0,9068$), enquanto `xp` cresce exponencialmente ($\rho = 0,9995$, assimetria $+7,33$), fundamentando a compressão logarítmica de XP no simulador.
2. **Bounded Accuracy e Independência de Destreza:** `armor_class` varia apenas entre `5` e `25` ($r = 0,7547$ com CR), e `dexterity` não possui correlação com `challenge_rating` ($r = -0,0100, p = 0,8556$).
3. **Anomalias Tratadas:** Identificados e filtrados 4 registros sem ação de ataque direto (`frog`, `sea-horse`, `shrieker`, `vampire-mist` CR 13) e tratados conjuradores (`mage` CR 6, `archmage` CR 12).
4. **Assimetria de Resistências:** `25,4%` das criaturas possuem resistência/imunidade física e `39,8%` resistência/imunidade elemental/mágica.

### 2. Comparação com Baselines (Experimento 3 — Validação Fora da Amostra em 10 Sementes Holdout)
| Método | Orçamento (Avaliações) | Salas em Treino (Média ± DP) | Salas em Validação (Média ± DP) | Mediana (Val) | Taxa Média Conclusão 100 Salas | Melhor Política em Validação | Tempo Médio |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Estratégia Fixa (Baseline)** | 1 | 79,20 ± 0,00 | 69,00 ± 7,23 | 70,50 | 0,00% | 69,00 (`0,0%`) | 0,03s |
| **Busca Aleatória** | 240 | 95,11 ± 0,97 | **92,27 ± 4,16** | **94,30** | 25,71% | 95,50 (`40,0%`) | 8,20s |
| **Algoritmo Genético** | 240 | **96,09 ± 1,04** | 90,96 ± 3,88 | 89,80 | **27,14%** | **96,90 ± 2,66** (`30,0%`) | 8,96s |

- **Significância contra o Baseline Fixo:** A estratégia campeã do AG supera o Baseline Fixo em **`+27,90` salas** na validação ($96,90$ vs. $69,00$, Mann-Whitney $U = 100,0, p = 0,000166 < 0,001$).
- **Generalização (Experimento 4):** Em novas composições de monstros (`301–310`), a estratégia campeã do AG atinge **`97,50 ± 1,75` salas** vs. **`75,50 ± 3,72`** do Baseline Fixo (**`+22,00` salas**); na dificuldade `+15%`, atinge **`73,40`** (mediana `92,0`) vs. **`51,40`** (`+22,00` salas); e sem baús (`enable_chests=False`), atinge **`80,00`** (mediana `94,5`) vs. **`61,10`** (`+18,90` salas).

---

## 🚀 Instruções de Reprodução Local

### 1. Instalar Dependências
```bash
python -m pip install -r requirements.txt
```

### 2. Executar Pipeline ETL e Análise Exploratória (EDA)
Usa o snapshot congelado por padrão; passe `--refresh` para reconsultar os 334 endpoints da API ao vivo:
```bash
python scripts/run_etl_and_eda.py
```

### 3. Executar os 4 Experimentos Científicos Reais
```bash
python scripts/run_scientific_experiments.py
```

### 4. Executar a Suíte de Testes Automatizados (17 Critérios de Aceitação)
```bash
python -m pytest -v
```

### 5. Iniciar a Aplicação Web Interativa (Streamlit)
```bash
python -m streamlit run app.py
```

---

## ☁️ Publicação no Streamlit Community Cloud

O repositório está integralmente configurado para publicação no **Streamlit Community Cloud** (`https://share.streamlit.io/`):
- **Arquivo de entrada:** `app.py`
- **Dependências:** `requirements.txt`
- **Configuração de servidor/tema:** `.streamlit/config.toml`
- **Dados e experimentos pré-computados:** versionados em `data/` e `results/` para carregamento instantâneo no plano gratuito de hospedagem, além do **Modo Demonstração** ao vivo na Página 4.

> **Status de Publicação:** A preparação técnica para o deploy no Streamlit Community Cloud está 100% concluída. Como a criação do vínculo no painel `share.streamlit.io` requer autenticação interativa OAuth da conta GitHub (`Duduzinhoextrem`), consulte a seção 5 de [`docs/materiais_divulgacao_e_apresentacao.md`](docs/materiais_divulgacao_e_apresentacao.md) para os 3 cliques finais de ativação da URL pública.

---

## 📚 Documentação Acadêmica Completa (`docs/`)

- [Relatório de Análise Exploratória de Dados (EDA)](docs/eda_report.md)
- [Canvas Inicial do Projeto](docs/canvas_projeto.md)
- [Ficha de Experimentos e Análise de Falhas](docs/ficha_experimentos.md)
- [Model Card da Solução](docs/model_card.md)
- [Resumo Expandido (2 Páginas)](docs/resumo_expandido.md)
- [Materiais de Divulgação, Slides (40 min), Roteiro de Vídeo e Guia de Deploy](docs/materiais_divulgacao_e_apresentacao.md)
