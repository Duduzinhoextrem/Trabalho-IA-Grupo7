"""Gera a apresentação oficial em PPTX e PDF com 20 slides acadêmicos bem estruturados e roteiro de defesa."""

from __future__ import annotations

import os
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

ROOT = Path(__file__).resolve().parents[2]
OUT_PRES = ROOT / "ENTREGA_FINAL_GRUPO7" / "03_APRESENTACAO"
OUT_PRES.mkdir(parents=True, exist_ok=True)

# Cores
RGB_PRIMARY = RGBColor(141, 61, 48)   # #8d3d30
RGB_SECONDARY = RGBColor(41, 39, 32)  # #292720
RGB_MUTED = RGBColor(116, 109, 96)    # #746d60
RGB_BG = RGBColor(243, 239, 229)      # #f3efe5
RGB_WHITE = RGBColor(255, 255, 255)
RGB_BRASS = RGBColor(161, 123, 64)    # #a17b40

C_PRIMARY = colors.HexColor("#8d3d30")
C_SECONDARY = colors.HexColor("#292720")
C_MUTED = colors.HexColor("#746d60")

def setup_reportlab_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=C_PRIMARY,
        spaceAfter=4,
        alignment=0
    ))
    styles.add(ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=C_MUTED,
        spaceAfter=10
    ))
    styles.add(ParagraphStyle(
        'SecHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=C_PRIMARY,
        spaceBefore=7,
        spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        'BodySm',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.2,
        leading=11.2,
        textColor=C_SECONDARY,
        spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        'BodySmBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.2,
        leading=11.2,
        textColor=C_SECONDARY,
    ))
    return styles

