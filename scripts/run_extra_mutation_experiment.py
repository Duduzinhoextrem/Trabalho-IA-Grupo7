"""Experimento adicional E5: mutação de 10% x 25% e busca aleatória em sementes inéditas.

A configuração foi fixada antes da execução em docs/FINALIZACAO/PRE_REGISTRO_E5.md.
O script não altera os arquivos dos experimentos v1 e v2.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import statistics
import sys

import numpy as np
from scipy import stats

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.dataset.preprocessing import load_processed_dataset
from src.experiments.baselines import run_random_search
from src.experiments.evaluation import (
    TRAIN_SEEDS,
    evaluate_chromosome_detailed_on_suite,
    generations_for_budget,
    summarize_metric_list,
)
from src.game.dungeon import build_dungeon_100_rooms
from src.game.monsters import load_balance_config
from src.genetic.optimizer import run_genetic_algorithm

NEW_VALIDATION_SEEDS = list(range(401, 421))
BUDGET = 240
POP_SIZE = 20
N_REPEATS = 10
BOOTSTRAP_RESAMPLES = 10_000
BOOTSTRAP_SEED = 20261110


def bootstrap_diff_ci(a: list[float], b: list[float]) -> dict[str, float]:
    """Intervalo bootstrap de 95% para a diferença de médias (a - b)."""
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    arr_a, arr_b = np.array(a), np.array(b)
    diffs = [
        rng.choice(arr_a, size=len(arr_a)).mean() - rng.choice(arr_b, size=len(arr_b)).mean()
        for _ in range(BOOTSTRAP_RESAMPLES)
    ]
    return {
        "mean_diff": round(float(arr_a.mean() - arr_b.mean()), 4),
        "ci95_low": round(float(np.percentile(diffs, 2.5)), 4),
        "ci95_high": round(float(np.percentile(diffs, 97.5)), 4),
    }


def compare(a: list[float], b: list[float]) -> dict[str, float]:
    u_stat, u_p = stats.mannwhitneyu(a, b, alternative="two-sided")
    return {"mann_whitney_u": float(u_stat), "mann_whitney_p": round(float(u_p), 6), **bootstrap_diff_ci(a, b)}


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    started = datetime.now(timezone.utc).isoformat()
    monsters = load_processed_dataset()
    cfg = load_balance_config()
    train = {s: build_dungeon_100_rooms(monsters, cfg, seed=s) for s in TRAIN_SEEDS}
    val = {s: build_dungeon_100_rooms(monsters, cfg, seed=s) for s in NEW_VALIDATION_SEEDS}
    generation_limit = generations_for_budget(POP_SIZE, BUDGET)

    methods: dict[str, dict] = {}
    plans = [
        ("ga_mut_10", "AG com mutação 10%", 5100, 0.10),
        ("ga_mut_25", "AG com mutação 25%", 5200, 0.25),
        ("random_search", "Busca aleatória", 5300, None),
    ]
    for key, label, base_seed, mutation in plans:
        repeats = []
        for i in range(N_REPEATS):
            run_seed = base_seed + 41 * i
            if mutation is None:
                res = run_random_search(train, cfg, budget_evaluations=BUDGET, seed=run_seed)
                best, evaluations = res.best_chromosome, BUDGET
            else:
                res = run_genetic_algorithm(
                    dungeons_by_seed=train, balance_cfg=cfg, pop_size=POP_SIZE,
                    generations=generation_limit, mutation_rate=mutation, max_evaluations=BUDGET,
                    seed=run_seed, stagnation_limit=generation_limit + 5,
                )
                best, evaluations = res.best_chromosome, res.total_objective_evaluations
            ev = evaluate_chromosome_detailed_on_suite(best, val, cfg)
            repeats.append({
                "repeat": i + 1, "seed": run_seed, "objective_evaluations": evaluations,
                "train_mean_rooms": best.mean_rooms_cleared, "val_mean_rooms": ev["mean_rooms"],
                "val_completion_rate": ev["completion_rate"], "best_genes": best.genes,
            })
            logging.info("%s repetição %d: treino %.1f, validação %.1f", label, i + 1,
                         best.mean_rooms_cleared, ev["mean_rooms"])
        val_rooms = [r["val_mean_rooms"] for r in repeats]
        methods[key] = {
            "label": label, "mutation_rate": mutation, "repeats": repeats,
            "val_rooms_across_repeats": summarize_metric_list(val_rooms),
            "train_rooms_across_repeats": summarize_metric_list([r["train_mean_rooms"] for r in repeats]),
            "val_completion_rate_mean": round(statistics.mean(r["val_completion_rate"] for r in repeats), 4),
        }

    vals = {k: [r["val_mean_rooms"] for r in m["repeats"]] for k, m in methods.items()}
    payload = {
        "metadata": {
            "experiment": "E5 — mutação 10% x 25% e busca aleatória em sementes inéditas",
            "preregistration": "docs/FINALIZACAO/PRE_REGISTRO_E5.md",
            "results_version": "e5-v1",
            "dataset_version": "srd-2014-v1.0.0",
            "balance_version": cfg.get("config_version", "balance-v1.0.0"),
            "train_seeds": TRAIN_SEEDS, "validation_seeds": NEW_VALIDATION_SEEDS,
            "budget_evaluations_per_repeat": BUDGET, "pop_size": POP_SIZE, "n_repeats": N_REPEATS,
            "started_at_utc": started, "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        },
        "methods": methods,
        "comparisons": {
            "ga25_vs_ga10": compare(vals["ga_mut_25"], vals["ga_mut_10"]),
            "ga10_vs_random": compare(vals["ga_mut_10"], vals["random_search"]),
            "ga25_vs_random": compare(vals["ga_mut_25"], vals["random_search"]),
        },
    }
    out = ROOT_DIR / "data/experiments/extra_mutation_e5_v1.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    logging.info("E5 salvo em %s", out)


if __name__ == "__main__":
    main()
