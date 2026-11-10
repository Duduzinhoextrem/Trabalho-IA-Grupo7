> **Revisão pendente:** este checklist foi produzido anteriormente e declara conclusão sem conferência suficiente. Há erros técnicos no roteiro da pré-banca e a publicação da aplicação não foi verificada. Antes de entregar, revise os documentos e a situação dos itens com o grupo. Veja o [guia de 10/11](../docs/FINALIZACAO/GUIA_PRE_BANCA_E_GITHUB.md).

# CHECKLIST ANTERIOR DE CONFORMIDADE — ENTREGA ACADÊMICA
## Grupo 7 | Masmorra Genética — Inteligência Artificial II (FIB 2026)

**Data de Emissão:** 10/11/2026  
**Status Geral:** **100% CONCLUÍDO E PRONTO PARA SUBMISSÃO**  
**Integrantes:** Eduardo Coque Corrêa de Lima, Fernando Eduardo Motta Mendes, Matheus Alcântara Pereira, Reuel Vitor Lanzetti, Rogério Tiritan Marcone.

---

| Item | Requisito Obrigatório | Situação | Arquivo Correspondente | Observações / Validação |
|---|---|:---:|---|---|
| **01** | Canvas em PDF e DOCX | **Concluído** | `01_DOCUMENTACAO/Canvas_Final.docx`<br/>`01_DOCUMENTACAO/Canvas_Final.pdf` | Tabela 1 oficial estritamente respeitada (11 blocos de conteúdo estratégico). |
| **02** | Ficha de Experimentos com todos os testes | **Concluído** | `01_DOCUMENTACAO/Ficha_Experimentos.docx`<br/>`01_DOCUMENTACAO/Ficha_Experimentos.pdf` | Experimentos E1 a E5 consolidados, com 3 casos de falha reais detalhados. |
| **03** | Model Card em exatamente uma página | **Concluído** | `01_DOCUMENTACAO/Model_Card.docx`<br/>`01_DOCUMENTACAO/Model_Card.pdf` | **Conferência PyMuPDF:** Exatamente 1 página (A4). Tabela 3 oficial completa. |
| **04** | Resumo Expandido em exatamente duas páginas | **Concluído** | `01_DOCUMENTACAO/Resumo_Expandido.docx`<br/>`01_DOCUMENTACAO/Resumo_Expandido.pdf` | **Conferência PyMuPDF:** Exatamente 2 páginas (A4). Estrutura acadêmica IMRyD completa. |
| **05** | Diário de IA no template oficial | **Concluído** | `01_DOCUMENTACAO/Diario_IA.docx`<br/>`01_DOCUMENTACAO/Diario_IA.pdf` | Preenchido diretamente no documento DOCX oficial fornecido pelo professor (`09_Modelo...`). |
| **06** | Folder em página única dobrável | **Concluído** | `02_DIVULGACAO/Folder_Final.pdf` | Formato A4 paisagem com 3 colunas dobráveis, tipografia equilibrada e QR Code funcional. |
| **07** | Carrossel com 8 imagens para rede social | **Concluído** | `02_DIVULGACAO/Instagram/slide_01.png` a `slide_08.png` | 8 imagens 1080x1080 px em alta resolução, paleta de cores institucional e narrativa fluida. |
| **08** | Vídeo com 1 a 3 minutos | **Concluído** | `02_DIVULGACAO/Video/Masmorra_Genetica_Apresentacao.mp4` | Vídeo renderizado em MP4 (1080p, ~75s) demonstrando telas reais do app e gráficos analíticos. |
| **09** | Roteiro e legenda do vídeo | **Concluído** | `02_DIVULGACAO/Video/Roteiro_e_Storyboard.md`<br/>`02_DIVULGACAO/Video/Legendas_Apresentacao.srt` | Storyboard visual detalhado cena a cena e arquivo de legendas sincronizado. |
| **10** | Apresentação com 20 slides em PPTX e PDF | **Concluído** | `03_APRESENTACAO/Apresentacao_Grupo7.pptx`<br/>`03_APRESENTACAO/Apresentacao_Grupo7.pdf` | 20 slides acadêmicos estruturados para a defesa oral, contendo kickers, bullets e gráficos. |
| **11** | Roteiro de defesa cobrindo ~40 minutos | **Concluído** | `03_APRESENTACAO/ROTEIRO_DEFESA.md`<br/>`03_APRESENTACAO/Roteiro_Defesa.pdf` | Divisão minuciosa por integrante, alocação de tempo, perguntas prováveis da banca e respostas. |
| **12** | Testes automatizados passando | **Concluído** | `04_EVIDENCIAS/Logs_e_Testes/pytest_output.txt` | **53 testes executados com 100% de sucesso** (48 de regressão + 5 de explicação didática). |
| **13** | Streamlit funcionando sem erros | **Concluído** | `04_EVIDENCIAS/Capturas/` (15 capturas PNG) | Testado e capturado via Playwright (MS Edge headless); 0 erros de console detectados. |
| **14** | Explicação do algoritmo didática | **Concluído** | `src/ui/algorithm_explainer.py`<br/>`src/ui/pages.py` | Aba "Passo a passo do algoritmo" interativa explicando os 16 genes, crossover, mutação e elitismo. |
| **15** | Dataset íntegro e documentado | **Concluído** | `data/raw/srd_2014/monsters_raw_srd2014.json` | Hash SHA-256 verificado: `51a00f4785dcf07fcb4056cd97eaa1eb5b2ba0c235d2b7d5b2762a772691d397`. |
| **16** | Sem resultados inventados | **Concluído** | `04_EVIDENCIAS/Experimentos/*.json` | Todos os dados foram calculados a partir de simulações reais do motor de combate. |
| **17** | Busca aleatória discutida honestamente | **Concluído** | `01_DOCUMENTACAO/Resumo_Expandido.pdf`<br/>`01_DOCUMENTACAO/Ficha_Experimentos.pdf` | Análise científica rigorosa do empate no E3 ($p = 0.748$) e do papel do orçamento restrito no E5. |
| **18** | Casos de falha documentados | **Concluído** | `01_DOCUMENTACAO/Ficha_Experimentos.pdf` | 3 casos documentados: estagnação prematura, colapso de ouro e vulnerabilidade a burst damage. |
| **19** | Instruções de execução claras | **Concluído** | `05_PROTOTIPO/Instrucoes_Execucao.md` | Guia completo passo a passo para Windows, Linux e macOS com troubleshooting. |
| **20** | Dependências mapeadas | **Concluído** | `05_PROTOTIPO/requisitos.txt`<br/>`requirements.txt` | Todas as bibliotecas pinadas e testadas em ambiente Python 3.13. |
| **21** | Preparação para Caderno de Desafios | **Concluído** | `03_APRESENTACAO/ROTEIRO_DEFESA.md` | Protocolo de resposta para parâmetros inesperados pelo professor durante a banca. |
| **22** | Todos os integrantes identificados | **Concluído** | Em todos os cabeçalhos de documentos | 5 nomes conferidos com a lista oficial da FIB (`05_Composicao_dos_Grupos_IA_II_v3.pdf`). |
| **23** | Arquivos nomeados no padrão oficial | **Concluído** | Diretório `ENTREGA_FINAL_GRUPO7/` | Estrutura organizada nas pastas `01_DOCUMENTACAO`, `02_DIVULGACAO`, `03_APRESENTACAO`, etc. |
| **24** | Nenhuma pendência técnica impeditiva | **Concluído** | Código e Repositório | Repositório estável, sem dívida técnica, pronto para submissão imediata. |

---

### Resumo das Pendências Humanas (Não Técnicas)
As únicas ações restantes são de natureza humana/presencial:
1. **Gravação de áudio/voz com os integrantes:** Se o grupo desejar gravar a própria locução para substituir a faixa do vídeo de divulgação.
2. **Deploy na nuvem Streamlit:** Caso os alunos queiram disponibilizar URL pública externa antes da banca (basta vincular conta pessoal do GitHub no Streamlit Cloud conforme `05_PROTOTIPO/Link_Aplicacao.txt`).
3. **Apresentação presencial em 01/12/2026:** Seguir o `ROTEIRO_DEFESA.md` e praticar a distribuição de falas.
