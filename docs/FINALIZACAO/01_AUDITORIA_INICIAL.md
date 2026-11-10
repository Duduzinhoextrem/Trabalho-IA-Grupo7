# 01 — Auditoria inicial

Data: 10/11/2026 (pré-banca). Branch de trabalho: `finalizacao-total`, criada a partir de `main` (commit `44036e3`, árvore limpa).
Esta auditoria descreve o estado **antes** das alterações desta finalização. O andamento está em [STATUS_EXECUCAO.md](STATUS_EXECUCAO.md).

## 1. Fontes consultadas

| Fonte | Local | Observação |
| --- | --- | --- |
| Repositório do projeto | `Trabalho-IA-Grupo7/` (75 arquivos versionados) | README, `src/`, `tests/`, `scripts/`, `data/`, `results/`, `docs/` lidos |
| Documentos oficiais da disciplina | `Downloads/OneDrive_1_10-11-2026.zip` (extraído em área temporária; original intacto) | Guia geral, cronograma, roteiro e avaliação, modelos e checklists, composição dos grupos, mapa do sorteio, orientações e modelo do Diário de IA |
| Backup do repositório | `Documents/Trabalho-IA-Grupo7.rar` | Contém `docs/diario_de_ia.md`, que **não existe** no repositório atual nem no histórico Git |
| Template da Jornada Científica da FIB | **não encontrado** | Procurado em Downloads, Documents e nos ZIP. Os documentos oficiais só dizem que o resumo segue o "template vigente" |
| Pacote `20_Checklist_Checkpoint1...docx` e `02_Cronograma...pdf` | Downloads | Conferidos contra o conjunto oficial |

Não há arquivo RAR/ZIP adicional com materiais do Grupo 7 além do backup acima.

## 2. Requisitos oficiais relevantes

- Tema do Grupo 7: **Algoritmos Genéticos — Evoluindo o Personagem Perfeito**, apresentação em **01/12/2026**, posição 1 do dia (mapa do sorteio).
- Entrega final comum a todos: **17/11/2026, até 17h**. Pré-banca em 10/11 (congelamento técnico).
- Desafio do tema: função fitness, convergência, mutação e diversidade; comparação mínima com busca aleatória ou heurística simples; tela que mostra gerações, fitness e evolução da melhor solução.
- Obrigatórios: ≥ 3 experimentos controlados (hipótese, alteração, resultado, interpretação); ≥ 3 erros ou casos inesperados; métricas justificadas; baseline; protótipo web; demonstração com entrada não preparada (Demo Challenge); analogia simples e explicação técnica.
- Entregas: palestra de ~40 min (núcleo), protótipo, repositório GitHub (README mínimo), resumo expandido de 2 páginas (formato Jornada Científica FIB), folder de 1 página com dobra e QR Code, carrossel Instagram, vídeo de 1 a 3 min, Model Card de 1 página, ficha de experimentos.
- Diário de IA: modelo `.docx` oficial; **não compõe a nota**; deve registrar o processo real, sem credenciais ou dados sensíveis.
- Critérios de avaliação (100 pts): problema 10, dados 15, domínio conceitual 15, experimentos 20, análise crítica 15, protótipo 15, comunicação 10. O novo algoritmo **não precisa vencer** o baseline.

## 3. Diagnóstico da arquitetura

Aplicação Python com camadas separadas e testadas:

| Camada | Arquivos | Papel |
| --- | --- | --- |
| Dados | `src/dataset/` | Coleta da D&D 5e SRD API, validação, pré-processamento, EDA, manifesto com SHA-256 |
| Simulador | `src/game/` | Salas (`dungeon.py`), adaptação dos monstros (`monsters.py`), combate, economia, aliados |
| Algoritmo genético | `src/genetic/` | Cromossomo de 16 genes, fitness lexicográfica, torneio, BLX-α, mutação gaussiana, elitismo, controle de diversidade, parada por geração/orçamento/estagnação/meta |
| Experimentos | `src/experiments/`, `scripts/` | Baselines, 4 experimentos, estatística, gráficos |
| Serviço | `src/services/journey.py` | Busca e simulação independentes do Streamlit |
| Interface | `app.py`, `src/ui/` | 7 páginas Streamlit (Início, Aventura, Como funciona, Resultados, Bestiário, Dados e fonte, Laboratório) |
| Testes | `tests/` | 48 testes (pytest + `AppTest` do Streamlit) |

