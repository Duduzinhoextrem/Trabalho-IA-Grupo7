"""Otimizador por Algoritmo Genético da Masmorra Genética.

Registra os cromossomos, métricas de aptidão, diversidade e orçamento de avaliações
a cada geração, suportando parada por número de gerações, orçamento máximo de avaliações
ou estagnação.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import random
import time
from typing import Any

from src.game.dungeon import DungeonRoom
from src.genetic.chromosome import Chromosome
from src.genetic.fitness import evaluate_chromosome
from src.genetic.operators import (
    apply_elitism,
    compute_population_diversity,
    enforce_diversity_control,
    hybrid_crossover,
    initialize_diverse_population,
    mutate_chromosome,
    tournament_selection,
)


@dataclass
class GenerationRecord:
    """Registro auditável de uma geração do Algoritmo Genético."""

    generation: int
    evaluations_cumulative: int
    best_fitness: float
    mean_fitness: float
    median_fitness: float
    std_fitness: float
    best_mean_rooms: float
    pop_mean_rooms: float
    best_completion_rate: float
    diversity_index: float
    diversity_interventions: int
    best_genes: list[float]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GARunResult:
    """Resultado completo de uma execução do Algoritmo Genético."""

    config: dict[str, Any]
    best_chromosome: Chromosome
    history: list[GenerationRecord] = field(default_factory=list)
    total_objective_evaluations: int = 0
    total_simulation_runs: int = 0
    elapsed_seconds: float = 0.0
    stopped_reason: str = "max_generations_reached"

    def to_dict(self) -> dict[str, Any]:
        return {
            "config": self.config,
            "best_chromosome": {
                "genes": self.best_chromosome.genes,
                "named_genes": self.best_chromosome.to_named_dict(),
                "fitness": self.best_chromosome.fitness,
                "mean_rooms_cleared": self.best_chromosome.mean_rooms_cleared,
                "completion_rate": self.best_chromosome.completion_rate,
                "mean_hp_ratio": self.best_chromosome.mean_hp_ratio,
                "mean_gold_left": self.best_chromosome.mean_gold_left,
            },
            "history": [h.to_dict() for h in self.history],
            "total_objective_evaluations": self.total_objective_evaluations,
            "total_simulation_runs": self.total_simulation_runs,
            "elapsed_seconds": round(self.elapsed_seconds, 4),
            "stopped_reason": self.stopped_reason,
        }


def run_genetic_algorithm(
    dungeons_by_seed: dict[int, list[DungeonRoom]],
    balance_cfg: dict[str, Any],
    pop_size: int = 24,
    generations: int = 20,
    mutation_rate: float = 0.10,
    crossover_rate: float = 0.85,
    tournament_size: int = 3,
    elite_count: int = 2,
    stagnation_limit: int = 15,
    max_evaluations: int | None = None,
    seed: int = 42,
    enable_allies: bool = True,
    enable_chests: bool = True,
) -> GARunResult:
    """Executa o ciclo evolutivo completo do Algoritmo Genético."""
    t0 = time.perf_counter()
    rng = random.Random(seed)
    num_seeds = len(dungeons_by_seed)

    population = initialize_diverse_population(pop_size=pop_size, rng=rng)
    total_evals = 0
    history: list[GenerationRecord] = []

    best_overall: Chromosome | None = None
    generations_without_improvement = 0
    stopped_reason = "max_generations_reached"

    for gen in range(1, generations + 1):
        # Avalia indivíduos que ainda não possuem fitness calculado
        for ind in population:
            if ind.fitness is None:
                if max_evaluations is not None and total_evals >= max_evaluations:
                    break
                evaluate_chromosome(
                    chromosome=ind,
                    dungeons_by_seed=dungeons_by_seed,
                    balance_cfg=balance_cfg,
                    enable_allies=enable_allies,
                    enable_chests=enable_chests,
                )
                total_evals += 1

        # Filtra apenas indivíduos avaliados caso o orçamento tenha esgotado no meio da geração
        evaluated_pop = [ind for ind in population if ind.fitness is not None]
        if not evaluated_pop:
            break

        evaluated_pop.sort(key=lambda c: float(c.fitness or -1e9), reverse=True)
        gen_best = evaluated_pop[0]

        if best_overall is None or float(gen_best.fitness or 0.0) > float(best_overall.fitness or 0.0) + 1e-6:
            best_overall = gen_best.copy()
            generations_without_improvement = 0
        else:
            generations_without_improvement += 1

        fit_vals = [float(c.fitness or 0.0) for c in evaluated_pop]
        room_vals = [float(c.mean_rooms_cleared) for c in evaluated_pop]
        n_eval = len(fit_vals)
        mean_fit = sum(fit_vals) / n_eval
        sorted_fits = sorted(fit_vals)
        median_fit = (
            sorted_fits[n_eval // 2]
            if n_eval % 2 == 1
            else 0.5 * (sorted_fits[n_eval // 2 - 1] + sorted_fits[n_eval // 2])
        )
        std_fit = (sum((x - mean_fit) ** 2 for x in fit_vals) / n_eval) ** 0.5
        div_idx = compute_population_diversity(evaluated_pop)

        # Verifica critério de parada por orçamento máximo ou estagnação
        if max_evaluations is not None and total_evals >= max_evaluations:
            history.append(
                GenerationRecord(
                    generation=gen,
                    evaluations_cumulative=total_evals,
                    best_fitness=round(float(best_overall.fitness or 0.0), 4),
                    mean_fitness=round(mean_fit, 4),
                    median_fitness=round(median_fit, 4),
                    std_fitness=round(std_fit, 4),
                    best_mean_rooms=round(best_overall.mean_rooms_cleared, 4),
                    pop_mean_rooms=round(sum(room_vals) / n_eval, 4),
                    best_completion_rate=round(best_overall.completion_rate, 4),
                    diversity_index=div_idx,
                    diversity_interventions=0,
                    best_genes=list(best_overall.genes),
                )
            )
            stopped_reason = "max_evaluations_reached"
            break

        if generations_without_improvement >= stagnation_limit and gen < generations:
            history.append(
                GenerationRecord(
                    generation=gen,
                    evaluations_cumulative=total_evals,
                    best_fitness=round(float(best_overall.fitness or 0.0), 4),
                    mean_fitness=round(mean_fit, 4),
                    median_fitness=round(median_fit, 4),
                    std_fitness=round(std_fit, 4),
                    best_mean_rooms=round(best_overall.mean_rooms_cleared, 4),
                    pop_mean_rooms=round(sum(room_vals) / n_eval, 4),
                    best_completion_rate=round(best_overall.completion_rate, 4),
                    diversity_index=div_idx,
                    diversity_interventions=0,
                    best_genes=list(best_overall.genes),
                )
            )
            stopped_reason = "stagnation_limit_reached"
            break

        # Cria próxima geração se ainda não for a última
        interventions = 0
        if gen < generations:
            elites = apply_elitism(evaluated_pop, elite_count=min(elite_count, len(evaluated_pop)))
            offspring: list[Chromosome] = []

            while len(offspring) < pop_size - len(elites):
                p1 = tournament_selection(evaluated_pop, tournament_size=tournament_size, rng=rng)
                p2 = tournament_selection(evaluated_pop, tournament_size=tournament_size, rng=rng)
                c1, c2 = hybrid_crossover(p1, p2, rng=rng, crossover_rate=crossover_rate)
                c1 = mutate_chromosome(c1, mutation_rate=mutation_rate, rng=rng)
                c2 = mutate_chromosome(c2, mutation_rate=mutation_rate, rng=rng)
                offspring.append(c1)
                if len(offspring) < pop_size - len(elites):
                    offspring.append(c2)

            offspring, interventions = enforce_diversity_control(offspring, rng=rng)
            population = elites + offspring

        history.append(
            GenerationRecord(
                generation=gen,
                evaluations_cumulative=total_evals,
                best_fitness=round(float(best_overall.fitness or 0.0), 4),
                mean_fitness=round(mean_fit, 4),
                median_fitness=round(median_fit, 4),
                std_fitness=round(std_fit, 4),
                best_mean_rooms=round(best_overall.mean_rooms_cleared, 4),
                pop_mean_rooms=round(sum(room_vals) / n_eval, 4),
                best_completion_rate=round(best_overall.completion_rate, 4),
                diversity_index=div_idx,
                diversity_interventions=interventions,
                best_genes=list(best_overall.genes),
            )
        )

    elapsed = time.perf_counter() - t0
    assert best_overall is not None

    return GARunResult(
        config={
            "pop_size": pop_size,
            "generations": generations,
            "mutation_rate": mutation_rate,
            "crossover_rate": crossover_rate,
            "tournament_size": tournament_size,
            "elite_count": elite_count,
            "stagnation_limit": stagnation_limit,
            "max_evaluations": max_evaluations,
            "seed": seed,
            "num_training_seeds": num_seeds,
            "enable_allies": enable_allies,
            "enable_chests": enable_chests,
        },
        best_chromosome=best_overall,
        history=history,
        total_objective_evaluations=total_evals,
        total_simulation_runs=total_evals * num_seeds,
        elapsed_seconds=elapsed,
        stopped_reason=stopped_reason,
    )
