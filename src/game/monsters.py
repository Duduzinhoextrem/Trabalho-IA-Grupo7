"""Adaptação dos registros D&D 5e SRD para o simulador.

Cada monstro simulado mantém a referência ao registro original:
- `source_index` (ID na API D&D 5e SRD)
- `source_name` (nome original)
- `source_url` (URL do endereço oficial na API)
- `is_simulated_instance = True`

Fórmulas documentadas em `config/balance.json`:
1. Vida (`max_hp`): combina `hit_points` real do SRD, bônus de `constitution` e fator moderado da sala.
2. Ataque (`attack_skill`): derivado de `max_attack_bonus` e maior modificador ofensivo (STR/DEX/INT).
3. Defesa (`defense`): derivada de `(armor_class - 10) * k_ac + mod(CON) * k_con + CR * k_cr`
   (compensa a precisão limitada pelas regras, observada na descoberta 2 da EDA).
4. Dano físico (`physical_damage`) e Dano mágico (`magical_damage`): derivados de
   `best_action_physical_damage`, `best_action_magical_damage`, `multiattack_count` e atributos.
5. Resistências (`phys_resistance`, `mag_resistance`): derivadas das listas reais de resistências,
   imunidades e vulnerabilidades do SRD, limitadas a `max_resistance_cap` (55%) para impedir invulnerabilidade.
6. Experiência (`xp_reward`) e Ouro (`gold_reward`): funções sublineares calibradas sobre `xp` e `challenge_rating`.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
from typing import Any

import pandas as pd

PASSIVE_EXCLUDED_INDICES = {"frog", "sea-horse", "shrieker", "vampire-mist"}


@dataclass
class MonsterCombatInstance:
    """Monstro simulado a partir de um registro D&D 5e SRD."""

    instance_id: str
    source_index: str
    source_name: str
    source_url: str
    creature_type: str
    size: str
    challenge_rating: float
    srd_xp: int
    room_number: int
    position: str  # Linha de frente ("frontline") ou retaguarda ("backline").
    max_hp: int
    current_hp: int
    attack_skill: int
    defense: float
    initiative: int
    physical_damage: float
    magical_damage: float
    phys_resistance: float
    mag_resistance: float
    xp_reward: int
    gold_reward: int
    debuff_stacks: int = 0
    debuff_turns_left: int = 0
    is_simulated_instance: bool = True

    @property
    def is_alive(self) -> bool:
        return self.current_hp > 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_balance_config(config_path: Path = Path("config/balance.json")) -> dict[str, Any]:
    """Carrega o arquivo versionado de parâmetros de balanceamento e transformação."""
    return json.loads(config_path.read_text(encoding="utf-8"))


def filter_combat_eligible_monsters(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna os monstros elegíveis para encontros ativos (exclui as 4 formas passivas documentadas na EDA)."""
    mask = ~df["index"].isin(PASSIVE_EXCLUDED_INDICES)
    return df[mask].copy().reset_index(drop=True)


