"""Gera os 5 documentos acadêmicos obrigatórios em PDF e DOCX com formatação profissional.

Documentos:
1. Canvas_Final (.docx e .pdf)
2. Model_Card (.docx e .pdf) — estritamente 1 página
3. Resumo_Expandido (.docx e .pdf) — estritamente 2 páginas
4. Ficha_Experimentos (.docx e .pdf)
5. Diario_IA (.docx e .pdf)
"""

from __future__ import annotations

import json
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import fitz  # PyMuPDF para conferência de páginas

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "ENTREGA_FINAL_GRUPO7" / "01_DOCUMENTACAO"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Paleta institucional e acadêmica
C_PRIMARY = colors.HexColor("#8d3d30")  # Vermelho Terracota
C_SECONDARY = colors.HexColor("#292720") # Tinta Escura
C_MUTED = colors.HexColor("#746d60")     # Cinza Neutro
C_BG_LIGHT = colors.HexColor("#f8f6f0")  # Papel Claro
C_LINE = colors.HexColor("#d2c9b7")      # Linha suave
C_WHITE = colors.white


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
    styles.add(ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=C_SECONDARY,
    ))
    styles.add(ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=C_SECONDARY,
    ))
    styles.add(ParagraphStyle(
        'TableHead',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=C_WHITE,
        alignment=1
    ))
    return styles


