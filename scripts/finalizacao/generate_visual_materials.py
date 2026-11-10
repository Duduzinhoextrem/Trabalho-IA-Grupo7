"""Gera os materiais visuais de divulgação:
1. Folder dobrável (A4 paisagem trifold em PDF)
2. Carrossel de Instagram (8 imagens 1080x1080 PNG em alta resolução)
3. Pacote do Vídeo de 1 a 3 min (roteiro, storyboard, legendas SRT e renderização MP4 via ffmpeg com capturas reais)
"""

from __future__ import annotations

import os
from pathlib import Path
import qrcode
from PIL import Image, ImageDraw, ImageFont

from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

ROOT = Path(__file__).resolve().parents[2]
OUT_DIV = ROOT / "ENTREGA_FINAL_GRUPO7" / "02_DIVULGACAO"
OUT_INSTA = OUT_DIV / "Instagram"
OUT_VIDEO = OUT_DIV / "Video"
OUT_DIV.mkdir(parents=True, exist_ok=True)
OUT_INSTA.mkdir(parents=True, exist_ok=True)
OUT_VIDEO.mkdir(parents=True, exist_ok=True)

# Paleta
PAPER = "#f3efe5"
INK = "#292720"
MUTED = "#746d60"
RED = "#8d3d30"
BRASS = "#a17b40"
LINE = "#d2c9b7"
WHITE = "#ffffff"


# ==============================================================================
# 1. FOLDER ACADÊMICO DOBRÁVEL (A4 PAISAGEM - 3 COLUNAS)
# ==============================================================================
def generate_folder():
    pdf_path = OUT_DIV / "Folder_Final.pdf"
    
    # Gera QR code provisório com indicação de URL
    qr = qrcode.QRCode(box_size=4, border=1)
    qr.add_data("http://localhost:8599 (URL pública em publicação)")
    qr_img = qr.make_image(fill_color=INK, back_color=PAPER)
    qr_path = ROOT / "docs" / "FINALIZACAO" / "evidencias" / "qrcode_folder.png"
    qr_path.parent.mkdir(parents=True, exist_ok=True)
    qr_img.save(str(qr_path))

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('FTitle', fontName='Helvetica-Bold', fontSize=12, leading=14, textColor=colors.HexColor(RED), spaceAfter=4)
    head_style = ParagraphStyle('FHead', fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=colors.HexColor(RED), spaceBefore=4, spaceAfter=2)
    body_style = ParagraphStyle('FBody', fontName='Helvetica', fontSize=7.5, leading=10, textColor=colors.HexColor(INK), spaceAfter=3)
    meta_style = ParagraphStyle('FMeta', fontName='Helvetica-Oblique', fontSize=6.5, leading=8.5, textColor=colors.HexColor(MUTED))

    # Coluna 1: O Desafio e os Dados
    col1 = [
        Paragraph("MASMORRA GENÉTICA", title_style),
        Paragraph("<b>A Evolução do Personagem Perfeito</b>", head_style),
        Paragraph("Como preparar um guerreiro para atravessar 100 salas de perigo crescente? Força bruta não basta: o personagem precisa equilibrar evolução de atributos, contratação de aliados e compras estratégicas no mercado.", body_style),
        Spacer(1, 4),
        Paragraph("<b>O Desafio das 100 Salas</b>", head_style),
        Paragraph("• Salas 1 a 10: Inimigos básicos (CR até 1.0).<br/>• Salas 11 a 60: Criaturas perigosas em grupos de 1 a 3.<br/>• Salas 61 a 99: Chefes colossais de elite.<br/>• Sala 100: O guardião final da masmorra.", body_style),
        Spacer(1, 4),
        Paragraph("<b>Dados Reais de Criaturas</b>", head_style),
        Paragraph("Utilizamos <b>334 criaturas reais</b> da <i>D&D 5e SRD API</i> (Wizards of the Coast / CC-BY-4.0). Vida, armadura e poder de ataque dos monstros vêm de estatísticas oficiais consolidadas.", body_style),
    ]

    # Coluna 2: A Técnica e os Resultados
    col2 = [
        Paragraph("COMO A IA EVOLUI", title_style),
        Paragraph("<b>Seleção, Cruzamento e Mutação</b>", head_style),
        Paragraph("Cada estratégia é um cromossomo de <b>16 decisões</b>. O Algoritmo Genético cria uma população, testa todos os guerreiros nas mesmas masmorras e combina as melhores decisões ao longo das gerações.", body_style),
        Spacer(1, 4),
        Paragraph("<b>O Que os Testes Revelaram?</b>", head_style),
        Paragraph("Comparamos o AG contra duas referências sob o mesmo orçamento de 240 avaliações:<br/>"
                  "• <b>Estratégia Fixa:</b> 69 salas concluídas (0% vitória).<br/>"
                  "• <b>Busca Aleatória:</b> 92,3 salas (25,7% vitória).<br/>"
                  "• <b>Algoritmo Genético:</b> 91,3 salas (28,6% vitória).<br/>"
                  "O AG e a busca aleatória empataram estatisticamente (p = 0,748), demonstrando que a diversidade é vital para não sobreajustar.", body_style),
        Spacer(1, 4),
        Paragraph("<b>Casos de Falha Reais</b>", head_style),
        Paragraph("Sem baús de recompensas, a média cai para 80 salas. Contra monstros com resistência mágica, a dependência de curandeiros atrasa o combate.", body_style),
    ]

    # Coluna 3: Protótipo, Créditos e QR Code
    col3 = [
        Paragraph("EXPERIMENTE AO VIVO", title_style),
        Paragraph("<b>Protótipo Web Interativo</b>", head_style),
        Paragraph("Navegue sala a sala, teste sua própria estratégia contra a da IA e explore o Bestiário interativo com filtros e download de dados.", body_style),
        Spacer(1, 6),
        Table([[RLImage(str(qr_path), width=75, height=75),
                Paragraph("<b>Acesse o projeto</b><br/>"
                          "Scaneie para rodar localmente ou acessar o repositório.<br/><br/>"
                          "<i>(Código 100% aberto)</i>", meta_style)]], colWidths=[80, 155]),
        Spacer(1, 8),
        Paragraph("<b>Grupo 7 · Inteligência Artificial II</b>", head_style),
        Paragraph("<b>FIB — Faculdades Integradas de Bauru (2026)</b><br/>"
                  "• Eduardo Coque Corrêa de Lima<br/>"
                  "• Fernando Eduardo Motta Mendes<br/>"
                  "• Matheus Alcântara Pereira<br/>"
                  "• Reuel Vitor Lanzetti<br/>"
                  "• Rogério Tiritan Marcone", meta_style),
    ]

    t = Table([[col1, col2, col3]], colWidths=[250, 250, 250])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LINEAFTER', (0,0), (1,0), 0.5, colors.HexColor(LINE)),
    ]))

    doc = SimpleDocTemplate(str(pdf_path), pagesize=landscape(A4), leftMargin=24, rightMargin=24, topMargin=24, bottomMargin=24)
    doc.build([t])
    print("Folder dobrável gerado em PDF.")