def adapt_srd_row_to_monster_instance(
    row: pd.Series | dict[str, Any],
    room_number: int,
    instance_seq: int,
    balance_cfg: dict[str, Any],
    difficulty_multiplier: float = 1.0,
) -> MonsterCombatInstance:
    """Transforma um registro tratado do SRD em uma instância de combate para a sala `room_number`."""
    m_cfg = balance_cfg["monster_adaptation"]

    idx = str(row["index"])
    name = str(row["name"])
    url = str(row["source_url"])
    ctype = str(row["type"])
    size = str(row["size"])
    cr = float(row["challenge_rating"])
    srd_xp = int(row["xp"])

    raw_hp = float(row["hit_points"])
    raw_ac = float(row["armor_class"])
    strength = int(row["strength"])
    dexterity = int(row["dexterity"])
    constitution = int(row["constitution"])
    intelligence = int(row["intelligence"])
    wisdom = int(row["wisdom"])
    charisma = int(row["charisma"])

    str_mod = (strength - 10) / 2.0
    dex_mod = (dexterity - 10) / 2.0
    con_mod = (constitution - 10) / 2.0
    mental_mod = max(intelligence, wisdom, charisma) / 2.0 - 5.0

    # 1. Vida (HP).
    room_hp_mult = 1.0 + m_cfg["room_hp_progression_rate"] * (room_number - 1)
    base_hp = m_cfg["hp_base_offset"] + raw_hp * m_cfg["hp_scale_factor"] + max(0.0, con_mod * 2.0)
    max_hp = max(12, int(round(base_hp * room_hp_mult * difficulty_multiplier)))

    # 2. Defesa.
    ac_delta = max(-3.0, raw_ac - m_cfg["defense_ac_baseline"])
    defense = max(
        2.0,
        round(
            (
                8.0
                + ac_delta * m_cfg["defense_per_ac_point"]
                + max(0.0, con_mod) * m_cfg["defense_per_con_mod"]
                + cr * m_cfg["defense_per_cr"]
            )
            * difficulty_multiplier,
            2,
        ),
    )

    # 3. Ataque e iniciativa.
    max_atk_bonus = int(row.get("max_attack_bonus", 3))
    attack_skill = max(1, int(round(max_atk_bonus + cr * 0.35 + room_number * 0.08)))
    initiative = max(1, int(round(10 + dex_mod + cr * 0.15)))

    # 4. Dano físico e mágico.
    raw_phys = float(row.get("best_action_physical_damage", 0.0))
    raw_mag = float(row.get("best_action_magical_damage", 0.0))
    multi = min(3, max(1, int(row.get("multiattack_count", 1))))
    multi_factor = 1.0 + 0.28 * (multi - 1)

    # Ajusta conjuradores (mage, archmage) e ataques especiais (rug-of-smothering).
    if raw_phys + raw_mag <= 0.5:
        if mental_mod > str_mod:
            raw_mag = max(6.0, cr * 4.5 + mental_mod * 2.0)
        else:
            raw_phys = max(5.0, cr * 4.0 + max(1.0, str_mod) * 2.0)

    room_dmg_mult = (1.0 + m_cfg["room_damage_progression_rate"] * (room_number - 1)) * difficulty_multiplier

    phys_dmg = 0.0
    mag_dmg = 0.0
    if raw_phys > 0:
        phys_dmg = round(
            (3.0 + raw_phys * m_cfg["damage_scale_factor"] * multi_factor + max(0.0, str_mod * 0.8))
            * room_dmg_mult,
            2,
        )
    if raw_mag > 0:
        mag_dmg = round(
            (3.0 + raw_mag * m_cfg["damage_scale_factor"] * multi_factor + max(0.0, mental_mod * 0.8))
            * room_dmg_mult,
            2,
        )

    # 5. Resistências limitadas a 55% para impedir invulnerabilidade.
    cap = float(m_cfg["max_resistance_cap"])
    has_phys_res = bool(row.get("has_physical_resistance", False))
    has_mag_res = bool(row.get("has_magical_resistance", False))
    res_cnt = int(row.get("resistances_count", 0))
    imm_cnt = int(row.get("immunities_count", 0))
    vuln_cnt = int(row.get("vulnerabilities_count", 0))

    phys_res = 0.0
    if has_phys_res:
        phys_res = min(cap, 0.22 + 0.04 * min(4, res_cnt + imm_cnt))
    if vuln_cnt > 0 and not has_phys_res:
        phys_res = max(-0.25, phys_res - 0.15)

    mag_res = 0.0
    if has_mag_res:
        mag_res = min(cap, 0.20 + 0.04 * min(5, res_cnt + imm_cnt))
    if vuln_cnt > 0 and not has_mag_res:
        mag_res = max(-0.25, mag_res - 0.15)

    # 6. Posição na linha de frente ou na retaguarda.
    position = "backline" if (mag_dmg > phys_dmg and size in ("Tiny", "Small", "Medium")) else "frontline"

    # 7. Experiência e recompensa em ouro.
    xp_reward = max(
        12,
        int(
            round(
                m_cfg["xp_base"]
                + (cr ** m_cfg["xp_cr_power"]) * 6.5
                + math.log1p(max(1, srd_xp)) * m_cfg["xp_srd_log_weight"]
            )
        ),
    )
    gold_reward = max(
        6,
        int(
            round(
                m_cfg["gold_base"]
                + cr * m_cfg["gold_per_cr"]
                + room_number * m_cfg["gold_per_room"]
            )
        ),
    )

    instance_id = f"room_{room_number:03d}_{idx}_{instance_seq}"
    return MonsterCombatInstance(
        instance_id=instance_id,
        source_index=idx,
        source_name=name,
        source_url=url,
        creature_type=ctype,
        size=size,
        challenge_rating=cr,
        srd_xp=srd_xp,
        room_number=room_number,
        position=position,
        max_hp=max_hp,
        current_hp=max_hp,
        attack_skill=attack_skill,
        defense=defense,
        initiative=initiative,
        physical_damage=phys_dmg,
        magical_damage=mag_dmg,
        phys_resistance=round(phys_res, 3),
        mag_resistance=round(mag_res, 3),
        xp_reward=xp_reward,
        gold_reward=gold_reward,
    )
