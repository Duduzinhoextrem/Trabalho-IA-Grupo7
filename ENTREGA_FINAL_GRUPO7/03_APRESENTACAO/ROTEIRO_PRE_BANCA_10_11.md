> **Atenção: roteiro anterior com erros técnicos.** Use o [guia revisado](../../docs/FINALIZACAO/GUIA_PRE_BANCA_E_GITHUB.md). A descrição dos genes, do fitness e de algumas conclusões neste arquivo não corresponde ao código ou extrapola os resultados. As cópias DOCX e PDF também precisam ser revisadas antes do uso.

# ROTEIRO ANTERIOR DA PRÉ-BANCA (10/11 — VALIDAR)
## Linha de Congelamento Técnico: Código, Modelo e Protótipo
### Grupo 7 | Masmorra Genética — Inteligência Artificial II (FIB 2026)

**Data da Pré-banca:** 10 de Novembro de 2026  
**Duração Total:** 15 minutos cronometrados  
**Estrutura Oficial da Banca:**
- **10 minutos:** Apresentação pelo grupo (Problema, Dataset, Técnica, Principal Experimento e Protótipo ao vivo).
- **5 minutos:** Perguntas do professor, teste não preparado (surpresa) e feedback.

**Integrantes do Grupo 7:**
- Eduardo Coque Corrêa de Lima
- Fernando Eduardo Motta Mendes
- Matheus Alcântara Pereira
- Reuel Vitor Lanzetti
- Rogério Tiritan Marcone

---

## 1. Visão Geral da Linha de Congelamento Técnico

> **Definição da FIB:** *"Até esta data, código, modelo e protótipo deverão estar funcionalmente concluídos para todos os grupos. Depois disso, o foco será refinamento, correção, ensaio e comunicação."*

### Status do Grupo 7 na Pré-Banca:
- **Código:** 100% concluído, modularizado e testado (53 testes passando no Pytest).
- **Modelo (Algoritmo Genético):** 16 genes parametrizados, crossover BLX-α, mutação gaussiana, seleção por torneio e elitismo 10%.
- **Dataset:** 334 criaturas do D&D 5e SRD 2014, balanceamento de Desafio (ND 0 a 16) e integridade verificada por SHA-256.
- **Protótipo:** Streamlit rodando localmente (100% offline) com 7 abas funcionais, simulador visual e laboratório ao vivo.

---

## 2. Cronograma Minuto a Minuto da Apresentação (10 Minutos)

Para manter o tempo rigorosamente dentro dos **10 minutos**, o grupo dividirá a fala em **5 blocos de 2 minutos** (um para cada integrante):

```
[00:00 - 02:00] Integrante 1: O Problema Investigado & Contexto
[02:00 - 04:00] Integrante 2: O Dataset Externo e Tratamento
[04:00 - 06:00] Integrante 3: A Técnica — Algoritmo Genético & Cromossomo
[06:00 - 08:00] Integrante 4: O Principal Experimento & Resultados Científicos
[08:00 - 10:00] Integrante 5: Demonstração do Protótipo Funcionando ao Vivo
```

---

### BLOCO 1 (Minuto 0:00 a 2:00) — O Problema Investigado
**Responsável Sugerido:** Integrante 1 (ex: Eduardo Coque)

- **O que falar:**
  - *"Boa noite, professor e colegas. Somos o Grupo 7 e o nosso tema sorteado é Algoritmos Genéticos aplicado à evolução de estratégias de combate e sobrevivência em jogos procedurais."*
  - *"O problema investigado é guiar um guerreiro em uma masmorra hostil de 100 salas de dificuldade crescente, enfrentando encontros estocásticos de 1 a 3 criaturas."*
  - *"O desafio não é trivial: uma estratégia de força bruta pura falha nas salas intermediárias porque o herói fica sem recursos de cura ou armadura pesada contra monstros de Desafio elevado. O herói precisa tomar decisões interdependentes: como distribuir atributos, quando poupar ouro, que tipo de aliado contratar (Clérigo, Mago, Ladino, etc.) e em qual percentual de vida tomar poções."*
  - *"Trata-se de um problema de otimização combinatória em espaço contínuo com alta incerteza estocástica."*

---

### BLOCO 2 (Minuto 2:00 a 4:00) — O Dataset Externo
**Responsável Sugerido:** Integrante 2 (ex: Fernando Motta)

- **O que falar:**
  - *"Para garantir rigor e realismo, não utilizamos números fictícios: nosso ambiente de combate é alimentado por um dataset externo legítimo com 334 criaturas extraídas do System Reference Document (SRD) de Dungeons & Dragons 5ª Edição (2014), sob licença aberta OGL v1.0a."*
  - *"Os monstros variam do Nível de Desafio (ND) 0 até ND 16, cobrindo pontos de vida (PV), classe de armadura (CA) e ataques canônicos."*
  - *"Realizamos tratamento de dados e validações estritas de negócio: remoção de atributos nulos, tipagem estrita e verificação criptográfica do arquivo bruto com hash SHA-256 (`51a00f47...`)."*
  - *"A masmorra divide a jornada em 5 faixas equilibradas: salas 1-20 (ND baixo), até as salas 81-100 (chefes e dragões). Separamos rigidamente as sementes de treino (101 a 105) das sementes de validação (201 a 210 e 401 a 420), garantindo que a IA nunca seja avaliada nos mesmos desafios onde treinou."*

