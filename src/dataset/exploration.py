"""Análise exploratória dos dados (EDA) do D&D 5e SRD (2014).

Calcula estatísticas descritivas, matrizes de correlação (Pearson e Spearman),
distribuições por CR, HP, AC, XP, tipos de criaturas, valores ausentes/inconsistências
e gera gráficos estáticos (PNG) e resumos em JSON.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


NUMERIC_ANALYSIS_COLS = [
    "challenge_rating",
    "hit_points",
    "armor_class",
    "xp",
    "strength",
    "dexterity",
    "constitution",
    "intelligence",
    "wisdom",
    "charisma",
    "max_attack_bonus",
    "best_action_damage",
    "estimated_dpr_raw",
    "resistances_count",
    "immunities_count",
]


def compute_eda_metrics(
    df: pd.DataFrame,
    validation_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Calcula as métricas e correlações dos dados tratados."""
    total_valid = len(df)

    # Estatísticas descritivas de colunas numéricas
    desc_stats: dict[str, dict[str, float]] = {}
    for col in NUMERIC_ANALYSIS_COLS:
        if col not in df.columns:
            continue
        s = df[col].dropna().astype(float)
        desc_stats[col] = {
            "count": int(s.count()),
            "mean": round(float(s.mean()), 4),
            "std": round(float(s.std()), 4),
            "min": round(float(s.min()), 4),
            "q25": round(float(s.quantile(0.25)), 4),
            "median": round(float(s.median()), 4),
            "q75": round(float(s.quantile(0.75)), 4),
            "max": round(float(s.max()), 4),
            "skewness": round(float(s.skew()), 4),
        }

    # Correlações da Seção 3 e dos atributos ofensivos.
    correlation_pairs = [
        ("challenge_rating", "hit_points"),
        ("challenge_rating", "armor_class"),
        ("challenge_rating", "xp"),
        ("challenge_rating", "max_attack_bonus"),
        ("challenge_rating", "best_action_damage"),
        ("challenge_rating", "estimated_dpr_raw"),
        ("challenge_rating", "strength"),
        ("challenge_rating", "constitution"),
        ("challenge_rating", "dexterity"),
        ("constitution", "hit_points"),
        ("strength", "best_action_damage"),
        ("dexterity", "armor_class"),
        ("hit_points", "armor_class"),
    ]

    pair_correlations: dict[str, dict[str, float]] = {}
    for col_x, col_y in correlation_pairs:
        sub = df[[col_x, col_y]].dropna()
        r_pearson, p_pearson = stats.pearsonr(sub[col_x], sub[col_y])
        r_spearman, p_spearman = stats.spearmanr(sub[col_x], sub[col_y])
        key = f"{col_x}_vs_{col_y}"
        pair_correlations[key] = {
            "pearson_r": round(float(r_pearson), 4),
            "pearson_p": float(p_pearson),
            "spearman_rho": round(float(r_spearman), 4),
            "spearman_p": float(p_spearman),
        }

    # Distribuição por tipo de criatura
    type_counts = df["type"].value_counts().to_dict()
    size_counts = df["size"].value_counts().to_dict()
    cr_counts = {str(k): int(v) for k, v in df["challenge_rating"].value_counts().sort_index().items()}

    # Verifica inconsistências e casos especiais nos dados externos.
    zero_attack_actions = df[df["attack_actions_count"] == 0][
        ["index", "name", "challenge_rating", "actions_count"]
    ].to_dict(orient="records")
    high_cr_low_ac = df[(df["challenge_rating"] >= 5) & (df["armor_class"] <= 12)][
        ["index", "name", "challenge_rating", "armor_class", "hit_points"]
    ].to_dict(orient="records")
    magical_attackers_count = int(df["has_magical_attack"].sum())
    phys_resistant_count = int(df["has_physical_resistance"].sum())
    mag_resistant_count = int(df["has_magical_resistance"].sum())

    # Agrupa por faixas de CR para analisar a progressão.
    df_temp = df.copy()
    df_temp["cr_tier"] = pd.cut(
        df_temp["challenge_rating"],
        bins=[-0.01, 0.5, 2.0, 5.0, 10.0, 17.0, 35.0],
        labels=["CR 0-0.5", "CR 1-2", "CR 3-5", "CR 6-10", "CR 11-17", "CR 18-30"],
    )
    tier_summary = (
        df_temp.groupby("cr_tier", observed=False)[
            ["hit_points", "armor_class", "xp", "max_attack_bonus", "estimated_dpr_raw"]
        ]
        .agg(["count", "mean", "median"])
        .round(2)
    )
    tier_summary_dict: dict[str, Any] = {}
    for tier_name, row in tier_summary.iterrows():
        tier_summary_dict[str(tier_name)] = {
            "count": int(row[("hit_points", "count")]),
            "hp_mean": float(row[("hit_points", "mean")]),
            "hp_median": float(row[("hit_points", "median")]),
            "ac_mean": float(row[("armor_class", "mean")]),
            "ac_median": float(row[("armor_class", "median")]),
            "xp_mean": float(row[("xp", "mean")]),
            "atk_bonus_mean": float(row[("max_attack_bonus", "mean")]),
            "dpr_mean": float(row[("estimated_dpr_raw", "mean")]),
        }

    return {
        "total_valid_records": total_valid,
        "descriptive_statistics": desc_stats,
        "pair_correlations": pair_correlations,
        "type_distribution": {str(k): int(v) for k, v in type_counts.items()},
        "size_distribution": {str(k): int(v) for k, v in size_counts.items()},
        "cr_distribution": cr_counts,
        "cr_tier_progression": tier_summary_dict,
        "inconsistencies_and_anomalies": {
            "monsters_without_direct_damage_actions_count": len(zero_attack_actions),
            "monsters_without_direct_damage_actions_examples": zero_attack_actions[:10],
            "high_cr_low_ac_count": len(high_cr_low_ac),
            "high_cr_low_ac_examples": high_cr_low_ac[:10],
            "magical_or_elemental_attackers_count": magical_attackers_count,
            "physical_resistant_or_immune_count": phys_resistant_count,
            "magical_resistant_or_immune_count": mag_resistant_count,
        },
        "validation_summary": validation_report or {},
    }