SLIDES_DATA = [
    {
        "title": "Masmorra Genética: A Evolução do Guerreiro",
        "kicker": "INTELIGÊNCIA ARTIFICIAL II · FIB 2026",
        "bullets": [
            "Otimização evolutiva de estratégias de combate e sobrevivência em masmorra procedural de 100 salas.",
            "Grupo 7: Eduardo Coque Corrêa de Lima, Fernando Eduardo Motta Mendes, Matheus Alcântara Pereira, Reuel Vitor Lanzetti, Rogério Tiritan Marcone.",
            "Tema Sorteado: Tema 9 — Algoritmos Genéticos (Apresentação: 01/12/2026).",
            "Entrega Final: 17/11/2026."
        ],
        "image": "results/finalizacao/graficos/grafico_evolucao_geracoes.png"
    },
    {
        "title": "O Problema Investigado",
        "kicker": "100 SALAS DE DIFICULDADE CRESCENTE",
        "bullets": [
            "Um guerreiro solitário deve atravessar uma masmorra estocástica de 100 salas com encontros de 1 a 3 criaturas.",
            "Desafio não-linear: Força bruta inicial fracassa nas salas avançadas por falta de suporte curativo ou armadura pesada.",
            "Espaço combinatorial: Distribuir atributos, escolher e contratar 5 classes de aliados, comprar itens e gerenciar reservas financeiras.",
            "Pergunta de pesquisa: Um Algoritmo Genético pode aprender políticas viáveis para superar heurísticas fixas e competir com busca aleatória sob mesmo orçamento?"
        ],
        "image": "docs/FINALIZACAO/evidencias/capturas/02_aventura_sala1.png"
    },
    {
        "title": "Objetivos da Investigação",
        "kicker": "METAS ACADÊMICAS E CIENTÍFICAS",
        "bullets": [
            "Objetivo Geral: Construir um pipeline evolutivo que otimize cromossomos de políticas de combate e avaliar seu desempenho frente a baselines.",
            "Investigar o impacto das taxas de mutação (2%, 10%, 25%) na convergência e preservação da diversidade genética.",
            "Analisar o efeito do dimensionamento populacional (12, 20, 40) sob orçamento computacional estritamente pareado (240 avaliações).",
            "Avaliar a robustez e generalização da melhor política em masmorras virgens (E5: sementes 401–420) e cenários adversos de escassez e dificuldade."
        ],
        "image": None
    },
    {
        "title": "Justificativa da Técnica",
        "kicker": "POR QUE ALGORITMOS GENÉTICOS?",
        "bullets": [
            "Natureza do problema: Não temos dados rotulados de jogadores para usar aprendizado supervisionado.",
            "Espaço de busca complexo: 16 decisões interconectadas com variáveis contínuas e discretas com descontinuidades causadas pela aleatoriedade dos combates.",
            "Capacidade do AG: Explora múltiplos pontos simultaneamente no hipercubo, recombinando blocos construtivos viáveis de alocação de recursos.",
            "Transparência: Políticas geradas são 100% interpretáveis (pesos de atributos, prioridades de classes e limiares econômicos)."
        ],
        "image": "docs/FINALIZACAO/evidencias/capturas/05_como_funciona_passo_a_passo.png"
    },
    {
        "title": "Dataset Externo: D&D 5e SRD 2014",
        "kicker": "PROVENIÊNCIA E TRANSPARÊNCIA DOS DADOS",
        "bullets": [
            "Origem: D&D 5e SRD API (comunidade 5e-bits / Wizards of the Coast sob licença CC-BY-4.0).",
            "Snapshot congelado: srd-2014-v1.0.0 coletado em 29/10/2026 com 334 registros completos de criaturas.",
            "Integridade auditada: SHA-256 verificado (51a00f4785dcf07fcb4056cd97eaa1eb5b2ba0c235d2b7d5b2762a772691d397).",
            "Separação estrita: Os monstros são dados externos reais; as fórmulas de combate, economia e progressão são simulações versionadas do grupo."
        ],
        "image": "docs/FINALIZACAO/evidencias/capturas/12_dados_e_fonte.png"
    },
    {
        "title": "Preparação e Tratamento dos Dados",
        "kicker": "ETL E ANÁLISE EXPLORATÓRIA (EDA)",
        "bullets": [
            "Normalização: Parsing de estruturas JSON aninhadas e cálculo probabilístico do dano médio esperado por ação.",
            "Tratamento de casos limites: 4 formas passivas não-ofensivas excluídas (frog, sea-horse, shrieker, vampire-mist).",
            "Descoberta de EDA 1: Correlação linear de Pearson de 0,9404 entre Challenge Rating (CR) e HP dos monstros.",
            "Descoberta de EDA 2: Forte assimetria nos pontos de XP (mediana 450 vs máximo 155.000), exigindo recompensa de XP sublinear logarítmica."
        ],
        "image": "docs/FINALIZACAO/evidencias/capturas/11_bestiario.png"
    },
    {
        "title": "Estrutura da Masmorra e Progressão",
        "kicker": "100 SALAS PROCEDURAIS DETERMINÍSTICAS",
        "bullets": [
            "Salas 1 a 10: Inimigos iniciais (CR 0.125 a 1.0).",
            "Salas 11 a 60: Criaturas perigosas (CR 1.0 a 11.0) em grupos de 1 a 3 monstros com posicionamento em linha de frente e retaguarda.",
            "Salas 61 a 99: Encontros épicos de alto desafio (CR 11.0 a 23.0).",
            "Sala 100: Guardião final colossal (CR 24+).",
            "Reprodutibilidade matemática: Cada masmorra é determinada unicamente por sua semente pseudoaleatória."
        ],
        "image": "docs/FINALIZACAO/evidencias/capturas/01_inicio.png"
    },
    {
        "title": "Representação Genética: O Cromossomo",
        "kicker": "16 GENES DE TOMADA DE DECISÃO",
        "bullets": [
            "Genes 0 a 2 (Contínuos, soma = 1.0): Pesos de alocação de atributos do Guerreiro (Força, Vitalidade, Defesa).",
            "Genes 3 a 7 (Contínuos [0, 1]): Prioridades relativas de contratação dos 5 Aliados (Mago, Arqueiro, Monge, Padre, Alquimista).",
            "Genes 8 a 10 (Contínuos, soma = 1.0): Pesos de evolução dos atributos dos Aliados (Poder, Vitalidade, Defesa).",
            "Gene 11: Prioridade entre armas ofensivas vs armaduras/escudos defensivos.",
            "Gene 12 (Discreto {0, 1}): Contratar aliados antes de adquirir armaduras.",
            "Genes 13 a 15: Reserva mínima de ouro (0 a 120 moedas) e limiares multiplicadores de segurança para compras no mercado."
        ],
        "image": None
    },
    {
        "title": "Função de Aptidão (Fitness)",
        "kicker": "PRIORIDADE LEXICOGRÁFICA ESTRITA",
        "bullets": [
            "Métrica primária estrita: Média de salas concluídas (0 a 100) no conjunto de masmorras de treinamento (sementes 101–105).",
            "Critérios secundários infinitesimais de desempate: Fração de vida restante e ouro remanescente com peso máximo de 0,009.",
            "Garantia matemática: O bônus secundário é estritamente inferior a 1/K (para qualquer K <= 100 masmorras), impedindo que ouro ou vida superem o avanço de +1 sala.",
            "Métrica auxiliar reportada separadamente: Taxa de conclusão integral das 100 salas (%)."
        ],
        "image": None
    },
    {
        "title": "Operadores Genéticos: Seleção e Cruzamento",
        "kicker": "RECOMBINAÇÃO HÍBRIDA CONTÍNUA E DISCRETA",
        "bullets": [
            "População Inicial: Amostragem estratificada por Hipercubo Latino, cobrindo todo o domínio dos 16 genes.",
            "Seleção por Torneio (k=3): Sorteia 3 indivíduos ao acaso e elege o de maior aptidão; equilibra pressão seletiva e diversidade.",
            "Crossover Híbrido BLX-α (taxa de 85%, α = 0,25): Para genes contínuos, recombina intervalos ampliados entre os pais; operador uniforme para o gene discreto.",
            "Normalização automática: Reparação pós-cruzamento garante que as somas de pesos somem exatamente 1,0."
        ],
        "image": None
    },
    {
        "title": "Mutação, Elitismo e Diversidade",
        "kicker": "EXPLORAÇÃO E PRESERVAÇÃO DE CONHECIMENTO",
        "bullets": [
            "Mutação Gaussiana: Aplica perturbação com desvio-padrão de 18% da amplitude do gene; inversão de bit no gene discreto.",
            "Elitismo Rígido (2 indivíduos): Os 2 melhores indivíduos passam intactos para a geração seguinte, garantindo que boas soluções não se percam.",
            "Controle de Diversidade Euclidiana: Monitoramento contínuo; se clones idênticos surgem, recebem mutação forçada; se diversidade cai abaixo de 0,06, introduz imigrantes aleatórios.",
            "Orçamento estrito: Indivíduos de elite preservados não são reavaliados e não consomem orçamento de computação."
        ],
        "image": "docs/FINALIZACAO/evidencias/capturas/05_como_funciona_passo_a_passo.png"
    },
    {
        "title": "Configurações Experimentais Controladas",
        "kicker": "RIGOR METODOLÓGICO E ORÇAMENTO EQUIPARADO",
        "bullets": [
            "Orçamento fixo: 240 avaliações efetivas da função objetivo por repetição independente.",
            "Conjunto de Treinamento: Masmorras 101, 102, 103, 104 e 105.",
            "Conjunto de Validação Padrão (Holdout): Masmorras 201 a 210 (10 masmorras distintas).",
            "Conjunto de Validação Inédito (E5): Masmorras 401 a 420 (20 masmorras nunca utilizadas em ajuste).",
            "Múltiplas repetições com sementes estocásticas independentes para cálculo de variância e testes de hipótese."
        ],
        "image": None
    },
    {
        "title": "Baselines de Comparação",
        "kicker": "BENCHMARKS IMPARCIAIS",
        "bullets": [
            "Baseline 1: Estratégia Fixa Heurística — Distribuição equilibrada de atributos (1/3 Força, 1/3 Vida, 1/3 Defesa), reserva fixa de 40 moedas e prioridade de contratação de Arqueiro e Mago.",
            "Baseline 2: Busca Aleatória (Random Search) — Sorteia candidatos válidos no hipercubo com o mesmo orçamento exato de 240 avaliações por repetição.",
            "Critério de justiça: Ambos os métodos de busca consomem exatamente 240 avaliações de simulação sobre as mesmas masmorras de treino."
        ],
        "image": None
    },
    {
        "title": "Resultados: Mutação e População (E1 e E2)",
        "kicker": "HIPERPARÂMETROS EM AÇÃO",
        "bullets": [
            "E1 — Taxa de Mutação: 25% alcançou média de 95,06 salas e 36% de conclusão na validação, superando 10% (92,12 salas) e 2% (91,28 salas). A taxa de 2% causou perda prematura de diversidade (0,0346).",
            "E2 — População com Orçamento Fixo: População de 40 indivíduos (7 gerações) obteve 89,56 salas vs 86,28 da População 12 (24 gerações).",
            "Conclusão: No regime de poucas avaliações, maior diversidade inicial e taxas de mutação mais ativas beneficiam a exploração."
        ],
        "image": "results/finalizacao/graficos/grafico_mutacao_e1.png"
    },
    {
        "title": "Resultados: Comparação com Baselines (E3)",
        "kicker": "O CONFRONTO CENTRAL",
        "bullets": [
            "Estratégia Fixa: Média de 69,00 salas concluídas na validação (0% de vitórias integrais).",
            "Busca Aleatória (7 repetições): Média de 92,27 ± 4,16 salas (25,71% de vitórias integrais).",
            "Algoritmo Genético (7 repetições): Média de 91,27 ± 4,11 salas (28,57% de vitórias integrais).",
            "Teste Mann-Whitney: U = 21,5, p = 0,748053 (Welch t = -0,4188, p = 0,682779). Não houve evidência suficiente de diferença.",
            "Estratégia campeã individual: Alcançou média de 96,9 salas e venceu 4 de 10 masmorras (40%)."
        ],
        "image": "results/finalizacao/graficos/grafico_comparacao_metodos.png"
    },
    {
        "title": "Experimento Adicional E5: Sementes Virgens",
        "kicker": "PRÉ-REGISTRO E VALIDAÇÃO INDEPENDENTE",
        "bullets": [
            "Pré-registrado em docs/FINALIZACAO/PRE_REGISTRO_E5.md antes da execução com 10 repetições de 240 evals.",
            "Avaliado em 20 sementes virgens (401–420): AG (10% mut) = 90,38 ± 3,83 salas; AG (25% mut) = 92,49 ± 2,80 salas; Busca Aleatória = 94,56 ± 2,42 salas.",
            "Mann-Whitney AG25 vs AG10: p = 0,241 (25% é superior numericamente, mas sem significância estrita).",
            "Mann-Whitney Busca Aleatória vs AG10: p = 0,021 (Busca Aleatória superior).",
            "O experimento não identifica a causa das diferenças entre os métodos."
        ],
        "image": "results/finalizacao/graficos/grafico_e5_sementes_ineditas.png"
    },
    {
        "title": "Robustez e Generalização de Cenários (E4)",
        "kicker": "TESTES ADVERSOS FORA DA DISTRIBUIÇÃO",
        "bullets": [
            "Novas composições de monstros (sementes 301–310): Desempenho resiliente com média de 94,4 salas (20% vitória).",
            "Dificuldade aumentada (+15% HP e dano nos monstros): Média cai para 73,4 salas (10% vitória; Fixa = 51,4).",
            "Sem baús (economia estrita): Média cai para 80,0 salas (20% vitória; Fixa = 61,1).",
            "A política do AG preserva vantagem consistente sobre a heurística fixa em todos os cenários (+16 a +22 salas de vantagem)."
        ],
        "image": "results/finalizacao/graficos/grafico_cenarios_e4.png"
    },
    {
        "title": "Análise Crítica de Falhas Reais",
        "kicker": "INVESTIGAÇÃO OBRIGATÓRIA DE DERROTAS",
        "bullets": [
            "Caso 1 (Semente 201, Dif +15%): Guerreiro caiu na Sala 25 contra Black Pudding. A falta de armas pesadas iniciais causou atrito excessivo.",
            "Caso 2 (Semente 209, Sem baús): Guerreiro derrotado na Sala 26 contra Succubus/Incubus com arma tier 2 e escudo tier 1, mas sem nenhuma armadura (tier 0) devido à reserva mínima de ouro travada.",
            "Caso 3 (Semente 308, Novas Criaturas): Derrota na Sala 79 contra Dragão Vermelho Adulto devido ao desgaste cumulativo em 3 salas duplas consecutivas anteriores."
        ],
        "image": "docs/FINALIZACAO/evidencias/capturas/03_aventura_final_e_comparacao.png"
    },
    {
        "title": "Protótipo Web: Masmorra Genética",
        "kicker": "INTERAÇÃO E DEMO AO VIVO",
        "bullets": [
            "Aplicação interativa em Streamlit estruturada em 7 capítulos.",
            "Modo Automático: Otimiza e joga automaticamente até vencer a masmorra selecionada.",
            "Replay Sala a Sala: Inspecione cada combate com registro dos turnos, HP e transações de mercado.",
            "Laboratório Didático: Permite testar parâmetros ao vivo para responder ao Demo Challenge da banca com qualquer semente ou dificuldade.",
            "Exportação: Download do relatório da jornada e histórico em JSON e CSV."
        ],
        "image": "docs/FINALIZACAO/evidencias/capturas/13_laboratorio.png"
    },
    {
        "title": "Conclusão, Aprendizados e Perguntas",
        "kicker": "SÍNTESE FINAL DO GRUPO 7",
        "bullets": [
            "O Algoritmo Genético aprendeu políticas sólidas que superam a heurística fixa por mais de 22 salas e concluem as 100 salas em até 40% das vezes.",
            "Com 240 avaliações, o E3 não mostrou vantagem clara do AG sobre a busca aleatória.",
            "Os resultados dependem das regras do simulador e das sementes avaliadas.",
            "Obrigado! Estamos prontos para as perguntas da banca examinadora."
        ],
        "image": "docs/FINALIZACAO/evidencias/capturas/14_treino_automatico.png"
    }
]


