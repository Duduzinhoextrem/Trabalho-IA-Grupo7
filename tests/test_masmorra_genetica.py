"""Suíte Completa de Testes Automatizados e Critérios de Aceitação (Seção 16).

Cobre todos os 17 itens obrigatórios usando dados externos reais e verificações formais.
"""

from __future__ import annotations

import json
from pathlib import Path
import random
from typing import Any

import pytest
import requests

from src.dataset.collector import (
    DataCollectionError,
    fetch_json_with_retry,
    load_or_collect_raw_monsters,
)
from src.dataset.preprocessing import (
    load_processed_dataset,
    normalize_monster_record,
    parse_dice_average,
)
from src.dataset.validation import validate_raw_dataset, validate_single_raw_record
from src.experiments.baselines import (
    create_fixed_baseline_chromosome,
    run_random_search,
)
from src.experiments.evaluation import (
    ALT_COMPOSITION_SEEDS,
    TRAIN_SEEDS,
    VALIDATION_SEEDS,
)
from src.game.characters import (
    Warrior,
    create_ally,
    create_initial_warrior,
    distribute_points_by_weights,
)
from src.game.combat import (
    compute_mitigated_damage,
    run_dungeon_simulation,
    simulate_single_room_combat,
)
from src.game.dungeon import build_dungeon_100_rooms
from src.game.economy import (
    compute_resale_value,
    roll_post_victory_chest,
    try_hire_ally_by_priority,
    try_purchase_equipment_upgrade,
)
from src.game.monsters import (
    adapt_srd_row_to_monster_instance,
    load_balance_config,
)
from src.genetic.chromosome import (
    Chromosome,
    NUM_GENES,
    create_random_chromosome,
    is_valid_chromosome_genes,
    repair_genes,
)
from src.genetic.fitness import compute_lexicographic_fitness, evaluate_chromosome
from src.genetic.operators import (
    apply_elitism,
    compute_population_diversity,
    hybrid_crossover,
    initialize_diverse_population,
    mutate_chromosome,
)
from src.genetic.optimizer import run_genetic_algorithm


@pytest.fixture(scope="module")
def balance_cfg() -> dict[str, Any]:
    return load_balance_config()


@pytest.fixture(scope="module")
def processed_df():
    return load_processed_dataset()


# 1. Coleta de dados com erros de rede
def test_01_network_error_handling_and_snapshot_fallback(tmp_path: Path) -> None:
    """Verifica que falhas HTTP/timeout são tratadas com retry e usam o snapshot real sem inventar dados."""
    class FailingSession:
        def get(self, *args: Any, **kwargs: Any) -> Any:
            raise requests.ConnectionError("Simulated network outage")

    with pytest.raises(DataCollectionError):
        fetch_json_with_retry(
            "https://www.dnd5eapi.co/api/2014/monsters",
            session=FailingSession(),  # type: ignore[arg-type]
            max_retries=2,
            backoff_base=0.01,
        )

    # Verifica que load_or_collect_raw_monsters carrega o snapshot versionado real
    records, manifest = load_or_collect_raw_monsters(force_refresh=False)
    assert len(records) == 334
    assert manifest["integrity_status"] == "VERIFIED"


# 2. Integridade dos dados externos
def test_02_external_dataset_integrity(processed_df) -> None:
    """Verifica a integridade do snapshot bruto, manifesto SHA-256 e dataset processado (334 criaturas)."""
    manifest_path = Path("data/metadata/collection_manifest.json")
    raw_path = Path("data/raw/monsters_raw_srd2014.json")
    assert manifest_path.exists()
    assert raw_path.exists()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["collected_records_count"] == 334
    assert manifest["failed_requests_count"] == 0
    assert len(processed_df) == 334
    assert "goblin" in set(processed_df["index"])
    assert "ancient-red-dragon" in set(processed_df["index"])


# 3. Transformação consistente dos registros
def test_03_consistent_record_transformation() -> None:
    """Verifica que expressões de dados e registros aninhados da API são normalizados consistentemente."""
    assert parse_dice_average("1d6+2") == 5.5
    assert parse_dice_average("2d8+4") == 13.0
    assert parse_dice_average("16d6") == 56.0

    raw_records, _ = load_or_collect_raw_monsters(force_refresh=False)
    goblin_raw = next(r for r in raw_records if r["index"] == "goblin")
    norm = normalize_monster_record(goblin_raw)
    assert norm["index"] == "goblin"
    assert norm["armor_class"] == 15
    assert norm["hit_points"] == 7
    assert norm["challenge_rating"] == 0.25
    assert norm["max_attack_bonus"] == 4
    assert norm["best_action_damage"] == 5.5
    assert norm["source_url"].endswith("/api/2014/monsters/goblin")


