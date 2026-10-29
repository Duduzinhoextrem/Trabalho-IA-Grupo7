# Materiais de Divulgação, Apresentação e Guia de Deploy — Masmorra Genética (Grupo 7)

**Disciplina:** Inteligência Artificial II — Faculdades Integradas de Bauru (FIB)  
**Integrantes:** Eduardo Coque Corrêa de Lima, Fernando Eduardo Motta Mendes, Matheus Alcântara Pereira, Reuel Vitor Lanzetti e Rogério Tiritan Marcone  

---

## 1. Folder Dobrável (Tríptico — 6 Painéis)

### Painel 1 (Capa Externa)
- **Título:** ⚔️ MASMORRA GENÉTICA: A Evolução do Guerreiro
- **Subtítulo:** Algoritmos Genéticos aplicados à Otimização de Estratégias em 100 Salas com Dados Reais do D&D 5e SRD
- **Identificação:** Grupo 7 — Inteligência Artificial II — FIB Bauru (2026)
- **Elemento Visual:** QR Code apontando para a Aplicação Web Pública no Streamlit Community Cloud e para o Repositório GitHub (`https://github.com/Duduzinhoextrem/Trabalho-IA-Grupo7`).

### Painel 2 (O Problema e o Dataset Oficial)
- **Desafio:** Sobreviver a 100 salas progressivas começando no Nível 1 com apenas uma espada básica, gerenciando atributos irreversíveis, economia com revenda a 40% e até 2 aliados dentre 5 classes.
- **Dados Reais:** 334 monstros coletados da **D&D 5e SRD API (2014)** (`CC-BY-4.0 / OGL 1.0a`).
- **Descobertas da EDA:** Correlação linear forte entre CR e HP ($r = 0,9404$), crescimento exponencial de XP ($\rho = 0,9995$) e independência entre CR e Destreza ($r = -0,0100$).

### Painel 3 (Como Funciona o Algoritmo Genético)
- **Cromossomo de 16 Genes:** Codifica pesos de Força/Vitalidade/Defesa do Guerreiro, prioridades de Mago/Arqueiro/Monge/Padre/Alquimista, pesos dos aliados, foco de equipamentos e limiares econômicos.
- **Operadores Evolutivos:** Seleção por torneio ($k=3$), cruzamento híbrido BLX-$\alpha$/uniforme, mutação gaussiana/discreta, reparo automático, elitismo e controle de diversidade.

### Painel 4 (Resultados dos Experimentos Reais)
- **Baseline Fixo (Equilibrado):** Avança em média **69,0 salas** na validação (`0%` de conclusão das 100 salas).
- **Algoritmo Genético (Campeão):** Avança **96,90 ± 2,66 salas** na validação (**+27,9 salas**, $p = 0,000166$) e **97,50 salas** em novas composições de monstros!
- **Descoberta da IA:** O AG descobriu que priorizar **Vitalidade/Defesa**, comprar **Armadura/Escudo** antes de armas caras e contratar o **Padre** (escolhido em 100% das execuções) supera builds puramente ofensivas.

### Painel 5 (Análise Crítica e Limitações)
- **Transparência Científica:** Comparação honesta com Busca Aleatória de mesmo orçamento (`240` avaliações), identificação do sobreajuste parcial (`gap = 5,13` salas em 5 sementes de treino) e análise do gargalo da Sala 25 quando os baús são desligados.

### Painel 6 (Contracapa — Equipe e Acesso)
- **Equipe Grupo 7:** Eduardo Lima, Fernando Mendes, Matheus Pereira, Reuel Lanzetti e Rogério Marcone.
- **Links e QR Codes:** App Streamlit interativo e repositório aberto no GitHub.

---

## 2. Carrossel de Instagram (8 Slides — Formato 1080×1350px)

- **Slide 1 (Capa):** *"Consegue vencer 100 salas de D&D começando apenas com uma espada básica? Nós colocamos um Algoritmo Genético para descobrir a estratégia perfeita!"* (Grupo 7 — IA II FIB).
- **Slide 2 (O Mito vs. Realidade):** *"Zero dados inventados! Coletamos e validamos os 334 monstros oficiais da API D&D 5e SRD (de Goblins CR 0.25 ao Tarrasque CR 30)."*
- **Slide 3 (Curiosidade da EDA):** *"Você sabia? No D&D 5e SRD, a Vida (HP) cresce linearmente com o Nível de Desafio ($r=0,94$), mas a Destreza tem correlação ZERO ($r=-0,01$)!"*
- **Slide 4 (O Jogo e a Economia):** *"Guerreiro Nv.1 + 5 Classes de Aliados (Mago, Arqueiro, Monge, Padre, Alquimista) + Mercado com perda de 60% na revenda. Cada decisão errada custa a vida!"*
- **Slide 5 (O DNA do Guerreiro):** *"Como transformar uma estratégia em código? Criamos um Cromossomo de 16 Genes que evolui por Seleção de Torneio, Cruzamento BLX-alpha, Mutação e Elitismo."*
- **Slide 6 (O Segredo que a IA Descobriu):** *"Enquanto humanos focam só em Ataque (Arqueiro + Mago) e morrem na Sala 69, o Algoritmo Genético descobriu a build imortal: Guerreiro Tanque + Padre Curandeiro (escolhido em 100% dos treinos!)."*
- **Slide 7 (Resultados Científicos):** *"Gráfico Real: Baseline Fixo (69,0 salas) vs. Estratégia Campeã do AG (96,9 salas em novas sementes e 97,5 salas em novas composições — $p < 0,001$!)."*
- **Slide 8 (Call to Action):** *"Teste sua estratégia manual contra a nossa IA agora pelo celular ou PC! Link na bio / QR Code."*

