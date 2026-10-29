"""Pré-processamento e normalização explícita dos registros brutos da API D&D 5e SRD.

Separa rigorosamente:
1. Colunas extraídas/normalizadas diretamente do registro externo (SRD 2014).
2. Métricas auxiliares de parsing de dados de ataque (média matemática de dados XdY+Z).
Exporta os dados tratados em CSV e Parquet (`data/processed/`).
"""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any

import pandas as pd

from src.dataset.validation import extract_armor_class_value

PHYSICAL_DAMAGE_TYPES = {"bludgeoning", "piercing", "slashing"}
MAGICAL_ELEMENTAL_DAMAGE_TYPES = {
    "acid",
    "cold",
    "fire",
    "force",
    "lightning",
    "necrotic",
    "poison",
    "psychic",
    "radiant",
    "thunder",
}

# Tabela oficial SRD 5.1 de XP por Challenge Rating (usada apenas se xp vier nulo)
SRD_XP_BY_CR: dict[float, int] = {
    0.0: 10,
    0.125: 25,
    0.25: 50,
    0.5: 100,
    1.0: 200,
    2.0: 450,
    3.0: 700,
    4.0: 1100,
    5.0: 1800,
    6.0: 2300,
    7.0: 2900,
    8.0: 3900,
    9.0: 5000,
    10.0: 5900,
    11.0: 7200,
    12.0: 8400,
    13.0: 10000,
    14.0: 11500,
    15.0: 13000,
    16.0: 15000,
    17.0: 18000,
    18.0: 20000,
    19.0: 22000,
    20.0: 25000,
    21.0: 33000,
    22.0: 41000,
    23.0: 50000,
    24.0: 62000,
    30.0: 155000,
}

DICE_EXPR_PATTERN = re.compile(r"(\d+)\s*d\s*(\d+)(?:\s*([+-])\s*(\d+))?", re.IGNORECASE)
DESC_HIT_DAMAGE_PATTERN = re.compile(r"Hit:\s*(\d+)\s*\(([^)]+)\)\s*([a-zA-Z]+)?\s*damage", re.IGNORECASE)

DEFAULT_CSV_PATH = Path("data/processed/monsters_srd2014_processed.csv")
DEFAULT_PARQUET_PATH = Path("data/processed/monsters_srd2014_processed.parquet")


def parse_dice_average(dice_str: str | None) -> float:
    """Calcula o valor esperado matemático de uma expressão de dados (ex: '2d6+3' -> 10.0).

    Fórmula exata: para N dados de S faces com modificador M, E[X] = N * (S + 1) / 2 + M.
    Também suporta valores inteiros fixos (ex: '1' -> 1.0) ou somas de múltiplos dados.
    """
    if not dice_str or not isinstance(dice_str, str):
        return 0.0
    cleaned = dice_str.strip()
    if cleaned.isdigit():
        return float(int(cleaned))

    matches = list(DICE_EXPR_PATTERN.finditer(cleaned))
    if not matches:
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    total_expected = 0.0
    for match in matches:
        num_dice = int(match.group(1))
        num_sides = int(match.group(2))
        sign = match.group(3)
        modifier = int(match.group(4)) if match.group(4) else 0
        if sign == "-":
            modifier = -modifier
        total_expected += num_dice * ((num_sides + 1.0) / 2.0) + modifier

    return round(max(0.0, total_expected), 2)


def extract_action_damage_components(action: dict[str, Any]) -> tuple[float, float, list[str]]:
    """Extrai o dano esperado físico e mágico/elemental de uma ação de monstro."""
    phys_dmg = 0.0
    mag_dmg = 0.0
    dmg_types: list[str] = []

    damage_list = action.get("damage", [])
    if isinstance(damage_list, list) and len(damage_list) > 0:
        for dmg_item in damage_list:
            if not isinstance(dmg_item, dict):
                continue
            dice_str = dmg_item.get("damage_dice")
            # Algumas ações possuem escolha de dano (ex: armas versáteis em `from.options`)
            if not dice_str and isinstance(dmg_item.get("from"), dict):
                options = dmg_item["from"].get("options", [])
                if options and isinstance(options[0], dict):
                    dice_str = options[0].get("damage_dice")

            avg_val = parse_dice_average(str(dice_str)) if dice_str else 0.0
            dtype_obj = dmg_item.get("damage_type") or {}
            dtype_idx = str(dtype_obj.get("index", "")).lower().strip()
            if dtype_idx:
                dmg_types.append(dtype_idx)
            if dtype_idx in MAGICAL_ELEMENTAL_DAMAGE_TYPES:
                mag_dmg += avg_val
            else:
                phys_dmg += avg_val
    else:
        # Fallback: verifica se a descrição textual contém "Hit: X (NdM + K) <type> damage"
        desc = str(action.get("desc", ""))
        for match in DESC_HIT_DAMAGE_PATTERN.finditer(desc):
            avg_val = float(match.group(1))
            dtype_idx = str(match.group(3) or "physical").lower().strip()
            dmg_types.append(dtype_idx)
            if dtype_idx in MAGICAL_ELEMENTAL_DAMAGE_TYPES:
                mag_dmg += avg_val
            else:
                phys_dmg += avg_val

    return round(phys_dmg, 2), round(mag_dmg, 2), dmg_types


