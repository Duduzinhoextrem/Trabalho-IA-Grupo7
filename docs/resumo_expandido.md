# Masmorra Genética: Otimização Evolutiva de Políticas de Combate em Ambiente Procedural

**Autores:** Eduardo Coque Corrêa de Lima¹, Fernando Eduardo Motta Mendes¹, Matheus Alcântara Pereira¹, Reuel Vitor Lanzetti¹, Rogério Tiritan Marcone¹  
¹Faculdades Integradas de Bauru (FIB) — Curso de Ciência da Computação  
Disciplina de Inteligência Artificial II — 2026

---

## 1. Introdução

Algoritmos genéticos (AGs) são técnicas de busca inspiradas em processos de seleção e hereditariedade. Eles permitem testar combinações de decisões quando examinar todas as possibilidades é difícil, como ocorre em jogos com muitos atributos e encontros variados.

O projeto Masmorra Genética usa um AG para buscar estratégias para um guerreiro em uma masmorra de 100 salas de dificuldade crescente. Em cada sala, ele enfrenta de uma a três criaturas com atributos obtidos de uma base externa. Ao longo da jornada, precisa administrar a vida e escolher como investir o ouro em equipamentos e aliados.

## 2. Objetivos

O objetivo é avaliar se um algoritmo genético, com genes contínuos e um gene discreto, encontra estratégias melhores que uma regra fixa de alocação equilibrada. Também comparamos seu desempenho e sua diversidade com uma busca aleatória, usando o mesmo orçamento de avaliações para as duas buscas.

Como objetivos específicos, o trabalho busca:
1. Caracterizar o impacto de diferentes taxas de mutação (2%, 10% e 25%) na preservação da diversidade genética e na mitigação de convergência prematura;
2. Analisar o comportamento de diferentes distribuições de população (12, 20 e 40 indivíduos) sob orçamento computacional equiparado (240 avaliações);
3. Avaliar a capacidade de generalização e robustez da melhor política evoluída em conjuntos de masmorras nunca observadas durante o treino e sob variações adversas nas regras do simulador.

## 3. Metodologia

O projeto reúne preparação dos dados, implementação do algoritmo e avaliação das estratégias.

### 3.1. Base de Dados Externa e Pré-processamento
Os atributos dos inimigos vêm de uma cópia local de 334 criaturas da edição 2014 da *D&D 5e SRD API* (`srd-2014-v1.0.0`). A coleta ocorreu em 29/10/2026, e o SHA-256 do arquivo bruto é `51a00f4785dcf07fcb4056cd97eaa1eb5b2ba0c235d2b7d5b2762a772691d397`. O conteúdo do SRD está disponível sob a licença Creative Commons Attribution 4.0.

Na etapa de tratamento de dados (ETL), estruturas JSON aninhadas foram normalizadas em tabelas relacionais. A análise exploratória (EDA) revelou forte correlação de Pearson entre *Challenge Rating* (CR) e pontos de vida ($r = 0,9404$), ausência de correlação linear com destreza ($r = -0,0100$) e acentuada assimetria na distribuição de pontos de experiência (mediana 450 XP; máximo 155.000 XP), motivando a adoção de uma função de recompensa sublinear com amortecimento logarítmico para nivelar a curva de progressão do guerreiro. Quatro criaturas passivas não-ofensivas (`frog`, `sea-horse`, `shrieker` e `vampire-mist`) foram filtradas do catálogo de combate.

### 3.2. Representação Cromossômica e Operadores Genéticos
Cada política de decisão é codificada em um cromossomo de **16 genes**:
- **Genes 0, 1 e 2 (Contínuos, soma normalizada = 1,0):** Pesos de alocação de atributos do guerreiro (Força, Vitalidade e Defesa).
- **Genes 3 a 7 (Contínuos, intervalo [0, 1]):** Vetor de prioridades de contratação das 5 classes de aliados (Mago, Arqueiro, Monge, Padre e Alquimista).
- **Genes 8, 9 e 10 (Contínuos, soma normalizada = 1,0):** Pesos de desenvolvimento dos aliados (Poder Ofensivo, Vitalidade e Defesa).
- **Gene 11 (Contínuo [0, 1]):** Prioridade entre equipamentos ofensivos (armas) e defensivos (armaduras e escudos).
- **Gene 12 (Discreto binário {0, 1}):** Prioridade temporal de contratação de aliados antes da compra de armaduras.
- **Gene 13 (Contínuo [0, 120]):** Reserva financeira mínima de ouro para contingências.
- **Genes 14 e 15 (Contínuos [1,0, 1,8]):** Limiares de multiplicador de segurança para compras no mercado.

A população inicial é construída via amostragem estratificada (*Latin Hypercube Sampling*). O processo evolutivo emprega **seleção por torneio** ($k=3$), **cruzamento híbrido BLX-$\alpha$** ($\alpha=0,25$) para genes contínuos com operador uniforme para o gene discreto, **mutação gaussiana** ($\sigma = 0,18$ da amplitude do gene) com inversão bit-flip no gene discreto, além de **elitismo rígido de 2 indivíduos**. O controle de diversidade monitora a dispersão euclidiana normalizada e realiza reposição de clones por operadores de mutação intensiva quando o índice de diversidade cai abaixo do limiar crítico de 0,06.

