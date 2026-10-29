"""Operadores Evolutivos do Algoritmo Genético (Seleção, Cruzamento, Mutação, Elitismo e Diversidade)."""

from __future__ import annotations

import math
import random

from src.genetic.chromosome import (
     Chromosome,
    DISCRETE_GENE_INDICES,
    GENE_BOUNDS,
    NUM_GENES,
    create_random_chromosome,
    repair_genes,
)


def initialize_diverse_population(pop_size: int, rng: random.Random) -> list[Chromosome]:
    """Cria população inicial variada combinando amostragem estratificada e aleatória uniforme."""
    if pop_size <= 0:
        raise ValueError("pop_size deve ser > 0")

    population: list[Chromosome] = []
    for idx in range(pop_size):
        raw: list[float] = []
        for g_idx, (lo, hi) in enumerate(GENE_BOUNDS):
            if g_idx in DISCRETE_GENE_INDICES:
                raw.append(float((idx + rng.randint(0, 1)) % 2))
            else:
                # Amostragem tipo Latin-Hypercube estratificada por indivíduo + ruído
                stratum_low = lo + (hi - lo) * (idx / pop_size)
                stratum_high = lo + (hi - lo) * ((idx + 1) / pop_size)
                raw.append(rng.uniform(stratum_low, stratum_high))
        rng_perm = raw[:]
        population.append(Chromosome(genes=repair_genes(rng_perm)))

    rng.shuffle(population)
    return population


def tournament_selection(
    population: list[Chromosome],
    tournament_size: int,
    rng: random.Random,
) -> Chromosome:
    """Seleção por torneio: escolhe `tournament_size` candidatos ao acaso e retorna o de maior fitness."""
    k = max(2, min(len(population), tournament_size))
    contenders = rng.sample(population, k)
    winner = max(contenders, key=lambda c: float(c.fitness if c.fitness is not None else -1e9))
    return winner.copy()


def hybrid_crossover(
    parent1: Chromosome,
    parent2: Chromosome,
    rng: random.Random,
    crossover_rate: float = 0.85,
    alpha: float = 0.25,
) -> tuple[Chromosome, Chromosome]:
    """Cruzamento híbrido compatível com genes contínuos (BLX-alpha / média ponderada) e discretos (uniforme)."""
    if rng.random() > crossover_rate:
        return parent1.copy(), parent2.copy()

    child1_genes: list[float] = []
    child2_genes: list[float] = []

    for i in range(NUM_GENES):
        g1 = parent1.genes[i]
        g2 = parent2.genes[i]

        if i in DISCRETE_GENE_INDICES:
            # Cruzamento uniforme para genes discretos
            if rng.random() < 0.5:
                child1_genes.append(g1)
                child2_genes.append(g2)
            else:
                child1_genes.append(g2)
                child2_genes.append(g1)
        else:
            # BLX-alpha para genes contínuos
            c_min = min(g1, g2)
            c_max = max(g1, g2)
            diff = c_max - c_min
            low_b = c_min - alpha * diff
            high_b = c_max + alpha * diff
            child1_genes.append(rng.uniform(low_b, high_b))
            child2_genes.append(rng.uniform(low_b, high_b))

    c1 = Chromosome(genes=repair_genes(child1_genes))
    c2 = Chromosome(genes=repair_genes(child2_genes))
    return c1, c2


def mutate_chromosome(
    chromosome: Chromosome,
    mutation_rate: float,
    rng: random.Random,
    sigma_scale: float = 0.18,
) -> Chromosome:
    """Aplica mutação gaussiana nos genes contínuos e inversão nos genes discretos conforme `mutation_rate`."""
    mutated_genes = list(chromosome.genes)
    for i in range(NUM_GENES):
        if rng.random() < mutation_rate:
            lo, hi = GENE_BOUNDS[i]
            if i in DISCRETE_GENE_INDICES:
                mutated_genes[i] = 1.0 - mutated_genes[i]
            else:
                span = hi - lo
                noise = rng.gauss(0.0, span * sigma_scale)
                mutated_genes[i] = mutated_genes[i] + noise

    return Chromosome(genes=repair_genes(mutated_genes))


def apply_elitism(
    current_population: list[Chromosome],
    elite_count: int,
) -> list[Chromosome]:
    """Preserva os `elite_count` melhores indivíduos intactos para a próxima geração."""
    if elite_count <= 0:
        return []
    ranked = sorted(
        current_population,
        key=lambda c: float(c.fitness if c.fitness is not None else -1e9),
        reverse=True,
    )
    return [ind.copy() for ind in ranked[:elite_count]]


def compute_population_diversity(population: list[Chromosome]) -> float:
    """Calcula o índice de diversidade genética normalizado da população em [0, 1].

    Baseado no desvio-padrão médio normalizado pelo intervalo de cada gene.
    """
    n = len(population)
    if n <= 1:
        return 0.0

    norm_stds: list[float] = []
    for g_idx in range(NUM_GENES):
        lo, hi = GENE_BOUNDS[g_idx]
        span = max(1e-6, hi - lo)
        vals = [(ind.genes[g_idx] - lo) / span for ind in population]
        mean_v = sum(vals) / n
        var_v = sum((v - mean_v) ** 2 for v in vals) / n
        norm_stds.append(math.sqrt(var_v))

    return round(sum(norm_stds) / len(norm_stds), 4)


def enforce_diversity_control(
    offspring: list[Chromosome],
    rng: random.Random,
    min_diversity_threshold: float = 0.06,
) -> tuple[list[Chromosome], int]:
    """Remove clones exatos na prole e injeta perturbação caso a diversidade caia abaixo do limiar."""
    seen_signatures: set[tuple[float, ...]] = set()
    adjusted: list[Chromosome] = []
    interventions = 0

    for ind in offspring:
        sig = tuple(round(g, 3) for g in ind.genes)
        if sig in seen_signatures:
            # Perturba clone para preservar variedade genética
            mut = mutate_chromosome(ind, mutation_rate=0.35, rng=rng, sigma_scale=0.25)
            adjusted.append(mut)
            seen_signatures.add(tuple(round(g, 3) for g in mut.genes))
            interventions += 1
        else:
            seen_signatures.add(sig)
            adjusted.append(ind)

    div = compute_population_diversity(adjusted)
    if div < min_diversity_threshold and len(adjusted) >= 4:
        # Substitui até 15% dos últimos indivíduos da prole por imigrantes aleatórios
        num_immigrants = max(1, len(adjusted) // 7)
        for k in range(1, num_immigrants + 1):
            adjusted[-k] = create_random_chromosome(rng)
            interventions += 1

    return adjusted, interventions