---

### BLOCO 3 (Minuto 4:00 a 6:00) — A Técnica: Algoritmo Genético
**Responsável Sugerido:** Integrante 3 (ex: Matheus Alcântara)

- **O que falar:**
  - *"Por que Algoritmo Genético? Porque não existe um 'gabarito' de ações ótimas a priori para aprendizado supervisionado, e o espaço de busca é vasto e não-linear."*
  - *"Modelamos a política de decisão como um cromossomo real de 16 genes normalizados entre 0 e 1:*
    - *Genes 0 a 3: Pesos de atributos (Força, Destreza, Constituição, Sabedoria).*
    - *Genes 4 a 8: Afinidade de contratação de 5 classes de companheiros.*
    - *Genes 9 a 12: Gatilhos econômicos e de uso de poções.*
    - *Genes 13 a 15: Postura tática (agressiva, equilibrada ou defensiva).*"
  - *"Operadores Genéticos:*
    - *Inicialização: Amostragem por Hipercubo Latino para dispersão uniforme.*
    - *Seleção: Torneio com k=3.*
    - *Cruzamento: Recombinação BLX-α com alfa=0.5, permitindo explorar além dos valores dos pais sem sair dos limites canônicos.*
    - *Mutação: Perturbação gaussiana aditiva com clamping estrito.*
    - *Elitismo: Preservação garantida dos melhores 10% da população."*
  - *"Função de Aptidão (Fitness): Dá prioridade hierárquica absoluta às salas sobrevividas ($10.000 \times \text{salas}$), somada à saúde restante e ouro poupado, aplicando forte penalidade por morte precoce."*

---

### BLOCO 4 (Minuto 6:00 a 8:00) — O Principal Experimento e Resultados Científicos
**Responsável Sugerido:** Integrante 4 (ex: Reuel Vitor)

- **O que falar:**
  - *"No Experimento E3, comparamos o Algoritmo Genético contra dois baselines sob o mesmo orçamento computacional estrito de 240 avaliações de masmorra:*
    - *Heurística Fixa: alcançou média de 69,00 salas e 0% de taxa de conclusão (morre invariavelmente nas salas 70-80).*
    - *Busca Aleatória: média de 92,27 salas e 25,71% de conclusão.*
    - *Algoritmo Genético (mutação 10%): média de 91,27 salas e 28,57% de conclusão (com o melhor indivíduo alcançando 96,9 salas e 40% de conclusão).*"
  - *"O teste estatístico de Mann-Whitney resultou em p = 0,748, indicando equivalência estatística entre o AG e a busca aleatória sob esse orçamento."*
  - *"Em vez de esconder esse dado ou manipular o teste, adotamos rigor científico pleno: em 16 dimensões, sob apenas 240 avaliações, a amostragem aleatória uniforme explora o espaço de forma agressiva sem se prender a ótimos locais, enquanto o AG sofreu leve sobreajuste às 5 sementes de treino."*
  - *"Para aprofundar, executamos o experimento complementar E5 com 20 novas sementes inéditas: quando elevamos a taxa de mutação do AG para 25%, o AG subiu sua média de 90,38 para 92,49 salas, demonstrando a importância de evitar a perda de diversidade genética."*

---

### BLOCO 5 (Minuto 8:00 a 10:00) — Demonstração do Protótipo ao Vivo
**Responsável Sugerido:** Integrante 5 (ex: Rogério Tiritan)

- **O que fazer e falar (na tela do computador projetada):**
  1. **Aba Aventura (1 minuto):**
     - *"Aqui está o nosso simulador em Streamlit rodando 100% offline. Vou carregar a estratégia campeã evoluída pelo AG e clicar em 'Executar Jornada'. O log sala a sala mostra o guerreiro comprando poções, contratando o Clérigo nas salas intermediárias e derrotando dragões nas salas 90+. O herói concluiu com sucesso as 100 salas."*
  2. **Aba Como Funciona -> Passo a Passo do Algoritmo (30 segundos):**
     - *"Implementamos um visualizador didático da anatomia dos 16 genes e da reprodução genética ao vivo. Aqui o professor pode ver dois pais recombinando seus cromossomos via BLX-α e sofrendo mutação gaussiana para gerar o filho."*
  3. **Aba Laboratório (30 segundos):**
     - *"E no Laboratório Interativo, podemos reconfigurar taxas de mutação, população e sementes em tempo real. O protótipo está 100% funcional e pronto para responder a qualquer teste surpresa do professor."*