A arquitetura é madura e coerente; **não há motivo para refatorar**.

## 4. Verificação direta dos números

Todos os valores do prompt foram conferidos em `data/experiments/scientific_experiments_v2.json`.

| Item | Valor no arquivo | Confere com o prompt? |
| --- | --- | --- |
| Estratégia fixa, validação | 69,00 salas, 0% conclusão | sim |
| Busca aleatória, validação (7 repetições) | 92,27 ± 4,16 salas; 25,71% | sim |
| AG (mutação 10%), validação (7 repetições) | 91,27 ± 4,11 salas; 28,57% | sim |
| Mann-Whitney AG × busca aleatória | U = 21,5; **p = 0,748053** (Welch p = 0,682779) | sim |
| Wilcoxon melhor AG × fixa (10 sementes) | p = 0,001953 | n/a no prompt |
| Orçamento | 240 avaliações efetivas por repetição nos dois métodos | verificado nos campos `objective_evaluations` |
| SHA-256 do JSON bruto | `51a00f47…d397`; recalculado e idêntico ao manifesto | verificado |
| Registros do dataset | 334 válidos, 0 inválidos, 0 duplicados, `subtype` ausente em 258 | verificado |

Mutação (E1, 5 repetições por taxa, validação 201–210): 2% → 91,28; 10% → 92,12; 25% → 95,06 salas.

## 5. Qualidade científica

**Pontos fortes**
- Validação separada (201–210) e composição alternativa (301–310); orçamento corrigido na `v2` (a `v1` foi preservada com a falha documentada).
- Resultado negativo reportado sem esconder: busca aleatória ≈ AG (p = 0,75).
- Análise de falhas, limitações e casos reproduzidos na ficha.

**Fragilidades encontradas**
1. **Mutação 10% × 25%.** O E3 usou 10% (hipótese inicial do grupo), enquanto o E1 mostrou 25% com a maior média. Nenhum documento explicava a escolha metodológica com evidência. As amostras do E1 são pequenas (5 repetições). → resolvido com o experimento adicional **E5** (pré-registrado), ver [PRE_REGISTRO_E5.md](PRE_REGISTRO_E5.md).
2. A validação 201–210 foi reutilizada em todos os experimentos e na escolha do "melhor AG". O p = 0,0019 contra a estratégia fixa compara uma estratégia escolhida entre sete com a regra fixa; é exploratório. → E5 usa 20 sementes nunca utilizadas (401–420).
3. A diferença AG × busca aleatória não é significativa e a variância entre repetições (± 4 salas) é maior que a diferença entre médias (1 sala). Os textos já dizem isso; faltava explicar **por quê** isso acontece (espaço de busca de 16 genes com muitas regiões boas, orçamento de apenas 240 avaliações, ruído da simulação). → incluído nos documentos finais.
4. A mesma configuração (AG com 10%) obteve 92,12 (E1, 5 repetições) e 91,27 (E3, 7 repetições): mostra o ruído natural entre execuções.

## 6. Qualidade técnica

- Suíte existente: **48 testes passaram** em 36,7 s (Python 3.13, Streamlit 1.66.1), executados antes de qualquer alteração.
- Código sem falhas bloqueantes encontradas na leitura. Parâmetros inválidos são validados antes da execução.
- `requirements.txt` com limites inferiores, sem versões fixas. A CI usa Python 3.12. Risco baixo; versões testadas serão registradas no README de implantação.
- Não há URL pública verificada. `.streamlit/config.toml` está adequado para implantação (tema, `headless`, proteção XSRF).
- A página "Como funciona" explicava só três ideias (criar, testar, evoluir). Seleção, cruzamento, mutação, elitismo, aptidão e os 16 genes **não eram explicados na interface**. → nova aba "Passo a passo do algoritmo".

## 7. Documentação e materiais

| Material | Estado inicial |
| --- | --- |
| Canvas | `docs/canvas_projeto.md` correto (Masmorra Genética), mas ainda aponta que o PDF antigo trata de rotas/Waze. Formato oficial (tabela de 11 campos) não gerado em PDF/DOCX |
| Model Card | Texto correto em Markdown, mais longo que 1 página e sem a estrutura de 12 itens do modelo oficial |
| Resumo expandido | **Rascunho** em Markdown; sem formatação nem limite de 2 páginas; template FIB ausente |
| Ficha de experimentos | Completa em Markdown; formato oficial é tabela E1–E4 |
| Diário de IA | Arquivo existia só no backup RAR (3 interações do Codex). Modelo `.docx` oficial não preenchido |
| Folder, Instagram, vídeo, slides | **Inexistentes** (apenas roteiros em Markdown) |
| Roteiro de defesa | Inexistente |
| README | Bom; falta seção de implantação, link do vídeo/resumo/aplicação e os materiais finais |

