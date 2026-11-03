"""Simulação e busca interativa, sem dependência do Streamlit."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Callable

import pandas as pd

from src.experiments.baselines import create_fixed_baseline_chromosome
from src.experiments.evaluation import TRAIN_SEEDS, generations_for_budget
from src.game.combat import DungeonRunResult, run_dungeon_simulation
from src.game.dungeon import build_dungeon_100_rooms
from src.genetic.chromosome import Chromosome
from src.genetic.optimizer import GenerationRecord, run_genetic_algorithm
from src.ui.search_history import attempt_record


def scenario_signature(monsters: pd.DataFrame, settings: dict, seed: int, chests: bool) -> str:
    """Identifica os dados e as regras para não misturar históricos incompatíveis."""
    data_hash = pd.util.hash_pandas_object(monsters, index=True).values.tobytes()
    rules = json.dumps({"settings": settings, "seed": seed, "chests": chests}, sort_keys=True)
    return hashlib.sha256(data_hash + rules.encode("utf-8")).hexdigest()


def simulate_journey(monsters: pd.DataFrame, settings: dict, seed: int, chests: bool,
                     strategy: Chromosome, mode: str, champion: Chromosome | None = None,
                     *, rooms: list | None = None) -> dict[str, Any]:
    """Reproduz uma estratégia e seus comparadores nas mesmas salas e regras."""
    if rooms is None:
        rooms = build_dungeon_100_rooms(monsters, settings, seed=seed)
    player = run_dungeon_simulation(rooms, strategy.to_policy_params(), settings, seed=seed,
                                    enable_chests=chests, record_detailed_logs=True)
    opponents = []
    if mode != "Estratégia fixa":
        opponents.append(("Estratégia fixa", create_fixed_baseline_chromosome()))
    if champion is not None and mode != "Estratégia do algoritmo":
        opponents.append(("Estratégia do estudo", champion))
    comparisons = [(name, run_dungeon_simulation(rooms, other.to_policy_params(), settings, seed=seed,
                                                enable_chests=chests)) for name, other in opponents]
    return {"rooms": rooms, "player": player, "comparisons": comparisons, "mode": mode,
            "seed": seed, "chests": chests, "index": 0, "selected_strategy": strategy.copy(),
            "scenario_signature": scenario_signature(monsters, settings, seed, chests)}


def search_journey(monsters: pd.DataFrame, settings: dict, seed: int, chests: bool,
                   champion: Chromosome | None = None, *, budget: int = 400, population: int = 16,
                   previous: dict | None = None,
                   on_progress: Callable[[dict], None] | None = None) -> dict[str, Any]:
    """Procura uma vitória com orçamento limitado e preserva as tentativas anteriores."""
    generations = generations_for_budget(population, budget)
    signature = scenario_signature(monsters, settings, seed, chests)
    if previous and previous.get("scenario_signature") != signature:
        raise ValueError("Os dados ou as regras mudaram. Inicie uma nova busca para este cenário.")
    total_before = previous.get("total_evaluations", 0) if previous else 0
    search_round = previous.get("search_round", 0) + 1 if previous else 1
    attempts = list(previous.get("attempts", [])) if previous else []
    best_strategy: Chromosome | None = None
    best_rooms = -1
    evaluations = 0
    generation = 1
    training_rooms = {s: build_dungeon_100_rooms(monsters, settings, seed=s)
                      for s in sorted(set(TRAIN_SEEDS) | {seed})}

    def next_generation(record: GenerationRecord) -> None:
        nonlocal generation
        generation = record.generation + 1

    def observe(candidate: Chromosome, runs: list[DungeonRunResult]) -> bool:
        nonlocal best_rooms, best_strategy, evaluations
        evaluations += 1
        target = next(run for run in runs if run.seed == seed)
        if (best_strategy is None or target.rooms_cleared > best_rooms or
                (target.rooms_cleared == best_rooms and
                 float(candidate.fitness or 0) > float(best_strategy.fitness or 0))):
            best_rooms, best_strategy = target.rooms_cleared, candidate.copy()
        last_room = target.failure_room or len(training_rooms[seed])
        enemies = [enemy.source_name for enemy in training_rooms[seed][last_room - 1].enemies]
        attempts.append(attempt_record(
            candidate, target, number=total_before + evaluations, round_number=search_round,
            generation=generation, previous_best=attempts[-1]["best_so_far"] if attempts else 0,
            enemies=enemies,
        ))
        if on_progress and (evaluations == 1 or evaluations % 8 == 0 or target.completed_all_100):
            on_progress({"evaluations": total_before + evaluations, "round_evaluations": evaluations,
                         "best_rooms": best_rooms, "budget": budget, "generation": generation})
        return target.completed_all_100

    initial = [previous["selected_strategy"]] if previous else []
    if champion is not None and not any(item.genes == champion.genes for item in initial):
        initial.append(champion)
    training = run_genetic_algorithm(
        training_rooms, settings, pop_size=population, generations=generations,
        mutation_rate=0.10, seed=41 + search_round, enable_chests=chests,
        initial_chromosomes=initial, max_evaluations=budget, stagnation_limit=generations + 1,
        stop_when=observe, on_generation=next_generation,
    )
    if best_strategy is None:
        raise ValueError("A busca não avaliou nenhuma estratégia.")
    selected = training.best_chromosome if training.stopped_reason == "target_reached" else best_strategy
    journey = simulate_journey(monsters, settings, seed, chests, selected, "Busca automática", champion,
                               rooms=training_rooms[seed])
    journey.update(training=training, attempts=attempts, search_round=search_round,
                   total_evaluations=total_before + training.total_objective_evaluations)
    journey["index"] = max(0, len(journey["player"].room_results) - 1)
    return journey


def journey_report(journey: dict, settings: dict) -> str:
    """Exporta regras, genes e resultados da simulação. O estado da sessão fica fora do relatório."""
    player = journey["player"]
    report = {
        "schema_version": 1,
        "mode": journey["mode"], "seed": journey["seed"], "enable_chests": journey["chests"],
        "scenario_signature": journey["scenario_signature"], "balance": settings,
        "genes": journey["selected_strategy"].genes,
        "outcome": {"rooms_cleared": player.rooms_cleared, "completed": player.completed_all_100,
                    "failure_room": player.failure_room, "failure_reason": player.failure_reason},
        "rooms": [{"room": room.room_number, "victory": room.victory,
                   "health": room.warrior_hp_end, "gold": room.gold_end,
                   "enemies": room.enemies_faced} for room in player.room_results],
        "comparisons": [{"method": name, "rooms_cleared": run.rooms_cleared,
                         "completed": run.completed_all_100} for name, run in journey["comparisons"]],
        "attempts": journey.get("attempts", []),
        "training": journey["training"].to_dict() if journey.get("training") else None,
    }
    return json.dumps(report, ensure_ascii=False, indent=2)
