"""Sistema de Mercado, Economia, Contratações e Baús Controlados por Semente.

Regras (Seção 8):
- Quatro níveis de armas (Tier 1 inicial a Tier 4).
- Quatro níveis de armaduras compráveis (Tier 0 inicial sem armadura; Tiers 1 a 4 compráveis).
- Três níveis de escudos compráveis (Tier 0 inicial sem escudo; Tiers 1 a 3 compráveis).
- Venda do item substituído por 40% do preço-base (`sell_price_ratio = 0.40`).
- Proibido saldo negativo (`gold >= 0`) ou compras impossíveis.
- Baús pós-vitória controlados por semente e desligáveis (`enable_chests=False`) nos experimentos.
"""

from __future__ import annotations

import random
from typing import Any

from src.game.characters import ALLY_CLASSES_ORDER, Warrior, create_ally


def compute_resale_value(base_cost: int, sell_ratio: float = 0.40) -> int:
    """Retorna o valor de venda (40% do preço-base)."""
    if base_cost <= 0:
        return 0
    return int(round(base_cost * sell_ratio))


def get_next_tier_item(
    catalog_list: list[dict[str, Any]],
    current_tier: int,
) -> dict[str, Any] | None:
    """Busca o próximo nível de equipamento imediatamente superior ao atual."""
    for item in catalog_list:
        if int(item["tier"]) == current_tier + 1:
            return item
    return None


def try_purchase_equipment_upgrade(
    warrior: Warrior,
    category: str,  # "weapon", "armor", "shield"
    balance_cfg: dict[str, Any],
    min_gold_reserve: int = 0,
    buy_threshold_multiplier: float = 1.0,
) -> dict[str, Any] | None:
    """Avalia o catálogo da categoria e decide se compra um nível superior agora ou economiza.

    Todos os níveis superiores ao atual estão disponíveis no catálogo conforme o dinheiro existente.
    Como a venda do item substituído retorna apenas 40% do preço-base, trocar de item repetidas
    vezes gera perda de 60% do capital investido; por outro lado, economizar demais deixa o
    guerreiro vulnerável. O gene `buy_threshold_multiplier` e `min_gold_reserve` governam essa decisão.
    """
    econ = balance_cfg["economy"]
    sell_ratio = float(econ.get("sell_price_ratio", 0.40))

    if category == "weapon":
        catalog = econ["weapons"]
        curr_tier = warrior.weapon_tier
        curr_item = warrior.get_weapon_data(balance_cfg)
    elif category == "armor":
        catalog = econ["armors"]
        curr_tier = warrior.armor_tier
        curr_item = warrior.get_armor_data(balance_cfg)
    elif category == "shield":
        catalog = econ["shields"]
        curr_tier = warrior.shield_tier
        curr_item = warrior.get_shield_data(balance_cfg)
    else:
        raise ValueError(f"Categoria de equipamento inválida: {category}")

    higher_items = [item for item in catalog if int(item["tier"]) > curr_tier]
    if not higher_items:
        return None

    resale_val = compute_resale_value(int(curr_item.get("cost", 0)), sell_ratio)
    spendable_gold = warrior.gold - max(0, min_gold_reserve)
    if spendable_gold <= 0:
        return None

    # Se o limiar de compra é alto (> 1.32) e existe um tier 2 níveis acima cujo custo já está > 60% coberto,
    # a estratégia opta por economizar para pular o tier intermediário e evitar a perda de 60% na revenda.
    if buy_threshold_multiplier >= 1.32 and len(higher_items) >= 2:
        skip_target = higher_items[1]
        skip_net_cost = max(0, int(skip_target["cost"]) - resale_val)
        if spendable_gold >= int(skip_net_cost * 0.58) and spendable_gold < skip_net_cost:
            return None

    # Seleciona o maior tier superior que cabe no orçamento respeitando o multiplicador de limiar
    chosen_item: dict[str, Any] | None = None
    for candidate in sorted(higher_items, key=lambda x: int(x["tier"]), reverse=True):
        net_c = max(0, int(candidate["cost"]) - resale_val)
        req_gold = int(round(net_c * max(1.0, buy_threshold_multiplier))) + max(0, min_gold_reserve)
        if warrior.gold >= net_c and warrior.gold >= req_gold:
            chosen_item = candidate
            break

    if chosen_item is None:
        return None

    base_cost = int(chosen_item["cost"])
    net_cost = max(0, base_cost - resale_val)
    warrior.gold -= net_cost
    if warrior.gold < 0:
        raise RuntimeError("Violação de invariante econômico: saldo negativo detectado.")

    if category == "weapon":
        warrior.weapon_tier = int(chosen_item["tier"])
    elif category == "armor":
        warrior.armor_tier = int(chosen_item["tier"])
    elif category == "shield":
        warrior.shield_tier = int(chosen_item["tier"])

    warrior.recalc_derived_stats(balance_cfg)
    return {
        "action": "buy_equipment",
        "category": category,
        "item_name": chosen_item["name"],
        "new_tier": int(chosen_item["tier"]),
        "base_cost": base_cost,
        "resale_credit": resale_val,
        "net_cost": net_cost,
        "gold_after": warrior.gold,
    }