# ==============================================================================
# 2. CARROSSEL DO INSTAGRAM (8 IMAGENS 1080x1080)
# ==============================================================================
def generate_instagram_carousel():
    slides = [
        {
            "slide": 1,
            "tag": "INTELIGÊNCIA ARTIFICIAL II · FIB",
            "title": "Uma IA Consegue\nCriar o Guerreiro\nPerfeito?",
            "sub": "O desafio de sobreviver a 100 salas de uma masmorra implacável.",
            "detail": "Grupo 7 | Algoritmos Genéticos em Ação",
        },
        {
            "slide": 2,
            "tag": "O PROBLEMA",
            "title": "100 Salas de Perigo\ne Decisões Difíceis",
            "sub": "Força bruta não basta. Como investir pontos?",
            "detail": "• 16 decisões estratégicas (atributos, aliados e mercado)\n• 1 a 3 monstros por sala com dificuldade crescente\n• Gestão de vida, ouro e turnos de combate",
        },
        {
            "slide": 3,
            "tag": "BASE DE DADOS REAL",
            "title": "334 Criaturas do\nD&D 5e SRD",
            "sub": "Sem dados inventados: estatísticas reais do RPG.",
            "detail": "• Dragões, demônios, mortos-vivos e feras reais\n• Pontos de vida de 1 a 676 e dano adaptado\n• Snapshot congelado com hash SHA-256 público",
        },
        {
            "slide": 4,
            "tag": "COMO A IA APRENDE",
            "title": "Evolução Artificial\nna Prática",
            "sub": "Inspirado no princípio neodarwiniano de seleção natural.",
            "detail": "1. CRIAR: População de estratégias variadas\n2. TESTAR: Todas enfrentam as mesmas masmorras\n3. SELECIONAR: As melhores geram filhos\n4. CRUZAR & MUTAR: Pequenas mudanças geram inovação",
        },
        {
            "slide": 5,
            "tag": "O GRANDE CONFRONTO",
            "title": "AG vs. Regra Fixa vs.\nBusca Aleatória",
            "sub": "240 avaliações rigorosas para cada método.",
            "detail": "• Estratégia Fixa: 69 salas (0% vitória)\n• Busca Aleatória: 92,3 salas (25,7% vitória)\n• Algoritmo Genético: 91,3 salas (28,6% vitória)\nResultado: Empate estatístico (p = 0,748)!",
        },
        {
            "slide": 6,
            "tag": "DESCOBERTA CIENTÍFICA",
            "title": "Por que a Busca\nAleatória Empatou?",
            "sub": "A importância da honestidade acadêmica.",
            "detail": "Com um orçamento curto (240 tentativas), a busca aleatória explora livremente o espaço sem sofrer vício de sobreajuste às masmorras de treino.\nA melhor estratégia do AG zerou 4 de 10 masmorras!",
        },
        {
            "slide": 7,
            "tag": "LIMITAÇÕES E FALHAS",
            "title": "Onde o Guerreiro\nMais Falhou?",
            "sub": "Ciência de verdade analisa as derrotas.",
            "detail": "• Sala 25 (+15% dificuldade): Black Pudding derrotou o campeão por falta de armas rápidas\n• Sala 26 (Sem baús): Derrota por falta de armadura\n• Sala 79: Dragão Vermelho venceu por desgaste cumulativo",
        },
        {
            "slide": 8,
            "tag": "TESTE AO VIVO",
            "title": "Explore o Atlas da\nMasmorra Genética",
            "sub": "Protótipo interativo completo em Streamlit.",
            "detail": "Acompanhe as batalhas sala por sala e veja a evolução.\n\nGrupo 7: Eduardo Lima · Fernando Mendes\nMatheus Pereira · Reuel Lanzetti · Rogério Marcone\nFaculdades Integradas de Bauru (FIB) — 2026",
        },
    ]

    for s in slides:
        img = Image.new("RGB", (1080, 1080), color=PAPER)
        draw = ImageDraw.Draw(img)

        # Borda estilizada
        draw.rectangle([40, 40, 1040, 1040], outline=LINE, width=3)
        draw.rectangle([48, 48, 1032, 1032], outline=BRASS, width=1)

        # Cabeçalho da tag
        draw.text((80, 85), s["tag"], fill=RED, font_size=28)
        draw.line([(80, 130), (1000, 130)], fill=LINE, width=2)

        # Título principal
        y_title = 180
        for line in s["title"].split("\n"):
            draw.text((80, y_title), line, fill=INK, font_size=68)
            y_title += 80

        # Subtítulo
        draw.text((80, y_title + 25), s["sub"], fill=MUTED, font_size=34)
        draw.line([(80, y_title + 90), (320, y_title + 90)], fill=BRASS, width=4)

        # Detalhes / Bullet points
        y_det = y_title + 130
        for line in s["detail"].split("\n"):
            draw.text((80, y_det), line, fill=INK, font_size=32)
            y_det += 55

        # Rodapé com número do slide
        draw.text((80, 970), "Masmorra Genética · Grupo 7", fill=MUTED, font_size=24)
        draw.text((940, 970), f"{s['slide']} / 8", fill=RED, font_size=28)

        out_img_path = OUT_INSTA / f"slide_{s['slide']:02d}.png"
        img.save(out_img_path, "PNG")
    print("Carrossel do Instagram gerado (8 imagens 1080x1080).")


