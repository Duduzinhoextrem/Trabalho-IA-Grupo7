"""Cromossomo de 16 genes, reparo de valores e conversão em política de decisões.

Estrutura dos 16 genes:
- [0, 1, 2]: Pesos de distribuição de atributos do guerreiro (Força, Vitalidade, Defesa): contínuos, soma = 1.0
- [3, 4, 5, 6, 7]: Prioridade de contratação das 5 classes de aliados (Mago, Arqueiro, Monge, Padre, Alquimista) em [0, 1]
- [8, 9, 10]: Pesos de evolução dos atributos dos aliados (Poder, Vitalidade, Defesa): contínuos, soma = 1.0
- [11]: Prioridade entre equipamentos ofensivos e defensivos em [0.0, 1.0]
- [12]: Gene discreto {0.0, 1.0}: priorizar a contratação de aliado antes da compra de equipamento
- [13]: Quantidade mínima de dinheiro a reservar (ouro) em [0.0, 120.0]
- [14]: Limiar econômico (multiplicador) para compra de equipamentos em [1.0, 1.8]
- [15]: Limiar econômico (multiplicador) para contratação de aliados em [1.0, 1.8]
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
import random
from typing import Any

from src.game.characters import ALLY_CLASSES_ORDER

GENE_NAMES = (
    "w_weight_str",
    "w_weight_vit",
    "w_weight_def",
    "ally_prio_mage",
    "ally_prio_archer",
    "ally_prio_monk",
    "ally_prio_priest",
    "ally_prio_alchemist",
    "ally_weight_power",
    "ally_weight_vit",
    "ally_weight_def",
    "equip_offense_priority",
    "hire_before_equip_discrete",
    "min_gold_reserve",
    "equipment_buy_threshold",
    "ally_hire_threshold",
)

GENE_BOUNDS: tuple[tuple[float, float], ...] = (
    (0.01, 1.0),   # 0: peso da força do guerreiro (w_weight_str)
    (0.01, 1.0),   # 1: peso da vitalidade do guerreiro (w_weight_vit)
    (0.01, 1.0),   # 2: peso da defesa do guerreiro (w_weight_def)
    (0.0, 1.0),    # 3: prioridade de contratação do mago (ally_prio_mage)
    (0.0, 1.0),    # 4: prioridade de contratação do arqueiro (ally_prio_archer)
    (0.0, 1.0),    # 5: prioridade de contratação do monge (ally_prio_monk)
    (0.0, 1.0),    # 6: prioridade de contratação do padre (ally_prio_priest)
    (0.0, 1.0),    # 7: prioridade de contratação do alquimista (ally_prio_alchemist)
    (0.01, 1.0),   # 8: peso do poder dos aliados (ally_weight_power)
    (0.01, 1.0),   # 9: peso da vitalidade dos aliados (ally_weight_vit)
    (0.01, 1.0),   # 10: peso da defesa dos aliados (ally_weight_def)
    (0.0, 1.0),    # 11: prioridade de equipamento ofensivo (equip_offense_priority)
    (0.0, 1.0),    # 12: contratar antes de equipar (hire_before_equip_discrete) {0.0, 1.0}
    (0.0, 120.0),  # 13: reserva mínima de ouro (min_gold_reserve)
    (1.0, 1.8),    # 14: limiar de compra de equipamento (equipment_buy_threshold)
    (1.0, 1.8),    # 15: limiar de contratação de aliado (ally_hire_threshold)
)

DISCRETE_GENE_INDICES = {12}
NUM_GENES = len(GENE_NAMES)


def repair_genes(raw_genes: list[float] | tuple[float, ...]) -> list[float]:
    """Ajusta os genes aos limites, normaliza os pesos e corrige os valores discretos."""
    if len(raw_genes) != NUM_GENES:
        raise ValueError(f"Esperados {NUM_GENES} genes, recebido {len(raw_genes)}.")

    repaired: list[float] = []
    for i, val in enumerate(raw_genes):
        lo, hi = GENE_BOUNDS[i]
        v = float(val) if not (math.isnan(float(val)) or math.isinf(float(val))) else (lo + hi) / 2.0
        v = max(lo, min(hi, v))
        if i in DISCRETE_GENE_INDICES:
            v = 1.0 if v >= 0.5 else 0.0
        repaired.append(v)

    # Normaliza pesos de atributos do guerreiro [0, 1, 2] para somarem 1.0
    w_sum = repaired[0] + repaired[1] + repaired[2]
    if w_sum <= 1e-6:
        repaired[0], repaired[1], repaired[2] = 1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0
    else:
        repaired[0] = round(repaired[0] / w_sum, 4)
        repaired[1] = round(repaired[1] / w_sum, 4)
        repaired[2] = round(max(0.01, 1.0 - repaired[0] - repaired[1]), 4)

    # Normaliza pesos de atributos dos aliados [8, 9, 10] para somarem 1.0
    a_sum = repaired[8] + repaired[9] + repaired[10]
    if a_sum <= 1e-6:
        repaired[8], repaired[9], repaired[10] = 1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0
    else:
        repaired[8] = round(repaired[8] / a_sum, 4)
        repaired[9] = round(repaired[9] / a_sum, 4)
        repaired[10] = round(max(0.01, 1.0 - repaired[8] - repaired[9]), 4)

    return [round(g, 4) for g in repaired]


def is_valid_chromosome_genes(genes: list[float] | tuple[float, ...]) -> bool:
    """Verifica os limites dos genes e as somas dos pesos."""
    if len(genes) != NUM_GENES:
        return False
    for i, val in enumerate(genes):
        if math.isnan(val) or math.isinf(val):
            return False
        lo, hi = GENE_BOUNDS[i]
        if val < lo - 1e-4 or val > hi + 1e-4:
            return False
        if i in DISCRETE_GENE_INDICES and val not in (0.0, 1.0):
            return False
    w_sum = genes[0] + genes[1] + genes[2]
    a_sum = genes[8] + genes[9] + genes[10]
    if abs(w_sum - 1.0) > 0.02 or abs(a_sum - 1.0) > 0.02:
        return False
    return True


@dataclass
class Chromosome:
    """Indivíduo da população do algoritmo genético."""

    genes: list[float]
    fitness: float | None = None
    mean_rooms_cleared: float = 0.0
    completion_rate: float = 0.0
    mean_hp_ratio: float = 0.0
    mean_gold_left: float = 0.0
    evaluated_seeds: list[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.genes = repair_genes(self.genes)

    def copy(self) -> Chromosome:
        return Chromosome(
            genes=list(self.genes),
            fitness=self.fitness,
            mean_rooms_cleared=self.mean_rooms_cleared,
            completion_rate=self.completion_rate,
            mean_hp_ratio=self.mean_hp_ratio,
            mean_gold_left=self.mean_gold_left,
            evaluated_seeds=list(self.evaluated_seeds),
        )

    def to_policy_params(self) -> dict[str, Any]:
        """Converte os 16 genes nos parâmetros que orientam as decisões durante a simulação."""
        g = self.genes
        ally_prios = {
            ALLY_CLASSES_ORDER[0]: g[3],  # Mago
            ALLY_CLASSES_ORDER[1]: g[4],  # Arqueiro
            ALLY_CLASSES_ORDER[2]: g[5],  # Monge
            ALLY_CLASSES_ORDER[3]: g[6],  # Padre
            ALLY_CLASSES_ORDER[4]: g[7],  # Alquimista
        }
        return {
            "warrior_attr_weights": (g[0], g[1], g[2]),
            "ally_priorities": ally_prios,
            "ally_attr_weights": (g[8], g[9], g[10]),
            "equip_offense_priority": g[11],
            "hire_before_equip_priority": g[12],
            "min_gold_reserve": g[13],
            "equipment_buy_threshold": g[14],
            "ally_hire_threshold": g[15],
        }

    def to_named_dict(self) -> dict[str, float]:
        return {GENE_NAMES[i]: self.genes[i] for i in range(NUM_GENES)}


def create_random_chromosome(rng: random.Random) -> Chromosome:
    """Gera um cromossomo aleatório válido com distribuição uniforme nos domínios."""
    raw: list[float] = []
    for i, (lo, hi) in enumerate(GENE_BOUNDS):
        if i in DISCRETE_GENE_INDICES:
            raw.append(float(rng.choice([0.0, 1.0])))
        else:
            raw.append(rng.uniform(lo, hi))
    return Chromosome(genes=repair_genes(raw))