# 4. Validação dos atributos dos monstros
def test_04_monster_attribute_validation(balance_cfg, processed_df) -> None:
    """Verifica validação de campos obrigatórios, intervalos [1, 30] e adaptação para combate."""
    raw_records, _ = load_or_collect_raw_monsters(force_refresh=False)
    valid_recs, report = validate_raw_dataset(raw_records)
    assert len(valid_recs) == 334
    assert report.invalid_records_count == 0
    assert len(report.duplicate_indices) == 0

    # Testa detecção de registro corrompido artificialmente
    bad_rec = {"index": "broken-monster", "name": "Broken", "hit_points": -5, "strength": 99}
    bad_res = validate_single_raw_record(bad_rec)
    assert not bad_res.is_valid
    assert len(bad_res.errors) >= 3

    # Verifica adaptação de registro real para instância simulada
    row = processed_df[processed_df["index"] == "goblin"].iloc[0]
    inst = adapt_srd_row_to_monster_instance(row, room_number=1, instance_seq=1, balance_cfg=balance_cfg)
    assert inst.source_index == "goblin"
    assert inst.is_simulated_instance is True
    assert inst.max_hp > 0 and inst.defense > 0
    assert inst.physical_damage > 0


# 5. Reprodutibilidade da masmorra
def test_05_dungeon_reproducibility_by_seed(processed_df, balance_cfg) -> None:
    """Garante que a mesma semente produz exatamente as mesmas 100 salas e sementes diferentes variam."""
    d1 = build_dungeon_100_rooms(processed_df, balance_cfg, seed=101)
    d2 = build_dungeon_100_rooms(processed_df, balance_cfg, seed=101)
    d3 = build_dungeon_100_rooms(processed_df, balance_cfg, seed=202)

    assert len(d1) == 100
    assert [r.to_summary_dict() for r in d1] == [r.to_summary_dict() for r in d2]
    assert [r.to_summary_dict() for r in d1] != [r.to_summary_dict() for r in d3]
    # Progressão crescente de CR alvo da sala 1 à sala 100
    assert d1[0].target_cr < d1[49].target_cr < d1[99].target_cr


# 6. Regras de combate (sem invulnerabilidade e com limite de turnos)
def test_06_combat_rules_no_invulnerability_and_turn_limit(processed_df, balance_cfg) -> None:
    """Garante dano mínimo >= 1 mesmo com defesa extrema, limite de turnos e encerramento na morte do guerreiro."""
    # Mesmo contra defesa 99999 e resistência máxima, o dano mitigado é >= 1
    dmg = compute_mitigated_damage(raw_damage=10.0, target_defense=99999.0, target_resistance=0.99)
    assert dmg >= 1

    rooms = build_dungeon_100_rooms(processed_df, balance_cfg, seed=101)
    warrior = create_initial_warrior(balance_cfg)
    rng = random.Random(42)
    victory, turns, reason, log = simulate_single_room_combat(
        warrior, rooms[0].clone_for_simulation(), balance_cfg, rng, record_log=True
    )
    assert turns <= int(balance_cfg["combat"]["max_turns"])
    assert reason in ("enemies_defeated", "warrior_died", "max_turns_exceeded")
    assert len(log) > 0


# 7. Progressão de níveis e irreversibilidade dos pontos
def test_07_level_progression_and_non_refundable_points(balance_cfg) -> None:
    """Verifica subida de nível por XP e aplicação irreversível de pontos de atributos."""
    w = create_initial_warrior(balance_cfg)
    s0, v0, d0 = w.strength, w.vitality, w.defense
    levels = w.gain_xp_and_evolve(250, attr_weights=(0.6, 0.2, 0.2), balance_cfg=balance_cfg)
    assert levels >= 2
    assert w.level == 1 + levels
    assert (w.strength - s0) + (w.vitality - v0) + (w.defense - d0) == levels * 3
    assert w.strength >= s0 and w.vitality >= v0 and w.defense >= d0

    ds, dv, dd = distribute_points_by_weights(3, (0.5, 0.3, 0.2))
    assert ds + dv + dd == 3


