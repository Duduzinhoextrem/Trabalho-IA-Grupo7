"""Execução dos Experimentos Científicos Reais e Análise de Falhas (Seção 10).

Implementa:
- Experimento 1: Taxas de Mutação (2%, 10%, 25%)
- Experimento 2: Configurações de População com orçamento equivalente (240 avaliações)
- Experimento 3: Comparação formal (Estratégia Fixa vs Busca Aleatória vs Algoritmo Genético)
- Experimento 4: Generalização fora das condições de treinamento (novas sementes, novas composições, dificuldade +15%, sem baús)
- Análise Obrigatória de Falhas (convergência prematura, diversidade, aleatoriedade, sobreajuste, dominância de classes/equipamentos)
"""

from __future__ import annotations

import json
from pathlib import Path
import statistics
import time
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from src.experiments.baselines import (
    create_fixed_baseline_chromosome,
    run_random_search,
)
from src.game.dungeon import DungeonRoom, build_dungeon_100_rooms
from src.genetic.chromosome import ALLY_CLASSES_ORDER, Chromosome
from src.genetic.fitness import evaluate_chromosome
from src.genetic.optimizer import GARunResult, run_genetic_algorithm

TRAIN_SEEDS = [101, 102, 103, 104, 105]
VALIDATION_SEEDS = [201, 202, 203, 204, 205, 206, 207, 208, 209, 210]
ALT_COMPOSITION_SEEDS = [301, 302, 303, 304, 305, 306, 307, 308, 309, 310]


def summarize_metric_list(values: list[float]) -> dict[str, float]:
    """Calcula média, mediana, desvio-padrão, mínimo e máximo de uma lista numérica."""
    if not values:
        return {"mean": 0.0, "median": 0.0, "std": 0.0, "min": 0.0, "max": 0.0}
    mean_v = float(statistics.mean(values))
    median_v = float(statistics.median(values))
    std_v = float(statistics.pstdev(values)) if len(values) > 1 else 0.0
    return {
        "mean": round(mean_v, 4),
        "median": round(median_v, 4),
        "std": round(std_v, 4),
        "min": round(float(min(values)), 4),
        "max": round(float(max(values)), 4),
    }


def evaluate_chromosome_detailed_on_suite(
    chromosome: Chromosome,
    dungeons_suite: dict[int, list[DungeonRoom]],
    balance_cfg: dict[str, Any],
    enable_allies: bool = True,
    enable_chests: bool = True,
) -> dict[str, Any]:
    """Avalia um cromossomo em um conjunto de masmorras e retorna estatísticas completas por semente."""
    copy_ind = chromosome.copy()
    _, runs = evaluate_chromosome(
        chromosome=copy_ind,
        dungeons_by_seed=dungeons_suite,
        balance_cfg=balance_cfg,
        enable_allies=enable_allies,
        enable_chests=enable_chests,
    )
    rooms_list = [float(r.rooms_cleared) for r in runs]
    comp_list = [1.0 if r.completed_all_100 else 0.0 for r in runs]
    stats_rooms = summarize_metric_list(rooms_list)
    return {
        "mean_rooms": stats_rooms["mean"],
        "median_rooms": stats_rooms["median"],
        "std_rooms": stats_rooms["std"],
        "min_rooms": stats_rooms["min"],
        "max_rooms": stats_rooms["max"],
        "completion_rate": round(sum(comp_list) / len(comp_list), 4),
        "per_seed_rooms": {str(r.seed): r.rooms_cleared for r in runs},
        "final_levels": [r.final_warrior_level for r in runs],
        "active_allies_samples": [r.active_allies_final for r in runs],
        "final_equipment_tiers": [
            {
                "weapon": r.final_weapon_tier,
                "armor": r.final_armor_tier,
                "shield": r.final_shield_tier,
            }
            for r in runs
        ],
    }