## 8. Riscos

| # | Risco | Gravidade |
| --- | --- | --- |
| R1 | Template FIB do resumo não disponível; não é possível comprovar conformidade do layout | Alta |
| R2 | URL pública inexistente: QR Codes do folder, Instagram e vídeo dependem dela | Alta |
| R3 | Demo Challenge: a banca pode dar semente/cenário inédito; o AG pode não vencer | Média |
| R4 | Integrantes precisam saber defender todo o código; o histórico do repositório mostra apenas um autor de commits | Média |
| R5 | Papéis dos integrantes no Canvas são "proposta", não confirmados | Média |
| R6 | Dependência de internet na demonstração (aplicação não precisa da API; o snapshot é local) | Baixa |
| R7 | Grafia do nome "Alcântara" (app/README) × "Alcantara" (lista oficial) | Baixa |

## 9. Matriz de rastreabilidade dos requisitos

Legenda: A = atendido; P = parcialmente; N = não atendido; V = não verificável por mim.

| # | Requisito oficial | Evidência | Estado inicial |
| --- | --- | --- | --- |
| 1 | Problema, público e resultado esperado definidos | `README.md`, `docs/canvas_projeto.md` | A |
| 2 | Origem, significado, qualidade e limitações do dataset | `docs/dados_e_fonte.md`, `data/metadata/`, `docs/eda_report.md` | A |
| 3 | Técnica explicada com analogia e com precisão técnica | README, aba "Como funciona" (parcial) | P |
| 4 | Pelo menos um baseline | `src/experiments/baselines.py` (fixa e aleatória) | A |
| 5 | ≥ 3 experimentos controlados com hipótese, alteração, resultado, interpretação | E1–E4 em `docs/ficha_experimentos.md` | A |
| 6 | Métricas justificadas | Média de salas, taxa de conclusão (ficha, README) | A |
| 7 | ≥ 3 erros/casos inesperados | Três casos reproduzidos na ficha | A |
| 8 | Protótipo web funcional | Streamlit, 7 páginas, 48 testes | A |
| 9 | Demo Challenge com entrada não preparada | Laboratório e Aventura aceitam semente livre | A (ensaio pendente) |
| 10 | Tela que mostra gerações, fitness e evolução da melhor solução | "Como funciona" (curvas) | A |
| 11 | Resumo expandido de 2 páginas no formato FIB | Rascunho Markdown | N |
| 12 | Model Card de 1 página | Markdown longo | P |
| 13 | Ficha de experimentos (tabela) | Markdown | P |
| 14 | Canvas | Markdown | P |
| 15 | Folder de 1 página com dobra + QR Code | Inexistente | N |
| 16 | Carrossel de Instagram | Inexistente | N |
| 17 | Vídeo de 1 a 3 min | Inexistente | N |
| 18 | Slides / palestra de ~40 min | Inexistente | N |
| 19 | Repositório GitHub organizado com README mínimo | README completo; publicação não verificada | P |
| 20 | Diário de IA (modelo oficial) | Rascunho em Markdown (só no backup) | P |
| 21 | Protótipo testado em outro computador/navegador | Não testado em outra máquina | V |
| 22 | Plano B sem internet | Citado, não documentado | P |
| 23 | QR Codes testados | Sem URL | N |
| 24 | Revisão ortográfica final | Pendente | P |

## 10. Plano de execução decorrente

1. Estabilizar e testar (concluído na leitura: 48/48 testes).
2. Explicação do algoritmo na interface e testes novos.
3. E5 pré-registrado; atualizar ficha, Model Card, resumo e Canvas com resultado real, qualquer que seja.
4. Gerar documentos finais no formato oficial; folder, carrossel, vídeo (capturas reais), slides, roteiro de defesa e demonstração.
5. Preparar implantação (sem publicar), rodar testes finais, montar `ENTREGA_FINAL_GRUPO7/`, relatório final.