---

## 3. Preparação para os 5 Minutos Finais: Perguntas, Teste Surpresa e Feedback

Os 5 minutos finais são o momento mais crítico da pré-banca. O professor testará a autenticidade e a resiliência do sistema com perguntas e um **teste não preparado**.

---

### Cenário de Teste Surpresa 1: O Professor Pede uma Semente Inédita
*Exemplo: "Rode agora a masmorra com a semente 777 ou 999 na minha frente."*

- **O que fazer na hora:**
  1. No Streamlit, vá na barra lateral ou na página **"Aventura"** ou **"Laboratório"**.
  2. Altere o campo **Semente da Masmorra** para o número que o professor pediu (ex: `777`).
  3. Clique em **"Iniciar Aventura"** (ou **"Simular"**).
  4. Mostre que em menos de 2 segundos a simulação estocástica é resolvida e o gráfico de vida/salas é atualizado.
- **O que responder verbalmente:**
  - *"O motor é totalmente determinístico por semente: o gerador pseudoaleatório constrói a masmorra e os combates de acordo com a semente solicitada, garantindo reprodutibilidade científica instantânea."*

---

### Cenário de Teste Surpresa 2: O Professor Pede um Parâmetro Extremo
*Exemplo: "O que acontece se colocar taxa de mutação em 50% ou população de apenas 4 indivíduos?"*

- **O que fazer na hora:**
  1. Vá na aba **"Laboratório"**.
  2. Ajuste o slider de **Taxa de Mutação** para `0.50` (ou arraste o tamanho populacional para o mínimo).
  3. Clique em **"Evoluir População"**.
- **O que responder verbalmente:**
  - *"Como a teoria de Algoritmos Genéticos prevê, com mutação em 50% o algoritmo perde a capacidade de explorar blocos construtivos e degenera em uma caminhada aleatória com alto ruído destrutivo. Já com população muito pequena (ex: 4), ocorre perda drástica de diversidade genética e estagnação precoce em mínimos locais."*

---

### Pergunta Difícil 1: "Por que a Busca Aleatória foi tão bem contra o Algoritmo Genético?"
- **Resposta Perfeita (Sem titubear):**
  - *"Professor, essa é a nossa principal constatação acadêmica e científica. Em espaços contínuos com 16 parâmetros e sob um orçamento computacional baixo de 240 avaliações, a Busca Aleatória não sofre viés e amostra uniformemente todo o espaço. O AG tradicional, com mutação baixa (10%), treinou em 5 sementes e sofreu um leve sobreajuste amostral. Quando testamos o AG com mutação de 25% no experimento E5, o algoritmo manteve a exploração ativa e aumentou a média em sementes inéditas. Decidimos manter a honestidade científica dos dados em vez de falsear os resultados."*

---

### Pergunta Difícil 2: "O Guerreiro é imortal? Vocês não trapacearam no combate?"
- **Resposta Perfeita:**
  - *"Não, professor. O código de combate respeita estritamente as regras de D&D 5e (D20 + bônus de acerto contra Classe de Armadura). Inclusive, em nossa Ficha de Experimentos, documentamos 3 casos de falha reais: por exemplo, quando o guerreiro campeão enfrentou dano massivo concentrado (burst damage) de dois monstros na sala 60 e morreu antes de conseguir acionar sua poção de cura. Além disso, temos o teste automatizado `test_06` que verifica matematicamente que o herói não possui invulnerabilidade."*

---

## 4. Quadro para Anotação de Feedback do Professor

Utilize a tabela abaixo durante a pré-banca para registrar os apontamentos do professor para os ajustes finais até 17/11:

| Item Avaliado | Avaliação do Professor (OK / Ajustar) | Comentários e Recomendações da Banca |
|---|:---:|---|
| **Problema & Contexto** | [ &nbsp; ] | |
| **Dataset e Integridade** | [ &nbsp; ] | |
| **Modelagem do AG** | [ &nbsp; ] | |
| **Rigor dos Experimentos** | [ &nbsp; ] | |
| **Estabilidade do Protótipo** | [ &nbsp; ] | |
| **Teste Surpresa Executado** | [ &nbsp; ] Semente / Parâmetro testado: | |
| **Orientações para 17/11** | [ &nbsp; ] | |

---

## 5. Checklist de Contingência para a Pré-Banca

- [x] Streamlit rodando localmente em `http://localhost:8501`.
- [x] Modo offline verificado: nenhuma requisição externa de rede é necessária.
- [x] Arquivo `executar_prototipo.bat` pronto na raiz para reiniciar o app em 1 segundo se fechar.
- [x] Slides em PDF (`Apresentacao_Grupo7.pdf`) abertos como plano B caso o projetor falhe.
- [x] Todos os 5 integrantes com suas falas de 2 minutos decoradas e alinhadas.