def run_experiment_1_mutation(
    train_dungeons: dict[int, list[DungeonRoom]],
    val_dungeons: dict[int, list[DungeonRoom]],
    balance_cfg: dict[str, Any],
    mutation_rates: tuple[float, ...] = (0.02, 0.10, 0.25),
    pop_size: int = 20,
    generations: int = 12,
    n_repeats: int = 5,
) -> dict[str, Any]:
    """Experimento 1 — Impacto da Taxa de Mutação (2%, 10%, 25%) na convergência e diversidade."""
    results_by_rate: dict[str, Any] = {}

    for m_rate in mutation_rates:
        rate_label = f"{int(round(m_rate * 100))}%"
        runs_data: list[dict[str, Any]] = []
        train_rooms_all: list[float] = []
        val_rooms_all: list[float] = []
        val_comp_all: list[float] = []
        final_diversities: list[float] = []
        convergence_gens: list[int] = []
        elapsed_list: list[float] = []

        # Curvas médias por geração
        gen_best_matrix: list[list[float]] = []
        gen_mean_matrix: list[list[float]] = []
        gen_div_matrix: list[list[float]] = []

        for rep in range(n_repeats):
            run_seed = 1000 + int(m_rate * 1000) + rep * 17
            ga_res: GARunResult = run_genetic_algorithm(
                dungeons_by_seed=train_dungeons,
                balance_cfg=balance_cfg,
                pop_size=pop_size,
                generations=generations,
                mutation_rate=m_rate,
                seed=run_seed,
                stagnation_limit=generations + 5,  # Executa todas as gerações para comparar curvas
            )
            val_eval = evaluate_chromosome_detailed_on_suite(
                ga_res.best_chromosome, val_dungeons, balance_cfg
            )

            # Identifica geração em que atingiu 99% do fitness final da execução
            target_f = (ga_res.best_chromosome.fitness or 0.0) * 0.99
            conv_gen = generations
            for h in ga_res.history:
                if h.best_fitness >= target_f:
                    conv_gen = h.generation
                    break

            train_rooms_all.append(ga_res.best_chromosome.mean_rooms_cleared)
            val_rooms_all.append(val_eval["mean_rooms"])
            val_comp_all.append(val_eval["completion_rate"])
            final_diversities.append(ga_res.history[-1].diversity_index)
            convergence_gens.append(conv_gen)
            elapsed_list.append(ga_res.elapsed_seconds)

            gen_best_matrix.append([h.best_mean_rooms for h in ga_res.history])
            gen_mean_matrix.append([h.pop_mean_rooms for h in ga_res.history])
            gen_div_matrix.append([h.diversity_index for h in ga_res.history])

            runs_data.append(
                {
                    "repeat": rep + 1,
                    "seed": run_seed,
                    "train_mean_rooms": ga_res.best_chromosome.mean_rooms_cleared,
                    "train_completion_rate": ga_res.best_chromosome.completion_rate,
                    "val_mean_rooms": val_eval["mean_rooms"],
                    "val_median_rooms": val_eval["median_rooms"],
                    "val_std_rooms": val_eval["std_rooms"],
                    "val_completion_rate": val_eval["completion_rate"],
                    "final_diversity": ga_res.history[-1].diversity_index,
                    "convergence_generation": conv_gen,
                    "elapsed_seconds": round(ga_res.elapsed_seconds, 4),
                    "best_genes": ga_res.best_chromosome.genes,
                }
            )

        avg_best_curve = np.mean(np.array(gen_best_matrix), axis=0).round(4).tolist()
        avg_mean_curve = np.mean(np.array(gen_mean_matrix), axis=0).round(4).tolist()
        avg_div_curve = np.mean(np.array(gen_div_matrix), axis=0).round(4).tolist()

        results_by_rate[rate_label] = {
            "mutation_rate": m_rate,
            "n_repeats": n_repeats,
            "objective_evaluations_per_run": pop_size * generations,
            "train_rooms_summary": summarize_metric_list(train_rooms_all),
            "val_rooms_summary": summarize_metric_list(val_rooms_all),
            "val_completion_rate_mean": round(float(statistics.mean(val_comp_all)), 4),
            "final_diversity_summary": summarize_metric_list(final_diversities),
            "mean_convergence_generation": round(float(statistics.mean(convergence_gens)), 2),
            "mean_elapsed_seconds": round(float(statistics.mean(elapsed_list)), 4),
            "curves_by_generation": {
                "generation": list(range(1, generations + 1)),
                "best_rooms_mean": avg_best_curve,
                "pop_rooms_mean": avg_mean_curve,
                "diversity_mean": avg_div_curve,
            },
            "repeats": runs_data,
        }

    return {
        "experiment_name": "Experimento 1 — Taxas de Mutação (2%, 10%, 25%)",
        "hypothesis": "Taxas de mutação muito baixas (2%) reduzem a diversidade genética e favorecem convergência prematura a ótimos locais, enquanto taxas excessivas (25%) introduzem ruído estocástico nas políticas elitistas; uma taxa intermediária (10%) equilibra exploração e explotação.",
        "budget_objective_evaluations": pop_size * generations,
        "results": results_by_rate,
    }