def generate_eda_charts(df: pd.DataFrame, output_dir: Path = Path("results/eda")) -> list[str]:
    """Gera gráficos estáticos para o relatório de EDA e a documentação."""
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_files: list[str] = []

    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    # 1. Distribuição do nível de desafio (CR) e dos pontos de vida (HP).
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].hist(df["challenge_rating"], bins=25, color="#2b5c8f", edgecolor="white", alpha=0.9)
    axes[0].set_title("Distribuição por Nível de Desafio (CR) — D&D 5e SRD (n=334)")
    axes[0].set_xlabel("Challenge Rating (CR)")
    axes[0].set_ylabel("Quantidade de Criaturas")

    axes[1].hist(df["hit_points"], bins=25, color="#b84a39", edgecolor="white", alpha=0.9)
    axes[1].set_title("Distribuição de Pontos de Vida (HP) — D&D 5e SRD (n=334)")
    axes[1].set_xlabel("Hit Points (HP)")
    axes[1].set_ylabel("Quantidade de Criaturas")
    fig.tight_layout()
    p1 = output_dir / "01_distribuicao_cr_e_hp.png"
    fig.savefig(p1, dpi=160)
    plt.close(fig)
    generated_files.append(str(p1.as_posix()))

    # 2. Relações do CR com vida, defesa (AC) e experiência (XP).
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8))
    axes[0].scatter(df["challenge_rating"], df["hit_points"], alpha=0.65, color="#1f77b4", edgecolors="none")
    m_hp, b_hp = np.polyfit(df["challenge_rating"], df["hit_points"], 1)
    x_line = np.linspace(df["challenge_rating"].min(), df["challenge_rating"].max(), 100)
    axes[0].plot(x_line, m_hp * x_line + b_hp, color="#d62728", linestyle="--", linewidth=1.8)
    axes[0].set_title("Relação CR vs Pontos de Vida (HP)")
    axes[0].set_xlabel("Challenge Rating (CR)")
    axes[0].set_ylabel("Hit Points (HP)")

    axes[1].scatter(df["challenge_rating"], df["armor_class"], alpha=0.65, color="#2ca02c", edgecolors="none")
    m_ac, b_ac = np.polyfit(df["challenge_rating"], df["armor_class"], 1)
    axes[1].plot(x_line, m_ac * x_line + b_ac, color="#d62728", linestyle="--", linewidth=1.8)
    axes[1].set_title("Relação CR vs Classe de Armadura (AC)")
    axes[1].set_xlabel("Challenge Rating (CR)")
    axes[1].set_ylabel("Armor Class (AC)")

    axes[2].scatter(df["challenge_rating"], df["xp"], alpha=0.65, color="#9467bd", edgecolors="none")
    axes[2].set_title("Relação Não-Linear CR vs Experiência (XP)")
    axes[2].set_xlabel("Challenge Rating (CR)")
    axes[2].set_ylabel("Experiência (XP)")
    fig.tight_layout()
    p2 = output_dir / "02_relacoes_cr_hp_ac_xp.png"
    fig.savefig(p2, dpi=160)
    plt.close(fig)
    generated_files.append(str(p2.as_posix()))

    # 3. Distribuição dos tipos de criaturas.
    fig, ax = plt.subplots(figsize=(10, 5.5))
    type_series = df["type"].value_counts().sort_values(ascending=True)
    ax.barh(type_series.index, type_series.values, color="#3b7a57")
    ax.set_title("Distribuição dos Tipos de Criaturas no SRD 2014")
    ax.set_xlabel("Quantidade de Registros")
    ax.set_ylabel("Tipo de Criatura (type)")
    for i, v in enumerate(type_series.values):
        ax.text(v + 1, i, str(v), va="center", fontsize=9)
    fig.tight_layout()
    p3 = output_dir / "03_distribuicao_tipos_criaturas.png"
    fig.savefig(p3, dpi=160)
    plt.close(fig)
    generated_files.append(str(p3.as_posix()))

    # 4. Bônus de ataque e dano por CR.
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    axes[0].scatter(df["challenge_rating"], df["max_attack_bonus"], alpha=0.65, color="#e67e22")
    axes[0].set_title("CR vs Maior Bônus de Ataque")
    axes[0].set_xlabel("Challenge Rating (CR)")
    axes[0].set_ylabel("Max Attack Bonus")

    axes[1].scatter(df["challenge_rating"], df["estimated_dpr_raw"], alpha=0.65, color="#c0392b")
    axes[1].set_title("CR vs Dano Bruto Estimado por Turno (DPR)")
    axes[1].set_xlabel("Challenge Rating (CR)")
    axes[1].set_ylabel("DPR Bruto Estimado (Média de Dados x Multiattack)")
    fig.tight_layout()
    p4 = output_dir / "04_comportamento_atributos_ofensivos.png"
    fig.savefig(p4, dpi=160)
    plt.close(fig)
    generated_files.append(str(p4.as_posix()))

    # 5. Mapa de calor das correlações de Pearson.
    corr_cols = [
        "challenge_rating",
        "hit_points",
        "armor_class",
        "xp",
        "strength",
        "dexterity",
        "constitution",
        "max_attack_bonus",
        "best_action_damage",
        "estimated_dpr_raw",
    ]
    corr_matrix = df[corr_cols].corr(method="pearson")
    fig, ax = plt.subplots(figsize=(9.5, 8))
    im = ax.imshow(corr_matrix.values, cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr_cols)))
    ax.set_yticks(range(len(corr_cols)))
    ax.set_xticklabels(corr_cols, rotation=45, ha="right")
    ax.set_yticklabels(corr_cols)
    for i in range(len(corr_cols)):
        for j in range(len(corr_cols)):
            val = corr_matrix.values[i, j]
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", color="black", fontsize=8)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    ax.set_title("Matriz de Correlação de Pearson — Atributos D&D 5e SRD")
    fig.tight_layout()
    p5 = output_dir / "05_matriz_correlacao_pearson.png"
    fig.savefig(p5, dpi=160)
    plt.close(fig)
    generated_files.append(str(p5.as_posix()))

    return generated_files


def run_full_eda(
    df: pd.DataFrame,
    validation_report: dict[str, Any] | None = None,
    output_dir: Path = Path("results/eda"),
) -> dict[str, Any]:
    """Executa toda a análise exploratória, gera gráficos e salva o JSON de resultados."""
    output_dir.mkdir(parents=True, exist_ok=True)
    metrics = compute_eda_metrics(df, validation_report=validation_report)
    chart_files = generate_eda_charts(df, output_dir=output_dir)
    metrics["generated_charts"] = chart_files

    summary_path = output_dir / "eda_summary.json"
    summary_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    return metrics
