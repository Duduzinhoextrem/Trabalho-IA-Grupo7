"""Implementação das duas referências obrigatórias (Seção 10):

1. Baseline Fixo (`create_fixed_baseline_chromosome`):
   Estratégia determinística de regras fixas com evolução equilibrada (1/3 Força, 1/3 Vitalidade, 1/3 Defesa),
   reserva moderada fixa (35 ouro), compras conservadoras (limiar 1.25x) e contratação clássica (Arqueiro/Mago).

2. Busca Aleatória (`run_random_search`):
   Amostra estratégias válidas aleatórias usando exatamente o mesmo orçamento de avaliações da função
   objetivo (`budget_evaluations`) que o Algoritmo Genético e retorna a melhor encontrada.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import random
import time
from typing import Any

from src.game.dungeon import DungeonRoom
from src.genetic.chromosome import Chromosome, create_random_chromosome
from src.genetic.fitness import evaluate_chromosome


def create_fixed_baseline_chromosome() -> Chromosome:
    """Retorna o cromossomo representativo da Estratégia Fixa Equilibrada."""
    fixed_genes = [
        0.34,  # 0: w_weight_str (equilibrado)
        0.33,  # 1: w_weight_vit (equilibrado)
        0.33,  # 2: w_weight_def (equilibrado)
        0.70,  # 3: ally_prio_mage
        0.80,  # 4: ally_prio_archer (prefere arqueiro primeiro, depois mago)
        0.40,  # 5: ally_prio_monk
        0.35,  # 6: ally_prio_priest
        0.30,  # 7: ally_prio_alchemist
        0.34,  # 8: ally_weight_power
        0.33,  # 9: ally_weight_vit
        0.33,  # 10: ally_weight_def
        0.50,  # 11: equip_offense_priority (equilibrado)
        0.0,   # 12: hire_before_equip_discrete (compra equipamento básico antes de aliado)
        40.0,  # 13: min_gold_reserve (reserva fixa de 40 moedas)
        1.25,  # 14: equipment_buy_threshold (compra quando tem 125% do custo + reserva)
        1.25,  # 15: ally_hire_threshold
    ]
    return Chromosome(genes=fixed_genes)


@dataclass
class RandomSearchResult:
    """Resultado completo da Busca Aleatória com orçamento equivalente de avaliações."""

    budget_evaluations: int
    seed: int
    best_chromosome: Chromosome
    best_so_far_curve: list[float] = field(default_factory=list)
    mean_all_sampled_rooms: float = 0.0
    std_all_sampled_rooms: float = 0.0
    total_simulation_runs: int = 0
    elapsed_seconds: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "budget_evaluations": self.budget_evaluations,
            "seed": self.seed,
            "best_chromosome": {
                "genes": self.best_chromosome.genes,
                "named_genes": self.best_chromosome.to_named_dict(),
                "fitness": self.best_chromosome.fitness,
                "mean_rooms_cleared": self.best_chromosome.mean_rooms_cleared,
                "completion_rate": self.best_chromosome.completion_rate,
            },
            "best_so_far_curve": self.best_so_far_curve,
            "mean_all_sampled_rooms": round(self.mean_all_sampled_rooms, 4),
            "std_all_sampled_rooms": round(self.std_all_sampled_rooms, 4),
            "total_simulation_runs": self.total_simulation_runs,
            "elapsed_seconds": round(self.elapsed_seconds, 4),
        }


def run_random_search(
    dungeons_by_seed: dict[int, list[DungeonRoom]],
    balance_cfg: dict[str, Any],
    budget_evaluations: int = 360,
    seed: int = 42,
    enable_allies: bool = True,
    enable_chests: bool = True,
) -> RandomSearchResult:
    """Executa Busca Aleatória avaliando `budget_evaluations` cromossomos válidos aleatórios."""
    if budget_evaluations <= 0:
        raise ValueError("budget_evaluations deve ser > 0")

    t0 = time.perf_counter()
    rng = random.Random(seed)
    num_seeds = len(dungeons_by_seed)

    best_ind: Chromosome | None = None
    best_curve: list[float] = []
    sampled_rooms: list[float] = []

    for _ in range(budget_evaluations):
        candidate = create_random_chromosome(rng)
        evaluate_chromosome(
            chromosome=candidate,
            dungeons_by_seed=dungeons_by_seed,
            balance_cfg=balance_cfg,
            enable_allies=enable_allies,
            enable_chests=enable_chests,
        )
        sampled_rooms.append(candidate.mean_rooms_cleared)
        if best_ind is None or float(candidate.fitness or 0.0) > float(best_ind.fitness or 0.0):
            best_ind = candidate.copy()
        best_curve.append(round(float(best_ind.fitness or 0.0), 4))

    elapsed = time.perf_counter() - t0
    assert best_ind is not None

    mean_s = sum(sampled_rooms) / len(sampled_rooms)
    std_s = (sum((x - mean_s) ** 2 for x in sampled_rooms) / len(sampled_rooms)) ** 0.5

    return RandomSearchResult(
        budget_evaluations=budget_evaluations,
        seed=seed,
        best_chromosome=best_ind,
        best_so_far_curve=best_curve,
        mean_all_sampled_rooms=mean_s,
        std_all_sampled_rooms=std_s,
        total_simulation_runs=budget_evaluations * num_seeds,
        elapsed_seconds=elapsed,
    )