# ==============================================================================
# 3. PACOTE DE VÍDEO (ROTEIRO, STORYBOARD, LEGENDAS E MP4 RENDERIZADO VIA FFMPEG)
# ==============================================================================
def generate_video_package():
    # 1. Roteiro e Storyboard
    roteiro_content = """# Roteiro e Storyboard do Vídeo Demonstrativo (1 a 3 minutos)

**Projeto:** Masmorra Genética — Grupo 7 (IA II - FIB 2026)  
**Duração estimada:** 2 minutos e 10 segundos (130 segundos)  
**Estilo:** Apresentação acadêmica dinâmica com capturas reais do sistema e gráficos comprobatórios.

---

## Estrutura Temporal Segundo as Normas Oficiais

| Bloco | Tempo | Cena Visual | Áudio / Narração Sugerida |
| :--- | :--- | :--- | :--- |
| **1. Problema** | 00:00 – 00:15 | Tela de abertura e Atlas das 100 salas (`01_inicio.png`). | "Um guerreiro precisa atravessar uma masmorra de 100 salas de dificuldade crescente. Distribuir atributos no achismo não funciona: é preciso uma estratégia." |
| **2. Solução & Dados** | 00:15 – 00:35 | Bestiário com criaturas D&D e tela de dados (`11_bestiario.png`, `12_dados_e_fonte.png`). | "O Grupo 7 utilizou 334 criaturas reais da base D&D 5e SRD para compor os encontros, aplicando Algoritmos Genéticos para evoluir 16 decisões de combate, contratação e economia." |
| **3. Demonstração Real** | 00:35 – 01:15 | Aventura sala a sala e aba do algoritmo (`02_aventura_sala1.png`, `05_como_funciona_passo_a_passo.png`, `14_treino_automatico.png`). | "O algoritmo seleciona, cruza e muta políticas a cada geração. Na interface, o usuário acompanha a jornada sala a sala, vê os turnos de combate e analisa o histórico de tentativas." |
| **4. Resultados & Limitações** | 01:15 – 01:55 | Gráfico de baselines e cenários adversos (`07_resultados.png`, `grafico_comparacao_metodos.png`). | "Com 240 avaliações, o AG alcançou média de 91 salas e 28% de vitória integral, superando a regra fixa de 69 salas e empatando com a busca aleatória. A retirada de baús reduziu em 16 salas a sobrevivência." |
| **5. Encerramento** | 01:55 – 02:10 | Tela final com QR Code, links e créditos dos integrantes (`15_inicio_mobile.png`). | "O Masmorra Genética comprova que o rigor metodológico vale mais que alegações de superioridade. Acesse o protótipo e confira a documentação completa!" |
"""
    (OUT_VIDEO / "Roteiro_e_Storyboard.md").write_text(roteiro_content, encoding="utf-8")

    # 2. Legendas SRT
    srt_content = """1
00:00:01,000 --> 00:00:08,000
Masmorra Genética: Como a Inteligência Artificial pode evoluir a estratégia de um personagem?

2
00:00:08,500 --> 00:00:16,000
Em uma masmorra de 100 salas, o guerreiro enfrenta desafios gerados com dados reais do D&D 5e SRD.

3
00:00:16,500 --> 00:00:26,000
Cada estratégia é codificada em 16 genes: atributos de combate, prioridades de 5 aliados e mercado.

4
00:00:26,500 --> 00:00:38,000
O Algoritmo Genético opera seleção por torneio, recombinação BLX-alfa, mutação gaussiana e elitismo.

5
00:00:38,500 --> 00:00:52,000
No aplicativo Streamlit, o usuário pode testar estratégias próprias ou acionar a busca automática.

6
00:00:52,500 --> 00:01:06,000
Em 240 avaliações, o AG atingiu média de 91 salas e 28% de vitória, superando a regra fixa de 69 salas.

7
00:01:06,500 --> 00:01:20,000
A comparação com busca aleatória mostrou empate estatístico (p = 0,748), evidenciando transparência.

8
00:01:20,500 --> 00:01:30,000
Grupo 7 · Ciência da Computação · Faculdades Integradas de Bauru (FIB 2026).
"""
    (OUT_VIDEO / "Legendas_Apresentacao.srt").write_text(srt_content, encoding="utf-8")

    # 3. Renderização do Vídeo MP4 via ffmpeg
    # Utiliza as capturas reais existentes em docs/FINALIZACAO/evidencias/capturas/
    cap_dir = ROOT / "docs" / "FINALIZACAO" / "evidencias" / "capturas"
    img_list = [
        cap_dir / "01_inicio.png",
        cap_dir / "11_bestiario.png",
        cap_dir / "05_como_funciona_passo_a_passo.png",
        cap_dir / "02_aventura_sala1.png",
        cap_dir / "07_resultados.png",
        ROOT / "results" / "finalizacao" / "graficos" / "grafico_comparacao_metodos.png",
        cap_dir / "13_laboratorio.png",
        cap_dir / "03_aventura_final_e_comparacao.png"
    ]
    
    # Filtra imagens existentes
    valid_imgs = [p for p in img_list if p.exists()]
    if valid_imgs:
        # Monta concat script para o ffmpeg (cada cena exibida por 5 segundos)
        concat_txt = OUT_VIDEO / "concat_scenes.txt"
        with open(concat_txt, "w", encoding="utf-8") as f:
            for p in valid_imgs:
                # Escapa barras para ffmpeg
                f.write(f"file '{p.resolve().as_posix()}'\n")
                f.write("duration 6\n")
            f.write(f"file '{valid_imgs[-1].resolve().as_posix()}'\n")

        mp4_out = OUT_VIDEO / "Masmorra_Genetica_Apresentacao.mp4"
        ffmpeg_cmd = (
            f'ffmpeg -y -f concat -safe 0 -i "{concat_txt.resolve().as_posix()}" '
            f'-vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=#292720" '
            f'-c:v libx264 -pix_fmt yuv420p -r 24 "{mp4_out.resolve().as_posix()}"'
        )
        print("Renderizando vídeo com capturas reais via ffmpeg...")
        ret = os.system(ffmpeg_cmd)
        if ret == 0 and mp4_out.exists():
            print(f"Vídeo renderizado com sucesso: {mp4_out.name} ({mp4_out.stat().st_size} bytes)")
        else:
            print("Aviso: ffmpeg gerou código", ret)
    print("Pacote de vídeo concluído.")


def main():
    generate_folder()
    generate_instagram_carousel()
    generate_video_package()
    print("Todos os materiais visuais foram gerados com sucesso!")


if __name__ == "__main__":
    main()
