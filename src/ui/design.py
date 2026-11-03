"""Identidade visual do atlas e componentes de leitura da expedição."""

from __future__ import annotations

import base64
from html import escape
from pathlib import Path

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st


ASSET_DIR = Path(__file__).resolve().parent / "assets"
INK = "#292720"
RED = "#8d3d30"
GREEN = "#526952"
BRASS = "#a17b40"


def _svg_image(svg: str, alt: str = "") -> str:
    # Algumas versões de st.html removem SVG embutido; os arquivos vetoriais locais preservam a arte.
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f'<img src="data:image/svg+xml;base64,{encoded}" alt="{escape(alt, quote=True)}">'


def apply_theme() -> None:
    st.html(f"<style>{(ASSET_DIR / 'atlas.css').read_text(encoding='utf-8')}</style>")
    pio.templates["atlas"] = go.layout.Template(layout=go.Layout(
        colorway=[RED, GREEN, BRASS, "#6a777c", "#9b7a6b"],
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI, sans-serif", color=INK, size=13),
        xaxis=dict(gridcolor="#ded8ca", zerolinecolor="#c5bdac"),
        yaxis=dict(gridcolor="#ded8ca", zerolinecolor="#c5bdac"),
        margin=dict(l=16, r=16, t=35, b=24),
        legend=dict(orientation="h", y=-0.2, x=0),
        hoverlabel=dict(bgcolor="#fffaf0", font_color=INK),
    ))
    pio.templates.default = "atlas"


def heading(kicker: str, title: str, text: str) -> None:
    st.html(f'<header class="page-heading"><div class="eyebrow">{escape(kicker)}</div>'
            f'<h1>{escape(title)}</h1><p class="intro">{escape(text)}</p></header>')


def sidebar_brand() -> None:
    st.html('''<div class="brand"><div class="brand-symbol" aria-hidden="true">✣</div>
        <div class="brand-name">Masmorra<br><em>Genética</em></div>
        <div class="brand-caption">Atlas de estratégias · Grupo 7</div></div>''')


def section_label(number: str, title: str, note: str = "") -> None:
    st.html(f'<div class="section-label"><span>{escape(number)}</span>'
            f'<h2>{escape(title)}</h2><small>{escape(note)}</small></div>')