def run_experiment_2_population(
    train_dungeons: dict[int, list[DungeonRoom]],
    val_dungeons: dict[int, list[DungeonRoom]],
    balance_cfg: dict[str, Any],
    configs: tuple[tuple[str, int, int], ...] = (
        ("Pop 12 x 20 Ger (240 aval)", 12, 20),
        ("Pop 20 x 12 Ger (240 aval)", 20, 12),
        ("Pop 40 x 6 Ger (240 aval)", 40, 6),
    ),
    mutation_rate: float = 0.10,
    n_repeats: int = 5,
) -> dict[str, Any]:
    """Experimento 2 — Configurações de População sob orçamento equivalente (240 avaliações)."""
    results_by_cfg: dict[str, Any] = {}

    for label, pop_sz, gens in configs:
        budget = pop_sz * gens
        train_rooms_all: list[float] = []
        val_rooms_all: list[float] = []
        val_comp_all: list[float] = []
        final_div_all: list[float] = []
        elapsed_all: list[float] = []
        runs_data: list[dict[str, Any]] = []
        eval_axis = [g * pop_sz for g in range(1, gens + 1)]
        best_curves: list[list[float]] = []

        for rep in range(n_repeats):
            run_seed = 2000 + pop_sz * 10 + rep * 23
            ga_res = run_genetic_algorithm(
                dungeons_by_seed=train_dungeons,
                balance_cfg=balance_cfg,
                pop_size=pop_sz,
                generations=gens,
                mutation_rate=mutation_rate,
                max_evaluations=budget,
                seed=run_seed,
                stagnation_limit=gens + 5,
            )
            val_eval = evaluate_chromosome_detailed_on_suite(
                ga_res.best_chromosome, val_dungeons, balance_cfg
            )
            train_rooms_all.append(ga_res.best_chromosome.mean_rooms_cleared)
            val_rooms_all.append(val_eval["mean_rooms"])
            val_comp_all.append(val_eval["completion_rate"])
            final_div_all.append(ga_res.history[-1].diversity_index)
            elapsed_all.append(ga_res.elapsed_seconds)
            best_curves.append([h.best_mean_rooms for h in ga_res.history])

            runs_data.append(
                {
                    "repeat": rep + 1,
                    "seed": run_seed,
                    "train_mean_rooms": ga_res.best_chromosome.mean_rooms_cleared,
                    "val_mean_rooms": val_eval["mean_rooms"],
                    "val_completion_rate": val_eval["completion_rate"],
                    "final_diversity": ga_res.history[-1].diversity_index,
                    "objective_evaluations": ga_res.total_objective_evaluations,
                    "elapsed_seconds": round(ga_res.elapsed_seconds, 4),
                }
            )

        results_by_cfg[label] = {
            "pop_size": pop_sz,
            "generations": gens,
            "budget_evaluations": budget,
            "n_repeats": n_repeats,
            "train_rooms_summary": summarize_metric_list(train_rooms_all),
            "val_rooms_summary": summarize_metric_list(val_rooms_all),
            "val_completion_rate_mean": round(float(statistics.mean(val_comp_all)), 4),
            "final_diversity_summary": summarize_metric_list(final_div_all),
            "mean_elapsed_seconds": round(float(statistics.mean(elapsed_all)), 4),
            "convergence_by_evaluations": {
                "evaluations": eval_axis,
                "best_rooms_mean": np.mean(np.array(best_curves), axis=0).round(4).tolist(),
            },
            "repeats": runs_data,
        }

    return {
        "experiment_name": "Experimento 2 — Tamanho de População com Orçamento Fixo (240 avaliações)",
        "hypothesis": "Com orçamento computacional fixo (240 avaliações), populações muito pequenas (12) sofrem maior deriva genética, enquanto populações muito grandes (40) dispõem de poucas gerações (6) para refinar blocos construtivos; configurações intermediárias (20x12) maximizam a qualidade final.",
        "results": results_by_cfg,
    }


