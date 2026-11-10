"""Dados didáticos do algoritmo genético, calculados com os operadores reais do projeto.

Nada aqui é uma ilustração inventada: os valores vêm das constantes e funções de `src/genetic`.
"""

from __future__ import annotations

import random
from typing import Any

import pandas as pd

from src.genetic.chromosome import GENE_BOUNDS, GENE_NAMES, Chromosome
from src.genetic.operators import hybrid_crossover, mutate_chromosome
from src.ui.localization import GENE_FRIENDLY_INFO

GENE_GROUPS: tuple[tuple[str, range], ...] = (
    ("Distribuição de atributos do guerreiro (soma 1)", range(0, 3)),
    ("Prioridade de contratação de cada aliado", range(3, 8)),
    ("Evolução dos atributos dos aliados (soma 1)", range(8, 11)),
    ("Decisões de compra e economia", range(11, 16)),
)

# Valores padrão usados em `run_genetic_algorithm` e `hybrid_crossover`.
DEFAULT_PARAMETERS: dict[str, Any] = {
    "tournament_size": 3,
    "crossover_rate": 0.85,
    "blx_alpha": 0.25,
    "mutation_sigma_fraction": 0.18,
    "elite_count": 2,
    "stagnation_limit": 15,
}


def gene_table() -> pd.DataFrame:
    """Tabela dos 16 genes: grupo, nome amigável, intervalo e significado."""
    group_of = {i: title for title, indexes in GENE_GROUPS for i in indexes}
    rows = []
    for i, name in enumerate(GENE_NAMES):
        info = GENE_FRIENDLY_INFO.get(name, {"nome": name, "explicacao": ""})
        lo, hi = GENE_BOUNDS[i]
        rows.append({
            "Gene": i + 1,
            "Grupo": group_of[i],
            "Escolha": info["nome"],
            "Intervalo": "0 ou 1" if name.endswith("discrete") else f"{lo:g} a {hi:g}",
            "Significado": info["explicacao"],
        })
    return pd.DataFrame(rows)


def reproduction_example(parent_a: Chromosome, parent_b: Chromosome, seed: int,
                         mutation_rate: float) -> tuple[pd.DataFrame, dict[str, int]]:
    """Cruza e muta dois pais reais com os operadores do algoritmo.

    O cruzamento é forçado (`crossover_rate=1`) para que o exemplo sempre mostre a recombinação.
    Retorna a tabela gene a gene e a contagem de genes alterados.
    """
    rng = random.Random(seed)
    child, _ = hybrid_crossover(parent_a, parent_b, rng=rng, crossover_rate=1.0)
    mutant = mutate_chromosome(child, mutation_rate=mutation_rate, rng=rng)
    rows = []
    mutated_count = 0
    for i, name in enumerate(GENE_NAMES):
        info = GENE_FRIENDLY_INFO.get(name, {"nome": name})
        changed = abs(mutant.genes[i] - child.genes[i]) > 1e-9
        mutated_count += int(changed)
        rows.append({
            "Gene": i + 1,
            "Escolha": info["nome"],
            "Pai A": parent_a.genes[i],
            "Pai B": parent_b.genes[i],
            "Filho (cruzamento)": child.genes[i],
            "Filho (após mutação)": mutant.genes[i],
            "Mutou?": "sim" if changed else "",
        })
    return pd.DataFrame(rows), {"mutated_genes": mutated_count, "total_genes": len(GENE_NAMES)}
