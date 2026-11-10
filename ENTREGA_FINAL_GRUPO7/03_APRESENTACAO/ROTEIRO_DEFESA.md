# Roteiro Oficial de Defesa e Arguição — Masmorra Genética

**Disciplina:** Inteligência Artificial II — 2026  
**Instituição:** Faculdades Integradas de Bauru (FIB)  
**Grupo:** 07 | **Apresentação:** 01/12/2026 (40 a 45 minutos)  
**Integrantes e Divisão de Fala:**
- **Eduardo Coque Corrêa de Lima** (Abertura, Algoritmo Genético, Operadores e Demonstração do Código) — ~9 min
- **Matheus Alcântara Pereira** (Dados, API D&D 5e SRD, Tratamento ETL e EDA) — ~6 min
- **Fernando Eduardo Motta Mendes** (Simulador de Combate, Economia e Protótipo ao Vivo) — ~8 min
- **Rogério Tiritan Marcone** (Contexto do Problema, Canvas, Model Card e Ética de IA) — ~7 min
- **Reuel Vitor Lanzetti** (Metodologia Experimental, Baselines, Resultados E1 a E5 e Casos de Falha) — ~10 min

---

## 1. Organização do Tempo da Palestra (Total: ~40 minutos de núcleo)

| Bloco | Tempo | Responsável Principal | Tópicos Centrais |
| :--- | :---: | :--- | :--- |
| **1. Abertura & Pergunta Central** | 3 min | Eduardo | Pergunta motivadora: "Quem chega à centésima sala?". Apresentação do tema. |
| **2. Problema & Justificativa** | 4 min | Rogério | Regras da masmorra, espaço de busca combinatorial e por que usar AG em vez de força bruta. |
| **3. Conceitos e Algoritmo** | 9 min | Eduardo | Analogia biológica simples + formulação matemática dos 16 genes, seleção, BLX-α, mutação gaussiana e elitismo. |
| **4. Dados e Pré-processamento** | 6 min | Matheus | D&D 5e SRD 2014, validação SHA-256, correlações da EDA, assimetria de XP e limpeza de monstros passivos. |
| **5. Experimentos e Comparações** | 8 min | Reuel | Orçamento de 240 avaliações, resultados E1, E2, E3 (p=0,748) e E5 (sementes inéditas). |
| **6. Análise de Falhas e Limitações** | 4 min | Reuel | Os 3 casos reproduzidos de derrota (Black Pudding dif +15%, Succubus sem baús, Dragão Vermelho). |
| **7. Protótipo ao Vivo & Demo Challenge** | 5 min | Fernando | Demonstração no Streamlit com sorteio de semente fornecida pela banca ou plateia. |
| **8. Conclusão & Perguntas** | 3 min | Rogério / Todos | Aprendizados sobre honestidade metodológica e abertura para arguição. |

---

## 2. Perguntas Obrigatórias da Disciplina (Respostas Técnicas Prontas)

### P1: Por que essa técnica foi escolhida?
**Resposta:** O problema de otimização de decisões em 100 salas não possui exemplos supervisionados de partidas humanas prévias. O espaço combinatorial possui 16 dimensões mistas (pesos contínuos e escolhas discretas) com descontinuidades causadas pela estocasticidade das rolagens de combate. Algoritmos genéticos são altamente indicados para explorar espaços não-lineares sem exigência de derivadas, recombinando blocos construtivos viáveis de alocação de atributos e mercado.

### P2: Qual seria uma alternativa mais simples?
**Resposta:** Comparamos com uma regra fixa equilibrada, que teve média de 69 salas e não concluiu as 100 salas nas sementes avaliadas. Também usamos busca aleatória com o mesmo orçamento de 240 avaliações do AG; ela teve média de 92,27 salas.

### P3: Qual foi o maior problema encontrado nos dados?
**Resposta:** Três problemas centrais no snapshot da D&D SRD API: (1) forte assimetria na experiência (XP com mediana 450 e máximo de 155.000), o que exigiu transformação sublinear logarítmica para evitar que um único monstro concedesse 20 níveis de uma vez; (2) ausência de dano direto interpretável em 5 monstros, com exclusão de 4 criaturas passivas sem ataque (`frog`, `sea-horse`, `shrieker`, `vampire-mist`); e (3) ausência do campo opcional `subtype` em 258 dos 334 registros.