def run_experiment_3_baselines_comparison(
    train_dungeons: dict[int, list[DungeonRoom]],
    val_dungeons: dict[int, list[DungeonRoom]],
    balance_cfg: dict[str, Any],
    pop_size: int = 20,
    generations: int = 12,
    n_repeats: int = 7,
) -> tuple[dict[str, Any], Chromosome, GARunResult]:
    """Experimento 3 — Comparação formal: Estratégia Fixa vs Busca Aleatória vs Algoritmo Genético."""
    budget = pop_size * generations

    # 1. Estratégia Fixa (Baseline Determinístico de Regra)
    t0_fb = time.perf_counter()
    fixed_chrom = create_fixed_baseline_chromosome()
    fb_train_eval = evaluate_chromosome_detailed_on_suite(fixed_chrom, train_dungeons, balance_cfg)
    fb_val_eval = evaluate_chromosome_detailed_on_suite(fixed_chrom, val_dungeons, balance_cfg)
    fb_elapsed = time.perf_counter() - t0_fb

    # 2. Busca Aleatória (Random Search) com mesmo orçamento (budget avaliações por repetição)
    rs_train_rooms: list[float] = []
    rs_val_rooms: list[float] = []
    rs_val_comp: list[float] = []
    rs_elapsed_list: list[float] = []
    rs_all_val_per_seed: list[float] = []
    rs_repeats: list[dict[str, Any]] = []

    for rep in range(n_repeats):
        r_seed = 3000 + rep * 31
        rs_res = run_random_search(
            dungeons_by_seed=train_dungeons,
            balance_cfg=balance_cfg,
            budget_evaluations=budget,
            seed=r_seed,
        )
        val_ev = evaluate_chromosome_detailed_on_suite(rs_res.best_chromosome, val_dungeons, balance_cfg)
        rs_train_rooms.append(rs_res.best_chromosome.mean_rooms_cleared)
        rs_val_rooms.append(val_ev["mean_rooms"])
        rs_val_comp.append(val_ev["completion_rate"])
        rs_elapsed_list.append(rs_res.elapsed_seconds)
        rs_all_val_per_seed.extend(val_ev["per_seed_rooms"].values())
        rs_repeats.append(
            {
                "repeat": rep + 1,
                "seed": r_seed,
                "train_mean_rooms": rs_res.best_chromosome.mean_rooms_cleared,
                "val_mean_rooms": val_ev["mean_rooms"],
                "val_median_rooms": val_ev["median_rooms"],
                "val_std_rooms": val_ev["std_rooms"],
                "val_completion_rate": val_ev["completion_rate"],
                "objective_evaluations": budget,
                "elapsed_seconds": round(rs_res.elapsed_seconds, 4),
            }
        )

    # 3. Algoritmo Genético (GA) com mesmo orçamento (budget avaliações por repetição)
    ga_train_rooms: list[float] = []
    ga_val_rooms: list[float] = []
    ga_val_comp: list[float] = []
    ga_elapsed_list: list[float] = []
    ga_all_val_per_seed: list[float] = []
    ga_repeats: list[dict[str, Any]] = []
    best_ga_overall: Chromosome | None = None
    best_ga_run_result: GARunResult | None = None

    for rep in range(n_repeats):
        g_seed = 4000 + rep * 37
        ga_res = run_genetic_algorithm(
            dungeons_by_seed=train_dungeons,
            balance_cfg=balance_cfg,
            pop_size=pop_size,
            generations=generations,
            mutation_rate=0.10,
            max_evaluations=budget,
            seed=g_seed,
            stagnation_limit=generations + 5,
        )
        val_ev = evaluate_chromosome_detailed_on_suite(ga_res.best_chromosome, val_dungeons, balance_cfg)
        ga_train_rooms.append(ga_res.best_chromosome.mean_rooms_cleared)
        ga_val_rooms.append(val_ev["mean_rooms"])
        ga_val_comp.append(val_ev["completion_rate"])
        ga_elapsed_list.append(ga_res.elapsed_seconds)
        ga_all_val_per_seed.extend(val_ev["per_seed_rooms"].values())

        if best_ga_overall is None or (ga_res.best_chromosome.fitness or 0.0) > (best_ga_overall.fitness or 0.0):
            best_ga_overall = ga_res.best_chromosome.copy()
            best_ga_run_result = ga_res

        ga_repeats.append(
            {
                "repeat": rep + 1,
                "seed": g_seed,
                "train_mean_rooms": ga_res.best_chromosome.mean_rooms_cleared,
                "val_mean_rooms": val_ev["mean_rooms"],
                "val_median_rooms": val_ev["median_rooms"],
                "val_std_rooms": val_ev["std_rooms"],
                "val_completion_rate": val_ev["completion_rate"],
                "objective_evaluations": ga_res.total_objective_evaluations,
                "elapsed_seconds": round(ga_res.elapsed_seconds, 4),
                "best_genes": ga_res.best_chromosome.genes,
            }
        )

    assert best_ga_overall is not None and best_ga_run_result is not None

    # Testes estatísticos (Mann-Whitney U e t-test de Welch sobre as médias de validação das repetições)
    u_stat, u_pval = stats.mannwhitneyu(ga_val_rooms, rs_val_rooms, alternative="two-sided")
    t_stat, t_pval = stats.ttest_ind(ga_val_rooms, rs_val_rooms, equal_var=False)

    fb_seed_vals = [float(v) for v in fb_val_eval["per_seed_rooms"].values()]
    best_ga_val_eval = evaluate_chromosome_detailed_on_suite(best_ga_overall, val_dungeons, balance_cfg)
    best_ga_seed_vals = [float(v) for v in best_ga_val_eval["per_seed_rooms"].values()]
    u_fb_stat, u_fb_pval = stats.mannwhitneyu(best_ga_seed_vals, fb_seed_vals, alternative="two-sided")

    summary = {
        "experiment_name": "Experimento 3 — Comparação com Baselines (Fixo vs Busca Aleatória vs Algoritmo Genético)",
        "budget_objective_evaluations_per_run": budget,
        "n_independent_repeats": n_repeats,
        "train_seeds": TRAIN_SEEDS,
        "validation_seeds": VALIDATION_SEEDS,
        "methods": {
            "fixed_baseline": {
                "label": "Estratégia Fixa (Baseline)",
                "train_mean_rooms": fb_train_eval["mean_rooms"],
                "val_mean_rooms": fb_val_eval["mean_rooms"],
                "val_median_rooms": fb_val_eval["median_rooms"],
                "val_std_rooms": fb_val_eval["std_rooms"],
                "val_completion_rate": fb_val_eval["completion_rate"],
                "objective_evaluations": 1,
                "simulation_runs": len(TRAIN_SEEDS) + len(VALIDATION_SEEDS),
                "elapsed_seconds": round(fb_elapsed, 4),
                "per_seed_validation_rooms": fb_val_eval["per_seed_rooms"],
                "genes": fixed_chrom.genes,
                "named_genes": fixed_chrom.to_named_dict(),
            },
            "random_search": {
                "label": "Busca Aleatória (Orçamento Equivalente)",
                "train_rooms_across_repeats": summarize_metric_list(rs_train_rooms),
                "val_rooms_across_repeats": summarize_metric_list(rs_val_rooms),
                "pooled_val_rooms_all_seeds": summarize_metric_list([float(x) for x in rs_all_val_per_seed]),
                "val_completion_rate_mean": round(float(statistics.mean(rs_val_comp)), 4),
                "objective_evaluations_per_run": budget,
                "simulation_runs_per_run": budget * len(TRAIN_SEEDS),
                "mean_elapsed_seconds": round(float(statistics.mean(rs_elapsed_list)), 4),
                "repeats": rs_repeats,
            },
            "genetic_algorithm": {
                "label": "Algoritmo Genético (Proposto)",
                "train_rooms_across_repeats": summarize_metric_list(ga_train_rooms),
                "val_rooms_across_repeats": summarize_metric_list(ga_val_rooms),
                "pooled_val_rooms_all_seeds": summarize_metric_list([float(x) for x in ga_all_val_per_seed]),
                "val_completion_rate_mean": round(float(statistics.mean(ga_val_comp)), 4),
                "objective_evaluations_per_run": budget,
                "simulation_runs_per_run": budget * len(TRAIN_SEEDS),
                "mean_elapsed_seconds": round(float(statistics.mean(ga_elapsed_list)), 4),
                "best_overall_chromosome": {
                    "genes": best_ga_overall.genes,
                    "named_genes": best_ga_overall.to_named_dict(),
                    "train_mean_rooms": best_ga_overall.mean_rooms_cleared,
                    "train_completion_rate": best_ga_overall.completion_rate,
                    "val_mean_rooms": best_ga_val_eval["mean_rooms"],
                    "val_median_rooms": best_ga_val_eval["median_rooms"],
                    "val_std_rooms": best_ga_val_eval["std_rooms"],
                    "val_completion_rate": best_ga_val_eval["completion_rate"],
                    "per_seed_validation_rooms": best_ga_val_eval["per_seed_rooms"],
                },
                "repeats": ga_repeats,
            },
        },
        "statistical_tests": {
            "ga_vs_random_search_repeats": {
                "mann_whitney_u": float(u_stat),
                "mann_whitney_p": round(float(u_pval), 6),
                "welch_t_stat": round(float(t_stat), 4),
                "welch_t_p": round(float(t_pval), 6),
            },
            "best_ga_vs_fixed_baseline_validation_seeds": {
                "mann_whitney_u": float(u_fb_stat),
                "mann_whitney_p": round(float(u_fb_pval), 6),
            },
        },
    }
    return summary, best_ga_overall, best_ga_run_result


