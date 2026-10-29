"""Validação de integridade, tipos e campos obrigatórios do dataset D&D 5e SRD."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

REQUIRED_RAW_FIELDS = (
    "index",
    "name",
    "size",
    "type",
    "armor_class",
    "hit_points",
    "challenge_rating",
    "strength",
    "dexterity",
    "constitution",
    "intelligence",
    "wisdom",
    "charisma",
)

ABILITY_FIELDS = (
    "strength",
    "dexterity",
    "constitution",
    "intelligence",
    "wisdom",
    "charisma",
)

OPTIONAL_MONITORED_FIELDS = (
    "subtype",
    "alignment",
    "hit_dice",
    "hit_points_roll",
    "xp",
    "damage_vulnerabilities",
    "damage_resistances",
    "damage_immunities",
    "condition_immunities",
    "actions",
    "special_abilities",
    "legendary_actions",
    "reactions",
    "image",
)


@dataclass
class RecordValidationResult:
    """Resultado de validação individual de um registro bruto da API."""

    index: str
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class DatasetValidationReport:
    """Relatório consolidado de validação do dataset bruto e tratado."""

    total_records: int
    valid_records_count: int
    invalid_records_count: int
    duplicate_indices: list[str]
    missing_fields_count: dict[str, int]
    empty_lists_or_nulls_count: dict[str, int]
    invalid_records: list[dict[str, Any]]
    warnings_summary: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def extract_armor_class_value(raw_ac: Any) -> tuple[int | None, str]:
    """Extrai o valor numérico e o tipo da Classe de Armadura (AC) do formato aninhado da API.

    Na API D&D 5e 2014, `armor_class` é uma lista de objetos como:
    `[{"type": "armor", "value": 15, ...}]` ou um inteiro direto em versões legadas.
    """
    if isinstance(raw_ac, (int, float)):
        return int(raw_ac), "numeric"
    if isinstance(raw_ac, list) and len(raw_ac) > 0:
        first = raw_ac[0]
        if isinstance(first, dict) and "value" in first:
            val = first.get("value")
            ac_type = str(first.get("type", "natural"))
            if isinstance(val, (int, float)):
                return int(val), ac_type
        elif isinstance(first, (int, float)):
            return int(first), "numeric_list"
    return None, "missing"


def validate_single_raw_record(record: dict[str, Any]) -> RecordValidationResult:
    """Valida tipos, limites numéricos e campos obrigatórios de um registro bruto."""
    idx = str(record.get("index", "")).strip() or "<missing_index>"
    errors: list[str] = []
    warnings: list[str] = []

    for req in REQUIRED_RAW_FIELDS:
        if req not in record or record[req] is None or record[req] == "":
            errors.append(f"Campo obrigatório ausente ou nulo: '{req}'")

    hp = record.get("hit_points")
    if not isinstance(hp, (int, float)) or int(hp) <= 0:
        errors.append(f"hit_points inválido: {hp!r} (deve ser inteiro > 0)")

    ac_val, _ = extract_armor_class_value(record.get("armor_class"))
    if ac_val is None or ac_val <= 0:
        errors.append(f"armor_class inválido ou não extraível: {record.get('armor_class')!r}")

    cr = record.get("challenge_rating")
    if not isinstance(cr, (int, float)) or float(cr) < 0:
        errors.append(f"challenge_rating inválido: {cr!r} (deve ser >= 0)")

    xp = record.get("xp")
    if xp is None:
        warnings.append("Campo 'xp' ausente (será inferido da tabela oficial SRD por CR)")
    elif not isinstance(xp, (int, float)) or int(xp) < 0:
        errors.append(f"xp inválido: {xp!r}")

    for ab in ABILITY_FIELDS:
        val = record.get(ab)
        if not isinstance(val, (int, float)) or not (1 <= int(val) <= 30):
            errors.append(f"Atributo '{ab}' fora do intervalo válido [1, 30]: {val!r}")

    actions = record.get("actions")
    if not isinstance(actions, list) or len(actions) == 0:
        warnings.append("Monstro sem lista de 'actions' ofensivas diretas")

    return RecordValidationResult(
        index=idx,
        is_valid=(len(errors) == 0),
        errors=errors,
        warnings=warnings,
    )


def validate_raw_dataset(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], DatasetValidationReport]:
    """Valida a lista completa de registros brutos, filtrando válidos e gerando relatório."""
    seen_indices: set[str] = set()
    duplicates: list[str] = []
    valid_records: list[dict[str, Any]] = []
    invalid_details: list[dict[str, Any]] = []

    all_monitored = list(REQUIRED_RAW_FIELDS) + list(OPTIONAL_MONITORED_FIELDS)
    missing_counts: dict[str, int] = {k: 0 for k in all_monitored}
    empty_or_null_counts: dict[str, int] = {k: 0 for k in all_monitored}
    warnings_summary: dict[str, int] = {}

    for rec in records:
        idx = str(rec.get("index", "")).strip()
        if idx in seen_indices:
            duplicates.append(idx)
            invalid_details.append({"index": idx, "errors": ["Registro duplicado"]})
            continue
        if idx:
            seen_indices.add(idx)

        for field_name in all_monitored:
            val = rec.get(field_name)
            if val is None or val == "":
                missing_counts[field_name] += 1
                empty_or_null_counts[field_name] += 1
            elif isinstance(val, (list, dict)) and len(val) == 0:
                empty_or_null_counts[field_name] += 1

        res = validate_single_raw_record(rec)
        for w in res.warnings:
            warnings_summary[w] = warnings_summary.get(w, 0) + 1

        if res.is_valid:
            valid_records.append(rec)
        else:
            invalid_details.append({"index": res.index, "errors": res.errors, "warnings": res.warnings})

    report = DatasetValidationReport(
        total_records=len(records),
        valid_records_count=len(valid_records),
        invalid_records_count=len(invalid_details),
        duplicate_indices=duplicates,
        missing_fields_count=missing_counts,
        empty_lists_or_nulls_count=empty_or_null_counts,
        invalid_records=invalid_details,
        warnings_summary=warnings_summary,
    )
    return valid_records, report