def create_pptx():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    for idx, data in enumerate(SLIDES_DATA, start=1):
        slide = prs.slides.add_slide(blank_layout)

        # Barra decorativa no topo
        top_bar = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(13.333), Inches(0.12))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = RGB_PRIMARY
        top_bar.line.color.rgb = RGB_PRIMARY

        # Kicker / Tag
        tx_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.5), Inches(0.4))
        p = tx_box.text_frame.paragraphs[0]
        p.text = data["kicker"]
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = RGB_PRIMARY

        # Título
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.5), Inches(0.8))
        tp = t_box.text_frame.paragraphs[0]
        tp.text = data["title"]
        tp.font.size = Pt(24)
        tp.font.bold = True
        tp.font.color.rgb = RGB_SECONDARY

        has_img = data["image"] and (ROOT / data["image"]).exists()
        w_bullets = Inches(6.8) if has_img else Inches(11.5)

        # Bullets
        b_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.8), w_bullets, Inches(5.0))
        tf = b_box.text_frame
        tf.word_wrap = True
        for b_idx, bullet in enumerate(data["bullets"]):
            bp = tf.add_paragraph() if b_idx > 0 else tf.paragraphs[0]
            bp.text = f"•  {bullet}"
            bp.font.size = Pt(13.5)
            bp.font.color.rgb = RGB_SECONDARY
            bp.space_after = Pt(12)

        # Imagem lateral
        if has_img:
            img_path = str(ROOT / data["image"])
            slide.shapes.add_picture(img_path, Inches(8.0), Inches(1.8), width=Inches(4.6))

        # Rodapé com número
        foot = slide.shapes.add_textbox(Inches(0.8), Inches(6.9), Inches(11.5), Inches(0.4))
        fp = foot.text_frame.paragraphs[0]
        fp.text = f"Masmorra Genética · Grupo 7 (IA II - FIB 2026)                                                                                                              Slide {idx} / {len(SLIDES_DATA)}"
        fp.font.size = Pt(9.5)
        fp.font.color.rgb = RGB_MUTED

    pptx_path = OUT_PRES / "Apresentacao_Grupo7.pptx"
    prs.save(str(pptx_path))
    print(f"Apresentação gerada com sucesso: {pptx_path.name} ({len(SLIDES_DATA)} slides).")


