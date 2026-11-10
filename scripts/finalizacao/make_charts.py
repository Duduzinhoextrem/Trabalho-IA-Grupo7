"""Gráficos finais (em português) gerados a partir dos JSON de resultados.

Nenhum número é digitado aqui: tudo é lido de `data/experiments/`.
Uso: python scripts/finalizacao/make_charts.py
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "finalizacao" / "graficos"
OUT.mkdir(parents=True, exist_ok=True)

PAPER, INK, MUTED = "#f3efe5", "#292720", "#746d60"
RED, GREEN, BRASS, GRAY = "#8d3d30", "#526952", "#a17b40", "#8e8778"

plt.rcParams.update({
    "figure.facecolor": PAPER, "axes.facecolor": PAPER, "savefig.facecolor": PAPER,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
    "text.color": INK, "font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
    "font.size": 12,
})

v2 = json.loads((ROOT / "data/experiments/scientific_experiments_v2.json").read_text(encoding="utf-8"))
e5_path = ROOT / "data/experiments/extra_mutation_e5_v1.json"
e5 = json.loads(e5_path.read_text(encoding="utf-8")) if e5_path.exists() else None


def jitter(n: int, seed: int = 3) -> np.ndarray:
    return np.random.default_rng(seed).uniform(-0.12, 0.12, n)


def save(fig: plt.Figure, name: str) -> None:
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(OUT / name, dpi=200)
    plt.close(fig)
    print("gerado", name)


def dots_chart(labels, values_list, colors, title, subtitle, name, ylim=(0, 105), ref=None):
    fig, ax = plt.subplots(figsize=(8, 5.2))
    for i, (vals, color) in enumerate(zip(values_list, colors)):
        vals = np.array(vals, dtype=float)
        ax.bar(i, vals.mean(), width=0.55, color=color, alpha=0.88, zorder=2)
        ax.scatter(i + jitter(len(vals), seed=i + 1), vals, s=34, color=INK, alpha=0.75, zorder=3)
        ax.text(i, ylim[0] + (vals.mean() - ylim[0]) * 0.5, f"{vals.mean():.1f}", ha="center", va="center", fontweight="bold", color="white", fontsize=15)
    if ref is not None:
        ax.axhline(ref[0], color=MUTED, ls="--", lw=1)
        ax.text(len(labels) - 0.5, ref[0] + 0.4, ref[1], ha="right", color=MUTED, fontsize=10)
    ax.set_xticks(range(len(labels)), labels)
    ax.set_ylim(*ylim)
    ax.set_ylabel("Média de salas concluídas (validação)")
    ax.set_title(title, loc="left", fontsize=15, fontweight="bold")
    fig.text(0.01, 0.01, textwrap.fill(subtitle, 100), fontsize=9.5, color=MUTED, va="bottom")
    ax.grid(axis="y", color="#d2c9b7", lw=0.6, zorder=0)
    save(fig, name)


# 1. Comparação principal (E3)
m = v2["experiment_3_baselines"]["methods"]
rs = [r["val_mean_rooms"] for r in m["random_search"]["repeats"]]
ga = [r["val_mean_rooms"] for r in m["genetic_algorithm"]["repeats"]]
fixed = m["fixed_baseline"]["val_mean_rooms"]
p = v2["experiment_3_baselines"]["statistical_tests"]["ga_vs_random_search_repeats"]["mann_whitney_p"]
dots_chart(
    ["Estratégia fixa", "Busca aleatória", "Algoritmo genético"], [[fixed], rs, ga], [GRAY, BRASS, RED],
    "Busca aleatória e AG ficaram praticamente empatados",
    f"Pontos: 1 por repetição (7 repetições, 240 avaliações cada). Validação: sementes 201–210. Mann-Whitney AG × aleatória: p = {p:.3f}.",
    "grafico_comparacao_metodos.png",
)

# 2. Mutação (E1)
e1 = v2["experiment_1_mutation"]["results"]
dots_chart(
    ["2%", "10%", "25%"], [[r["val_mean_rooms"] for r in e1[k]["repeats"]] for k in ("2%", "10%", "25%")], [GRAY, BRASS, RED],
    "Taxa de mutação (E1): 25% teve a maior média",
    "Pontos: 1 por repetição (5 por taxa, 240 avaliações). Validação 201–210. Diferença pequena diante da dispersão entre repetições.",
    "grafico_mutacao_e1.png", ylim=(0, 105),
)

# 3. População (E2)
e2 = v2["experiment_2_population"]["results"]
keys = sorted(e2, key=lambda k: e2[k]["pop_size"])
dots_chart(
    [f"População {e2[k]['pop_size']}" for k in keys], [[r["val_mean_rooms"] for r in e2[k]["repeats"]] for k in keys],
    [GRAY, BRASS, RED], "Tamanho da população (E2) com o mesmo orçamento",
    "Pontos: 1 por repetição (5 por configuração, 240 avaliações). Validação 201–210.",
    "grafico_populacao_e2.png", ylim=(0, 105),
)

# 4. Cenários (E4)
sc = v2["experiment_4_generalization"]["scenarios"]
fig, ax = plt.subplots(figsize=(9, 5.2))
labels = ["Treino\n101–105", "Validação\n201–210", "Composição\nalternativa", "Dificuldade\n+15%", "Sem baús"]
ga_v = [s["genetic_algorithm"]["mean_rooms"] for s in sc.values()]
fx_v = [s["fixed_baseline"]["mean_rooms"] for s in sc.values()]
x = np.arange(len(labels))
ax.bar(x - 0.2, fx_v, 0.38, color=GRAY, label="Estratégia fixa")
ax.bar(x + 0.2, ga_v, 0.38, color=RED, label="Estratégia selecionada (AG)")
for xi, (a, b) in enumerate(zip(fx_v, ga_v)):
    ax.text(xi - 0.2, a + 1, f"{a:.1f}", ha="center", fontsize=10)
    ax.text(xi + 0.2, b + 1, f"{b:.1f}", ha="center", fontsize=10, fontweight="bold")
ax.set_xticks(x, labels)
ax.set_ylim(0, 112)
ax.set_ylabel("Média de salas concluídas")
ax.set_title("Novos cenários (E4): o desempenho cai quando as regras mudam", loc="left", fontsize=14, fontweight="bold")
ax.legend(frameon=False, loc="upper right", ncol=2)
ax.grid(axis="y", color="#d2c9b7", lw=0.6, zorder=0)
save(fig, "grafico_cenarios_e4.png")

# 5. Evolução por gerações (execução selecionada)
hist = v2["best_champion_strategy"]["history"]
fig, ax = plt.subplots(figsize=(8, 5.2))
gens = [h["generation"] for h in hist]
ax.plot(gens, [h["best_mean_rooms"] for h in hist], "-o", color=RED, lw=2.4, label="Melhor estratégia")
ax.plot(gens, [h["pop_mean_rooms"] for h in hist], "-o", color=BRASS, lw=2.4, label="Média da população")
ax.set_xlabel("Geração")
ax.set_ylabel("Média de salas no treino (sementes 101–105)")
ax.set_ylim(0, 105)
ax.set_title("Evolução em uma execução do AG", loc="left", fontsize=15, fontweight="bold")
ax.legend(frameon=False, loc="lower right")
ax.grid(color="#d2c9b7", lw=0.6)
ax.text(0, -0.17, f"Execução selecionada no E3; {v2['best_champion_strategy']['total_objective_evaluations']} avaliações.",
        transform=ax.transAxes, fontsize=9.5, color=MUTED)
save(fig, "grafico_evolucao_geracoes.png")

# 6. E5
if e5:
    mm = e5["methods"]
    dots_chart(
        ["AG mutação 10%", "AG mutação 25%", "Busca aleatória"],
        [[r["val_mean_rooms"] for r in mm[k]["repeats"]] for k in ("ga_mut_10", "ga_mut_25", "random_search")],
        [BRASS, RED, GRAY], "E5: sementes inéditas (401–420)",
        "Pontos: 1 por repetição (10 por método, 240 avaliações). Validação em 20 masmorras nunca usadas antes.",
        "grafico_e5_sementes_ineditas.png", ylim=(0, 105),
    )

