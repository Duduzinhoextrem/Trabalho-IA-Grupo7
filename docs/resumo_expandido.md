# Masmorra Genética: evolução de estratégias para um personagem em combate simulado

Eduardo Coque Corrêa de Lima; Fernando Eduardo Motta Mendes; Matheus Alcântara Pereira; Reuel Vitor Lanzetti; Rogério Tiritan Marcone.

Este texto é um rascunho de conteúdo. A equipe deve revisá-lo e formatá-lo no modelo vigente de duas páginas da Jornada Científica da FIB antes da entrega.

## Introdução e objetivo

Algoritmos genéticos são métodos de busca inspirados em processos evolutivos. Eles combinam soluções candidatas e pequenas alterações para explorar um espaço de possibilidades. Neste trabalho, investigamos seu uso para escolher políticas de evolução de um personagem em uma masmorra simulada de 100 salas. Uma política define prioridades para distribuir atributos, contratar aliados e comprar equipamentos. O objetivo é comparar o avanço obtido pelo algoritmo com uma estratégia fixa e com uma busca aleatória, além de investigar o efeito de parâmetros e mudanças no ambiente.

## Dados e método

O projeto utiliza uma cópia congelada de 334 registros de criaturas fictícias da D&D 5e SRD API, coletada em 29 de outubro de 2026. O tratamento normaliza campos aninhados e estima o dano esperado de ações interpretáveis. Cada inimigo da simulação mantém referência ao registro de origem. As regras de combate, os equipamentos e as recompensas foram definidos pelo grupo; não se trata de um conjunto de partidas reais ou de uma reprodução completa de D&D.

Na análise exploratória, a correlação de Pearson entre nível de desafio e pontos de vida foi 0,9404. A experiência apresentou mediana de 450 e máximo de 155.000 pontos, justificando a avaliação de uma transformação sublinear para a recompensa do simulador. Também foram identificados cinco registros sem dano direto reconhecido nas ações. Quatro formas passivas ou alternativas foram excluídas da seleção de encontros, e o simulador utiliza uma estimativa própria quando o dano não pode ser obtido diretamente.

Cada estratégia é representada por 16 valores. O algoritmo usa seleção por torneio, cruzamento, mutação, elitismo e controle de diversidade. A métrica principal é a média de salas concluídas; a taxa de conclusão das 100 salas é reportada separadamente. Foram usadas cinco sementes na otimização e dez na validação, sem sobreposição. A comparação com a busca aleatória empregou 240 avaliações efetivas por repetição para cada método, considerando que indivíduos preservados pelo elitismo não são reavaliados.

## Resultados e discussão

Na versão `v2` dos experimentos, a estratégia fixa concluiu em média 69,00 salas no conjunto de validação. Em sete repetições, a busca aleatória obteve média de 92,27 salas e o algoritmo genético, 91,27; as taxas médias de conclusão foram, respectivamente, 25,71% e 28,57%. Nesse conjunto, a busca aleatória obteve maior média de salas, enquanto o algoritmo genético obteve maior taxa média de conclusão. A diferença observada não garante superioridade geral de nenhum método.

Entre as taxas de mutação avaliadas, 25% obteve a maior média de validação nesta execução (95,06 salas), diante de 92,12 para 10% e 91,28 para 2%. A estratégia individual selecionada no treino concluiu em média 96,9 salas na validação padrão, com quatro conclusões completas em dez tentativas. Em cenários com dificuldade 15% maior ou sem baús, suas médias foram 73,4 e 80,0 salas, respectivamente. A ficha de experimentos registra os orçamentos, sementes, hipóteses e três situações de falha.

## Conclusão

O algoritmo genético encontrou estratégias competitivas dentro do simulador, mas a busca aleatória também alcançou bons resultados. O desempenho depende das regras escolhidas, do conjunto de criaturas e das sementes. O conjunto de validação é reutilizado em vários experimentos, e a amostra de treino é pequena; por isso, os resultados não devem ser generalizados para outros jogos ou apresentados como uma estratégia ótima universal. Como próximos passos, o grupo pode testar mais sementes independentes e investigar o impacto das regras de economia e cura.

## Referências essenciais

- 5e-bits. D&D 5e SRD API. Disponível em: <https://docs.dnd5eapi.co/>.
- Wizards of the Coast. System Reference Document 5.1. Disponível em: <https://www.dndbeyond.com/srd>.
- Resultados e código do projeto: `data/experiments/scientific_experiments_v2.json` e repositório do Grupo 7.