def try_hire_ally_by_priority(
    warrior: Warrior,
    ally_priority_scores: dict[str, float],
    balance_cfg: dict[str, Any],
    min_gold_reserve: int = 0,
    hire_threshold_multiplier: float = 1.0,
) -> dict[str, Any] | None:
    """Avalia a contratação de aliado conforme a ordem de prioridade genética e recursos disponíveis."""
    max_slots = warrior.unlocked_ally_slots(balance_cfg)
    active_allies = [a for a in warrior.allies if a.is_alive]
    if len(active_allies) >= max_slots:
        return None

    # Limpa aliados mortos da lista ativa caso o slot precise ser ocupado por uma nova classe
    warrior.allies = active_allies
    existing_classes = {a.ally_class for a in warrior.allies}

    ordered_classes = sorted(
        ALLY_CLASSES_ORDER,
        key=lambda c: (-float(ally_priority_scores.get(c, 0.0)), c),
    )

    classes_cfg = balance_cfg["allies"]["classes"]
    for candidate_cls in ordered_classes:
        if candidate_cls in existing_classes:
            continue
        cost = int(classes_cfg[candidate_cls]["hire_cost"])
        required_gold = int(round(cost * max(1.0, hire_threshold_multiplier))) + max(0, min_gold_reserve)
        if warrior.gold >= cost and warrior.gold >= required_gold:
            warrior.gold -= cost
            initial_ally_lvl = max(1, warrior.level - 2)
            new_ally = create_ally(candidate_cls, balance_cfg=balance_cfg, initial_level=initial_ally_lvl)
            warrior.allies.append(new_ally)
            return {
                "action": "hire_ally",
                "ally_class": candidate_cls,
                "ally_name": new_ally.name,
                "cost": cost,
                "ally_initial_level": new_ally.level,
                "gold_after": warrior.gold,
            }
    return None


