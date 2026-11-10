# Canvas Inicial do Projeto — Masmorra Genética

**Disciplina:** Inteligência Artificial II — 2026  
**Instituição:** Faculdades Integradas de Bauru (FIB)  
**Grupo:** 07 | **Posição no Sorteio:** 9 (Apresentação: 01/12/2026)  
**Integrantes:** Eduardo Coque Corrêa de Lima, Fernando Eduardo Motta Mendes, Matheus Alcântara Pereira, Reuel Vitor Lanzetti, Rogério Tiritan Marcone  

---

### Tabela 1 — Canvas Oficial do Projeto (Modelo Institucional)

| Campo | Preenchimento Oficial do Grupo 7 |
| :--- | :--- |
| **Tema/técnica** | **Algoritmos Genéticos** (Tema 9: *Evoluindo o Personagem Perfeito*). Otimização evolutiva de políticas de decisão para personagens em combates por turnos. |
| **Problema a resolver** | Determinar de forma autônoma como distribuir atributos, contratar classes de aliados e gerenciar economia de equipamentos para maximizar o avanço de um guerreiro em uma masmorra estocástica de 100 salas. |
| **Usuário/público** | Estudantes e pessoas interessadas em computação ou jogos que queiram entender algoritmos genéticos, além da banca avaliadora da disciplina. |
| **Entrada do sistema** | Configurações da política de estratégia: foco de distribuição de atributos do guerreiro (Força, Vitalidade, Defesa), prioridades de contratação de 5 classes de aliados, pesos de evolução dos aliados, prioridade de mercado (armas vs armaduras/escudos), reserva de ouro e limiares econômicos; semente (`seed`) da masmorra para geração procedural determinística. |
| **Saída esperada** | Relatório de jornada sala por sala (1 a 100) com combate detalhado, HP restante, nível, transações econômicas, taxa de conclusão das 100 salas, curva de convergência e diversidade populacional ao longo das gerações. |
| **Dataset/fonte** | Snapshot congelado de 334 registros da **D&D 5e SRD API** (`srd-2014-v1.0.0`), coletado em 29/10/2026. Fornece criaturas reais do SRD 5.1 (atributos, AC, HP, Challenge Rating, ações de dano). Fórmulas de combate, geração de salas e progressão são simulações versionadas do grupo (`balance-v1.0.0`). |
| **Baseline** | Dois baselines para comparação justa: <br>1. **Estratégia Fixa Heurística:** distribuição equilibrada (1/3 Força, 1/3 Vitalidade, 1/3 Defesa), reserva fixa de 40 moedas e prioridade Arqueiro/Mago.<br>2. **Busca Aleatória (Random Search):** amostragem uniforme de estratégias válidas com o mesmo orçamento exato de avaliações (240 avaliações). |
| **Hipóteses iniciais** | 1. O algoritmo genético terá desempenho maior que a política fixa.<br>2. A taxa de mutação afeta a diversidade genética e a velocidade de convergência.<br>3. Aumentar a dificuldade ou retirar os baús ajudará a revelar os limites da estratégia escolhida. |
| **Experimentos planejados** | • **E1:** Efeito de 3 taxas de mutação (2%, 10%, 25%) na diversidade e convergência.<br>• **E2:** Efeito de 3 tamanhos de população (12, 20, 40) sob orçamento equivalente de 240 avaliações.<br>• **E3:** Comparação controlada entre Heurística Fixa, Busca Aleatória e Algoritmo Genético em 7 repetições independentes com teste Mann-Whitney.<br>• **E4:** Teste de robustez e generalização fora da amostra (Holdout de sementes, pool alternativo, dificuldade +15%, sem baús).<br>• **E5 (Pré-registrado):** Avaliação em 20 sementes inéditas (401–420) com 10 repetições. |
| **Ideia do protótipo web** | Aplicação interativa em **Streamlit** com identidade visual de "Atlas de Expedição": modo de treino automático com visualização da evolução, jornada sala a sala com replay de combates, Bestiário com filtros e download de dados, tela de proveniência com verificação SHA-256 e Laboratório com parâmetros customizáveis para o Demo Challenge da banca. |
| **Divisão inicial de responsabilidades** | • **Eduardo:** Coordenação técnica, formulação matemática do cromossomo, operadores genéticos e integração do pipeline.<br>• **Matheus:** Coleta, limpeza e tratamento do dataset D&D 5e SRD, manifesto de proveniência e EDA.<br>• **Fernando:** Simulador de combate por turnos, sistema de economia, catálogo de equipamentos e interface Streamlit.<br>• **Rogério:** Canvas, Model Card oficial, Resumo Expandido e Diário de Uso de IA Generativa.<br>• **Reuel:** Ficha de experimentos, scripts de automação científica, análise estatística e materiais de apresentação. |