def create_slides_pdf():
    pdf_path = OUT_PRES / "Apresentacao_Grupo7.pdf"
    styles = getSampleStyleSheet()
    title_st = ParagraphStyle('STitle', fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=colors.HexColor("#8d3d30"), spaceAfter=3)
    kicker_st = ParagraphStyle('SKicker', fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=colors.HexColor("#a17b40"), spaceAfter=2)
    body_st = ParagraphStyle('SBody', fontName='Helvetica', fontSize=11, leading=15, textColor=colors.HexColor("#292720"), spaceAfter=8)

    story = []
    for idx, data in enumerate(SLIDES_DATA, start=1):
        story.append(Paragraph(data["kicker"], kicker_st))
        story.append(Paragraph(data["title"], title_st))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#8d3d30"), spaceAfter=14))
        for bullet in data["bullets"]:
            story.append(Paragraph(f"• {bullet}", body_st))
        story.append(Spacer(1, 15))
        story.append(Paragraph(f"<i>Masmorra Genética · Grupo 7 · Slide {idx} de {len(SLIDES_DATA)}</i>", ParagraphStyle('F', fontName='Helvetica-Oblique', fontSize=9, textColor=colors.HexColor("#746d60"))))
        if idx < len(SLIDES_DATA):
            story.append(PageBreak())

    doc = SimpleDocTemplate(str(pdf_path), pagesize=landscape(letter), leftMargin=40, rightMargin=40, topMargin=35, bottomMargin=35)
    doc.build(story)
    print(f"PDF dos Slides gerado: {pdf_path.name}.")