def atlas_html(current_room: int | None = None, failure_room: int | None = None) -> str:
    """Mapa esquemático de 100 salas, com cores de progresso obtidas da reprodução da tentativa."""
    cells = []
    centers = []
    for number in range(1, 101):
        row, offset = divmod(number - 1, 10)
        col = offset if row % 2 == 0 else 9 - offset
        x, y = 57 + col * 35, 78 + row * 29
        centers.append(f"{x + 10},{y + 8}")
        visited = current_room is not None and number <= current_room
        failed = visited and number == failure_room
        active = number == current_room
        milestone = number in (1, 25, 50, 75, 100)
        fill = RED if failed else GREEN if visited else "#e3d7bf" if milestone else "#eee7d8"
        stroke = INK if active else "#a99b80" if milestone else "#c4b89f"
        color = "#fffaf0" if visited else "#675e4e"
        label = f"Sala {number}" + (" · derrota" if failed else " · registrada" if visited else "")
        cells.append(f'<g><title>{label}</title><rect x="{x}" y="{y}" width="20" height="16" '
                     f'fill="{fill}" stroke="{stroke}" stroke-width="{2 if active else 0.8}"/>'
                     f'<text x="{x + 10}" y="{y + 11}" text-anchor="middle" font-size="7.2" '
                     f'fill="{color}">{number:02d}</text></g>')
        if active:
            cells.append(f'<path d="M{x+10} {y-8} l-4 -6 h8 z" fill="{RED}"/>')
    title = "Planta da masmorra" if current_room is None else f"Registro até a sala {current_room}"
    subtitle = "100 SALAS / DIFICULDADE CRESCENTE" if current_room is None else "VERDE · PERCORRIDO     VERMELHO · DERROTA"
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 460 430" role="img" aria-label="{title}">
        <defs><pattern id="atlas-grid" width="17.5" height="14.5" patternUnits="userSpaceOnUse">
        <path d="M 17.5 0 H 0 V 14.5" fill="none" stroke="#d6cbb5" stroke-width="0.35"/>
        </pattern></defs>
        <rect x="17" y="17" width="426" height="396" fill="url(#atlas-grid)"/>
        <rect x="17" y="17" width="426" height="396" fill="none" stroke="#c2b59a"/>
        <path d="M17 33 V17 H33 M427 17 H443 V33 M443 397 V413 H427 M33 413 H17 V397"
            fill="none" stroke="#76694e" stroke-width="1.5"/>
        <text x="38" y="45" fill="#665a45" font-family="Georgia, serif" font-size="15">{title}</text>
        <text x="38" y="60" fill="#7d7058" font-size="7" letter-spacing="1.1">{subtitle}</text>
        <polyline points="{' '.join(centers)}" fill="none" stroke="#c2ad85" stroke-width="5"/>
        {''.join(cells)}
        <g transform="translate(409 52)" stroke="#8d3d30" fill="none" stroke-width="1">
            <path d="M0 -15 V15 M-10 0 H10 M0 -12 L4 0 L0 -3 L-4 0 Z"/>
            <text x="0" y="-19" text-anchor="middle" stroke="none" fill="#8d3d30" font-size="7">N</text>
        </g>
        <path d="M38 378 H422" stroke="#bdb092" stroke-width="0.8"/>
        <text x="38" y="397" fill="#76694e" font-size="8">I. ENTRADA</text>
        <text x="422" y="397" text-anchor="end" fill="#8d3d30" font-size="8">C. ÚLTIMO ENCONTRO</text>
        </svg>'''
    return f'<div class="atlas-sheet">{_svg_image(svg, title)}<div class="map-footnote">Planta esquemática · os encontros dependem da semente</div></div>'


def strategy_summary(weights: tuple | list, ally: str, market: str) -> None:
    bars = "".join(f'<span style="width:{value * 100:.2f}%;background:{color}"></span>'
                   for value, color in zip(weights, [RED, GREEN, BRASS]))
    st.html(f'''<div class="strategy-note"><div class="eyebrow">Plano de expedição</div>
        <div class="attribute-bar" aria-hidden="true">{bars}</div>
        <div class="attribute-legend"><span>Força {weights[0]:.0%}</span>
        <span>Vida {weights[1]:.0%}</span><span>Defesa {weights[2]:.0%}</span></div>
        <p>Aliado prioritário <strong>{escape(ally)}</strong><br>
        Mercado <strong>{escape(market)}</strong></p></div>''')


def creature_seal(creature_type: str) -> str:
    """Gravuras geométricas de cada família, feitas localmente com os nomes existentes."""
    motifs = {
        "dragon": '<path d="M28 64 L18 33 L41 44 L50 20 L59 44 L82 33 L72 64 L61 79 H39 Z"/><path d="M35 59 L43 62 M65 59 L57 62 M44 72 H56"/>',
        "undead": '<path d="M30 61 V45 A20 22 0 0 1 70 45 V61 L62 68 V79 H38 V68 Z"/><circle cx="41" cy="51" r="5"/><circle cx="59" cy="51" r="5"/><path d="M50 58 L47 64 H53 Z M45 70 V78 M55 70 V78"/>',
        "beast": '<path d="M28 66 L24 26 L43 41 H57 L76 26 L72 66 L50 81 Z"/><path d="M33 53 L43 57 M67 53 L57 57 M44 66 H56 L50 73 Z"/>',
        "humanoid": '<path d="M28 72 V39 L50 23 L72 39 V72 L50 81 Z M28 48 H72 M50 48 V81"/><path d="M35 57 H44 M56 57 H65"/>',
    }
    motif = motifs.get(creature_type, '<path d="M50 21 L76 37 V67 L50 82 L24 67 V37 Z M24 37 L50 53 L76 37 M50 53 V82"/><circle cx="50" cy="52" r="12"/>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="46" fill="none" stroke="#c9b99d" stroke-dasharray="2 4"/><g fill="none" stroke="{RED}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{motif}</g></svg>'
    return _svg_image(svg)


def footer() -> None:
    st.html('<footer class="atlas-footer"><span>Masmorra Genética</span>'
            '<span>Grupo 7 · IA II · FIB · 2026</span></footer>')