def execute_market_phase(
    warrior: Warrior,
    policy_params: dict[str, Any],
    balance_cfg: dict[str, Any],
    enable_allies: bool = True,
) -> list[dict[str, Any]]:
    """Executa decisões de mercado (contratação de aliados e compra de equipamentos) guiadas pela política."""
    transactions: list[dict[str, Any]] = []
    min_reserve = int(round(float(policy_params.get("min_gold_reserve", 15.0))))
    buy_thresh = float(policy_params.get("equipment_buy_threshold", 1.05))
    hire_thresh = float(policy_params.get("ally_hire_threshold", 1.05))
    equip_offense_pref = float(policy_params.get("equip_offense_priority", 0.5))
    ally_first_pref = float(policy_params.get("hire_before_equip_priority", 0.6))
    ally_priorities: dict[str, float] = policy_params.get(
        "ally_priorities",
        {c: 0.5 for c in ALLY_CLASSES_ORDER},
    )

    if equip_offense_pref >= 0.55:
        equip_order = ["weapon", "armor", "shield"]
    elif equip_offense_pref <= 0.40:
        equip_order = ["armor", "shield", "weapon"]
    else:
        equip_order = ["weapon", "armor", "shield"]

    def _attempt_allies() -> None:
        if not enable_allies:
            return
        for _ in range(2):
            tx = try_hire_ally_by_priority(
                warrior=warrior,
                ally_priority_scores=ally_priorities,
                balance_cfg=balance_cfg,
                min_gold_reserve=min_reserve,
                hire_threshold_multiplier=hire_thresh,
            )
            if tx:
                transactions.append(tx)
            else:
                break

    def _attempt_equipment() -> None:
        for cat in equip_order:
            tx = try_purchase_equipment_upgrade(
                warrior=warrior,
                category=cat,
                balance_cfg=balance_cfg,
                min_gold_reserve=min_reserve,
                buy_threshold_multiplier=buy_thresh,
            )
            if tx:
                transactions.append(tx)

    if ally_first_pref >= 0.5:
        _attempt_allies()
        _attempt_equipment()
    else:
        _attempt_equipment()
        _attempt_allies()

    return transactions


def roll_post_victory_chest(
    warrior: Warrior,
    room_number: int,
    rng: random.Random,
    balance_cfg: dict[str, Any],
    enable_chests: bool = True,
) -> dict[str, Any] | None:
    """Sorteia baú pós-vitória controlado por semente; pode ser desligado nos experimentos."""
    if not enable_chests:
        return None

    econ = balance_cfg["economy"]
    drop_chance = float(econ.get("chest_drop_chance", 0.12))
    if rng.random() >= drop_chance:
        return None

    sell_ratio = float(econ.get("sell_price_ratio", 0.40))
    cat = rng.choice(["weapon", "armor", "shield"])

    # Escolhe tier compatível com a profundidade da sala
    if room_number <= 25:
        max_drop_tier = 2
    elif room_number <= 60:
        max_drop_tier = 3
    else:
        max_drop_tier = 4

    if cat == "weapon":
        catalog = [w for w in econ["weapons"] if 2 <= int(w["tier"]) <= max_drop_tier]
        curr_tier = warrior.weapon_tier
        curr_item = warrior.get_weapon_data(balance_cfg)
    elif cat == "armor":
        catalog = [a for a in econ["armors"] if 1 <= int(a["tier"]) <= max_drop_tier]
        curr_tier = warrior.armor_tier
        curr_item = warrior.get_armor_data(balance_cfg)
    else:
        catalog = [s for s in econ["shields"] if 1 <= int(s["tier"]) <= min(3, max_drop_tier)]
        curr_tier = warrior.shield_tier
        curr_item = warrior.get_shield_data(balance_cfg)

    if not catalog:
        return None

    dropped_item = rng.choice(catalog)
    dropped_tier = int(dropped_item["tier"])
    dropped_cost = int(dropped_item["cost"])

    if dropped_tier > curr_tier:
        resale_old = compute_resale_value(int(curr_item.get("cost", 0)), sell_ratio)
        warrior.gold += resale_old
        if cat == "weapon":
            warrior.weapon_tier = dropped_tier
        elif cat == "armor":
            warrior.armor_tier = dropped_tier
        else:
            warrior.shield_tier = dropped_tier
        warrior.recalc_derived_stats(balance_cfg)
        return {
            "event": "chest_equip",
            "category": cat,
            "item_name": dropped_item["name"],
            "tier": dropped_tier,
            "gold_gained_from_old_item": resale_old,
        }

    # Item repetido ou inferior: vendido automaticamente por 40% do valor-base
    resale_dup = compute_resale_value(dropped_cost, sell_ratio)
    warrior.gold += resale_dup
    return {
        "event": "chest_sell_duplicate",
        "category": cat,
        "item_name": dropped_item["name"],
        "tier": dropped_tier,
        "gold_gained": resale_dup,
    }