# 8. Contratações e proibição de classes duplicadas
def test_08_ally_hiring_levels_and_no_duplicates(balance_cfg) -> None:
    """Verifica desbloqueio nos níveis 5 e 15, máximo de 2 aliados e proibição de classe duplicada."""
    w = create_initial_warrior(balance_cfg)
    w.gold = 2000
    prios = {"mage": 0.9, "archer": 0.8, "monk": 0.7, "priest": 0.6, "alchemist": 0.5}

    # Nível 1: nenhum slot liberado
    assert w.unlocked_ally_slots(balance_cfg) == 0
    assert try_hire_ally_by_priority(w, prios, balance_cfg) is None

    # Nível 5: 1 slot liberado
    w.level = 5
    assert w.unlocked_ally_slots(balance_cfg) == 1
    tx1 = try_hire_ally_by_priority(w, prios, balance_cfg)
    assert tx1 is not None and tx1["ally_class"] == "mage"
    # Não pode contratar segundo aliado ainda no nível 5
    assert try_hire_ally_by_priority(w, prios, balance_cfg) is None

    # Nível 15: 2 slots liberados; não pode duplicar 'mage'
    w.level = 15
    assert w.unlocked_ally_slots(balance_cfg) == 2
    assert not w.can_hire_ally("mage", balance_cfg)
    tx2 = try_hire_ally_by_priority(w, prios, balance_cfg)
    assert tx2 is not None and tx2["ally_class"] == "archer"
    assert len(w.allies) == 2
    assert len({a.ally_class for a in w.allies}) == 2
    # Terceiro aliado bloqueado
    assert try_hire_ally_by_priority(w, prios, balance_cfg) is None


# 9. Economia sem saldos negativos e venda por 40%
def test_09_economy_no_negative_gold_and_40pct_resale(balance_cfg) -> None:
    """Verifica venda por 40%, bloqueio de compras sem ouro suficiente e desligamento de baús."""
    assert compute_resale_value(100, 0.40) == 40
    w = create_initial_warrior(balance_cfg)
    w.gold = 10  # Insuficiente para comprar arma tier 2 (custo 95)
    assert try_purchase_equipment_upgrade(w, "weapon", balance_cfg) is None
    assert w.gold == 10

    w.gold = 150
    tx = try_purchase_equipment_upgrade(w, "weapon", balance_cfg, min_gold_reserve=10, buy_threshold_multiplier=1.0)
    assert tx is not None
    assert w.weapon_tier == 2
    assert w.gold >= 0

    # Verifica que baús desligados (enable_chests=False) sempre retornam None
    rng = random.Random(1)
    for _ in range(50):
        assert roll_post_victory_chest(w, 20, rng, balance_cfg, enable_chests=False) is None


# 10. Cromossomos válidos e reparo
def test_10_valid_chromosomes_and_repair() -> None:
    """Verifica tamanho fixo de 16 genes, reparo de valores fora do domínio e normalização de pesos."""
    rng = random.Random(99)
    for _ in range(25):
        c = create_random_chromosome(rng)
        assert len(c.genes) == NUM_GENES
        assert is_valid_chromosome_genes(c.genes)

    invalid_raw = [-5.0, 0.0, 0.0, 2.5, -1.0, 0.5, 0.5, 0.5, 0.0, 0.0, 0.0, 9.0, 0.72, 999.0, 0.2, 5.0]
    repaired = repair_genes(invalid_raw)
    assert is_valid_chromosome_genes(repaired)
    assert repaired[12] == 1.0
    assert repaired[13] == 120.0


# 11. Cruzamento e mutação
def test_11_crossover_and_mutation_operators() -> None:
    """Verifica que cruzamento híbrido e mutação produzem descendentes válidos e diversos."""
    rng = random.Random(123)
    p1 = create_random_chromosome(rng)
    p2 = create_random_chromosome(rng)
    c1, c2 = hybrid_crossover(p1, p2, rng=rng, crossover_rate=1.0)
    assert is_valid_chromosome_genes(c1.genes)
    assert is_valid_chromosome_genes(c2.genes)

    m1 = mutate_chromosome(c1, mutation_rate=0.50, rng=rng)
    assert is_valid_chromosome_genes(m1.genes)
    assert m1.genes != c1.genes


# 12. Elitismo
def test_12_elitism_preservation() -> None:
    """Verifica que o operador de elitismo preserva os melhores indivíduos intactos."""
    rng = random.Random(77)
    pop = initialize_diverse_population(10, rng)
    for idx, ind in enumerate(pop):
        ind.fitness = float(idx * 10)
    elites = apply_elitism(pop, elite_count=2)
    assert len(elites) == 2
    assert elites[0].fitness == 90.0
    assert elites[1].fitness == 80.0
    assert compute_population_diversity(pop) > 0.0


