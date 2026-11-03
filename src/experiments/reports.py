"""Gráficos e relatórios dos experimentos 1 a 4 e da análise de falhas."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def generate_experiment_charts(
    full_results: dict[str, Any],
    output_dir: Path = Path("results/experiments"),
) -> list[str]:
    """Gera gráficos estáticos com os resultados dos 4 experimentos."""
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    generated: list[str] = []

    # 1. Convergência e diversidade por taxa de mutação.
    exp1 = full_results["experiment_1_mutation"]["results"]
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 4.8))
    colors = {"2%": "#1f77b4", "10%": "#2ca02c", "25%": "#d62728"}
    for rate_label, data in exp1.items():
        gens = data["curves_by_generation"]["generation"]
        best_c = data["curves_by_generation"]["best_rooms_mean"]
        div_c = data["curves_by_generation"]["diversity_mean"]
        c = colors.get(rate_label, "#333333")
        axes[0].plot(gens, best_c, marker="o", linewidth=2.0, label=f"Mutação {rate_label}", color=c)
        axes[1].plot(gens, div_c, marker="s", linewidth=2.0, label=f"Mutação {rate_label}", color=c)

    axes[0].set_title("Exp. 1 — Convergência da Melhor Estratégia por Taxa de Mutação")
    axes[0].set_xlabel("Geração")
    axes[0].set_ylabel("Média de Salas Concluídas (Treino)")
    axes[0].legend()

    axes[1].set_title("Exp. 1 — Evolução da Diversidade Genética por Geração")
    axes[1].set_xlabel("Geração")
    axes[1].set_ylabel("Índice de Diversidade Normalizado")
    axes[1].legend()
    fig.tight_layout()
    p1 = output_dir / "exp1_mutacao_convergencia_diversidade.png"
    fig.savefig(p1, dpi=160)
    plt.close(fig)
    generated.append(str(p1.as_posix()))

    # 2. Configurações de população com o mesmo orçamento (240 avaliações).
    exp2 = full_results["experiment_2_population"]["results"]
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 4.8))
    pop_colors = ["#8e44ad", "#2980b9", "#e67e22"]
    labels_2: list[str] = []
    val_means_2: list[float] = []
    val_stds_2: list[float] = []

    for idx, (cfg_label, data) in enumerate(exp2.items()):
        evals_x = data["convergence_by_evaluations"]["evaluations"]
        best_y = data["convergence_by_evaluations"]["best_rooms_mean"]
        axes[0].plot(
            evals_x,
            best_y,
            marker="o",
            linewidth=2.0,
            color=pop_colors[idx % len(pop_colors)],
            label=cfg_label,
        )
        labels_2.append(f"Pop {data['pop_size']}\n({data['generations']} ger)")
        val_means_2.append(data["val_rooms_summary"]["mean"])
        val_stds_2.append(data["val_rooms_summary"]["std"])

    axes[0].set_title("Exp. 2 — Convergência por Orçamento de Avaliações (240 aval)")
    axes[0].set_xlabel("Avaliações da Função Objetivo Acumuladas")
    axes[0].set_ylabel("Melhor Média de Salas (Treino)")
    axes[0].legend()

    x_pos = np.arange(len(labels_2))
    axes[1].bar(x_pos, val_means_2, yerr=val_stds_2, capsize=6, color=pop_colors[: len(labels_2)], alpha=0.88)
    axes[1].set_xticks(x_pos)
    axes[1].set_xticklabels(labels_2)
    axes[1].set_ylim(0, 105)
    axes[1].set_title("Exp. 2 — Desempenho em Validação (Fora da Amostra)")
    axes[1].set_ylabel("Média de Salas Concluídas ± DP")
    for i, v in enumerate(val_means_2):
        axes[1].text(i, v + 2.0, f"{v:.1f}", ha="center", fontweight="bold")
    fig.tight_layout()
    p2 = output_dir / "exp2_populacao_orcamento_equivalente.png"
    fig.savefig(p2, dpi=160)
    plt.close(fig)
    generated.append(str(p2.as_posix()))

    # 3. Comparação entre estratégia fixa, busca aleatória e algoritmo genético.
    exp3_m = full_results["experiment_3_baselines"]["methods"]
    fb_val = exp3_m["fixed_baseline"]["val_mean_rooms"]
    rs_val = exp3_m["random_search"]["val_rooms_across_repeats"]["mean"]
    ga_val = exp3_m["genetic_algorithm"]["val_rooms_across_repeats"]["mean"]

    fb_comp = exp3_m["fixed_baseline"]["val_completion_rate"] * 100.0
    rs_comp = exp3_m["random_search"]["val_completion_rate_mean"] * 100.0
    ga_comp = exp3_m["genetic_algorithm"]["val_completion_rate_mean"] * 100.0

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    m_labels = ["Baseline Fixo", "Busca Aleatória\n(240 aval)", "Algoritmo Genético\n(240 aval)"]
    m_means = [fb_val, rs_val, ga_val]
    m_colors = ["#7f8c8d", "#e67e22", "#27ae60"]

    axes[0].bar(m_labels, m_means, color=m_colors, alpha=0.9)
    axes[0].set_ylim(0, 108)
    axes[0].set_title("Exp. 3 — Média de Salas Concluídas em Validação")
    axes[0].set_ylabel("Média de salas concluídas")
    for i, v in enumerate(m_means):
        axes[0].text(i, v + 2.5, f"{v:.1f}", ha="center", fontweight="bold")

    m_comps = [fb_comp, rs_comp, ga_comp]
    axes[1].bar(m_labels, m_comps, color=m_colors, alpha=0.9)
    axes[1].set_ylim(0, 105)
    axes[1].set_title("Exp. 3 — Taxa de Conclusão das 100 Salas (%)")
    axes[1].set_ylabel("Taxa de Conclusão Total (%)")
    for i, v in enumerate(m_comps):
        axes[1].text(i, v + 2.0, f"{v:.1f}%", ha="center", fontweight="bold")
    fig.tight_layout()
    p3 = output_dir / "exp3_comparacao_baselines.png"
    fig.savefig(p3, dpi=160)
    plt.close(fig)
    generated.append(str(p3.as_posix()))

    # 4. Generalização em diferentes cenários.
    exp4_s = full_results["experiment_4_generalization"]["scenarios"]
    scen_names = [
        "Treino\n(In-Sample)",
        "Novas Sementes\n(Holdout)",
        "Novas Composições\nde Monstros",
        "Dificuldade\n+15%",
        "Sem Baús\n(Econ. Estrita)",
    ]
    scen_keys = [
        "1_in_sample_train",
        "2_out_of_sample_seeds",
        "3_alternate_monster_compositions",
        "4_increased_difficulty_15pct",
        "5_no_chests_strict_economy",
    ]
    ga_scen_vals = [exp4_s[k]["genetic_algorithm"]["mean_rooms"] for k in scen_keys]
    fb_scen_vals = [exp4_s[k]["fixed_baseline"]["mean_rooms"] for k in scen_keys]

    x = np.arange(len(scen_names))
    width = 0.36
    fig, ax = plt.subplots(figsize=(11.5, 5.0))
    rects1 = ax.bar(x - width / 2, fb_scen_vals, width, label="Estratégia Fixa (Baseline)", color="#7f8c8d")
    rects2 = ax.bar(x + width / 2, ga_scen_vals, width, label="Melhor Estratégia (Algoritmo Genético)", color="#2b5c8f")
    ax.set_ylabel("Média de Salas Concluídas")
    ax.set_title("Exp. 4 — Generalização Fora das Condições de Treinamento")
    ax.set_xticks(x)
    ax.set_xticklabels(scen_names)
    ax.set_ylim(0, 110)
    ax.legend()
    for r in rects1:
        h = r.get_height()
        ax.text(r.get_x() + r.get_width() / 2.0, h + 1.2, f"{h:.1f}", ha="center", fontsize=8.5)
    for r in rects2:
        h = r.get_height()
        ax.text(r.get_x() + r.get_width() / 2.0, h + 1.2, f"{h:.1f}", ha="center", fontsize=8.5, fontweight="bold")
    fig.tight_layout()
    p4 = output_dir / "exp4_generalizacao_cenarios.png"
    fig.savefig(p4, dpi=160)
    plt.close(fig)
    generated.append(str(p4.as_posix()))

    return generated