def create_defense_script():
    md_path = ROOT / "docs" / "FINALIZACAO" / "ROTEIRO_DEFESA.md"
    pdf_path = OUT_PRES / "Roteiro_Defesa.pdf"

    script_content = """# Roteiro Oficial de Defesa e Arguição — Masmorra Genética

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
| **5. Experimentos e Comparações** | 8 min | Reuel | Orçamento equiparado (240 evals), resultados E1, E2, E3 (empate p=0,748) e E5 (sementes virgens). |
| **6. Análise de Falhas e Limitações** | 4 min | Reuel | Os 3 casos reproduzidos de derrota (Black Pudding dif +15%, Succubus sem baús, Dragão Vermelho). |
| **7. Protótipo ao Vivo & Demo Challenge** | 5 min | Fernando | Demonstração no Streamlit com sorteio de semente fornecida pela banca ou plateia. |
| **8. Conclusão & Perguntas** | 3 min | Rogério / Todos | Aprendizados sobre honestidade metodológica e abertura para arguição. |

---

## 2. Perguntas Obrigatórias da Disciplina (Respostas Técnicas Prontas)

### P1: Por que essa técnica foi escolhida?
**Resposta:** O problema de otimização de decisões em 100 salas não possui exemplos supervisionados de partidas humanas prévias. O espaço combinatorial possui 16 dimensões mistas (pesos contínuos e escolhas discretas) com descontinuidades causadas pela estocasticidade das rolagens de combate. Algoritmos genéticos são altamente indicados para explorar espaços não-lineares sem exigência de derivadas, recombinando blocos construtivos viáveis de alocação de atributos e mercado.

### P2: Qual seria uma alternativa mais simples?
**Resposta:** Implementamos duas alternativas: (1) uma **heurística fixa equilibrada** (distribuir 1/3 em cada atributo, reserva de 40 moedas e priorizar arqueiro/mago), que concluiu apenas 69 salas e 0% das 100 salas; e (2) uma **busca aleatória (Random Search)** com o mesmo orçamento de 240 avaliações, que atingiu média de 92,27 salas.

### P3: Qual foi o maior problema encontrado nos dados?
**Resposta:** Três problemas centrais no snapshot da D&D SRD API: (1) forte assimetria na experiência (XP com mediana 450 e máximo de 155.000), o que exigiu transformação sublinear logarítmica para evitar que um único monstro concedesse 20 níveis de uma vez; (2) ausência de dano direto interpretável em 5 monstros, com exclusão de 4 criaturas passivas sem ataque (`frog`, `sea-horse`, `shrieker`, `vampire-mist`); e (3) ausência do campo opcional `subtype` em 258 dos 334 registros.

### P4: O que aconteceria se uma variável importante fosse removida?
**Resposta:** Se removermos a variável de contratação de aliados (`enable_allies=False`), o guerreiro enfrenta todas as salas sozinho. Sem a divisão de linha de frente do Monge e sem o suporte vital de cura do Padre, o desgaste cumulativo derruba o alcance do guerreiro mesmo com atributos máximos, não passando da Sala 40 em testes exploratórios. Se removermos a reserva de ouro (`min_gold_reserve`), o combatente gasta todo o ouro imediatamente em armas e fica sem fundos para comprar armaduras quando surgem no mercado.

### P5: Como vocês evitaram avaliar apenas no conjunto de treinamento?
**Resposta:** Nos experimentos, usamos as sementes 101 a 105 para treino e 201 a 210 para validação. Como reutilizamos a validação em várias análises, pré-registramos o E5 com outras 20 sementes, de 401 a 420. Isso permite avaliar outras masmorras, mas não elimina todas as dúvidas sobre generalização.

### P6: Qual métrica foi priorizada e por quê?
**Resposta:** Priorizamos a **média de salas concluídas** (de 0 a 100), pois reflete a distância real percorrida na masmorra. A taxa de conclusão integral (%) foi reportada como métrica secundária, pois é binária e não penaliza proporcionalmente quem cai na sala 2 ou na sala 99. Pontos de vida e ouro atuam apenas como termos de desempate infinitesimal na fitness com peso total máximo de 0,009, garantindo que o avanço de salas seja a prioridade absoluta.

### P7: Onde o modelo mais errou?
**Resposta:** No E5, a busca aleatória teve média maior que o AG com mutação de 10% (p = 0,021), mas o experimento não identifica a causa da diferença. No E4, sem baús, a média da estratégia escolhida caiu 16,9 salas, com uma derrota na sala 26; com dificuldade aumentada, houve uma derrota na sala 25 contra Black Pudding.

### P8: Que mudança poderia melhorar o projeto?
**Resposta:** (1) Expandir o conjunto de treinamento de 5 para 20 masmorras dinâmicas por geração; (2) implementar operadores meméticos (busca local tipo hill-climbing após recombinação); e (3) adotar políticas dinâmicas dependentes de estado (onde as decisões de compra mudam em tempo real conforme a vida atual do guerreiro, e não como uma regra estática pré-estabelecida).

### P9: Como o protótipo transforma o modelo em aplicação compreensível?
**Resposta:** O protótipo Streamlit adota metáfora visual de "Atlas de Expedição": substitui tabelas áridas por mapas sala a sala, replay de combates por turnos, fichas dos monstros do Bestiário com links para a fonte oficial do D&D, aba interativa com simulador visual de cruzamento e mutação dos 16 genes e um Laboratório aberto onde a banca pode alterar qualquer parâmetro em tempo real.

---

## 3. Procedimento Operacional para o Demo Challenge (Ao Vivo)

1. **Abrir a aba "Laboratório" no Streamlit:**
   - Solicitar à banca ou à plateia um número de semente (ex: semente 777 ou a data de nascimento de alguém).
   - Ajustar um multiplicador de dificuldade (ex: 120% ou recuperação de 15%).
2. **Executar a simulação comparativa:**
   - Clicar em "Comparar neste cenário".
   - A tela executa em 2 segundos e apresenta o gráfico de vida e as salas atingidas pela Estratégia do AG vs. a Estratégia Fixa.
3. **Interpretação técnica obrigatória (sem prometer vitória cega):**
   - *"Como demonstramos em nossos experimentos, em sementes inéditas a política do AG supera com folga a heurística fixa na vasta maioria das vezes, mas devido à estocasticidade dos combates e rolagens críticas de dano dos monstros, há cenários específicos onde mesmo a melhor estratégia pode cair precocemente. É a física real do simulador operando."*

---

## 4. Plano de Contingência Offline (Sem Internet)

- O aplicativo Streamlit não consulta a API externa em tempo de execução: o snapshot `monsters_raw_srd2014.json` e os dados tratados em parquet/csv estão armazenados localmente no repositório.
- Para rodar sem qualquer conexão de rede:
  ```bash
  python -m streamlit run app.py --server.port 8599 --server.headless true
  ```
- Os slides em PDF e o vídeo MP4 renderizado na pasta `ENTREGA_FINAL_GRUPO7/` garantem apresentação autônoma caso ocorra falha de energia ou conectividade no dia do seminário.
"""
    md_path.write_text(script_content, encoding="utf-8")

    # Gera PDF do roteiro de defesa
    styles = setup_reportlab_styles()
    story = [
        Paragraph("ROTEIRO OFICIAL DE DEFESA E ARGUIÇÃO — MASMORRA GENÉTICA", styles['DocTitle']),
        Paragraph("<b>Faculdades Integradas de Bauru (FIB) · Grupo 7 · Inteligência Artificial II (2026)</b><br/>"
                  "<b>Apresentação:</b> 01/12/2026 (Núcleo de ~40 minutos) · <b>Tema:</b> Algoritmos Genéticos", styles['DocSubTitle']),
        HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#8d3d30"), spaceAfter=8),
    ]

    for line in script_content.split("\n"):
        if line.startswith("## "):
            story.append(Spacer(1, 8))
            story.append(Paragraph(line.replace("## ", ""), styles['SecHeading']))
        elif line.startswith("### "):
            story.append(Paragraph(line.replace("### ", ""), styles['BodySmBold']))
        elif line.startswith("- **") or line.startswith("• "):
            story.append(Paragraph(line, styles['BodySm']))
        elif line.strip() and not line.startswith("#"):
            story.append(Paragraph(line, styles['BodySm']))

    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    doc.build(story)
    print("Roteiro de Defesa gerado (Markdown e PDF).")


def main():
    create_pptx()
    create_slides_pdf()
    create_defense_script()
    print("Módulo de apresentação concluído com sucesso!")


if __name__ == "__main__":
    main()
