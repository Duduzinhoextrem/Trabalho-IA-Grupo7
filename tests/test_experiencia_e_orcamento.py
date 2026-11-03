"""Verificações da jornada e das comparações de orçamento."""

from __future__ import annotations

from pathlib import Path
import json
import os
import subprocess
import sys
from types import SimpleNamespace

import pytest
from streamlit.testing.v1 import AppTest

from src.dataset.preprocessing import load_processed_dataset
from src.experiments.baselines import create_fixed_baseline_chromosome
from src.experiments.evaluation import run_experiment_2_population, run_experiment_3_baselines_comparison
from src.game.dungeon import build_dungeon_100_rooms
from src.game.monsters import load_balance_config
from src.genetic.chromosome import is_valid_chromosome_genes
from src.genetic.fitness import evaluate_chromosome
from src.genetic.optimizer import run_genetic_algorithm
import src.genetic.optimizer as optimizer
import src.ui.pages as pages
from src.ui.experience import make_manual_strategy, termination_label


def _suites():
    settings = load_balance_config()
    monsters = load_processed_dataset()
    train = {101: build_dungeon_100_rooms(monsters, settings, seed=101)}
    validation = {201: build_dungeon_100_rooms(monsters, settings, seed=201)}
    return settings, train, validation


def test_orcamento_efetivo_e_igual_entre_metodos():
    settings, train, validation = _suites()
    experiment, _, _ = run_experiment_3_baselines_comparison(
        train, validation, settings, pop_size=4, generations=3, n_repeats=2
    )
    methods = experiment["methods"]
    for name in ("random_search", "genetic_algorithm"):
        assert [r["objective_evaluations"] for r in methods[name]["repeats"]] == [12, 12]


def test_populacoes_registram_avaliacoes_reais():
    settings, train, validation = _suites()
    experiment = run_experiment_2_population(
        train, validation, settings, configs=(("pequena", 4, 3), ("maior", 6, 2)), n_repeats=1
    )
    for result in experiment["results"].values():
        assert result["repeats"][0]["objective_evaluations"] == 12
        assert result["convergence_by_evaluations"]["evaluations"][-1] == 12


def test_composicao_alternativa_reproduz_entre_processos():
    program = (
        "import json; "
        "from src.dataset.preprocessing import load_processed_dataset; "
        "from src.game.monsters import load_balance_config; "
        "from src.game.dungeon import build_dungeon_100_rooms; "
        "rooms=build_dungeon_100_rooms(load_processed_dataset(), load_balance_config(), seed=301, composition_mode='alternate_pool'); "
        "print(json.dumps([r.to_summary_dict() for r in rooms], sort_keys=True))"
    )
    outputs = []
    for hash_seed in ("1", "987"):
        env = os.environ.copy()
        env["PYTHONHASHSEED"] = hash_seed
        outputs.append(subprocess.check_output([sys.executable, "-B", "-c", program], env=env, text=True))
    assert outputs[0] == outputs[1]


def test_acompanhamento_de_geracoes_nao_altera_resultado():
    settings, train, _ = _suites()
    records = []
    first = run_genetic_algorithm(train, settings, pop_size=6, generations=3, seed=42)
    observed = run_genetic_algorithm(train, settings, pop_size=6, generations=3, seed=42, on_generation=records.append)
    assert [r.to_dict() for r in first.history] == [r.to_dict() for r in records]
    assert first.best_chromosome.genes == observed.best_chromosome.genes


def test_estrategia_inicial_e_reavaliada_no_treino_atual():
    settings, train, _ = _suites()
    candidate = create_fixed_baseline_chromosome()
    evaluate_chromosome(candidate, train, settings)
    expected_fitness = candidate.fitness
    candidate.fitness = 999999.0
    result = run_genetic_algorithm(train, settings, pop_size=6, generations=3, seed=42,
                                   initial_chromosomes=[candidate])
    assert result.best_chromosome.fitness >= expected_fitness
    assert result.best_chromosome.fitness < 101


def test_busca_para_quando_objetivo_e_encontrado(monkeypatch):
    evaluated = []

    def fake_evaluation(chromosome, **kwargs):
        evaluated.append(chromosome.genes.copy())
        chromosome.mean_rooms_cleared = 95.0 if len(evaluated) == 1 else 80.0
        chromosome.fitness = chromosome.mean_rooms_cleared
        achieved = len(evaluated) == 2
        return chromosome.fitness, [SimpleNamespace(seed=201, completed_all_100=achieved)]

    monkeypatch.setattr(optimizer, "evaluate_chromosome", fake_evaluation)
    result = run_genetic_algorithm({201: []}, {}, pop_size=4, generations=5, seed=42,
                                   stop_when=lambda candidate, runs: runs[0].completed_all_100)
    assert result.stopped_reason == "target_reached"
    assert result.total_objective_evaluations == 2
    assert result.best_chromosome.genes == evaluated[1]
    assert result.history[-1].best_mean_rooms == 95.0


