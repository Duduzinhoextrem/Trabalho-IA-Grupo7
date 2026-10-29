"""Função de Aptidão (Fitness) Multi-Semente da Masmorra Genética.

Regras (Seção 9):
- Prioriza estritamente a média de salas concluídas (`mean_rooms_cleared`).
- Reporta separadamente a taxa de conclusão das 100 salas (`completion_rate`).
- Critérios secundários (vida restante e ouro restante) possuem peso total <= 0.009,
  garantindo matematicamente que NUNCA invertam a prioridade de avanço de salas.
"""

from __future__ import annotations

from typing import Any

from src.game.combat import DungeonRunResult, run_dungeon_simulation
from src.game.dungeon import DungeonRoom
from src.genetic.chromosome import Chromosome


def compute_lexicographic_fitness(
    mean_rooms: float,
    mean_hp_ratio: float,
    mean_gold: float,
) -> float:
    """Calcula o valor escalar de fitness preservando a ordem lexicográfica estrita por salas.

    O bônus secundário máximo é 0.006 + 0.003 = 0.009 < 1/K (para qualquer K <= 100 sementes),
    impedindo que vida ou ouro superem sequer +1 sala concluída em uma única semente.
    """
    hp_component = 0.006 * max(0.0, min(1.0, mean_hp_ratio))
    gold_component = 0.003 * max(0.0, min(1.0, mean_gold / 2000.0))
    return round(float(mean_rooms) + hp_component + gold_component, 6)


def evaluate_chromosome(
    chromosome: Chromosome,
    dungeons_by_seed: dict[int, list[DungeonRoom]],
    balance_cfg: dict[str, Any],
    enable_allies: bool = True,
    enable_chests: bool = True,
) -> tuple[float, list[DungeonRunResult]]:
    """Avalia um cromossomo em múltiplos cenários (sementes fixas compartilhadas entre concorrentes)."""
    policy = chromosome.to_policy_params()
    seeds = sorted(dungeons_by_seed.keys())
    if not seeds:
        raise ValueError("Nenhuma masmorra fornecida em dungeons_by_seed para avaliação.")

    runs: list[DungeonRunResult] = []
    for s in seeds:
        res = run_dungeon_simulation(
            rooms_template=dungeons_by_seed[s],
            policy_params=policy,
            balance_cfg=balance_cfg,
            seed=s,
            enable_allies=enable_allies,
            enable_chests=enable_chests,
            record_detailed_logs=False,
        )
        runs.append(res)

    k = len(runs)
    mean_rooms = sum(r.rooms_cleared for r in runs) / k
    completion_rate = sum(1 for r in runs if r.completed_all_100) / k
    mean_hp_ratio = sum(r.final_warrior_hp / max(1, r.final_warrior_max_hp) for r in runs) / k
    mean_gold = sum(r.final_gold for r in runs) / k

    fitness_val = compute_lexicographic_fitness(
        mean_rooms=mean_rooms,
        mean_hp_ratio=mean_hp_ratio,
        mean_gold=mean_gold,
    )

    chromosome.fitness = fitness_val
    chromosome.mean_rooms_cleared = round(mean_rooms, 4)
    chromosome.completion_rate = round(completion_rate, 4)
    chromosome.mean_hp_ratio = round(mean_hp_ratio, 4)
    chromosome.mean_gold_left = round(mean_gold, 2)
    chromosome.evaluated_seeds = seeds

    return fitness_val, runs
