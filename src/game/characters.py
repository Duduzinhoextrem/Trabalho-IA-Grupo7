"""Guerreiro principal e aliados das 5 classes contratáveis.

Regras das Seções 5 e 6:
- O guerreiro começa no nível 1, sala 1, com espada básica (categoria 1), sem aliados, armadura ou escudo (categoria 0).
- Evolução por XP com distribuição irreversível de pontos em Força, Vitalidade e Defesa.
- Cinco classes de aliados: Mago (`mage`), Arqueiro (`archer`), Monge (`monk`), Padre (`priest`), Alquimista (`alchemist`).
- A primeira vaga de aliado abre no nível 5 e a segunda no nível 15; são permitidos até 2 aliados, de classes diferentes.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

ALLY_CLASSES_ORDER = ("mage", "archer", "monk", "priest", "alchemist")


def distribute_points_by_weights(
    total_points: int,
    weights: tuple[float, float, float],
) -> tuple[int, int, int]:
    """Distribui `total_points` inteiros entre 3 atributos proporcionalmente aos pesos contínuos.

    A soma é igual a `total_points`, os valores são >= 0 e os pontos não são reembolsados.
    """
    if total_points <= 0:
        return 0, 0, 0
    w0 = max(0.0, float(weights[0]))
    w1 = max(0.0, float(weights[1]))
    w2 = max(0.0, float(weights[2]))
    w_sum = w0 + w1 + w2
    if w_sum <= 1e-9:
        w0, w1, w2, w_sum = 1.0, 1.0, 1.0, 3.0

    raw = [total_points * (w0 / w_sum), total_points * (w1 / w_sum), total_points * (w2 / w_sum)]
    floored = [int(x) for x in raw]
    remainder = total_points - sum(floored)
    fractions = sorted(
        [(raw[i] - floored[i], i) for i in range(3)],
        key=lambda item: (-item[0], item[1]),
    )
    for k in range(remainder):
        floored[fractions[k][1]] += 1
    return floored[0], floored[1], floored[2]


@dataclass
class Ally:
    """Representa um aliado contratado com progressão própria de nível e atributos."""

    ally_class: str  # Mago ("mage"), arqueiro ("archer"), monge ("monk"), padre ("priest") ou alquimista ("alchemist").
    name: str
    role: str
    position: str  # Linha de frente ("frontline") ou retaguarda ("backline").
    level: int = 1
    xp: int = 0
    power: int = 10
    vitality: int = 8
    defense: int = 6
    max_hp: int = 50
    current_hp: int = 50
    initiative: int = 12
    dmg_per_power: float = 1.5
    heals_remaining: int = 0
    max_heals_per_combat: int = 0
    heal_base: int = 0
    heal_per_power: float = 0.0
    buff_duration_turns: int = 0
    max_buff_stacks: int = 0
    atk_buff_per_stack: float = 0.0
    def_debuff_per_stack: float = 0.0
    total_points_allocated: int = 0

    @property
    def is_alive(self) -> bool:
        return self.current_hp > 0

    def xp_for_next_level(self, base_xp: int = 40, growth: float = 1.15) -> int:
        return int(round(base_xp * (growth ** (self.level - 1))))

    def recalc_stats(self, base_hp: int) -> None:
        old_max = self.max_hp
        self.max_hp = int(round(base_hp + (self.vitality - 7) * 8.5 + (self.level - 1) * 6.0))
        hp_gain = max(0, self.max_hp - old_max)
        if self.current_hp > 0:
            self.current_hp = min(self.max_hp, self.current_hp + hp_gain)

    def gain_xp_and_evolve(
        self,
        xp_amount: int,
        ally_weights: tuple[float, float, float],
        points_per_level: int,
        base_hp: int,
    ) -> int:
        """Adiciona XP ao aliado e distribui os pontos de atributo ao subir de nível, sem reembolso."""
        if xp_amount <= 0 or not self.is_alive:
            return 0
        self.xp += xp_amount
        levels_gained = 0
        while self.xp >= self.xp_for_next_level():
            self.xp -= self.xp_for_next_level()
            self.level += 1
            levels_gained += 1
            dp, dv, dd = distribute_points_by_weights(points_per_level, ally_weights)
            self.power += dp
            self.vitality += dv
            self.defense += dd
            self.total_points_allocated += dp + dv + dd
        if levels_gained > 0:
            self.recalc_stats(base_hp=base_hp)
        return levels_gained

    def compute_raw_damage(self, buff_multiplier: float = 1.0) -> float:
        return round((6.0 + self.power * self.dmg_per_power + self.level * 1.3) * buff_multiplier, 2)

    def compute_heal_amount(self) -> int:
        return int(round(self.heal_base + self.power * self.heal_per_power + self.level * 1.8))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def create_ally(ally_class: str, balance_cfg: dict[str, Any], initial_level: int = 1) -> Ally:
    """Cria um aliado de uma das 5 classes permitidas."""
    classes_cfg = balance_cfg["allies"]["classes"]
    if ally_class not in classes_cfg:
        raise ValueError(f"Classe de aliado desconhecida: {ally_class}")
    c = classes_cfg[ally_class]
    base_hp = int(c["base_hp"])
    ally = Ally(
        ally_class=ally_class,
        name=str(c["name"]),
        role=str(c["role"]),
        position=str(c["position"]),
        level=1,
        xp=0,
        power=int(c["base_power"]),
        vitality=int(c["base_vitality"]),
        defense=int(c["base_defense"]),
        max_hp=base_hp,
        current_hp=base_hp,
        initiative=int(c["initiative"]),
        dmg_per_power=float(c["dmg_per_power"]),
        heals_remaining=int(c.get("max_heals_per_combat", 0)),
        max_heals_per_combat=int(c.get("max_heals_per_combat", 0)),
        heal_base=int(c.get("heal_base", 0)),
        heal_per_power=float(c.get("heal_per_power", 0.0)),
        buff_duration_turns=int(c.get("buff_duration_turns", 0)),
        max_buff_stacks=int(c.get("max_buff_stacks", 0)),
        atk_buff_per_stack=float(c.get("atk_buff_per_stack", 0.0)),
        def_debuff_per_stack=float(c.get("def_debuff_per_stack", 0.0)),
    )
    # O aliado começa em um nível proporcional ao do guerreiro na contratação.
    if initial_level > 1:
        pts_per_lvl = int(balance_cfg["allies"].get("attribute_points_per_level", 3))
        for _ in range(initial_level - 1):
            ally.level += 1
            ally.power += 1
            ally.vitality += 1
            ally.defense += max(0, pts_per_lvl - 2)
            ally.total_points_allocated += pts_per_lvl
        ally.recalc_stats(base_hp=base_hp)
        ally.current_hp = ally.max_hp
    return ally


@dataclass
class Warrior:
    """Guerreiro controlado pela estratégia na Masmorra Genética."""

    level: int = 1
    current_room: int = 1
    xp: int = 0
    gold: int = 25
    strength: int = 10
    vitality: int = 10
    defense: int = 8
    max_hp: int = 75
    current_hp: int = 75
    weapon_tier: int = 1  # Começa com espada básica (categoria 1).
    armor_tier: int = 0   # Começa sem armadura (categoria 0).
    shield_tier: int = 0  # Começa sem escudo (categoria 0).
    allies: list[Ally] = field(default_factory=list)
    total_points_allocated: int = 0
    buff_stacks: int = 0
    buff_turns_left: int = 0

    @property
    def is_alive(self) -> bool:
        return self.current_hp > 0

    def xp_for_next_level(self, balance_cfg: dict[str, Any]) -> int:
        w_cfg = balance_cfg["warrior"]
        base_xp = float(w_cfg["base_xp_to_level"])
        growth = float(w_cfg["xp_level_growth_factor"])
        return int(round(base_xp * (growth ** (self.level - 1))))

    def get_weapon_data(self, balance_cfg: dict[str, Any]) -> dict[str, Any]:
        for w in balance_cfg["economy"]["weapons"]:
            if int(w["tier"]) == self.weapon_tier:
                return w
        return balance_cfg["economy"]["weapons"][0]

    def get_armor_data(self, balance_cfg: dict[str, Any]) -> dict[str, Any]:
        for a in balance_cfg["economy"]["armors"]:
            if int(a["tier"]) == self.armor_tier:
                return a
        return balance_cfg["economy"]["armors"][0]

    def get_shield_data(self, balance_cfg: dict[str, Any]) -> dict[str, Any]:
        for s in balance_cfg["economy"]["shields"]:
            if int(s["tier"]) == self.shield_tier:
                return s
        return balance_cfg["economy"]["shields"][0]

    def recalc_derived_stats(self, balance_cfg: dict[str, Any]) -> None:
        w_cfg = balance_cfg["warrior"]
        armor = self.get_armor_data(balance_cfg)
        old_max = self.max_hp
        base_hp = int(w_cfg["initial_hp"])
        vit_bonus = (self.vitality - int(w_cfg["initial_vitality"])) * int(w_cfg["hp_per_vitality_point"])
        lvl_bonus = (self.level - 1) * int(w_cfg["hp_per_level"])
        armor_hp = int(armor.get("hp_bonus", 0))
        self.max_hp = max(30, base_hp + vit_bonus + lvl_bonus + armor_hp)
        hp_diff = max(0, self.max_hp - old_max)
        if self.current_hp > 0:
            self.current_hp = min(self.max_hp, self.current_hp + hp_diff)

    def compute_physical_damage(self, balance_cfg: dict[str, Any], buff_multiplier: float = 1.0) -> float:
        w_cfg = balance_cfg["warrior"]
        weapon = self.get_weapon_data(balance_cfg)
        base_dmg = (
            6.0
            + self.strength * float(w_cfg["phys_dmg_per_strength_point"])
            + float(weapon["phys_damage_bonus"])
            + self.level * 1.1
        )
        return round(base_dmg * buff_multiplier, 2)

    def compute_total_defense(self, balance_cfg: dict[str, Any]) -> float:
        w_cfg = balance_cfg["warrior"]
        armor = self.get_armor_data(balance_cfg)
        shield = self.get_shield_data(balance_cfg)
        return round(
            self.defense * float(w_cfg["defense_per_defense_point"])
            + float(armor["defense_bonus"])
            + float(shield["defense_bonus"]),
            2,
        )

    def compute_block_mitigation(self, balance_cfg: dict[str, Any]) -> float:
        shield = self.get_shield_data(balance_cfg)
        return float(shield.get("block_mitigation", 0.0))

    def gain_xp_and_evolve(
        self,
        xp_amount: int,
        attr_weights: tuple[float, float, float],
        balance_cfg: dict[str, Any],
    ) -> int:
        """Adiciona XP ao guerreiro e distribui os pontos ao subir de nível, sem reembolso."""
        if xp_amount <= 0 or not self.is_alive:
            return 0
        self.xp += xp_amount
        pts_per_level = int(balance_cfg["warrior"]["attribute_points_per_level"])
        levels_gained = 0
        while self.xp >= self.xp_for_next_level(balance_cfg):
            self.xp -= self.xp_for_next_level(balance_cfg)
            self.level += 1
            levels_gained += 1
            ds, dv, dd = distribute_points_by_weights(pts_per_level, attr_weights)
            self.strength += ds
            self.vitality += dv
            self.defense += dd
            self.total_points_allocated += ds + dv + dd
        if levels_gained > 0:
            self.recalc_derived_stats(balance_cfg)
        return levels_gained

    def unlocked_ally_slots(self, balance_cfg: dict[str, Any]) -> int:
        a_cfg = balance_cfg["allies"]
        if self.level >= int(a_cfg["slot_2_unlock_level"]):
            return 2
        if self.level >= int(a_cfg["slot_1_unlock_level"]):
            return 1
        return 0

    def can_hire_ally(self, ally_class: str, balance_cfg: dict[str, Any]) -> bool:
        """Verifica se o guerreiro pode contratar o aliado."""
        max_slots = self.unlocked_ally_slots(balance_cfg)
        active_allies = [a for a in self.allies if a.is_alive]
        if len(active_allies) >= max_slots:
            return False
        if any(a.ally_class == ally_class and a.is_alive for a in self.allies):
            return False  # Não permite dois aliados da mesma classe.
        classes_cfg = balance_cfg["allies"]["classes"]
        if ally_class not in classes_cfg:
            return False
        cost = int(classes_cfg[ally_class]["hire_cost"])
        return self.gold >= cost


def create_initial_warrior(balance_cfg: dict[str, Any]) -> Warrior:
    """Cria o guerreiro com as condições iniciais da Seção 5."""
    w_cfg = balance_cfg["warrior"]
    w = Warrior(
        level=int(w_cfg["initial_level"]),
        current_room=1,
        xp=0,
        gold=int(w_cfg["initial_gold"]),
        strength=int(w_cfg["initial_strength"]),
        vitality=int(w_cfg["initial_vitality"]),
        defense=int(w_cfg["initial_defense"]),
        max_hp=int(w_cfg["initial_hp"]),
        current_hp=int(w_cfg["initial_hp"]),
        weapon_tier=1,
        armor_tier=0,
        shield_tier=0,
        allies=[],
    )
    w.recalc_derived_stats(balance_cfg)
    w.current_hp = w.max_hp
    return w