# ==============================================================================
# 1. CANVAS DO PROJETO
# ==============================================================================
def generate_canvas():
    pdf_path = OUT_DIR / "Canvas_Final.pdf"
    docx_path = OUT_DIR / "Canvas_Final.docx"
    styles = setup_reportlab_styles()

    story = [
        Paragraph("CANVAS DO PROJETO DE INTELIGÊNCIA ARTIFICIAL II", styles['DocTitle']),
        Paragraph("<b>Faculdades Integradas de Bauru (FIB)</b> · Ciência da Computação · 2026<br/>"
                  "<b>Grupo 7</b> | Tema 9: Algoritmos Genéticos (Apresentação: 01/12/2026)<br/>"
                  "<b>Integrantes:</b> Eduardo Coque Corrêa de Lima, Fernando Eduardo Motta Mendes, Matheus Alcântara Pereira, Reuel Vitor Lanzetti, Rogério Tiritan Marcone", styles['DocSubTitle']),
        HRFlowable(width="100%", thickness=1, color=C_PRIMARY, spaceAfter=8),
    ]

    canvas_data = [
        ("Tema/técnica", "<b>Algoritmos Genéticos</b> (Tema 9: Evoluindo o Personagem Perfeito). Otimização evolutiva de políticas de combate em ambiente de RPG por turnos."),
        ("Problema a resolver", "Otimizar simultaneamente atributos de combate, contratação de classes de aliados e economia de equipamentos para atravessar uma masmorra procedural de 100 salas."),
        ("Usuário/público", "Estudantes e entusiastas de computação sem experiência prévia em IA (compreensão intuitiva) e a banca acadêmica examinadora (rigor científico e reprodutibilidade)."),
        ("Entrada do sistema", "Vetor cromossômico de 16 genes que orienta decisões de alocação de atributos, prioridade de aliados, alocação de pontos de aliados, prioridades de compras e reservas financeiras; semente de masmorra."),
        ("Saída esperada", "Simulação sala por sala detalhada, curva de convergência geracional, gráficos de diversidade genética, taxa de conclusão das 100 salas e relatório de jornada."),
        ("Dataset/fonte", "Snapshot de 334 criaturas da <b>D&D 5e SRD API</b> (edição 2014, srd-2014-v1.0.0, SHA-256 verificado: 51a00f47...). Regras de combate e economia são simulações versionadas do grupo (balance-v1.0.0)."),
        ("Baseline", "Dois comparadores controlados: (1) <b>Estratégia Fixa Heurística</b> (equilibrada 1/3, reserva de 40 moedas) e (2) <b>Busca Aleatória</b> com 240 avaliações efetivas da função objetivo."),
        ("Hipóteses iniciais", "H1: O AG superará a heurística fixa. H2: Taxas de mutação afetam diretamente diversidade e convergência prematura. H3: Mudanças de regras revelarão limites de robustez da estratégia campeã."),
        ("Experimentos planejados", "<b>E1:</b> Mutação (2%, 10%, 25%). <b>E2:</b> População com orçamento fixo de 240 avaliações. <b>E3:</b> Comparação com baselines (7 repetições). <b>E4:</b> Generalização e robustez em cenários adversos. <b>E5:</b> Sementes virgens (401-420)."),
        ("Ideia do protótipo web", "Aplicação Streamlit em estilo 'Atlas de Expedição': aventura com replay sala por sala, busca automática, aba didática de anatomia do AG, Bestiário com download e Laboratório para o Demo Challenge."),
        ("Divisão de responsabilidades", "• Eduardo: Algoritmo genético, operadores matemáticos e integração.<br/>• Matheus: Coleta e limpeza do dataset SRD e EDA.<br/>• Fernando: Simulador de combate, catálogo de itens e Streamlit.<br/>• Rogério: Canvas, Model Card, Resumo Expandido e Diário de IA.<br/>• Reuel: Automação experimental, análise estatística e materiais."),
    ]

    table_data = [[Paragraph("<b>Campo (Modelo Oficial)</b>", styles['TableHead']), Paragraph("<b>Definição e Preenchimento — Grupo 7</b>", styles['TableHead'])]]
    for campo, desc in canvas_data:
        table_data.append([Paragraph(f"<b>{campo}</b>", styles['TableCellBold']), Paragraph(desc, styles['TableCell'])])

    t = Table(table_data, colWidths=[120, 390])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, C_LINE),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [C_WHITE, C_BG_LIGHT]),
    ]))
    story.append(t)

    doc_pdf = SimpleDocTemplate(str(pdf_path), pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    doc_pdf.build(story)

    # DOCX
    d = docx.Document()
    d.add_heading("Canvas Inicial do Projeto — Masmorra Genética", level=1)
    d.add_paragraph("Faculdades Integradas de Bauru (FIB) · Ciência da Computação · Inteligência Artificial II · 2026\n"
                    "Grupo 7 | Tema 9: Algoritmos Genéticos (Apresentação: 01/12/2026)\n"
                    "Integrantes: Eduardo Coque Corrêa de Lima, Fernando Eduardo Motta Mendes, Matheus Alcântara Pereira, Reuel Vitor Lanzetti, Rogério Tiritan Marcone")
    table = d.add_table(rows=1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = table.rows[0].cells
    hdr[0].text = "Campo"
    hdr[1].text = "Definição do Grupo 7"
    for campo, desc in canvas_data:
        row = table.add_row().cells
        row[0].text = campo
        row[1].text = desc.replace("<b>", "").replace("</b>", "").replace("<br/>", "\n")
    d.save(str(docx_path))
    print("Canvas gerado com sucesso (PDF e DOCX).")


# ==============================================================================
# 2. MODEL CARD (ESTRITAMENTE 1 PÁGINA)
# ==============================================================================
def generate_model_card():
    pdf_path = OUT_DIR / "Model_Card.pdf"
    docx_path = OUT_DIR / "Model_Card.docx"
    styles = setup_reportlab_styles()

    story = [
        Paragraph("MODEL CARD SIMPLIFICADA — MASMORRA GENÉTICA", styles['DocTitle']),
        Paragraph("<b>Grupo 7 · Tema 9: Algoritmos Genéticos</b> · FIB Inteligência Artificial II (2026)<br/>"
                  "<b>Autores:</b> Eduardo Lima, Fernando Mendes, Matheus Pereira, Reuel Lanzetti, Rogério Marcone", styles['DocSubTitle']),
        HRFlowable(width="100%", thickness=0.8, color=C_PRIMARY, spaceAfter=5),
    ]

    items = [
        ("1. Nome da solução", "<b>Masmorra Genética — Otimizador Evolutivo de Estratégias</b> (masmorra-genetica-ga-v2)."),
        ("2. Problema", "Otimizar autonomamente alocação de atributos, contratação de aliados e compras no mercado para maximizar a sobrevivência de um guerreiro em 100 salas de dificuldade incremental."),
        ("3. Técnica/algoritmo", "<b>Algoritmo Genético</b> com 16 genes (15 contínuos normalizados + 1 discreto). População estratificada (Latin Hypercube), torneio (k=3), recombinação BLX-α (α=0,25), mutação gaussiana (σ=0,18) e elitismo de 2 indivíduos. Fitness lexicográfica com desempate infinitesimal por HP e ouro."),
        ("4. Dados utilizados", "Snapshot de 334 criaturas da <b>D&D 5e SRD API</b> (edição 2014, srd-2014-v1.0.0; SHA-256 verificado: 51a00f47...). Regras de combate e balanceamento são simulações próprias versionadas (balance-v1.0.0)."),
        ("5. Principais variáveis", "16 genes: pesos de Força/Vitalidade/Defesa; prioridades das 5 classes de aliados; evolução dos aliados; balanço arma vs armadura; contratação prioritária; reserva mínima de ouro; limiares de compra. Criaturas: CR (0,125 a 24), HP, AC e dano de ações."),
        ("6. Pré-processamento", "Normalização de JSONs aninhados; estimativa de dano médio de dados; remoção de 4 monstros passivos sem ataque (frog, sea-horse, shrieker, vampire-mist); recompensa de XP sublinear logarítmica."),
        ("7. Métrica principal", "<b>Média de salas concluídas</b> (0 a 100) nas masmorras de validação (sementes fixas). Métrica secundária: <b>Taxa de conclusão integral das 100 salas</b> (%)."),
        ("8. Resultado principal", "• Validação padrão (sementes 201–210, 7 repetições, 240 avaliações cada): AG obteve <b>91,27 ± 4,11 salas</b> (28,57% conclusão), empatando com a Busca Aleatória (92,27 ± 4,16 salas, p=0,748 via Mann-Whitney) e superando a Fixa (69,00 salas, 0% conclusão). Estratégia campeã individual atingiu <b>96,9 salas</b> e 40% de conclusão.<br/>• Sementes virgens (E5, sementes 401–420, 10 repetições): AG-25% atingiu <b>92,49 ± 2,80 salas</b> vs 90,38 do AG-10% e 94,56 da busca aleatória."),
        ("9. Baseline", "• <b>Estratégia Fixa Equilibrada:</b> 69,00 salas na validação (0% de conclusão).<br/>• <b>Busca Aleatória (Random Search):</b> 92,27 salas na validação sob o mesmo orçamento de 240 avaliações."),
        ("10. Limitações", "O combate usa regras simplificadas e posicionamento abstrato. O treino em cinco masmorras limita a avaliação da generalização. O AG não garante encontrar a melhor estratégia possível."),
        ("11. Vieses / Riscos", "Padre é selecionado prioritariamente em 85% dos indivíduos devido à alta atrição de combate. Retirar baús reduz o rendimento em 16,9 salas. Vencer no treino não garante vencer sementes inéditas."),
        ("12. Quando não utilizar", "Não usar para prever partidas de RPG de mesa humano com regras complexas; não usar como preditor de jogadores reais; não usar em sistemas críticos de decisão com tolerância zero a falhas estocásticas."),
    ]

    table_data = [[Paragraph("<b>Item (Modelo Oficial)</b>", styles['TableHead']), Paragraph("<b>Especificação — Grupo 7</b>", styles['TableHead'])]]
    for item, desc in items:
        table_data.append([Paragraph(f"<b>{item}</b>", styles['TableCellBold']), Paragraph(desc, styles['TableCell'])])

    t = Table(table_data, colWidths=[110, 400])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, C_LINE),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [C_WHITE, C_BG_LIGHT]),
    ]))
    story.append(t)

    doc_pdf = SimpleDocTemplate(str(pdf_path), pagesize=A4, leftMargin=32, rightMargin=32, topMargin=28, bottomMargin=28)
    doc_pdf.build(story)

    # DOCX
    d = docx.Document()
    d.add_heading("Model Card Simplificada — Masmorra Genética", level=1)
    d.add_paragraph("Faculdades Integradas de Bauru (FIB) · Grupo 7 · IA II 2026\n"
                    "Autores: Eduardo Lima, Fernando Mendes, Matheus Pereira, Reuel Lanzetti, Rogério Marcone")
    table = d.add_table(rows=1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.rows[0].cells[0].text = "Item"
    table.rows[0].cells[1].text = "Especificação"
    for item, desc in items:
        row = table.add_row().cells
        row[0].text = item
        row[1].text = desc.replace("<b>", "").replace("</b>", "").replace("<br/>", "\n")
    d.save(str(docx_path))

    # Verifica se PDF tem exatamente 1 página
    doc_fitz = fitz.open(str(pdf_path))
    print(f"Model Card gerado: {len(doc_fitz)} página(s) (Meta: estritamente 1 página).")
    doc_fitz.close()


# ==============================================================================
# 3. RESUMO EXPANDIDO (ESTRITAMENTE 2 PÁGINAS)
# ==============================================================================
def generate_resumo_expandido():
    pdf_path = OUT_DIR / "Resumo_Expandido.pdf"
    docx_path = OUT_DIR / "Resumo_Expandido.docx"
    styles = setup_reportlab_styles()

    story = [
        Paragraph("Masmorra Genética: Otimização Evolutiva de Políticas de Combate em Ambiente Procedural", styles['DocTitle']),
        Paragraph("<b>Eduardo Coque Corrêa de Lima, Fernando Eduardo Motta Mendes, Matheus Alcântara Pereira, Reuel Vitor Lanzetti, Rogério Tiritan Marcone</b><br/>"
                  "Faculdades Integradas de Bauru (FIB) — Curso de Ciência da Computação — Inteligência Artificial II — 2026", styles['DocSubTitle']),
        HRFlowable(width="100%", thickness=0.8, color=C_PRIMARY, spaceAfter=4),

        Paragraph("1. Introdução", styles['SecHeading']),
        Paragraph("Algoritmos Genéticos (AGs) são métodos de busca meta-heurística inspirados no princípio neodarwiniano de seleção natural e hereditariedade. Em jogos digitais com geração procedural de desafios, o espaço combinatorial de configurações de personagens e decisões táticas inviabiliza abordagens de força bruta. O projeto <b>Masmorra Genética</b> investiga a aplicação de AGs para otimizar autonomamente a alocação de atributos, contratação de classes aliadas e decisões de mercado de um combatente em uma masmorra de 100 salas de dificuldade estritamente incremental.", styles['BodySm']),

        Paragraph("2. Objetivos", styles['SecHeading']),
        Paragraph("O objetivo primordial é verificar empiricamente se o AG converge para políticas que superem significativamente uma heurística fixa de distribuição equilibrada e analisar seu comportamento comparativo diante de uma busca puramente aleatória (<i>Random Search</i>) com orçamento estritamente equiparado (240 avaliações). Especificamente, busca-se: (a) mensurar o efeito de taxas de mutação (2%, 10%, 25%) na diversidade genética; (b) comparar diferentes tamanhos de população (12, 20, 40) sob mesmo teto computacional; e (c) avaliar a robustez da política campeã em sementes inéditas e cenários adversos.", styles['BodySm']),

        Paragraph("3. Metodologia", styles['SecHeading']),
        Paragraph("<b>Dataset e Pré-processamento:</b> Utilizou-se um snapshot congelado de 334 criaturas da <i>D&D 5e SRD API</i> (versão srd-2014-v1.0.0; SHA-256 verificado: 51a00f47...). A análise exploratória revelou correlação de Pearson de 0,9404 entre Challenge Rating (CR) e HP, ausência de correlação com destreza (r = -0,0100) e assimetria acentuada de XP (mediana 450; máx. 155.000), justificando a adoção de recompensa sublinear com amortecimento logarítmico. Quatro formas passivas não-combatentes foram excluídas.<br/>"
                  "<b>Representação Genética:</b> Cromossomo composto por 16 genes: 3 pesos normalizados de atributos do guerreiro (Força, Vitalidade, Defesa); 5 prioridades de contratação de aliados (Mago, Arqueiro, Monge, Padre, Alquimista); 3 pesos de desenvolvimento dos aliados; prioridade de compra arma vs armadura; 1 gene discreto binário de contratação prioritária; reserva mínima de ouro; e 2 limiares de segurança para compras no mercado.<br/>"
                  "<b>Operadores e Fitness:</b> População inicial por amostragem estratificada (Latin Hypercube); seleção por torneio (k=3); cruzamento híbrido BLX-α (α=0,25) com operador uniforme para o gene discreto; mutação gaussiana (σ=0,18 da amplitude do gene); elitismo de 2 indivíduos; e controle de diversidade euclidiana com reposição de clones. A função de aptidão adota prioridade lexicográfica estrita: a métrica principal é a média de salas concluídas nas masmorras de treino (sementes 101–105), com HP e ouro como termos infinitesimais de desempate (peso total <= 0,009).", styles['BodySm']),

        PageBreak(), # Força início exato da Página 2

        Paragraph("4. Resultados e Discussão", styles['SecHeading']),
        Paragraph("Os experimentos foram executados com controle de avaliações efetivas (elites não são reavaliadas):<br/>"
                  "• <b>Taxas de Mutação (E1):</b> A taxa de 25% alcançou média de <b>95,06 ± 2,02 salas</b> na validação (201–210) e 36% de conclusão integral das 100 salas, superando a taxa de 10% (92,12 ± 3,42 salas) e de 2% (91,28 ± 3,31 salas). A diversidade final com mutação de 2% estagnou prematuramente em 0,0346, enquanto 25% preservou 0,1104.<br/>"
                  "• <b>Tamanho de População (E2):</b> População 40 obteve 89,56 ± 3,43 salas vs 86,82 da População 20 e 86,28 da População 12, evidenciando que uma amostragem inicial ampla beneficia o espaço contínuo em orçamentos curtos.<br/>"
                  "• <b>Comparação com Baselines (E3 — 7 repetições de 240 avaliações):</b><br/>"
                  "  - Estratégia Fixa Heurística: média de 69,00 salas (0% conclusão).<br/>"
                  "  - Busca Aleatória: média de 92,27 ± 4,16 salas (25,71% conclusão).<br/>"
                  "  - Algoritmo Genético (10% mutação): média de 91,27 ± 4,11 salas (28,57% conclusão).<br/>"
                  "O teste de Mann-Whitney resultou em U = 21,5 com <b>p = 0,748053</b> (Welch p = 0,682779). Não houve evidência suficiente de diferença entre as buscas. A melhor estratégia individual atingiu 96,9 salas e 40% de conclusão.<br/>"
                  "• <b>Experimento E5 em 20 sementes inéditas (401–420, 10 repetições):</b> O AG-25% obteve 92,49 ± 2,80 salas (19% conclusão) vs 90,38 ± 3,83 salas (14,5% conclusão) do AG-10% (p = 0,241). A busca aleatória obteve 94,56 ± 2,42 salas (20% conclusão), acima do AG-10% (p = 0,021). O experimento não identifica a causa da diferença.<br/>"
                  "• <b>Robustez e Falhas (E4):</b> A política campeã sofreu redução expressiva em dificuldade +15% (73,4 salas; morte na sala 25 contra Black Pudding) e em regime sem baús (80,0 salas; derrota na sala 26 contra Succubus por falta de armadura), mantendo bom rendimento em pool alternativo de criaturas (94,4 salas).", styles['BodySm']),

        Paragraph("5. Conclusão", styles['SecHeading']),
        Paragraph("No E3, o algoritmo genético encontrou estratégias que avançaram mais que a regra fixa. A comparação não demonstrou vantagem clara sobre a busca aleatória com o mesmo orçamento de 240 avaliações. O resultado depende das regras do simulador e das sementes escolhidas. Trabalhos futuros podem investigar representações adaptativas com meta-aprendizado.", styles['BodySm']),

        Paragraph("6. Referências Essenciais", styles['SecHeading']),
        Paragraph("1. 5E-BITS. <b>D&D 5e SRD API</b>. Disponível em: &lt;https://docs.dnd5eapi.co/&gt;. Acesso em: 29 out. 2026.<br/>"
                  "2. EIBEN, A. E.; SMITH, J. E. <b>Introduction to Evolutionary Computing</b>. 2. ed. Berlin: Springer, 2015.<br/>"
                  "3. GOLDBERG, D. E. <b>Genetic Algorithms in Search, Optimization, and Machine Learning</b>. Addison-Wesley, 1989.<br/>"
                  "4. RUSSELL, S.; NORVIG, P. <b>Inteligência Artificial: Uma Abordagem Moderna</b>. 4. ed. Rio de Janeiro: GEN LTC, 2022.<br/>"
                  "5. WIZARDS OF THE COAST. <b>System Reference Document 5.1 (SRD 5.1)</b>. CC-BY-4.0. Disponível em: &lt;https://www.dndbeyond.com/srd&gt;.", styles['BodySm']),
    ]

    doc_pdf = SimpleDocTemplate(str(pdf_path), pagesize=A4, leftMargin=34, rightMargin=34, topMargin=28, bottomMargin=28)
    doc_pdf.build(story)

    # DOCX
    d = docx.Document()
    d.add_heading("Masmorra Genética: Otimização Evolutiva de Políticas de Combate em Ambiente Procedural", level=1)
    d.add_paragraph("Eduardo Coque Corrêa de Lima, Fernando Eduardo Motta Mendes, Matheus Alcântara Pereira, Reuel Vitor Lanzetti, Rogério Tiritan Marcone\n"
                    "Faculdades Integradas de Bauru (FIB) — Curso de Ciência da Computação — Inteligência Artificial II — 2026")
    for sec_num, sec_title, text in [
        ("1", "Introdução", "Algoritmos genéticos são técnicas de busca inspiradas em seleção e hereditariedade. O projeto procura estratégias para um guerreiro atravessar uma masmorra de 100 salas, administrando atributos, aliados e equipamentos."),
        ("2", "Objetivos", "Comparar o algoritmo genético com uma regra fixa e uma busca aleatória. Também avaliamos taxas de mutação, tamanhos de população e mudanças nas regras do simulador."),
        ("3", "Metodologia", "Usamos uma cópia de 334 criaturas da D&D 5e SRD API. Cada estratégia tem 16 genes que orientam atributos, aliados e compras. O algoritmo usa seleção por torneio, cruzamento, mutação e elitismo. O treino usa as sementes 101 a 105; a validação principal usa 201 a 210. No E3, cada repetição das duas buscas teve 240 avaliações."),
        ("4", "Resultados e Discussão", "No E1, a mutação de 25% teve média de 95,06 salas. No E2, a população de 40 teve média de 89,56. No E3, a regra fixa obteve 69,00 salas, a busca aleatória 92,27 e o AG 91,27. Não houve evidência suficiente de diferença entre as buscas (p=0,748). No E5, as médias foram 90,38 para AG com mutação de 10%, 92,49 para 25% e 94,56 para busca aleatória."),
        ("5", "Conclusão", "O AG avançou mais que a regra fixa no E3, mas a comparação não demonstrou vantagem clara sobre a busca aleatória. Os resultados dependem das sementes e das regras do simulador."),
        ("6", "Referências", "5e-bits SRD API; Eiben & Smith (2015); Goldberg (1989); Russell & Norvig (2022); Wizards of the Coast (2016)."),
    ]:
        d.add_heading(f"{sec_num}. {sec_title}", level=2)
        d.add_paragraph(text)
    d.save(str(docx_path))

    doc_fitz = fitz.open(str(pdf_path))
    print(f"Resumo Expandido gerado: {len(doc_fitz)} página(s) (Meta: estritamente 2 páginas).")
    doc_fitz.close()


# ==============================================================================
# 4. FICHA DE EXPERIMENTOS
# ==============================================================================
def generate_ficha_experimentos():
    pdf_path = OUT_DIR / "Ficha_Experimentos.pdf"
    docx_path = OUT_DIR / "Ficha_Experimentos.docx"
    styles = setup_reportlab_styles()

    story = [
        Paragraph("FICHA DE EXPERIMENTOS CONTROLADOS — MASMORRA GENÉTICA", styles['DocTitle']),
        Paragraph("<b>Grupo 7 · Tema 9: Algoritmos Genéticos</b> · FIB Inteligência Artificial II (2026)<br/>"
                  "<b>Dataset:</b> D&D 5e SRD 2014 (srd-2014-v1.0.0) · <b>Regras:</b> balance-v1.0.0 · <b>Orçamento:</b> 240 avaliações efetivas", styles['DocSubTitle']),
        HRFlowable(width="100%", thickness=0.8, color=C_PRIMARY, spaceAfter=6),
    ]

    exp_table_data = [
        [Paragraph("<b>Exp.</b>", styles['TableHead']),
         Paragraph("<b>Hipótese</b>", styles['TableHead']),
         Paragraph("<b>Alteração / Configuração</b>", styles['TableHead']),
         Paragraph("<b>Métrica / Resultado</b>", styles['TableHead']),
         Paragraph("<b>Interpretação Científica</b>", styles['TableHead'])],

        [Paragraph("<b>E1</b>", styles['TableCellBold']),
         Paragraph("Taxas de mutação afetam o equilíbrio entre exploração e diversidade genética.", styles['TableCell']),
         Paragraph("Mutação a 2%, 10% e 25%. Pop 20, 12 ger. (240 evals), 5 repetições. Validação sementes 201–210.", styles['TableCell']),
         Paragraph("• 2%: 91,28 ± 3,31 (28% conc.)<br/>• 10%: 92,12 ± 3,42 (20% conc.)<br/>• 25%: <b>95,06 ± 2,02</b> (36% conc.)", styles['TableCell']),
         Paragraph("Mutação de 25% sustentou maior diversidade (0,110 vs 0,035) sem degenerar a busca, mitigando estagnação precoce.", styles['TableCell'])],

        [Paragraph("<b>E2</b>", styles['TableCellBold']),
         Paragraph("Com orçamento fixo (240 evals), variar tamanho de população altera a exploração.", styles['TableCell']),
         Paragraph("Populações 12 (24 ger), 20 (14 ger) e 40 (7 ger). Mutação 10%, 5 repetições. Validação 201–210.", styles['TableCell']),
         Paragraph("• Pop 12: 86,28 ± 5,63 (18% conc.)<br/>• Pop 20: 86,82 ± 3,58 (20% conc.)<br/>• Pop 40: <b>89,56 ± 3,43</b> (20% conc.)", styles['TableCell']),
         Paragraph("População maior (40) explorou melhor o hipercubo contínuo inicialmente, reduzindo gerações ociosas estagnadas.", styles['TableCell'])],

        [Paragraph("<b>E3</b>", styles['TableCellBold']),
         Paragraph("O AG supera a política fixa heurística e compete com a busca aleatória.", styles['TableCell']),
         Paragraph("Fixa vs Busca Aleatória (240 evals) vs AG (240 evals, mut 10%). 7 repetições. Validação 201–210.", styles['TableCell']),
         Paragraph("• Fixa: 69,00 (0% conc.)<br/>• Aleatória: 92,27 ± 4,16 (25,7% conc.)<br/>• AG: 91,27 ± 4,11 (28,6% conc.)<br/>Mann-Whitney: <b>p = 0,748</b>", styles['TableCell']),
         Paragraph("O AG teve média maior que a regra fixa. Não houve evidência suficiente de diferença entre AG e busca aleatória (p > 0,05).", styles['TableCell'])],

        [Paragraph("<b>E4</b>", styles['TableCellBold']),
         Paragraph("A estratégia campeã sofre queda de rendimento quando o ambiente é modificado.", styles['TableCell']),
         Paragraph("Estratégia campeã avaliada em: Treino (101–105), Validação (201–210), Pool alternativo, Dificuldade +15%, Sem baús.", styles['TableCell']),
         Paragraph("• Treino: 98,2 (60% conc.)<br/>• Validação: 96,9 (40% conc.)<br/>• Pool alt.: 94,4 (20% conc.)<br/>• Dif +15%: <b>73,4</b> (10% conc.)<br/>• Sem baús: <b>80,0</b> (20% conc.)", styles['TableCell']),
         Paragraph("Estratégia mantém robustez em novos monstros (+16,9 salas vs fixa), mas é sensível a choques de atrito (+15% dif) e privação econômica (sem baús).", styles['TableCell'])],

        [Paragraph("<b>E5</b><br/><i>(Pré-reg.)</i>", styles['TableCellBold']),
         Paragraph("Validação cruzada de AG (10% e 25%) vs Busca Aleatória em 20 sementes virgens.", styles['TableCell']),
         Paragraph("Treino nas sementes 101–105. Validação em 20 sementes inéditas (401–420). 10 repetições de 240 evals.", styles['TableCell']),
         Paragraph("• AG 10%: 90,38 ± 3,83 (14,5% conc.)<br/>• AG 25%: 92,49 ± 2,80 (19,0% conc.)<br/>• Aleatória: <b>94,56 ± 2,42</b> (20,0% conc.)<br/>AG25 vs 10 p=0,241; Aleat vs AG10 p=0,021", styles['TableCell']),
         Paragraph("A média com 25% foi maior, mas a diferença entre as taxas não foi conclusiva. A busca aleatória teve média maior que o AG-10%; o experimento não identifica a causa.", styles['TableCell'])],
    ]

    t = Table(exp_table_data, colWidths=[40, 115, 115, 115, 125])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, C_LINE),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [C_WHITE, C_BG_LIGHT]),
    ]))
    story.append(t)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Análise Obrigatória de Três Casos Limite / Falhas Concretas", styles['SecHeading']))
    failures = [
        ("1. Semente 201, Dificuldade +15% (Derrota na Sala 25 contra Black Pudding):",
         "O guerreiro campeão concluiu 24 salas, enquanto a heurística fixa concluiu 25 salas no mesmo cenário. Com +15% de HP e dano nos monstros, a política do AG demorou a priorizar armas de tier avançado, sofrendo desgaste acumulativo no combate corpo a corpo demorado."),
        ("2. Semente 209, Sem Baús (Derrota na Sala 26 contra Succubus/Incubus):",
         "O guerreiro chegou à sala 26 com arma nível 2, escudo nível 1, mas <b>sem nenhuma armadura</b> (tier 0) e 38 moedas restantes. A reserva de contingência (38,8 moedas) travou a compra da armadura de couro, expondo o combatente ao dano mágico direto da criatura."),
        ("3. Semente 308, Composição Alternativa (Derrota na Sala 79 contra Adult Red Dragon):",
         "Entre as salas 76 e 78, a vida pós-recuperação caiu sucessivamente de 380 para 332 devido a três salas duplas com resistências elementais. O guerreiro iniciou a sala 79 com HP incompleto e esgotou os 40 turnos de combate sem conseguir superar o dragão."),
    ]
    for title, desc in failures:
        story.append(Paragraph(f"<b>{title}</b> {desc}", styles['BodySm']))

    doc_pdf = SimpleDocTemplate(str(pdf_path), pagesize=A4, leftMargin=32, rightMargin=32, topMargin=28, bottomMargin=28)
    doc_pdf.build(story)

    # DOCX
    d = docx.Document()
    d.add_heading("Ficha de Experimentos — Masmorra Genética", level=1)
    d.add_paragraph("Faculdades Integradas de Bauru (FIB) · Grupo 7 · IA II 2026\n"
                    "Dataset: D&D 5e SRD (srd-2014-v1.0.0) · Regras: balance-v1.0.0 · Orçamento: 240 avaliações")
    table = d.add_table(rows=1, cols=5)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(["Exp.", "Hipótese", "Alteração", "Métrica/Resultado", "Interpretação"]):
        table.rows[0].cells[i].text = h
    for row in exp_table_data[1:]:
        r = table.add_row().cells
        for col_idx in range(5):
            r[col_idx].text = row[col_idx].text.replace("<b>", "").replace("</b>", "").replace("<br/>", "\n")
    d.add_heading("Análise de Três Casos de Falha", level=2)
    for title, desc in failures:
        d.add_paragraph(f"{title}\n{desc.replace('<b>','').replace('</b>','')}")
    d.save(str(docx_path))
    print("Ficha de Experimentos gerada (PDF e DOCX).")


