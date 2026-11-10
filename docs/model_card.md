# Model Card Simplificada — Masmorra Genética

**Projeto:** Masmorra Genética: A Evolução do Guerreiro  
**Disciplina:** Inteligência Artificial II — FIB Bauru (2026)  
**Grupo:** 07 (Tema 9: Algoritmos Genéticos)  
**Autores:** Eduardo Coque Corrêa de Lima, Fernando Eduardo Motta Mendes, Matheus Alcântara Pereira, Reuel Vitor Lanzetti, Rogério Tiritan Marcone  

---

### Especificações do Modelo (Formato Oficial — Tabela 3)

| Item | Descrição / Especificação |
| :--- | :--- |
| **1. Nome da solução** | **Masmorra Genética — Otimizador Evolutivo de Estratégias** (`masmorra-genetica-ga-v2`). |
| **2. Problema** | Encontrar de forma autônoma políticas de alocação de atributos, contratação de aliados e compras em mercado que maximizem a sobrevivência de um personagem ao longo de uma masmorra de 100 salas de dificuldade crescente. |
| **3. Técnica/algoritmo** | **Algoritmo Genético (AG)** com codificação mista (15 genes contínuos com limites reais e 1 discreto binário). Utiliza inicialização por amostragem estratificada (Latin Hypercube), seleção por torneio ($k=3$), recombinação híbrida BLX-$\alpha$ ($\alpha=0,25$) com cruzamento uniforme discreto, mutação gaussiana adaptativa ($\sigma=0,18$) e elitismo rígido (2 indivíduos). Função fitness lexicográfica com prioridade estrita para salas concluídas e desempate infinitesimal por HP e ouro. |
| **4. Dados utilizados** | Snapshot congelado de 334 criaturas da **D&D 5e SRD API** (`srd-2014-v1.0.0`, coletado em 29/10/2026, SHA-256: `51a00f4785dcf07fcb4056cd97eaa1eb5b2ba0c235d2b7d5b2762a772691d397`). Licença SRD 5.1 / CC-BY-4.0. |
| **5. Principais variáveis** | • **Genes do Cromossomo (16):** pesos de atributos do guerreiro (Força, Vitalidade, Defesa; soma=1,0); prioridades de contratação de 5 aliados (Mago, Arqueiro, Monge, Padre, Alquimista); pesos de evolução dos aliados (Poder, Vitalidade, Defesa; soma=1,0); foco em armas vs armaduras; prioridade de aliado vs equipamento; reserva mínima de ouro; limiares econômicos de compra.<br>• **Variáveis das Criaturas:** Challenge Rating (CR 0,125 a 24), HP original, AC, atributos base, dano estimado de ações e resistências/imunidades. |
| **6. Pré-processamento** | Extração e normalização de estruturas JSON aninhadas; estimativa probabilística de dano por turno baseada em dados de rolagem ($d$); remoção de 4 criaturas não-combatentes passivas do pool de salas (`frog`, `sea-horse`, `shrieker`, `vampire-mist`); tratamento de dano nulo via interpolação de CR; transformação logarítmica sublinear para recompensa de XP. |
| **7. Métrica principal** | **Média de salas concluídas** (de 0 a 100) em conjunto de masmorras de validação com sementes pseudoaleatórias fixadas. Métrica secundária: **taxa de conclusão integral das 100 salas** (%). |
| **8. Resultado principal** | • **Validação padrão (sementes 201–210):** em 7 repetições de 240 avaliações, o AG teve média de **91,27 ± 4,11 salas** e **28,57% de conclusão**. A regra fixa teve média de 69,00 salas e 0% de conclusão. Não houve evidência suficiente de diferença entre o AG e a busca aleatória (92,27 ± 4,16 salas; p = 0,748 no teste de Mann-Whitney).<br>• **Melhor indivíduo:** média de **96,9 salas** e **40% de conclusão** (4 em 10 masmorras).<br>• **E5 (sementes 401–420, 10 repetições):** AG com mutação de 25% obteve 92,50 ± 2,80 salas, contra 90,38 ± 3,83 com mutação de 10% e 94,56 ± 2,42 da busca aleatória. |
| **9. Baseline** | • **Estratégia Fixa Equilibrada:** 69,00 salas na validação (0% conclusão integral).<br>• **Busca Aleatória (Random Search):** 92,27 salas na validação (orçamento pareado de 240 avaliações). |
| **10. Limitações** | O simulador usa regras simplificadas e não reproduz todo o D&D 5e: magias complexas e posicionamento espacial livre foram abstraídos. O treino usa apenas 5 masmorras, o que limita a avaliação da capacidade de generalização. O AG não garante encontrar a melhor estratégia possível. |
| **11. Possíveis vieses/riscos** | • **Viés de composição:** Classes curativas (Padre) são prioritárias na maioria dos cromossomos campeões devido à mecânica de desgaste contínuo do simulador.<br>• **Dependência econômica:** Retirar os baús derruba o avanço da melhor política em 16,9 salas, revelando vulnerabilidade a regimes de escassez.<br>• **Risco de má interpretação:** Tratar o sucesso no treino da aplicação interativa como garantia de invencibilidade em qualquer masmorra. |
| **12. Quando não utilizar** | • **Não utilizar** para prever combates de RPG de mesa com intervenção de mestres humanos ou regras oficiais completas.<br>• **Não utilizar** como modelo preditivo de comportamento de jogadores reais.<br>• **Não utilizar** em ambientes críticos de tomada de decisão com penalidade severa para falhas estocásticas. |

---
*Documento elaborado e conferido pelo Grupo 7 da disciplina Inteligência Artificial II — FIB Bauru, Novembro/2026.*