def estimate_multiattack_multiplier(actions: list[dict[str, Any]]) -> int:
    """Identifica o número de ataques em 'Multiattack' quando estruturado na API."""
    for act in actions:
        if not isinstance(act, dict):
            continue
        if str(act.get("name", "")).lower().startswith("multiattack"):
            sub_actions = act.get("actions", [])
            if isinstance(sub_actions, list) and len(sub_actions) > 0:
                total = 0
                for sub in sub_actions:
                    if isinstance(sub, dict):
                        cnt = sub.get("count", 1)
                        try:
                            total += int(cnt)
                        except (ValueError, TypeError):
                            total += 1
                if total > 0:
                    return min(total, 6)
            desc = str(act.get("desc", "")).lower()
            for word, num in (("two", 2), ("three", 3), ("four", 4), ("five", 5)):
                if f"makes {word}" in desc:
                    return num
    return 1


def normalize_monster_record(raw: dict[str, Any]) -> dict[str, Any]:
    """Transforma um registro JSON aninhado da API em um registro tabular plano e auditável."""
    idx = str(raw.get("index", "")).strip()
    name = str(raw.get("name", "")).strip()
    size = str(raw.get("size", "Medium")).strip()
    mtype = str(raw.get("type", "unknown")).strip().lower()
    subtype_raw = raw.get("subtype")
    subtype = str(subtype_raw).strip().lower() if subtype_raw else None
    alignment = str(raw.get("alignment", "unaligned")).strip().lower()

    ac_val, ac_type = extract_armor_class_value(raw.get("armor_class"))
    hp = int(raw.get("hit_points", 1))
    hit_dice = str(raw.get("hit_dice", "1d8")).strip()
    cr = float(raw.get("challenge_rating", 0.0))

    raw_xp = raw.get("xp")
    xp = int(raw_xp) if isinstance(raw_xp, (int, float)) and int(raw_xp) > 0 else SRD_XP_BY_CR.get(cr, 10)

    strength = int(raw.get("strength", 10))
    dexterity = int(raw.get("dexterity", 10))
    constitution = int(raw.get("constitution", 10))
    intelligence = int(raw.get("intelligence", 10))
    wisdom = int(raw.get("wisdom", 10))
    charisma = int(raw.get("charisma", 10))

    vulnerabilities = [str(v).lower() for v in (raw.get("damage_vulnerabilities") or [])]
    resistances = [str(r).lower() for r in (raw.get("damage_resistances") or [])]
    immunities = [str(i).lower() for i in (raw.get("damage_immunities") or [])]

    actions = raw.get("actions") or []
    if not isinstance(actions, list):
        actions = []

    multiattack_count = estimate_multiattack_multiplier(actions)

    attack_bonuses: list[int] = []
    action_names: list[str] = []
    best_single_total_dmg = 0.0
    best_single_phys_dmg = 0.0
    best_single_mag_dmg = 0.0
    all_phys_dmgs: list[float] = []
    all_mag_dmgs: list[float] = []
    damage_types_seen: list[str] = []

    for act in actions:
        if not isinstance(act, dict):
            continue
        act_name = str(act.get("name", "Action")).strip()
        action_names.append(act_name)

        atk_bonus = act.get("attack_bonus")
        if isinstance(atk_bonus, (int, float)):
            attack_bonuses.append(int(atk_bonus))

        phys_d, mag_d, dtypes = extract_action_damage_components(act)
        tot_d = phys_d + mag_d
        if tot_d > 0:
            all_phys_dmgs.append(phys_d)
            all_mag_dmgs.append(mag_d)
            damage_types_seen.extend(dtypes)
            if tot_d > best_single_total_dmg:
                best_single_total_dmg = tot_d
                best_single_phys_dmg = phys_d
                best_single_mag_dmg = mag_d

    max_attack_bonus = max(attack_bonuses) if attack_bonuses else max(0, (strength - 10) // 2 + 2)
    avg_action_damage = (
        round((sum(all_phys_dmgs) + sum(all_mag_dmgs)) / len(all_phys_dmgs), 2)
        if all_phys_dmgs
        else 0.0
    )

    # Verifica se o monstro possui resistências físicas ou mágicas/elementais
    has_phys_resistance = any(
        any(p in r for p in PHYSICAL_DAMAGE_TYPES) for r in (resistances + immunities)
    )
    has_mag_resistance = any(
        any(m in r for m in MAGICAL_ELEMENTAL_DAMAGE_TYPES) for r in (resistances + immunities)
    )

    rel_url = str(raw.get("url", f"/api/2014/monsters/{idx}"))
    source_url = raw.get(
        "_source_api_url",
        f"https://www.dnd5eapi.co{rel_url}" if rel_url.startswith("/") else rel_url,
    )

    return {
        "index": idx,
        "name": name,
        "size": size,
        "type": mtype,
        "subtype": subtype,
        "alignment": alignment,
        "hit_points": hp,
        "hit_dice": hit_dice,
        "armor_class": int(ac_val or 10),
        "armor_class_type": ac_type,
        "challenge_rating": cr,
        "xp": xp,
        "strength": strength,
        "dexterity": dexterity,
        "constitution": constitution,
        "intelligence": intelligence,
        "wisdom": wisdom,
        "charisma": charisma,
        "resistances_list": ";".join(resistances),
        "vulnerabilities_list": ";".join(vulnerabilities),
        "immunities_list": ";".join(immunities),
        "resistances_count": len(resistances),
        "vulnerabilities_count": len(vulnerabilities),
        "immunities_count": len(immunities),
        "has_physical_resistance": has_phys_resistance,
        "has_magical_resistance": has_mag_resistance,
        "actions_count": len(actions),
        "attack_actions_count": len(all_phys_dmgs),
        "action_names": ";".join(action_names),
        "max_attack_bonus": int(max_attack_bonus),
        "multiattack_count": int(multiattack_count),
        "best_action_damage": round(best_single_total_dmg, 2),
        "best_action_physical_damage": round(best_single_phys_dmg, 2),
        "best_action_magical_damage": round(best_single_mag_dmg, 2),
        "avg_action_damage": avg_action_damage,
        "estimated_dpr_raw": round(best_single_total_dmg * max(1, min(multiattack_count, 3)), 2),
        "primary_damage_types": ";".join(sorted(set(damage_types_seen))),
        "has_magical_attack": best_single_mag_dmg > 0,
        "special_abilities_count": len(raw.get("special_abilities") or []),
        "legendary_actions_count": len(raw.get("legendary_actions") or []),
        "source_url": str(source_url),
        "dataset_version": "srd-2014-v1.0.0",
    }


def preprocess_and_export_dataset(
    valid_raw_records: list[dict[str, Any]],
    csv_path: Path = DEFAULT_CSV_PATH,
    parquet_path: Path = DEFAULT_PARQUET_PATH,
) -> pd.DataFrame:
    """Normaliza todos os registros válidos e exporta para CSV e Parquet."""
    normalized_rows = [normalize_monster_record(rec) for rec in valid_raw_records]
    df = pd.DataFrame(normalized_rows)
    df = df.sort_values(by=["challenge_rating", "xp", "index"], ascending=[True, True, True]).reset_index(drop=True)

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    parquet_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(csv_path, index=False, encoding="utf-8")
    df.to_parquet(parquet_path, index=False)
    return df


def load_processed_dataset(
    parquet_path: Path = DEFAULT_PARQUET_PATH,
    csv_path: Path = DEFAULT_CSV_PATH,
) -> pd.DataFrame:
    """Carrega o dataset tratado do snapshot congelado (Parquet ou CSV)."""
    if parquet_path.exists():
        return pd.read_parquet(parquet_path)
    if csv_path.exists():
        return pd.read_csv(csv_path)
    raise FileNotFoundError(
        f"Dataset processado não encontrado em {parquet_path} nem em {csv_path}. Execute o pipeline ETL primeiro."
    )