# ==============================================================================
# 5. DIÁRIO DE IA (PDF)
# ==============================================================================
def generate_diario_ia_pdf():
    pdf_path = OUT_DIR / "Diario_IA.pdf"
    docx_path = OUT_DIR / "Diario_IA.docx"
    styles = setup_reportlab_styles()

    story = [
        Paragraph("DIÁRIO DE USO DE IA GENERATIVA — GRUPO 7", styles['DocTitle']),
        Paragraph("<b>Faculdades Integradas de Bauru (FIB)</b> · Ciência da Computação · IA II (2026)<br/>"
                  "<b>Projeto:</b> Masmorra Genética: A Evolução do Guerreiro<br/>"
                  "<b>Integrantes:</b> Eduardo Lima, Fernando Mendes, Matheus Pereira, Reuel Lanzetti, Rogério Marcone", styles['DocSubTitle']),
        HRFlowable(width="100%", thickness=0.8, color=C_PRIMARY, spaceAfter=6),

        Paragraph("1. Ferramentas Utilizadas", styles['SecHeading']),
        Paragraph("• <b>Codex (OpenAI):</b> Utilizado em 29/10/2026 para prototipação da interface Streamlit, modo de busca automática com parada ao atingir 100 salas e histórico de tentativas.<br/>"
                  "• <b>Google Antigravity (Google DeepMind):</b> Utilizado em 10/11/2026 para auditoria de requisitos oficiais, aba didática com os 16 genes reais, pré-registro e execução do experimento E5 em 20 sementes virgens, geração de capturas automatizadas via Playwright e pacote de entrega.", styles['BodySm']),

        Paragraph("2. Resumo das Interações Relevantes", styles['SecHeading']),
        Paragraph("• <b>29/10 (Codex):</b> Solicitação de identidade temática (Atlas de RPG). A IA propôs layout em capítulos; o grupo adaptou para não ocultar os dados estatísticos reais.<br/>"
                  "• <b>29/10 (Codex):</b> Implementação do loop de treino interativo (`search_journey`). O grupo estabeleceu teto de 400 avaliações para evitar travamentos e adicionou alerta de que vencer no treino é resultado in-sample.<br/>"
                  "• <b>29/10 (Codex):</b> Histórico de tentativas e replay. O grupo adicionou trava de segurança por assinatura SHA-256 para evitar mesclar corridas de regras diferentes.<br/>"
                  "• <b>10/11 (Antigravity):</b> Auditoria do projeto e aba 'Passo a passo do algoritmo'. Implementado `src/ui/algorithm_explainer.py` com simulador real de crossover e mutação; 5 novos testes pytest adicionados.<br/>"
                  "• <b>10/11 (Antigravity):</b> Experimento adicional E5 com pré-registro. Executadas 10 repetições nas sementes 401–420; o grupo abraçou o resultado de que a busca aleatória supera o AG conservador em sementes virgens sob 240 avaliações.<br/>"
                  "• <b>10/11 (Antigravity):</b> Geração de 15 capturas reais no Edge headless e gráficos temáticos sem interpolações enganosas.", styles['BodySm']),

        Paragraph("3. Síntese dos Checkpoints e Autoavaliação", styles['SecHeading']),
        Paragraph("• <b>27/10:</b> Coleta e congelamento dos dados via SHA-256; normalização de monstros; primeiro baseline.<br/>"
                  "• <b>03/11:</b> Experimentos E1 a E4. Correção do orçamento v1 (na v2 elites não são recontadas). O grupo rejeitou sugestão de manipular sementes para forçar vitória do AG.<br/>"
                  "• <b>10/11 (Pré-banca):</b> Auditoria integral, E5 em 20 sementes virgens, 53 testes passando (100%), capturas Playwright e consolidação final.<br/>"
                  "• <b>Autoavaliação do Grupo:</b> Postura madura e reflexiva (nível 5): o grupo valida todo código com asserts automatizados, compreende a matemática por trás dos operadores e assume integralmente a responsabilidade técnica e científica sobre o trabalho entregue.", styles['BodySm']),
    ]

    doc_pdf = SimpleDocTemplate(str(pdf_path), pagesize=A4, leftMargin=36, rightMargin=36, topMargin=32, bottomMargin=32)
    doc_pdf.build(story)

    # Copia o docx oficial preenchido para a pasta de entrega
    import shutil
    shutil.copy(str(ROOT / "docs" / "diario_de_ia_oficial.docx"), str(docx_path))
    print("Diário de IA gerado (PDF e cópia do DOCX oficial).")


def main():
    generate_canvas()
    generate_model_card()
    generate_resumo_expandido()
    generate_ficha_experimentos()
    generate_diario_ia_pdf()
    print("Todos os 5 documentos acadêmicos foram gerados em ENTREGA_FINAL_GRUPO7/01_DOCUMENTACAO/.")


if __name__ == "__main__":
    main()