### P4: O que aconteceria se uma variável importante fosse removida?
**Resposta:** Se removermos a variável de contratação de aliados (`enable_allies=False`), o guerreiro enfrenta todas as salas sozinho. Sem a divisão de linha de frente do Monge e sem o suporte vital de cura do Padre, o desgaste cumulativo derruba o alcance do guerreiro mesmo com atributos máximos, não passando da Sala 40 em testes exploratórios. Se removermos a reserva de ouro (`min_gold_reserve`), o combatente gasta todo o ouro imediatamente em armas e fica sem fundos para comprar armaduras quando surgem no mercado.

### P5: Como vocês evitaram avaliar apenas no conjunto de treinamento?
**Resposta:** Nos experimentos, usamos as sementes 101 a 105 para treino e 201 a 210 para validação. Como reutilizamos o conjunto de validação em várias análises, pré-registramos o E5 com outras 20 sementes, de 401 a 420. Isso permite avaliar o comportamento em outras masmorras, mas não elimina todas as dúvidas sobre generalização.

### P6: Qual métrica foi priorizada e por quê?
**Resposta:** Priorizamos a **média de salas concluídas** (de 0 a 100), pois reflete a distância real percorrida na masmorra. A taxa de conclusão integral (%) foi reportada como métrica secundária, pois é binária e não penaliza proporcionalmente quem cai na sala 2 ou na sala 99. Pontos de vida e ouro atuam apenas como termos de desempate infinitesimal na fitness com peso total máximo de 0,009, garantindo que o avanço de salas seja a prioridade absoluta.

### P7: Onde o modelo mais errou?
**Resposta:** No E5, a busca aleatória teve média maior que o AG com mutação de 10% (p = 0,021), mas o experimento não identifica a causa da diferença. Também observamos quedas no E4: sem baús, a média da estratégia escolhida caiu 16,9 salas, com uma derrota na sala 26; com dificuldade aumentada, ela foi derrotada na sala 25 em um dos testes contra Black Pudding.

### P8: Que mudança poderia melhorar o projeto?
**Resposta:** (1) Expandir o conjunto de treinamento de 5 para 20 masmorras dinâmicas por geração; (2) implementar operadores meméticos (busca local tipo hill-climbing após recombinação); e (3) adotar políticas dinâmicas dependentes de estado (onde as decisões de compra mudam em tempo real conforme a vida atual do guerreiro, e não como uma regra estática pré-estabelecida).

### P9: Como o protótipo transforma o modelo em aplicação compreensível?
**Resposta:** O protótipo em Streamlit mostra o mapa da masmorra e permite acompanhar os combates, consultar as criaturas e experimentar estratégias. A aba Como funciona explica os genes e os operadores, enquanto o Laboratório permite mudar condições como semente, dificuldade, recuperação e presença de baús ou aliados.

---

## 3. Procedimento Operacional para o Demo Challenge (Ao Vivo)

1. **Abrir a aba "Laboratório" no Streamlit:**
   - Solicitar à banca ou à plateia um número de semente (ex: semente 777 ou a data de nascimento de alguém).
   - Ajustar um multiplicador de dificuldade (ex: 120% ou recuperação de 15%).
2. **Executar a simulação comparativa:**
   - Clicar em "Comparar neste cenário".
   - A tela apresenta o gráfico de vida e as salas atingidas pela estratégia do AG e pela estratégia fixa.
3. **Interpretação técnica obrigatória (sem prometer vitória cega):**
   - *"Nesta masmorra, as duas estratégias enfrentaram o mesmo cenário. O resultado pode mudar com a semente e as regras. Uma única comparação ajuda a observar o comportamento, mas não basta para concluir qual método é melhor em geral."*

---

## 4. Plano de Contingência Offline (Sem Internet)

- O aplicativo Streamlit não consulta a API externa em tempo de execução: o snapshot `monsters_raw_srd2014.json` e os dados tratados em parquet/csv estão armazenados localmente no repositório.
- Para rodar sem qualquer conexão de rede:
  ```bash
  python -m streamlit run app.py --server.port 8599 --server.headless true
  ```
- Os slides em PDF e o vídeo MP4 na pasta `ENTREGA_FINAL_GRUPO7/` podem servir de apoio se a conexão falhar. É preciso ter um equipamento com bateria para usá-los em caso de falta de energia.
