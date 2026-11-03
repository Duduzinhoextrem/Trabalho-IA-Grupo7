# Canvas do projeto — Masmorra Genética

| Campo | Definição |
| --- | --- |
| Tema e técnica | Algoritmos genéticos aplicados à evolução de estratégias para um personagem. |
| Problema | Investigar quais escolhas de evolução, contratação e equipamentos ajudam um guerreiro a avançar em uma masmorra simulada de 100 salas. |
| Público | Pessoas interessadas em jogos e estudantes sem conhecimento prévio de IA; também a banca, que precisa verificar método e resultados. |
| Entrada | Foco dos atributos, aliado preferido, prioridade no mercado e número da masmorra; no laboratório, também as condições de simulação. |
| Saída | Jornada sala por sala, decisões e estado do guerreiro, comparação com outras estratégias e resultados dos experimentos. |
| Dataset | Snapshot de 334 criaturas da D&D 5e SRD API, com origem, data, validação e atribuição no manifesto em `data/metadata/`. |
| Baselines | Estratégia fixa equilibrada e busca aleatória de estratégias válidas. |
| Hipóteses | Taxa de mutação e população podem alterar os resultados; o AG pode encontrar estratégias competitivas; mudanças nas condições podem reduzir seu desempenho. |
| Experimentos | Mutação, tamanho da população, comparação com baselines e teste de generalização. Os dados e interpretações estão na ficha de experimentos. |
| Protótipo web | Streamlit com busca automática por uma estratégia que vença as 100 salas escolhidas, aventura guiada, explicação do algoritmo, treinamento demonstrativo, bestiário, resultados e laboratório. A masmorra escolhida faz parte da busca interativa. |
| Limitações | Regras simplificadas, poucas sementes de treino, validação reutilizada entre experimentos e resultados dependentes do balanceamento. |

## Organização inicial

- Eduardo: coordenação técnica, algoritmo genético e integração.
- Matheus: dados, coleta, tratamento e análise exploratória.
- Fernando: simulador, combate, interface e integração.
- Rogério: Canvas, metodologia, Model Card e resumo.
- Reuel: experimentos, análise de resultados e materiais de apresentação.

A divisão é uma proposta. Todos precisam conhecer as decisões e participar da validação do trabalho. O PDF preenchido anteriormente com a ideia de rotas deve ser atualizado se continuar fazendo parte da entrega.