def test_busca_sem_sucesso_respeita_limite():
    settings, train, _ = _suites()
    result = run_genetic_algorithm(train, settings, pop_size=4, generations=5, max_evaluations=8,
                                   seed=42, stop_when=lambda candidate, runs: False)
    assert result.stopped_reason == "max_evaluations_reached"
    assert result.total_objective_evaluations == 8


def test_escolhas_simples_formam_estrategia_valida():
    strategy = make_manual_strategy("Mais vida", "Padre", "Proteção primeiro")
    policy = strategy.to_policy_params()
    assert is_valid_chromosome_genes(strategy.genes)
    assert policy["warrior_attr_weights"] == (0.2, 0.6, 0.2)
    assert max(policy["ally_priorities"], key=policy["ally_priorities"].get) == "priest"
    assert policy["equip_offense_priority"] < 0.4
    assert "limite de turnos" in termination_label("max_turns_exceeded")


def test_resultados_publicados_conferem_com_cada_semente():
    payload = json.loads(Path("data/experiments/scientific_experiments_v2.json").read_text(encoding="utf-8"))
    for scenario in payload["experiment_4_generalization"]["scenarios"].values():
        for method in ("genetic_algorithm", "fixed_baseline"):
            result = scenario[method]
            rooms = list(result["per_seed_rooms"].values())
            assert result["mean_rooms"] == pytest.approx(sum(rooms) / len(rooms), abs=0.0001)
            assert result["completion_rate"] == pytest.approx(rooms.count(100) / len(rooms), abs=0.0001)
    for experiment in ("experiment_1_mutation", "experiment_2_population"):
        for result in payload[experiment]["results"].values():
            assert all(run["objective_evaluations"] == 240 for run in result["repeats"])


def test_jornada_mantem_estado_ao_avancar():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=30).run()
    assert not app.exception
    app.radio(key="page").set_value("Aventura").run()
    next(button for button in app.button if button.label == "Iniciar com esta estratégia").click().run()
    assert not app.exception
    assert app.session_state["journey"]["index"] == 0
    assert any(item.value == "Sala 1 de 100" for item in app.subheader)
    next(button for button in app.button if button.label.startswith("Próxima sala")).click().run()
    assert not app.exception
    assert app.session_state["journey"]["index"] == 1
    assert any(item.value == "Sala 2 de 100" for item in app.subheader)


def test_treinamento_automatico_inicia_jornada_com_resultado_real():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=60).run()
    next(button for button in app.button if button.label == "Treinar e iniciar automaticamente").click().run()
    assert not app.exception
    journey = app.session_state["journey"]
    assert journey["mode"] == "Busca automática"
    assert journey["training"].total_objective_evaluations > 0
    assert journey["training"].stopped_reason == "target_reached"
    assert journey["player"].completed_all_100
    assert journey["player"].rooms_cleared == 100
    assert journey["index"] == len(journey["player"].room_results) - 1
    assert len(journey["comparisons"]) >= 1
    attempts = journey["attempts"]
    assert len(attempts) == journey["total_evaluations"]
    assert [item["number"] for item in attempts] == list(range(1, len(attempts) + 1))
    assert any(not item["completed"] for item in attempts)
    assert attempts[-1]["completed"] and attempts[-1]["rooms_cleared"] == 100
    assert attempts[-1]["genes"] == journey["selected_strategy"].genes
    assert attempts[0]["generation"] == 1
    assert attempts[-1]["generation"] == len(journey["training"].history)
    assert [item["best_so_far"] for item in attempts] == sorted(item["best_so_far"] for item in attempts)
    assert any(item.label == "Ver tentativas anteriores e evolução" for item in app.expander)
    next(box for box in app.selectbox if box.label == "Tentativa anterior").set_value(2).run()
    next(box for box in app.checkbox if box.label == "Mostrar todas as tentativas").check().run()
    assert not app.exception
    next(button for button in app.button if button.label == "Rever o combate final da tentativa anterior").click().run()
    assert not app.exception
    replay = app.session_state["attempt_replay"]["result"]
    assert replay.rooms_cleared == attempts[1]["rooms_cleared"]
    assert replay.failure_room == attempts[1]["failure_room"]


def test_busca_sem_vitoria_pode_continuar(monkeypatch):
    monkeypatch.setattr(pages, "AUTO_SEARCH_BUDGET", 2)
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=60).run()
    next(button for button in app.button if button.label == "Treinar e iniciar automaticamente").click().run()
    first = app.session_state["journey"]
    assert not app.exception
    assert not first["player"].completed_all_100
    assert first["total_evaluations"] == 2
    next(button for button in app.button if button.label == "Continuar procurando").click().run()
    second = app.session_state["journey"]
    assert not app.exception
    assert second["search_round"] == 2
    assert second["total_evaluations"] == 4
    assert [item["number"] for item in second["attempts"]] == [1, 2, 3, 4]
    assert [item["round"] for item in second["attempts"]] == [1, 1, 2, 2]
    assert second["player"].rooms_cleared >= first["player"].rooms_cleared