---

## 3. Roteiro de Vídeo Demonstrativo (1 a 3 Minutos — Tempo Alvo: 2m15s)

- **0:00 – 0:25 | Gancho e Problema (Eduardo):** Apresentação do projeto *Masmorra Genética (Grupo 7 — FIB)*, destacando o desafio de otimizar políticas em 100 salas sem inventar dados sintéticos.
- **0:25 – 0:55 | Dataset D&D 5e SRD e EDA na Página 2 do App (Matheus):** Demonstração rápida na tela da Página 2 do Streamlit filtrando os 334 monstros reais da API, mostrando a matriz de correlação e as anomalias tratadas (`vampire-mist`, conjuradores).
- **0:55 – 1:30 | Simulador de Combate e Masmorra na Página 3 (Fernando):** Execução ao vivo na Página 3 comparando a Estratégia Fixa (caindo antes da sala 80) com a Estratégia Otimizada pelo AG (chegando à Sala 100), inspecionando o log turno a turno e o link direto do monstro na API.
- **1:30 – 2:00 | Evolução Genética e Experimentos nas Páginas 4 e 5 (Reuel):** Exibição da evolução por geração no Modo Demonstração e das tabelas/gráficos dos 4 experimentos científicos (Mutação, População, Baselines e Generalização).
- **2:00 – 2:15 | Laboratório e Encerramento (Rogério):** Demonstração rápida do Laboratório (Página 6) com dificuldade `+15%` e convite para acessar a URL pública.

---

## 4. Estrutura de Slides para Apresentação da Banca (~40 Minutos)

| Bloco | Slides | Tempo | Responsável Sugerido | Conteúdo Principal |
| :--- | :---: | :---: | :---: | :--- |
| **1. Introdução e Problema** | 1 a 5 | 6 min | Rogério | Contexto acadêmico, diferença entre otimização de políticas por AG vs. ML supervisionado, regras da masmorra de 100 salas e Canvas do projeto. |
| **2. Engenharia de Dados (ETL) e EDA** | 6 a 12 | 8 min | Matheus | Arquitetura ETL da API D&D 5e SRD, licenciamento CC-BY-4.0, controle de versão SHA-256, estatísticas dos 334 monstros e as 4 descobertas empíricas da EDA. |
| **3. Simulador, Combate e Economia** | 13 a 18 | 7 min | Fernando | Camada de adaptação de atributos (`config/balance.json`), mecânica de linha de frente/retaguarda, 5 classes de aliados, mercado (revenda 40%) e garantias contra invulnerabilidade/loops. |
| **4. Algoritmo Genético** | 19 a 24 | 8 min | Eduardo | Representação do cromossomo de 16 genes, reparo de restrições, operadores (torneio, BLX-$\alpha$/uniforme, mutação, elitismo, controle de diversidade) e função fitness lexicográfica. |
| **5. Experimentos Científicos e Falhas** | 25 a 32 | 7 min | Reuel | Metodologia (separação treino/validação), resultados dos Experimentos 1, 2, 3 e 4, testes estatísticos, análise crítica do empate médio com Busca Aleatória e dominância do Padre. |
| **6. Demonstração ao Vivo (Web App)** | 33 a 35 | 4 min | Todos | Navegação ao vivo pelas 6 páginas da aplicação publicada no Streamlit Community Cloud (e teste com entrada nova no Laboratório). |

---

## 5. Instruções de Publicação no Streamlit Community Cloud e Contingência

### Passo a Passo para Publicação Pública (URL Pública)
1. Todos os arquivos necessários (`app.py`, `requirements.txt`, `.streamlit/config.toml`, `config/balance.json`, `data/processed/`, `data/experiments/`, `results/`, `src/`) estão versionados e prontos no repositório GitHub: `https://github.com/Duduzinhoextrem/Trabalho-IA-Grupo7`.
2. Acesse [https://share.streamlit.io/](https://share.streamlit.io/) e autentique-se com a conta GitHub proprietária/colaboradora do repositório (`Duduzinhoextrem`).
3. Clique em **"Create app"** $\rightarrow$ **"Yup, I have an app"**.
4. Preencha:
   - **Repository:** `Duduzinhoextrem/Trabalho-IA-Grupo7`
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL (sugerida):** `https://masmorra-genetica-grupo7.streamlit.app`
5. Clique em **"Deploy!"**. O Streamlit Community Cloud instalará automaticamente os pacotes de `requirements.txt` e servirá a aplicação para computadores e celulares.

> **Nota de Transparência (Seção 11):** Como a vinculação final da conta no painel web do Streamlit Community Cloud exige login interativo OAuth da conta GitHub do estudante no navegador, o repositório foi integralmente preparado e validado localmente, restando apenas o clique de ativação no painel `share.streamlit.io`.

### Plano de Contingência para o Dia da Apresentação (01/12/2026)
Caso ocorra falha de internet no auditório durante a banca:
1. O snapshot completo do dataset (`data/raw/monsters_raw_srd2014.json` e `data/processed/monsters_srd2014_processed.parquet`) e os resultados científicos (`data/experiments/scientific_experiments_v1.json`) já estão embutidos localmente no repositório, permitindo operação **100% offline** sem depender de conexão externa à API D&D 5e.
2. Basta executar `python -m streamlit run app.py` no notebook de apresentação para abrir exatamente a mesma aplicação interativa localmente.