### 3.3. Função de Aptidão (Fitness) e Protocolo Experimental
A aptidão prioriza a média de salas concluídas nas masmorras de treinamento, com sementes de 101 a 105. Vida e ouro restantes recebem um bônus conjunto de até 0,009, menor que o ganho de uma sala em uma das sementes usadas. Indivíduos preservados pelo elitismo não são reavaliados. Na comparação principal, o AG e a busca aleatória usam 240 avaliações da função objetivo por repetição.

## 4. Resultados e Discussão

Os experimentos foram conduzidos em rodadas independentes com sementes e orçamentos controlados.

### 4.1. Efeito dos Hiperparâmetros de Mutação e População
No E1, com cinco repetições e 240 avaliações, a mutação de 25% teve média de 95,06 ± 2,02 salas e 36% de conclusão na validação (sementes 201–210). As taxas de 10% e 2% tiveram médias de 92,12 ± 3,42 e 91,28 ± 3,31 salas, com 20% e 28% de conclusão, respectivamente. A diversidade final foi 0,0346 com mutação de 2% e 0,1104 com 25%; a convergência média ocorreu na 5ª geração para 2% e na 8ª para 25%. No E2, a população de 40 indivíduos teve média de 89,56 ± 3,43 salas, contra 86,82 com 20 indivíduos e 86,28 com 12. Esses resultados descrevem as configurações testadas.

### 4.2. Comparação com Baselines (Experimento 3)
Em 7 repetições independentes com orçamento pareado de 240 avaliações por execução, observou-se:
- **Estratégia Fixa Heurística:** Média de 69,00 salas na validação (0,00% de conclusão integral).
- **Busca Aleatória (Random Search):** Média de **92,27 ± 4,16 salas** (25,71% de conclusão integral).
- **Algoritmo Genético (mutação 10%):** Média de **91,27 ± 4,11 salas** (28,57% de conclusão integral).

O teste de Mann-Whitney resultou em $U = 21,5$ e $p = 0,748053$; o teste t de Welch resultou em $t = -0,4188$ e $p = 0,682779$. Nessa comparação, não encontramos evidência suficiente de diferença entre o AG e a busca aleatória. Isso não demonstra que os métodos sejam equivalentes. A melhor estratégia individual selecionada no treino atingiu média de 96,9 salas e concluiu 4 das 10 masmorras de validação. Esse resultado individual não deve ser confundido com a média das sete repetições.

### 4.3. Experimento Adicional E5 em Sementes Inéditas (401–420)
Para investigar o efeito da mutação em outras masmorras, fizemos o experimento pré-registrado E5, com dez repetições de 240 avaliações e validação em 20 sementes ainda não usadas, de 401 a 420. O AG com mutação de 25% alcançou 92,49 ± 2,80 salas e 19,0% de conclusão; com mutação de 10%, alcançou 90,38 ± 3,83 salas e 14,5% de conclusão. A diferença entre as duas taxas não foi conclusiva ($p = 0,241$; IC 95% [-0,86, +5,13]). A busca aleatória teve média de 94,56 ± 2,42 salas e 20,0% de conclusão, acima do AG com mutação de 10% nessa comparação ($p = 0,021$). Os resultados não estabelecem a causa das diferenças.

### 4.4. Robustez e Casos Limite de Falha (Experimento 4)
A estratégia escolhida teve média de 73,4 salas com dificuldade 15% maior e de 80,0 sem baús. Entre os casos analisados, houve uma derrota na sala 25 contra `Black Pudding` e outra na sala 26 contra `Succubus/Incubus`. Com uma composição alternativa de criaturas nas sementes 301–310, a média foi de 94,4 salas. As mudanças de dificuldade e de recursos mostram limites da estratégia nos cenários testados.

## 5. Conclusão

O AG encontrou estratégias que, no E3, avançaram em média mais salas que a regra fixa. A melhor estratégia individual concluiu quatro das dez masmorras de validação, mas o AG não apresentou vantagem clara sobre a busca aleatória no orçamento de 240 avaliações. O desempenho também caiu quando alteramos a dificuldade e a disponibilidade de baús. Esses resultados dependem das regras do simulador e das sementes usadas. Entre as possibilidades de continuação estão ampliar o conjunto de treino e investigar uma representação dinâmica ou uma abordagem híbrida com aprendizado por reforço.

## 6. Referências Essenciais

1. 5E-BITS. **D&D 5e SRD API Documentation**. Disponível em: <https://docs.dnd5eapi.co/>. Acesso em: 29 out. 2026.
2. EIBEN, A. E.; SMITH, J. E. **Introduction to Evolutionary Computing**. 2. ed. Berlin: Springer, 2015.
3. GOLDBERG, D. E. **Genetic Algorithms in Search, Optimization, and Machine Learning**. Boston: Addison-Wesley, 1989.
4. RUSSELL, S.; NORVIG, P. **Inteligência Artificial: Uma Abordagem Moderna**. 4. ed. Rio de Janeiro: GEN LTC, 2022.
5. WIZARDS OF THE COAST. **System Reference Document 5.1 (SRD 5.1)**. Wizards of the Coast LLC, 2016. Disponível em: <https://www.dndbeyond.com/srd>. Acesso em: 29 out. 2026.
