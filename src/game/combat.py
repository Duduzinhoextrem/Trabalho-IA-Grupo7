"""Combate automático por turnos e simulação das 100 salas.

Compartilhado entre:
- Modo de aventura interativo (Streamlit)
- Treinamento do Algoritmo Genético
- Estratégias de referência (estratégia fixa e busca aleatória)
- Experimentos científicos e testes de generalização

Funciona sem interface gráfica. O dano mínimo e os limites de mitigação e turnos
impedem a invulnerabilidade e os combates infinitos (`min_damage_guaranteed = 1`, `max_mitigation_cap = 0.75`, `max_turns = 40`).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import random
from typing import Any

from src.game.characters import ALLY_CLASSES_ORDER, Ally, Warrior, create_initial_warrior
from src.game.dungeon import DungeonRoom
from src.game.economy import execute_market_phase, roll_post_victory_chest
from src.game.monsters import MonsterCombatInstance


@dataclass
class RoomCombatResult:
    """Resultado detalhado do combate em uma sala da masmorra."""

    room_number: int
    victory: bool
    turns_taken: int
    termination_reason: str  # Vitória ("enemies_defeated"), morte ("warrior_died") ou limite de turnos ("max_turns_exceeded").
    warrior_hp_start: int
    warrior_hp_end: int
    warrior_max_hp: int
    warrior_level_end: int
    gold_earned: int
    xp_earned: int
    gold_end: int
    active_allies_end: list[str]
    enemies_faced: list[str]
    enemy_source_indices: list[str]
    market_transactions: list[dict[str, Any]] = field(default_factory=list)
    chest_event: dict[str, Any] | None = None
    combat_log: list[str] = field(default_factory=list)
    weapon_tier_end: int = 1
    armor_tier_end: int = 0
    shield_tier_end: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DungeonRunResult:
    """Resultado consolidado de uma tentativa completa na masmorra de 100 salas."""

    seed: int
    rooms_cleared: int
    completed_all_100: bool
    final_warrior_level: int
    final_warrior_hp: int
    final_warrior_max_hp: int
    final_gold: int
    final_strength: int
    final_vitality: int
    final_defense: int
    final_weapon_tier: int
    final_armor_tier: int
    final_shield_tier: int
    hired_allies_history: list[str]
    active_allies_final: list[str]
    total_turns_fought: int
    failure_room: int | None
    failure_reason: str | None
    room_results: list[RoomCombatResult] = field(default_factory=list)


def compute_mitigated_damage(
    raw_damage: float,
    target_defense: float,
    target_resistance: float,
    defense_constant: float = 42.0,
    max_mitigation_cap: float = 0.75,
    extra_block: float = 0.0,
    min_damage: int = 1,
) -> int:
    """Calcula dano com redução hiperbólica por defesa e resistência, garantindo dano mínimo >= 1."""
    if raw_damage <= 0:
        return 0
    eff_def = max(0.0, target_defense)
    def_mitig = min(max_mitigation_cap, eff_def / (eff_def + defense_constant))
    res_clamped = min(0.60, max(-0.35, target_resistance))
    block_clamped = min(0.25, max(0.0, extra_block))

    multiplier = (1.0 - def_mitig) * (1.0 - res_clamped) * (1.0 - block_clamped)
    final_dmg = int(round(raw_damage * multiplier))
    return max(min_damage, final_dmg)


def select_enemy_target_for_hero(
    enemies: list[MonsterCombatInstance],
    is_ranged_or_magic: bool,
    prefer_low_phys_res: bool = False,
) -> MonsterCombatInstance | None:
    """Escolhe o alvo inimigo conforme a posição na linha de frente ou na retaguarda."""
    living = [e for e in enemies if e.is_alive]
    if not living:
        return None

    if not is_ranged_or_magic:
        frontline = [e for e in living if e.position == "frontline"]
        pool = frontline if frontline else living
        return min(pool, key=lambda e: (e.current_hp, e.defense, e.instance_id))

    # Mago e arqueiro podem atacar a retaguarda ou os inimigos mais vulneráveis.
    if prefer_low_phys_res:
        return min(living, key=lambda e: (e.phys_resistance, e.current_hp, e.instance_id))
    return min(living, key=lambda e: (e.mag_resistance, e.current_hp, e.instance_id))


def simulate_single_room_combat(
    warrior: Warrior,
    room: DungeonRoom,
    balance_cfg: dict[str, Any],
    rng: random.Random,
    record_log: bool = False,
) -> tuple[bool, int, str, list[str]]:
    """Executa o combate em turnos de uma sala até vitória, morte do guerreiro ou limite de turnos."""
    c_cfg = balance_cfg["combat"]
    max_turns = int(c_cfg["max_turns"])
    def_const = float(c_cfg["defense_mitigation_constant"])
    max_mitig = float(c_cfg["max_mitigation_cap"])
    min_dmg = int(c_cfg["min_damage_guaranteed"])
    frontline_weight = float(c_cfg["frontline_target_weight"])

    enemies = room.enemies
    combat_log: list[str] = []

    # Reinicia as cargas de cura do padre e os bônus e penalidades temporários.
    warrior.buff_stacks = 0
    warrior.buff_turns_left = 0
    for ally in warrior.allies:
        if ally.is_alive and ally.ally_class == "priest":
            ally.heals_remaining = ally.max_heals_per_combat

    for turn in range(1, max_turns + 1):
        # Verifica condições de término no início do turno
        if not warrior.is_alive:
            return False, turn - 1, "warrior_died", combat_log
        if not any(e.is_alive for e in enemies):
            return True, turn - 1, "enemies_defeated", combat_log

        # A partir do turno 2, reduz a duração dos bônus e penalidades no início da rodada.
        if turn > 1:
            if warrior.buff_turns_left > 0:
                warrior.buff_turns_left -= 1
                if warrior.buff_turns_left == 0:
                    warrior.buff_stacks = 0
            for e in enemies:
                if e.is_alive and e.debuff_turns_left > 0:
                    e.debuff_turns_left -= 1
                    if e.debuff_turns_left == 0:
                        e.debuff_stacks = 0

        # Monta a ordem de ação do turno.
        actors: list[tuple[int, int, str, Any]] = []
        w_init = 12 + warrior.weapon_tier
        actors.append((w_init, 0, "warrior", warrior))
        for idx_a, ally in enumerate(warrior.allies):
            if ally.is_alive:
                actors.append((ally.initiative, idx_a + 1, "ally", ally))
        for idx_e, enemy in enumerate(enemies):
            if enemy.is_alive:
                actors.append((enemy.initiative, idx_e + 10, "enemy", enemy))

        # Ordena pela maior iniciativa e desempata pela prioridade do índice.
        actors.sort(key=lambda item: (-item[0], item[1]))

        party_buff_mult = 1.0 + 0.14 * warrior.buff_stacks

        for _, _, actor_type, actor_obj in actors:
            if not warrior.is_alive:
                return False, turn, "warrior_died", combat_log
            if not any(e.is_alive for e in enemies):
                return True, turn, "enemies_defeated", combat_log

            if actor_type == "warrior":
                target = select_enemy_target_for_hero(enemies, is_ranged_or_magic=False)
                if target is None:
                    break
                raw_phys = warrior.compute_physical_damage(balance_cfg, buff_multiplier=party_buff_mult)
                debuff_factor = max(0.5, 1.0 - 0.14 * target.debuff_stacks)
                dmg = compute_mitigated_damage(
                    raw_damage=raw_phys,
                    target_defense=target.defense * debuff_factor,
                    target_resistance=target.phys_resistance * debuff_factor,
                    defense_constant=def_const,
                    max_mitigation_cap=max_mitig,
                    min_damage=min_dmg,
                )
                target.current_hp = max(0, target.current_hp - dmg)
                if record_log:
                    combat_log.append(
                        f"T{turn}: Guerreiro atacou {target.source_name} causando {dmg} de dano físico (HP inimigo: {target.current_hp}/{target.max_hp})."
                    )

            elif actor_type == "ally":
                ally: Ally = actor_obj
                if not ally.is_alive:
                    continue

                if ally.ally_class == "priest":
                    # Verifica se alguém precisa de cura e se restam cargas.
                    wounded_candidates: list[Any] = []
                    if warrior.current_hp < int(warrior.max_hp * 0.78):
                        wounded_candidates.append(warrior)
                    for other_a in warrior.allies:
                        if other_a.is_alive and other_a.current_hp < int(other_a.max_hp * 0.72):
                            wounded_candidates.append(other_a)

                    if wounded_candidates and ally.heals_remaining > 0:
                        # Cura primeiro o guerreiro se estiver com menos de 55% de vida; caso contrário, quem tiver a menor porcentagem.
                        if warrior.current_hp < int(warrior.max_hp * 0.55):
                            heal_target = warrior
                            target_name = "Guerreiro"
                        else:
                            heal_target = min(
                                wounded_candidates,
                                key=lambda u: u.current_hp / max(1, u.max_hp),
                            )
                            target_name = "Guerreiro" if heal_target is warrior else heal_target.name
                        heal_amt = ally.compute_heal_amount()
                        ally.heals_remaining -= 1
                        heal_target.current_hp = min(heal_target.max_hp, heal_target.current_hp + heal_amt)
                        if record_log:
                            combat_log.append(
                                f"T{turn}: Padre curou {target_name} em +{heal_amt} HP (cargas restantes: {ally.heals_remaining})."
                            )
                        continue

                    # Sem cura a realizar, o padre faz um ataque sagrado mágico.
                    target = select_enemy_target_for_hero(enemies, is_ranged_or_magic=True)
                    if target is not None:
                        raw_mag = ally.compute_raw_damage(buff_multiplier=party_buff_mult)
                        debuff_factor = max(0.5, 1.0 - 0.14 * target.debuff_stacks)
                        dmg = compute_mitigated_damage(
                            raw_damage=raw_mag,
                            target_defense=target.defense * 0.75 * debuff_factor,
                            target_resistance=target.mag_resistance * debuff_factor,
                            defense_constant=def_const,
                            max_mitigation_cap=max_mitig,
                            min_damage=min_dmg,
                        )
                        target.current_hp = max(0, target.current_hp - dmg)
                        if record_log:
                            combat_log.append(
                                f"T{turn}: Padre golpeou {target.source_name} com luz sagrada causando {dmg} de dano mágico."
                            )

                elif ally.ally_class == "alchemist":
                    # Aplica um bônus na equipe e uma penalidade no inimigo principal, além de dano químico.
                    warrior.buff_stacks = min(ally.max_buff_stacks, warrior.buff_stacks + 1)
                    warrior.buff_turns_left = ally.buff_duration_turns
                    target = select_enemy_target_for_hero(enemies, is_ranged_or_magic=True)
                    if target is not None:
                        target.debuff_stacks = min(ally.max_buff_stacks, target.debuff_stacks + 1)
                        target.debuff_turns_left = ally.buff_duration_turns
                        raw_mag = ally.compute_raw_damage(buff_multiplier=party_buff_mult)
                        debuff_factor = max(0.5, 1.0 - 0.14 * target.debuff_stacks)
                        dmg = compute_mitigated_damage(
                            raw_damage=raw_mag,
                            target_defense=target.defense * 0.75 * debuff_factor,
                            target_resistance=target.mag_resistance * debuff_factor,
                            defense_constant=def_const,
                            max_mitigation_cap=max_mitig,
                            min_damage=min_dmg,
                        )
                        target.current_hp = max(0, target.current_hp - dmg)
                        if record_log:
                            combat_log.append(
                                f"T{turn}: Alquimista aplicou Buff/Debuff (stacks={warrior.buff_stacks}) e causou {dmg} de dano a {target.source_name}."
                            )

                elif ally.ally_class == "mage":
                    target = select_enemy_target_for_hero(
                        enemies, is_ranged_or_magic=True, prefer_low_phys_res=False
                    )
                    if target is not None:
                        raw_mag = ally.compute_raw_damage(buff_multiplier=party_buff_mult)
                        debuff_factor = max(0.5, 1.0 - 0.14 * target.debuff_stacks)
                        dmg = compute_mitigated_damage(
                            raw_damage=raw_mag,
                            target_defense=target.defense * 0.68 * debuff_factor,
                            target_resistance=target.mag_resistance * debuff_factor,
                            defense_constant=def_const,
                            max_mitigation_cap=max_mitig,
                            min_damage=min_dmg,
                        )
                        target.current_hp = max(0, target.current_hp - dmg)
                        if record_log:
                            combat_log.append(
                                f"T{turn}: Mago lançou feitiço em {target.source_name} causando {dmg} de dano mágico."
                            )

                elif ally.ally_class == "archer":
                    target = select_enemy_target_for_hero(
                        enemies, is_ranged_or_magic=True, prefer_low_phys_res=True
                    )
                    if target is not None:
                        raw_phys = ally.compute_raw_damage(buff_multiplier=party_buff_mult)
                        debuff_factor = max(0.5, 1.0 - 0.14 * target.debuff_stacks)
                        dmg = compute_mitigated_damage(
                            raw_damage=raw_phys,
                            target_defense=target.defense * 0.85 * debuff_factor,
                            target_resistance=target.phys_resistance * debuff_factor,
                            defense_constant=def_const,
                            max_mitigation_cap=max_mitig,
                            min_damage=min_dmg,
                        )
                        target.current_hp = max(0, target.current_hp - dmg)
                        if record_log:
                            combat_log.append(
                                f"T{turn}: Arqueiro disparou em {target.source_name} causando {dmg} de dano físico."
                            )

                elif ally.ally_class == "monk":
                    target = select_enemy_target_for_hero(enemies, is_ranged_or_magic=False)
                    if target is not None:
                        raw_mag = ally.compute_raw_damage(buff_multiplier=party_buff_mult)
                        debuff_factor = max(0.5, 1.0 - 0.14 * target.debuff_stacks)
                        dmg = compute_mitigated_damage(
                            raw_damage=raw_mag,
                            target_defense=target.defense * 0.72 * debuff_factor,
                            target_resistance=target.mag_resistance * debuff_factor,
                            defense_constant=def_const,
                            max_mitigation_cap=max_mitig,
                            min_damage=min_dmg,
                        )
                        target.current_hp = max(0, target.current_hp - dmg)
                        if record_log:
                            combat_log.append(
                                f"T{turn}: Monge golpeou com Ki {target.source_name} causando {dmg} de dano espiritual."
                            )

            elif actor_type == "enemy":
                enemy: MonsterCombatInstance = actor_obj
                if not enemy.is_alive:
                    continue

                # Escolhe o alvo na equipe do guerreiro conforme a linha de frente e a retaguarda.
                living_allies = [a for a in warrior.allies if a.is_alive]
                frontline_allies = [a for a in living_allies if a.position == "frontline"]
                backline_allies = [a for a in living_allies if a.position == "backline"]

                target_is_warrior = True
                chosen_ally: Ally | None = None

                if living_allies:
                    if enemy.position == "frontline" and rng.random() < frontline_weight:
                        # O inimigo ataca a linha de frente (guerreiro ou monge).
                        if frontline_allies and rng.random() < 0.45:
                            target_is_warrior = False
                            chosen_ally = frontline_allies[0]
                    else:
                        # Ataques à distância ou mágicos podem atingir a retaguarda, se houver alguém nela.
                        if backline_allies and rng.random() < 0.35:
                            target_is_warrior = False
                            chosen_ally = min(backline_allies, key=lambda a: a.current_hp)
                        elif frontline_allies and rng.random() < 0.35:
                            target_is_warrior = False
                            chosen_ally = frontline_allies[0]

                total_enemy_dmg = 0
                if target_is_warrior or chosen_ally is None:
                    w_def = warrior.compute_total_defense(balance_cfg)
                    w_block = warrior.compute_block_mitigation(balance_cfg)
                    if enemy.physical_damage > 0:
                        total_enemy_dmg += compute_mitigated_damage(
                            raw_damage=enemy.physical_damage,
                            target_defense=w_def,
                            target_resistance=0.0,
                            defense_constant=def_const,
                            max_mitigation_cap=max_mitig,
                            extra_block=w_block,
                            min_damage=min_dmg,
                        )
                    if enemy.magical_damage > 0:
                        total_enemy_dmg += compute_mitigated_damage(
                            raw_damage=enemy.magical_damage,
                            target_defense=w_def * 0.75,
                            target_resistance=0.0,
                            defense_constant=def_const,
                            max_mitigation_cap=max_mitig,
                            extra_block=w_block * 0.5,
                            min_damage=min_dmg,
                        )
                    warrior.current_hp = max(0, warrior.current_hp - total_enemy_dmg)
                    if record_log:
                        combat_log.append(
                            f"T{turn}: {enemy.source_name} atacou Guerreiro causando {total_enemy_dmg} de dano (HP Guerreiro: {warrior.current_hp}/{warrior.max_hp})."
                        )
                    if not warrior.is_alive:
                        return False, turn, "warrior_died", combat_log
                else:
                    a_def = chosen_ally.defense * 2.0 + (6.0 if chosen_ally.ally_class == "monk" else 0.0)
                    a_mag_res = 0.18 if chosen_ally.ally_class in ("mage", "monk", "priest") else 0.0
                    a_phys_res = 0.15 if chosen_ally.ally_class == "monk" else 0.0
                    if enemy.physical_damage > 0:
                        total_enemy_dmg += compute_mitigated_damage(
                            raw_damage=enemy.physical_damage,
                            target_defense=a_def,
                            target_resistance=a_phys_res,
                            defense_constant=def_const,
                            max_mitigation_cap=max_mitig,
                            min_damage=min_dmg,
                        )
                    if enemy.magical_damage > 0:
                        total_enemy_dmg += compute_mitigated_damage(
                            raw_damage=enemy.magical_damage,
                            target_defense=a_def * 0.8,
                            target_resistance=a_mag_res,
                            defense_constant=def_const,
                            max_mitigation_cap=max_mitig,
                            min_damage=min_dmg,
                        )
                    chosen_ally.current_hp = max(0, chosen_ally.current_hp - total_enemy_dmg)
                    if record_log:
                        status_str = (
                            f"HP {chosen_ally.current_hp}/{chosen_ally.max_hp}"
                            if chosen_ally.is_alive
                            else "DERROTADO"
                        )
                        combat_log.append(
                            f"T{turn}: {enemy.source_name} atacou {chosen_ally.name} causando {total_enemy_dmg} de dano ({status_str})."
                        )

        if not any(e.is_alive for e in enemies):
            return True, turn, "enemies_defeated", combat_log

    # Encerra por exaustão se restarem inimigos vivos ao atingir o limite de turnos.
    return False, max_turns, "max_turns_exceeded", combat_log


def run_dungeon_simulation(
    rooms_template: list[DungeonRoom],
    policy_params: dict[str, Any],
    balance_cfg: dict[str, Any],
    seed: int = 42,
    enable_allies: bool = True,
    enable_chests: bool = True,
    record_detailed_logs: bool = False,
) -> DungeonRunResult:
    """Executa uma tentativa completa na masmorra de 100 salas seguindo a política informada.

    A política decide com base no estado atual do guerreiro e do mercado,
    sem acesso às informações das próximas salas.
    """
    rng = random.Random(seed + 10007)
    warrior = create_initial_warrior(balance_cfg)

    w_attr_weights: tuple[float, float, float] = tuple(
        policy_params.get("warrior_attr_weights", (0.40, 0.35, 0.25))
    )  # type: ignore[assignment]
    ally_attr_weights: tuple[float, float, float] = tuple(
        policy_params.get("ally_attr_weights", (0.45, 0.35, 0.20))
    )  # type: ignore[assignment]

    rooms_cleared = 0
    total_turns = 0
    hired_history: list[str] = []
    room_results: list[RoomCombatResult] = []
    failure_room: int | None = None
    failure_reason: str | None = None

    ally_pts_per_lvl = int(balance_cfg["allies"].get("attribute_points_per_level", 3))
    classes_cfg = balance_cfg["allies"]["classes"]
    base_heal_frac = float(balance_cfg["warrior"].get("post_room_heal_fraction", 0.34))

    for template_room in rooms_template:
        room = template_room.clone_for_simulation()
        warrior.current_room = room.room_number

        # Decisões de mercado antes da luta.
        tx_before = execute_market_phase(
            warrior=warrior,
            policy_params=policy_params,
            balance_cfg=balance_cfg,
            enable_allies=enable_allies,
        )
        for tx in tx_before:
            if tx.get("action") == "hire_ally":
                hired_history.append(str(tx["ally_class"]))

        hp_start = warrior.current_hp
        victory, turns_taken, reason, c_log = simulate_single_room_combat(
            warrior=warrior,
            room=room,
            balance_cfg=balance_cfg,
            rng=rng,
            record_log=record_detailed_logs,
        )
        total_turns += turns_taken

        if not victory:
            failure_room = room.room_number
            failure_reason = reason
            if record_detailed_logs:
                room_results.append(
                    RoomCombatResult(
                        room_number=room.room_number,
                        victory=False,
                        turns_taken=turns_taken,
                        termination_reason=reason,
                        warrior_hp_start=hp_start,
                        warrior_hp_end=warrior.current_hp,
                        warrior_max_hp=warrior.max_hp,
                        warrior_level_end=warrior.level,
                        gold_earned=0,
                        xp_earned=0,
                        gold_end=warrior.gold,
                        active_allies_end=[a.name for a in warrior.allies if a.is_alive],
                        enemies_faced=[e.source_name for e in room.enemies],
                        enemy_source_indices=[e.source_index for e in room.enemies],
                        market_transactions=tx_before,
                        chest_event=None,
                        combat_log=c_log,
                        weapon_tier_end=warrior.weapon_tier,
                        armor_tier_end=warrior.armor_tier,
                        shield_tier_end=warrior.shield_tier,
                    )
                )
            break

        # Soma as recompensas pela vitória na sala.
        rooms_cleared += 1
        room_gold = sum(e.gold_reward for e in room.enemies)
        room_xp = sum(e.xp_reward for e in room.enemies)

        warrior.gold += room_gold
        warrior.gain_xp_and_evolve(room_xp, attr_weights=w_attr_weights, balance_cfg=balance_cfg)

        # Aliados vivos recebem experiência e evoluem
        ally_xp = int(round(room_xp * 0.75))
        warrior.allies = [a for a in warrior.allies if a.is_alive]
        for ally in warrior.allies:
            base_hp_cls = int(classes_cfg[ally.ally_class]["base_hp"])
            ally.gain_xp_and_evolve(
                xp_amount=ally_xp,
                ally_weights=ally_attr_weights,
                points_per_level=ally_pts_per_lvl,
                base_hp=base_hp_cls,
            )

        # Sorteia o baú após a vitória conforme a semente e a opção enable_chests.
        chest_ev = roll_post_victory_chest(
            warrior=warrior,
            room_number=room.room_number,
            rng=rng,
            balance_cfg=balance_cfg,
            enable_chests=enable_chests,
        )

        # Decisões de mercado após a luta.
        tx_after = execute_market_phase(
            warrior=warrior,
            policy_params=policy_params,
            balance_cfg=balance_cfg,
            enable_allies=enable_allies,
        )
        for tx in tx_after:
            if tx.get("action") == "hire_ally":
                hired_history.append(str(tx["ally_class"]))

        # Recuperação parcial entre salas
        priest_alive = any(a.ally_class == "priest" and a.is_alive for a in warrior.allies)
        heal_frac = base_heal_frac + (0.08 if priest_alive else 0.0)
        warrior.current_hp = min(
            warrior.max_hp,
            warrior.current_hp + int(round(warrior.max_hp * heal_frac)),
        )
        for ally in warrior.allies:
            if ally.is_alive:
                ally.current_hp = min(
                    ally.max_hp,
                    ally.current_hp + int(round(ally.max_hp * (heal_frac + 0.05))),
                )

        if record_detailed_logs:
            room_results.append(
                RoomCombatResult(
                    room_number=room.room_number,
                    victory=True,
                    turns_taken=turns_taken,
                    termination_reason=reason,
                    warrior_hp_start=hp_start,
                    warrior_hp_end=warrior.current_hp,
                    warrior_max_hp=warrior.max_hp,
                    warrior_level_end=warrior.level,
                    gold_earned=room_gold,
                    xp_earned=room_xp,
                    gold_end=warrior.gold,
                    active_allies_end=[f"{a.name} (Nv.{a.level})" for a in warrior.allies if a.is_alive],
                    enemies_faced=[e.source_name for e in room.enemies],
                    enemy_source_indices=[e.source_index for e in room.enemies],
                    market_transactions=tx_before + tx_after,
                    chest_event=chest_ev,
                    combat_log=c_log,
                    weapon_tier_end=warrior.weapon_tier,
                    armor_tier_end=warrior.armor_tier,
                    shield_tier_end=warrior.shield_tier,
                )
            )

    return DungeonRunResult(
        seed=seed,
        rooms_cleared=rooms_cleared,
        completed_all_100=(rooms_cleared == len(rooms_template)),
        final_warrior_level=warrior.level,
        final_warrior_hp=warrior.current_hp,
        final_warrior_max_hp=warrior.max_hp,
        final_gold=warrior.gold,
        final_strength=warrior.strength,
        final_vitality=warrior.vitality,
        final_defense=warrior.defense,
        final_weapon_tier=warrior.weapon_tier,
        final_armor_tier=warrior.armor_tier,
        final_shield_tier=warrior.shield_tier,
        hired_allies_history=hired_history,
        active_allies_final=[a.ally_class for a in warrior.allies if a.is_alive],
        total_turns_fought=total_turns,
        failure_room=failure_room,
        failure_reason=failure_reason,
        room_results=room_results,
    )