def run_experiment_4_generalization(
    best_ga_chromosome: Chromosome,
    fixed_baseline_chromosome: Chromosome,
    monsters_df: pd.DataFrame,
    balance_cfg: dict[str, Any],
) -> dict[str, Any]:
    """Experimento Adicional Obrigatório — Generalização fora das condições de otimização."""
    scenarios: dict[str, dict[str, Any]] = {}

    suite_configs = [
        ("1_in_sample_train", "Treinamento (In-Sample, Sementes 101-105)", TRAIN_SEEDS, 1.0, "standard", True),
        ("2_out_of_sample_seeds", "Novas Sementes (Holdout 201-210)", VALIDATION_SEEDS, 1.0, "standard", True),
        (
            "3_alternate_monster_compositions",
            "Novas Composições de Monstros (Pool Alternativo 301-310)",
            ALT_COMPOSITION_SEEDS,
            1.0,
            "alternate_pool",
            True,
        ),
        (
            "4_increased_difficulty_15pct",
            "Dificuldade Aumentada (+15% Status Inimigos, Sementes 201-210)",
            VALIDATION_SEEDS,
            1.15,
            "standard",
            True,
        ),
        (
            "5_no_chests_strict_economy",
            "Sem Baús (Economia Estrita, Sementes 201-210)",
            VALIDATION_SEEDS,
            1.0,
            "standard",
            False,
        ),
    ]

    for key, label, seeds, diff_mult, comp_mode, chests_flag in suite_configs:
        d_suite = {
            s: build_dungeon_100_rooms(
                monsters_df=monsters_df,
                balance_cfg=balance_cfg,
                seed=s,
                difficulty_multiplier=diff_mult,
                composition_mode=comp_mode,
            )
            for s in seeds
        }
        ga_ev = evaluate_chromosome_detailed_on_suite(
            best_ga_chromosome, d_suite, balance_cfg, enable_allies=True, enable_chests=chests_flag
        )
        fb_ev = evaluate_chromosome_detailed_on_suite(
            fixed_baseline_chromosome, d_suite, balance_cfg, enable_allies=True, enable_chests=chests_flag
        )
        scenarios[key] = {
            "label": label,
            "seeds": seeds,
            "difficulty_multiplier": diff_mult,
            "composition_mode": comp_mode,
            "enable_chests": chests_flag,
            "genetic_algorithm": ga_ev,
            "fixed_baseline": fb_ev,
            "ga_advantage_rooms": round(ga_ev["mean_rooms"] - fb_ev["mean_rooms"], 4),
        }

    return {
        "experiment_name": "Experimento 4 (Adicional Obrigatório) — Generalização e Robustez",
        "scenarios": scenarios,
    }


