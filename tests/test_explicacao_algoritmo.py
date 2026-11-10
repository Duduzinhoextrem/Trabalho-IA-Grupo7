"""Testes da explicação didática do algoritmo (aba "Passo a passo do algoritmo")."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

from src.experiments.baselines import create_fixed_baseline_chromosome
from src.genetic.chromosome import GENE_BOUNDS, NUM_GENES, create_random_chromosome
from src.ui.algorithm_explainer import DEFAULT_PARAMETERS, gene_table, reproduction_example

import random


def test_tabela_de_genes_descreve_os_16_genes_do_cromossomo():
    table = gene_table()
    assert len(table) == NUM_GENES == 16
    assert table["Gene"].tolist() == list(range(1, 17))
    assert not (table["Significado"] == "").any()


def test_exemplo_de_reproducao_e_reprodutivel_e_valido():
    parent_a = create_fixed_baseline_chromosome()
    parent_b = create_random_chromosome(random.Random(3))
    first, counts = reproduction_example(parent_a, parent_b, seed=7, mutation_rate=0.25)
    second, _ = reproduction_example(parent_a, parent_b, seed=7, mutation_rate=0.25)
    assert first.equals(second)
    assert 0 <= counts["mutated_genes"] <= NUM_GENES
    for index, (low, high) in enumerate(GENE_BOUNDS):
        assert low - 1e-6 <= first.loc[index, "Filho (após mutação)"] <= high + 1e-6


def test_mutacao_zero_nao_altera_nenhum_gene():
    parent = create_fixed_baseline_chromosome()
    _, counts = reproduction_example(parent, parent, seed=1, mutation_rate=0.0)
    assert counts["mutated_genes"] == 0


def test_parametros_didaticos_coincidem_com_os_padroes_do_codigo():
    import inspect

    from src.genetic.operators import hybrid_crossover, mutate_chromosome
    from src.genetic.optimizer import run_genetic_algorithm

    ga = inspect.signature(run_genetic_algorithm).parameters
    assert DEFAULT_PARAMETERS["tournament_size"] == ga["tournament_size"].default
    assert DEFAULT_PARAMETERS["crossover_rate"] == ga["crossover_rate"].default
    assert DEFAULT_PARAMETERS["elite_count"] == ga["elite_count"].default
    assert DEFAULT_PARAMETERS["stagnation_limit"] == ga["stagnation_limit"].default
    assert DEFAULT_PARAMETERS["blx_alpha"] == inspect.signature(hybrid_crossover).parameters["alpha"].default
    assert DEFAULT_PARAMETERS["mutation_sigma_fraction"] == inspect.signature(mutate_chromosome).parameters["sigma_scale"].default


def test_pagina_como_funciona_exibe_o_passo_a_passo():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=30).run()
    app.radio(key="page").set_value("Como funciona").run()
    assert not app.exception
    assert [tab.label for tab in app.tabs][:3] == ["Experimento do grupo", "Faça uma demonstração", "Passo a passo do algoritmo"]
    titles = [item.label for item in app.expander]
    assert any(title.startswith("7 · Elitismo") for title in titles)