# 13. Cálculo da função fitness (prioridade lexicográfica estrita)
def test_13_fitness_strict_room_priority() -> None:
    """Garante que vida restante e ouro nunca invertam a prioridade de avanço de salas."""
    # Estratégia A avançou 80.2 salas com 0% HP e 0 ouro
    f_a = compute_lexicographic_fitness(mean_rooms=80.2, mean_hp_ratio=0.0, mean_gold=0.0)
    # Estratégia B avançou 80.0 salas com 100% HP e 5000 ouro
    f_b = compute_lexicographic_fitness(mean_rooms=80.0, mean_hp_ratio=1.0, mean_gold=5000.0)
    assert f_a > f_b

    # Em caso de empate exato de salas (80.0 vs 80.0), maior HP e ouro desempatam positivamente
    f_c = compute_lexicographic_fitness(mean_rooms=80.0, mean_hp_ratio=0.8, mean_gold=500.0)
    f_d = compute_lexicographic_fitness(mean_rooms=80.0, mean_hp_ratio=0.2, mean_gold=100.0)
    assert f_c > f_d


# 14. Comparação de baselines e orçamento equivalente
def test_14_baselines_and_equivalent_budget(processed_df, balance_cfg) -> None:
    """Verifica execução de Baseline Fixo, Busca Aleatória e AG com mesmo orçamento de avaliações."""
    d_suite = {101: build_dungeon_100_rooms(processed_df, balance_cfg, seed=101)}
    fb = create_fixed_baseline_chromosome()
    evaluate_chromosome(fb, d_suite, balance_cfg)
    assert fb.mean_rooms_cleared > 0

    rs = run_random_search(d_suite, balance_cfg, budget_evaluations=8, seed=11)
    ga = run_genetic_algorithm(
        d_suite, balance_cfg, pop_size=4, generations=10, max_evaluations=8, seed=11
    )
    assert rs.budget_evaluations == ga.total_objective_evaluations == 8


# 15. Separação entre otimização e validação final
def test_15_separation_between_train_and_validation_seeds() -> None:
    """Garante disjunção estrita entre sementes de treinamento, validação e composições alternativas."""
    train_set = set(TRAIN_SEEDS)
    val_set = set(VALIDATION_SEEDS)
    alt_set = set(ALT_COMPOSITION_SEEDS)
    assert train_set.isdisjoint(val_set)
    assert train_set.isdisjoint(alt_set)
    assert val_set.isdisjoint(alt_set)


# 16. Execução das 100 salas com rastreabilidade ao SRD
def test_16_full_100_rooms_execution_and_srd_traceability(processed_df, balance_cfg) -> None:
    """Verifica execução da simulação completa de 100 salas e rastreabilidade dos monstros ao SRD."""
    rooms = build_dungeon_100_rooms(processed_df, balance_cfg, seed=101)
    assert len(rooms) == 100
    srd_indices = set(processed_df["index"])
    for r in rooms:
        assert len(r.enemies) >= 1
        for e in r.enemies:
            assert e.source_index in srd_indices
            assert e.source_url.startswith("https://www.dnd5eapi.co/api/2014/monsters/")

    fb = create_fixed_baseline_chromosome()
    run_res = run_dungeon_simulation(rooms, fb.to_policy_params(), balance_cfg, seed=101, record_detailed_logs=True)
    assert 1 <= run_res.rooms_cleared <= 100
    assert len(run_res.room_results) >= run_res.rooms_cleared


# 17. Funcionamento e estrutura dos artefatos para aplicação publicada
def test_17_published_app_artifacts_and_dependencies() -> None:
    """Verifica presença dos arquivos de deploy, dataset congelado, resultados de EDA e 4 experimentos."""
    assert Path("app.py").exists()
    assert Path("requirements.txt").exists()
    assert Path(".streamlit/config.toml").exists()
    assert Path("config/balance.json").exists()
    assert Path("data/processed/monsters_srd2014_processed.parquet").exists()
    assert Path("data/processed/monsters_srd2014_processed.csv").exists()
    assert Path("results/eda/eda_summary.json").exists()
    exp_file = Path("data/experiments/scientific_experiments_v1.json")
    assert exp_file.exists()
    exp_data = json.loads(exp_file.read_text(encoding="utf-8"))
    assert "experiment_1_mutation" in exp_data
    assert "experiment_2_population" in exp_data
    assert "experiment_3_baselines" in exp_data
    assert "experiment_4_generalization" in exp_data
    assert "failure_and_dominance_analysis" in exp_data
