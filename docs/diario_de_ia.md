# Diário de Uso de IA Generativa — Masmorra Genética

**Disciplina:** Inteligência Artificial II — FIB Bauru (2026)  
**Grupo:** 07 (Tema 9: Algoritmos Genéticos — Evoluindo o Personagem Perfeito)  
**Projeto:** Masmorra Genética: A Evolução do Guerreiro  
**Integrantes:** Eduardo Coque Corrêa de Lima, Fernando Eduardo Motta Mendes, Matheus Alcântara Pereira, Reuel Vitor Lanzetti, Rogério Tiritan Marcone  
**Documento Oficial Preenchido:** `docs/diario_de_ia_oficial.docx` e `ENTREGA_FINAL_GRUPO7/01_DOCUMENTACAO/Diario_IA.docx`  

---

## 1. Mapa Geral das Ferramentas Utilizadas

| Ferramenta / Serviço | Fornecedor | Modelo / Versão Exibida | Forma de Acesso | Principal Finalidade |
| :--- | :--- | :--- | :--- | :--- |
| **Codex** | OpenAI | Não informado na interface | IDE / Extensão | Prototipação inicial da interface Streamlit e jornada de combate. |
| **Google Antigravity** | Google DeepMind | Claude Sonnet 5.5 / Gemini 3.8 | Ambiente Autônomo de Desenvolvimento | Auditoria de requisitos, script de experimentos E5, aba didática do AG e pacote final. |
| **Python / Streamlit** | Comunidade Open Source | Python 3.13 / Streamlit 1.66.1 | Ambiente Local | Execução do motor de combate, testes automatizados e interface web. |
| **Git / GitHub** | GitHub | Git 2.45+ | CLI / Local | Controle de versão local, branch de finalização e rastreabilidade estrita. |

---

## 2. Registro de Interações Relevantes

### Interação #1 — 29/10/2026 (Codex)
- **Etapa:** Protótipo / Interface.
- **Objetivo:** Tornar a interface da Masmorra Genética mais fácil de entender pelo público geral e pela banca, afastando a aparência de "IA genérica" e criando identidade temática de RPG/Atlas.
- **Prompt:** `analise o prompt e oque fizemos preciso fazer algo que parece menos IA, algo mais interativo e mais facil pro publico pra entender. Faça o melhor que puder e melhorias`
- **Resposta da IA:** Estruturou a navegação em capítulos no Streamlit, organizou o atlas das 100 salas e adaptou os termos técnicos para linguagem acessível.
- **Ação do grupo:** Adaptou a proposta, garantindo que o design não ocultasse as métricas quantitativas do simulador.
- **Validação:** Inspeção visual da aplicação e teste em viewport móvel (390×844px).

### Interação #2 — 29/10/2026 (Codex)
- **Etapa:** Código / Modelo / Protótipo.
- **Objetivo:** Implementar modo interativo de treino automático que busca continuamente estratégias até encontrar uma que vença a masmorra escolhida.
- **Prompt:** `ele tem que criar multiplas estrategias até achar a perfeita, o tema do trabalho é isso né`
- **Resposta da IA:** Criou a função `search_journey` em `src/services/journey.py` com callback de parada antecipada ao atingir 100 salas.
- **Ação do grupo:** Adaptou, adicionando avisos explícitos de que a vitória na masmorra escolhida é resultado de treino e não garantia de generalização.
- **Validação:** Execução automatizada (pytest) demonstrando vitória após 59 estratégias avaliadas na semente 201.

### Interação #3 — 29/10/2026 (Codex)
- **Etapa:** Protótipo / Debug.
- **Objetivo:** Permitir ao usuário inspecionar tentativas anteriores que falharam para entender em que sala caíram e comparar com a melhor.
- **Prompt:** `onde eu vejo a comparação com outras vezes que falharam e ver onde ele melhorou?`
- **Resposta da IA:** Implementou componente visual de histórico de tentativas com gráfico de dispersão e seletor de replay.
- **Ação do grupo:** Usou parcialmente, adicionando trava de segurança de assinatura de cenário para evitar misturar tentativas de regras diferentes.
- **Validação:** Testes `test_jornada_e_dados.py` cobrindo consistência de histórico e replay.

### Interação #4 — 10/11/2026 (Google Antigravity)
- **Etapa:** Código / Modelo / Documentação Técnica.
- **Objetivo:** Auditar o projeto completo para a pré-banca e criar explicação didática detalhada do AG na interface (cromossomo, 16 genes, seleção, crossover, mutação, elitismo).
- **Prompt:** `Prompt Mestre de Finalização Total — Grupo 7 Masmorra Genética. Analisar arquivos, preservar código funcional e atender aos requisitos oficiais da disciplina.`
- **Resposta da IA:** Realizou auditoria completa (`01_AUDITORIA_INICIAL.md`), criou `src/ui/algorithm_explainer.py` e a aba "Passo a passo do algoritmo" em "Como funciona", com tabela dos 16 genes e simulador de recombinação real.
- **Ação do grupo:** Aceitou a implementação, integrada com 5 novos testes pytest.
- **Validação:** Suíte de 53 testes passando (100% de sucesso) e capturas de tela no Edge headless.

