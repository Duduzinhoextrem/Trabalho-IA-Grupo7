"""Funções de apoio à experiência interativa."""

from __future__ import annotations

from src.experiments.baselines import create_fixed_baseline_chromosome
from src.genetic.chromosome import ALLY_CLASSES_ORDER, Chromosome


FOCUS_PRESETS = {
    "Equilibrado": (0.34, 0.33, 0.33),
    "Mais força": (0.60, 0.20, 0.20),
    "Mais vida": (0.20, 0.60, 0.20),
    "Mais defesa": (0.20, 0.20, 0.60),
}

ALLY_OPTIONS = {
    "Arqueiro": "archer",
    "Mago": "mage",
    "Monge": "monk",
    "Padre": "priest",
    "Alquimista": "alchemist",
}

EQUIPMENT_OPTIONS = {"Proteção primeiro": 0.1, "Arma primeiro": 0.9}


def make_manual_strategy(focus: str, ally: str, equipment: str) -> Chromosome:
    """Converte três escolhas em uma política para o simulador usado pelo AG."""
    genes = create_fixed_baseline_chromosome().genes.copy()
    genes[0:3] = FOCUS_PRESETS[focus]
    selected_class = ALLY_OPTIONS[ally]
    # A ordem das demais classes continua estável quando o primeiro aliado não puder ser contratado.
    genes[3:8] = [1.0 if name == selected_class else (0.4 - i * 0.05)
                  for i, name in enumerate(ALLY_CLASSES_ORDER)]
    genes[11] = EQUIPMENT_OPTIONS[equipment]
    return Chromosome(genes=genes)


def termination_label(reason: str | None) -> str:
    return {
        "warrior_died": "O guerreiro foi derrotado.",
        "max_turns_exceeded": "A luta atingiu o limite de turnos.",
        "enemies_defeated": "Todos os inimigos foram derrotados.",
    }.get(reason, "A tentativa terminou.")
