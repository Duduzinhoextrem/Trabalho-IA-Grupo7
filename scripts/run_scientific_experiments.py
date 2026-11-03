"""Execução dos experimentos no modo científico.

Executa com dados reais do SRD 2014:
1. Experimento 1: taxas de mutação (2%, 10%, 25%)
2. Experimento 2: configurações de população com orçamento equivalente (240 avaliações)
3. Experimento 3: comparação entre estratégia fixa, busca aleatória e AG
4. Experimento 4: generalização (novas sementes, novas composições, dificuldade +15%, sem baús)
5. Análise de falhas obrigatória
Exporta uma nova versão dos resultados, preservando o histórico anterior.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.dataset.preprocessing import load_processed_dataset
from src.experiments.baselines import create_fixed_baseline_chromosome
from src.experiments.evaluation import (
    TRAIN_SEEDS,
    VALIDATION_SEEDS,
    build_failure_and_dominance_analysis,
    run_experiment_1_mutation,
    run_experiment_2_population,
    run_experiment_3_baselines_comparison,
    run_experiment_4_generalization,
)
from src.experiments.reports import generate_experiment_charts
from src.game.dungeon import build_dungeon_100_rooms
from src.game.monsters import load_balance_config


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    started_utc = datetime.now(timezone.utc).isoformat()

    monsters_df = load_processed_dataset()
    balance_cfg = load_balance_config()

    logging.info("Pré-construindo masmorras de treinamento (%s) e validação (%s)...", TRAIN_SEEDS, VALIDATION_SEEDS)
    train_dungeons = {
        s: build_dungeon_100_rooms(monsters_df, balance_cfg, seed=s) for s in TRAIN_SEEDS
    }
    val_dungeons = {
        s: build_dungeon_100_rooms(monsters_df, balance_cfg, seed=s) for s in VALIDATION_SEEDS
    }

    logging.info("Executando Experimento 1 — Taxas de Mutação (2%%, 10%%, 25%%)...")
    exp1 = run_experiment_1_mutation(
        train_dungeons=train_dungeons,
        val_dungeons=val_dungeons,
        balance_cfg=balance_cfg,
        mutation_rates=(0.02, 0.10, 0.25),
        pop_size=20,
        generations=12,
        n_repeats=5,
    )

    logging.info("Executando Experimento 2 — Configurações de População (240 avaliações)...")
    exp2 = run_experiment_2_population(
        train_dungeons=train_dungeons,
        val_dungeons=val_dungeons,
        balance_cfg=balance_cfg,
        n_repeats=5,
    )

    logging.info("Executando Experimento 3 — Comparação com Baselines (7 repetições independentes)...")
    exp3, best_ga_chrom, best_ga_run = run_experiment_3_baselines_comparison(
        train_dungeons=train_dungeons,
        val_dungeons=val_dungeons,
        balance_cfg=balance_cfg,
        pop_size=20,
        generations=12,
        n_repeats=7,
    )

    logging.info("Executando Experimento 4 — Generalização Fora da Amostra...")
    fixed_chrom = create_fixed_baseline_chromosome()
    exp4 = run_experiment_4_generalization(
        best_ga_chromosome=best_ga_chrom,
        fixed_baseline_chromosome=fixed_chrom,
        monsters_df=monsters_df,
        balance_cfg=balance_cfg,
    )

    logging.info("Construindo Análise Obrigatória de Falhas e Dominância...")
    failure_analysis = build_failure_and_dominance_analysis(exp1, exp2, exp3, exp4)

    completed_utc = datetime.now(timezone.utc).isoformat()
    payload = {
        "metadata": {
            "project": "Masmorra Genética: A Evolução do Guerreiro — Grupo 7 (IA II - FIB)",
            "results_version": "v2",
            "budget_note": "O orçamento conta avaliações efetivas; elites preservadas não são reavaliadas. A última geração pode ser parcial.",
            "dungeon_version": "v2-composicao-alternativa-deterministica",
            "dataset_version": "srd-2014-v1.0.0",
            "balance_version": balance_cfg.get("config_version", "balance-v1.0.0"),
            "started_at_utc": started_utc,
            "completed_at_utc": completed_utc,
            "train_seeds": TRAIN_SEEDS,
            "validation_seeds": VALIDATION_SEEDS,
        },
        "best_champion_strategy": best_ga_run.to_dict(),
        "experiment_1_mutation": exp1,
        "experiment_2_population": exp2,
        "experiment_3_baselines": exp3,
        "experiment_4_generalization": exp4,
        "failure_and_dominance_analysis": failure_analysis,
    }

    out_data_path = Path("data/experiments/scientific_experiments_v2.json")
    out_res_path = Path("results/experiments_v2/experiments_summary.json")
    out_data_path.parent.mkdir(parents=True, exist_ok=True)
    out_res_path.parent.mkdir(parents=True, exist_ok=True)

    charts = generate_experiment_charts(payload, output_dir=Path("results/experiments_v2"))
    payload["generated_charts"] = charts

    json_str = json.dumps(payload, ensure_ascii=False, indent=2)
    out_data_path.write_text(json_str, encoding="utf-8")
    out_res_path.write_text(json_str, encoding="utf-8")
    logging.info("Experimentos científicos concluídos e salvos em %s", out_data_path)


if __name__ == "__main__":
    main()