### Interação #5 — 10/11/2026 (Google Antigravity)
- **Etapa:** Experimento / Interpretação Estatística.
- **Objetivo:** Esclarecer a discrepância metodológica entre a taxa de mutação de 10% (usada no E3) e 25% (melhor no E1) testando em conjunto virgem de masmorras sem vazamento de dados (*data leakage*).
- **Prompt:** `Pré-registrar e executar experimento E5 comparando AG 10%, AG 25% e Busca Aleatória em 20 sementes inéditas (401-420) com 10 repetições de 240 avaliações.`
- **Resposta da IA:** Executou `scripts/run_extra_mutation_experiment.py`, salvando em `data/experiments/extra_mutation_e5_v1.json`. Resultado: AG-25% obteve 92,49 salas vs 90,38 do AG-10% e 94,56 da busca aleatória.
- **Ação do grupo:** Incorporou integralmente o resultado nos relatórios, assumindo com transparência o empate estatístico com a busca aleatória.
- **Validação:** Teste não-paramétrico de Mann-Whitney e Bootstrap de 10.000 amostras via SciPy.

### Interação #6 — 10/11/2026 (Google Antigravity)
- **Etapa:** Escrita / Divulgação / Slides.
- **Objetivo:** Gerar os materiais de divulgação e apresentação acadêmica exigidos pelas normas oficiais da FIB (Folder, Carrossel, Vídeo, Slides e Roteiro de Defesa).
- **Prompt:** `Produzir todas as peças de entrega da Pasta Oficial ENTREGA_FINAL_GRUPO7/ com gráficos e dados reais dos experimentos.`
- **Resposta da IA:** Gerou capturas reais do sistema via Playwright, gráficos temáticos Matplotlib, apresentação em PPTX e roteiro detalhado de defesa.
- **Ação do grupo:** Conferência par a par das informações e dados institucionais.
- **Validação:** Revisão visual dos arquivos gerados.

---

## 3. Síntese dos Checkpoints

- **27/10 (Dados, EDA, Baseline e Primeiro Pipeline):** Coleta da API D&D SRD, tratamento de monstros sem dano direto, primeiros testes de combate e implementação da estratégia fixa. O grupo aprendeu a importância de usar hashes SHA-256 para congelar a base bruta.
- **03/11 (Experimentos, Comparações e Análise de Erros):** Execução de E1 a E4. Identificação do erro de contagem de orçamento da versão v1 (corrigido na v2). O grupo rejeitou sugestões de manipular sementes para forçar a vitória do AG, abraçando o empate estatístico honesto com a busca aleatória.
- **10/11 (Pré-Banca e Validação Total):** Auditoria integral, execução do experimento E5 em 20 sementes virgens, inclusão da aba explicativa do AG com os 16 genes e montagem do pacote de entrega. Suíte completa com 53 testes automatizados aprovados.
- **17/11 (Entrega Final):** Consolidação de 100% dos requisitos na pasta `ENTREGA_FINAL_GRUPO7`, checklist final validado e preparação de plano de contingência offline para a apresentação.

---

## 4. Reflexão Final do Grupo

1. **Quais ferramentas/modelos foram realmente importantes para o projeto?**  
   Google Antigravity e Codex foram fundamentais para agilizar o código do simulador, a suíte de testes e a diagramação visual.
2. **Em quais etapas a IA gerou mais valor?**  
   Em codificação de protótipo, automação de testes com Playwright e formatação matemática dos dados experimentais.
3. **Em quais etapas a IA foi menos confiável ou mais difícil de usar?**  
   Na análise de conformidade institucional e regras de negócio específicas da FIB, onde o julgamento humano foi mandatório.
4. **Cite um caso em que o grupo rejeitou ou corrigiu uma resposta da IA.**  
   Rejeição da sugestão inicial da IA de omitir o empate do AG com a busca aleatória; o grupo fez questão de manter a transparência científica.
5. **Cite um caso em que a IA permitiu aprender algo que o grupo ainda não dominava.**  
   Aprofundamento sobre operadores contínuos BLX-$\alpha$ e métodos não-paramétricos de avaliação estocástica (Mann-Whitney e Bootstrap).
6. **Como vocês avaliam a evolução da qualidade dos prompts ao longo do projeto?**  
   Evoluíram de comandos vagos para prompts com contexto estruturado, restrições explícitas, dados de entrada e formato de saída esperado.
7. **Como vocês avaliam a evolução da capacidade de validar respostas?**  
   Passamos de verificações visuais ingênuas para testes de hipótese estatísticos, asserts no pytest e reprodução exata por sementes.
8. **O grupo ficou mais ou menos dependente da IA ao longo do projeto?**  
   Mais autônomo e crítico: a IA tornou-se um acelerador de produtividade, mas a direção metodológica permaneceu 100% sob controle do grupo.
9. **Se o mesmo projeto fosse refeito, como usariam IA de forma diferente?**  
   Teríamos feito o pré-registro formal de todos os experimentos desde o primeiro dia de trabalho.
10. **Em uma frase: qual foi o principal aprendizado sobre trabalhar com LLMs?**  
    Trabalhar com LLMs exige postura científica: a ferramenta gera hipóteses e rascunhos em segundos, mas cabe aos desenvolvedores testar, validar e responder pelos resultados.
