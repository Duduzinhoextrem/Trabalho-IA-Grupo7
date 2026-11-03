"""Reprodução de jornadas, integridade dos dados e caminhos públicos da interface."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from src.dataset.preprocessing import load_processed_dataset
from src.dataset.provenance import inspect_snapshot
from src.experiments.baselines import create_fixed_baseline_chromosome
from src.game.combat import run_dungeon_simulation
from src.game.dungeon import build_dungeon_100_rooms
from src.game.monsters import load_balance_config
from src.genetic.chromosome import Chromosome
from src.genetic.optimizer import run_genetic_algorithm
from src.services.journey import journey_report, scenario_signature, search_journey, simulate_journey


@pytest.fixture(scope="module")
def inputs():
    return load_processed_dataset(), load_balance_config()


def test_relatorio_permite_reproduzir_resultado_com_as_regras_exportadas(inputs):
    monsters, settings = inputs
    journey = simulate_journey(monsters, settings, 707, False, create_fixed_baseline_chromosome(), "Minha estratégia")
    payload = json.loads(journey_report(journey, settings))
    rooms = build_dungeon_100_rooms(monsters, payload["balance"], seed=payload["seed"])
    replay = run_dungeon_simulation(rooms, Chromosome(genes=payload["genes"]).to_policy_params(),
                                    payload["balance"], seed=payload["seed"], enable_chests=payload["enable_chests"],
                                    record_detailed_logs=True)
    assert replay.rooms_cleared == payload["outcome"]["rooms_cleared"]
    assert replay.failure_room == payload["outcome"]["failure_room"]
    assert replay.failure_reason == payload["outcome"]["failure_reason"]
    assert [r.warrior_hp_end for r in replay.room_results] == [r["health"] for r in payload["rooms"]]
    assert payload["scenario_signature"] == scenario_signature(monsters, settings, 707, False)


@pytest.mark.parametrize("changed", ["seed", "chests", "settings", "monsters"])
def test_continuacao_recusa_misturar_cenarios(inputs, changed):
    monsters, settings = inputs
    previous = {"scenario_signature": scenario_signature(monsters, settings, 201, True)}
    current_monsters, current_settings = monsters.copy(), copy.deepcopy(settings)
    seed, chests = 201, True
    if changed == "seed":
        seed = 202
    elif changed == "chests":
        chests = False
    elif changed == "settings":
        current_settings["warrior"]["post_room_heal_fraction"] = 0.01
    else:
        current_monsters.loc[0, "hit_points"] += 1
    with pytest.raises(ValueError, match="nova busca"):
        search_journey(current_monsters, current_settings, seed, chests, previous=previous)


def test_busca_sem_interface_respeita_orcamento_e_preserva_historico(inputs):
    monsters, settings = inputs
    reports = []
    first = search_journey(monsters, settings, 201, True, budget=2, population=4, on_progress=reports.append)
    first_history = copy.deepcopy(first["attempts"])
    second = search_journey(monsters, settings, 201, True, budget=2, population=4, previous=first)
    assert first["total_evaluations"] == 2
    assert first["attempts"] == first_history
    assert second["total_evaluations"] == 4
    assert [row["number"] for row in second["attempts"]] == [1, 2, 3, 4]
    assert second["player"].rooms_cleared >= first["player"].rooms_cleared
    assert reports[0]["evaluations"] == 1


def test_conferencia_nao_confia_apenas_no_status_do_manifesto(tmp_path):
    target = tmp_path / "data/raw/monsters_raw_srd2014.json"
    target.parent.mkdir(parents=True)
    target.write_text('[{"index": "goblin"}]', encoding="utf-8")
    manifest = {"raw_file_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
                "collected_records_count": 1, "integrity_status": "VERIFIED"}
    frame = pd.DataFrame({"index": ["goblin"]})
    assert inspect_snapshot(frame, manifest, tmp_path)["verified"]
    target.write_text('[{"index": "dragon"}]', encoding="utf-8")
    report = inspect_snapshot(frame, manifest, tmp_path)
    assert not report["verified"] and not report["hash_matches"] and not report["same_ids"]


@pytest.mark.parametrize("kwargs", [{"max_evaluations": 0}, {"generations": 0}, {"elite_count": 4},
                                    {"mutation_rate": float("nan")}, {"crossover_rate": 1.1}])
def test_otimizador_informa_parametros_invalidos(kwargs):
    with pytest.raises(ValueError):
        run_genetic_algorithm({201: []}, {}, pop_size=4, **kwargs)


@pytest.mark.parametrize("page", ["Como funciona", "Resultados", "Bestiário", "Dados e fonte", "Laboratório"])
def test_paginas_de_consulta_abrem_sem_erro(page):
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=30).run()
    app.radio(key="page").set_value(page).run()
    assert not app.exception


def test_bestiario_aceita_busca_literal_e_resultado_vazio():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=30).run()
    app.radio(key="page").set_value("Bestiário").run()
    app.text_input[0].set_value("[").run()
    assert not app.exception
    assert any("Nenhuma criatura" in item.value for item in app.info)


def test_mapa_permite_pular_e_continuar_o_replay():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=30).run()
    app.radio(key="page").set_value("Aventura").run()
    next(button for button in app.button if button.label == "Iniciar com esta estratégia").click().run()
    app.select_slider[0].set_value(10).run()
    assert not app.exception
    assert app.session_state["journey"]["index"] == 9
    next(button for button in app.button if button.label.startswith("Próxima sala")).click().run()
    assert not app.exception
    assert app.session_state["journey"]["index"] == 10
