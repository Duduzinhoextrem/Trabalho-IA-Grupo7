"""Gerador determinístico por semente da Masmorra de 100 Salas baseado no Dataset D&D 5e SRD.

A montagem de cada sala considera:
- Nível de desafio (CR) dos monstros no dataset externo
- Vida, defesa e potencial ofensivo (físico e mágico)
- Número de inimigos (1 a 3 por sala conforme orçamento de encontro)
- Dificuldade prevista crescente da Sala 1 à Sala 100
- Reprodutibilidade exata por semente (`seed`)
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
import random
from typing import Any

import pandas as pd

from src.game.monsters import (
    MonsterCombatInstance,
    adapt_srd_row_to_monster_instance,
    filter_combat_eligible_monsters,
)


@dataclass
class DungeonRoom:
    """Representa uma das 100 salas da masmorra com sua composição de encontro e métricas."""

    room_number: int
    target_cr: float
    expected_difficulty: float
    enemies: list[MonsterCombatInstance]

    @property
    def total_enemy_hp(self) -> int:
        return sum(e.max_hp for e in self.enemies)

    @property
    def total_enemy_dpr(self) -> float:
        return round(sum(e.physical_damage + e.magical_damage for e in self.enemies), 2)

    def clone_for_simulation(self) -> DungeonRoom:
        """Retorna uma cópia limpa da sala para execução de combate sem mutar o template."""
        return DungeonRoom(
            room_number=self.room_number,
            target_cr=self.target_cr,
            expected_difficulty=self.expected_difficulty,
            enemies=[copy.copy(e) for e in self.enemies],
        )

    def to_summary_dict(self) -> dict[str, Any]:
        return {
            "room_number": self.room_number,
            "target_cr": self.target_cr,
            "expected_difficulty": self.expected_difficulty,
            "enemy_count": len(self.enemies),
            "enemy_names": ", ".join(f"{e.source_name} (CR {e.challenge_rating:g})" for e in self.enemies),
            "source_indices": ", ".join(e.source_index for e in self.enemies),
            "total_hp": self.total_enemy_hp,
            "total_dpr": self.total_enemy_dpr,
        }


def compute_room_target_cr(room_number: int) -> float:
    """Define a curva progressiva de Challenge Rating (CR) alvo para as salas 1 a 100."""
    if room_number <= 10:
        # Salas iniciais: CR 0.125 a 1.0
        return round(0.125 + (room_number - 1) * (0.875 / 9.0), 3)
    if room_number <= 30:
        # Salas 11 a 30: CR 1.0 a 4.5
        return round(1.0 + (room_number - 10) * (3.5 / 20.0), 3)
    if room_number <= 60:
        # Salas 31 a 60: CR 4.5 a 11.0
        return round(4.5 + (room_number - 30) * (6.5 / 30.0), 3)
    if room_number <= 90:
        # Salas 61 a 90: CR 11.0 a 18.5
        return round(11.0 + (room_number - 60) * (7.5 / 30.0), 3)
    if room_number < 100:
        # Salas 91 a 99: CR 18.5 a 23.0
        return round(18.5 + (room_number - 90) * (4.5 / 9.0), 3)
    # Sala 100 (Chefe Final): CR 24+
    return 24.0


def build_dungeon_100_rooms(
    monsters_df: pd.DataFrame,
    balance_cfg: dict[str, Any],
    seed: int = 42,
    difficulty_multiplier: float = 1.0,
    composition_mode: str = "standard",
) -> list[DungeonRoom]:
    """Constrói exatamente 100 salas reproduzíveis por semente a partir do dataset externo.

    Parâmetros:
    - `seed`: semente do gerador pseudoaleatório para reprodutibilidade exata.
    - `difficulty_multiplier`: fator multiplicador de dificuldade (1.0 padrão; >1.0 para testes de generalização).
    - `composition_mode`:
        - `"standard"`: utiliza todo o pool elegível do SRD.
        - `"alternate_pool"`: privilegia subconjunto alternativo de espécies/tipos para teste de generalização fora da amostra.
    """
    eligible_df = filter_combat_eligible_monsters(monsters_df)
    if eligible_df.empty:
        raise ValueError("Nenhum monstro elegível disponível para construir a masmorra.")

    rng = random.Random(seed)
    records = eligible_df.to_dict(orient="records")

    if composition_mode == "alternate_pool":
        # Desloca a preferência de amostragem para testar generalização em novas composições
        rng.shuffle(records)

    total_rooms = int(balance_cfg["dungeon"].get("total_rooms", 100))
    rooms: list[DungeonRoom] = []

    for room_num in range(1, total_rooms + 1):
        target_cr = compute_room_target_cr(room_num)

        # Determina quantidade de inimigos na sala (1 a 3) conforme progressão e semente
        if room_num in (1, 2, 3, 25, 50, 75, 100):
            num_enemies = 1  # Salas iniciais e salas de chefe/subchefe têm 1 inimigo principal
        elif room_num < 12:
            num_enemies = 1 if rng.random() < 0.72 else 2
        elif room_num < 70:
            roll = rng.random()
            if roll < 0.45:
                num_enemies = 1
            elif roll < 0.85:
                num_enemies = 2
            else:
                num_enemies = 3
        else:
            num_enemies = 1 if rng.random() < 0.58 else 2

        # Ajusta o CR individual quando há múltiplos inimigos para manter o orçamento de dificuldade coerente
        if num_enemies == 1:
            individual_target_cr = target_cr
        elif num_enemies == 2:
            individual_target_cr = max(0.125, target_cr * 0.62)
        else:
            individual_target_cr = max(0.125, target_cr * 0.44)

        # Seleciona candidatos próximos ao individual_target_cr
        scored_candidates: list[tuple[float, dict[str, Any]]] = []
        for rec in records:
            cr_val = float(rec["challenge_rating"])
            cr_dist = abs(cr_val - individual_target_cr)
            # Em modo alternate_pool, adiciona perturbação controlada por índice para variar espécies
            species_bias = 0.0
            if composition_mode == "alternate_pool":
                species_bias = (hash(str(rec["index"]) + str(seed)) % 100) / 250.0
            scored_candidates.append((cr_dist + species_bias, rec))

        scored_candidates.sort(key=lambda item: (round(item[0], 4), str(item[1]["index"])))
        top_k = min(len(scored_candidates), 12 if composition_mode == "standard" else 18)
        candidate_pool = [item[1] for item in scored_candidates[:top_k]]

        # Se múltiplos inimigos na mesma sala, reduz os atributos individuais ligeiramente para manter progressão suave
        group_balance_scale = 1.0 if num_enemies == 1 else (0.72 if num_enemies == 2 else 0.56)
        effective_mult = difficulty_multiplier * group_balance_scale

        room_enemies: list[MonsterCombatInstance] = []
        for seq in range(1, num_enemies + 1):
            chosen_rec = rng.choice(candidate_pool)
            inst = adapt_srd_row_to_monster_instance(
                row=chosen_rec,
                room_number=room_num,
                instance_seq=seq,
                balance_cfg=balance_cfg,
                difficulty_multiplier=effective_mult,
            )
            room_enemies.append(inst)

        # Garante que pelo menos 1 inimigo esteja na linha de frente no início do combate
        if room_enemies and all(e.position == "backline" for e in room_enemies):
            room_enemies[0].position = "frontline"

        # Calcula índice composto de dificuldade prevista para a sala
        expected_diff = round(
            sum(
                e.max_hp * 0.35 + (e.physical_damage + e.magical_damage) * 2.2 + e.defense * 1.4
                for e in room_enemies
            ),
            2,
        )

        rooms.append(
            DungeonRoom(
                room_number=room_num,
                target_cr=target_cr,
                expected_difficulty=expected_diff,
                enemies=room_enemies,
            )
        )

    return rooms
