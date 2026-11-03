"""Registro das estratégias avaliadas na busca interativa."""

from __future__ import annotations

from typing import Any

from src.game.combat import DungeonRunResult
from src.genetic.chromosome import Chromosome


def attempt_record(
    candidate: Chromosome,
    run: DungeonRunResult,
    *,
    number: int,
    round_number: int,
    generation: int,
    previous_best: int,
    enemies: list[str],
) -> dict[str, Any]:
    """Guarda o resultado da simulação na masmorra escolhida e as decisões da estratégia."""
    policy = candidate.to_policy_params()
    priorities = policy["ally_priorities"]
    return {
        "number": number,
        "round": round_number,
        "generation": generation,
        "rooms_cleared": run.rooms_cleared,
        "best_so_far": max(previous_best, run.rooms_cleared),
        "completed": run.completed_all_100,
        "failure_room": run.failure_room,
        "failure_reason": run.failure_reason,
        "enemies": list(enemies),
        "level": run.final_warrior_level,
        "health": run.final_warrior_hp,
        "max_health": run.final_warrior_max_hp,
        "gold": run.final_gold,
        "strength": run.final_strength,
        "vitality": run.final_vitality,
        "defense": run.final_defense,
        "weapon_tier": run.final_weapon_tier,
        "armor_tier": run.final_armor_tier,
        "shield_tier": run.final_shield_tier,
        "allies": list(run.active_allies_final),
        "preferred_ally": max(priorities, key=priorities.get),
        "warrior_weights": list(policy["warrior_attr_weights"]),
        "equipment_priority": policy["equip_offense_priority"],
        "mean_rooms": candidate.mean_rooms_cleared,
        "genes": list(candidate.genes),
    }