def build_failure_and_dominance_analysis(
    exp1: dict[str, Any],
    exp2: dict[str, Any],
    exp3: dict[str, Any],
    exp4: dict[str, Any],
) -> dict[str, Any]:
    """Consolida evidências empíricas para os 5 itens obrigatórios de Análise de Falhas (Seção 10)."""
    # 1. Convergência prematura e 2. Baixa diversidade genética
    r2 = exp1["results"]["2%"]
    r10 = exp1["results"]["10%"]
    r25 = exp1["results"]["25%"]

    # 3. Dependência de aleatoriedade (variância entre sementes e impacto dos baús)
    with_chests = exp4["scenarios"]["2_out_of_sample_seeds"]["genetic_algorithm"]
    without_chests = exp4["scenarios"]["5_no_chests_strict_economy"]["genetic_algorithm"]

    # 4. Sobreajuste à configuração de treinamento (Gap Treino vs Validação/Composições/Dificuldade)
    ga_methods = exp3["methods"]["genetic_algorithm"]
    train_mean = ga_methods["train_rooms_across_repeats"]["mean"]
    val_mean = ga_methods["val_rooms_across_repeats"]["mean"]
    overfit_gap = round(train_mean - val_mean, 4)

    # 5. Classes de aliados e equipamentos dominantes nas 7 repetições do AG
    repeats = ga_methods["repeats"]
    ally_top1_counts: dict[str, int] = {c: 0 for c in ALLY_CLASSES_ORDER}
    ally_top2_counts: dict[str, int] = {c: 0 for c in ALLY_CLASSES_ORDER}
    str_weights: list[float] = []
    vit_weights: list[float] = []
    def_weights: list[float] = []
    equip_offense_vals: list[float] = []

    for rep in repeats:
        g = rep["best_genes"]
        str_weights.append(g[0])
        vit_weights.append(g[1])
        def_weights.append(g[2])
        equip_offense_vals.append(g[11])
        prios = [(ALLY_CLASSES_ORDER[i], g[3 + i]) for i in range(5)]
        prios.sort(key=lambda x: -x[1])
        ally_top1_counts[prios[0][0]] += 1
        ally_top2_counts[prios[0][0]] += 1
        ally_top2_counts[prios[1][0]] += 1

    return {
        "1_premature_convergence": {
            "mut_2pct_mean_conv_gen": r2["mean_convergence_generation"],
            "mut_10pct_mean_conv_gen": r10["mean_convergence_generation"],
            "mut_25pct_mean_conv_gen": r25["mean_convergence_generation"],
            "mut_2pct_val_rooms": r2["val_rooms_summary"]["mean"],
            "mut_10pct_val_rooms": r10["val_rooms_summary"]["mean"],
            "finding": (
                f"Com mutação de 2%, a população estabiliza mais cedo (geração média {r2['mean_convergence_generation']}) "
                f"e atinge média de {r2['val_rooms_summary']['mean']:.2f} salas na validação, contra "
                f"{r10['val_rooms_summary']['mean']:.2f} salas na taxa de 10%."
            ),
        },
        "2_low_genetic_diversity": {
            "mut_2pct_final_diversity": r2["final_diversity_summary"]["mean"],
            "mut_10pct_final_diversity": r10["final_diversity_summary"]["mean"],
            "mut_25pct_final_diversity": r25["final_diversity_summary"]["mean"],
            "pop12_final_diversity": exp2["results"]["Pop 12 x 20 Ger (240 aval)"]["final_diversity_summary"]["mean"],
            "pop40_final_diversity": exp2["results"]["Pop 40 x 6 Ger (240 aval)"]["final_diversity_summary"]["mean"],
        },
        "3_randomness_dependence": {
            "validation_std_across_seeds": with_chests["std_rooms"],
            "validation_min_rooms": with_chests["min_rooms"],
            "validation_max_rooms": with_chests["max_rooms"],
            "mean_rooms_with_chests": with_chests["mean_rooms"],
            "mean_rooms_without_chests": without_chests["mean_rooms"],
            "chest_impact_delta_rooms": round(with_chests["mean_rooms"] - without_chests["mean_rooms"], 4),
        },
        "4_overfitting_to_dungeon_seeds": {
            "ga_train_mean_rooms": train_mean,
            "ga_validation_mean_rooms": val_mean,
            "generalization_gap_rooms": overfit_gap,
            "alternate_monster_pool_mean_rooms": exp4["scenarios"]["3_alternate_monster_compositions"]["genetic_algorithm"]["mean_rooms"],
            "harder_15pct_mean_rooms": exp4["scenarios"]["4_increased_difficulty_15pct"]["genetic_algorithm"]["mean_rooms"],
        },
        "5_dominant_classes_and_builds": {
            "ally_first_choice_frequency": ally_top1_counts,
            "ally_top2_pair_frequency": ally_top2_counts,
            "mean_warrior_weights": {
                "strength": round(float(statistics.mean(str_weights)), 4),
                "vitality": round(float(statistics.mean(vit_weights)), 4),
                "defense": round(float(statistics.mean(def_weights)), 4),
            },
            "mean_equip_offense_priority": round(float(statistics.mean(equip_offense_vals)), 4),
        },
    }
