"""Telas da aplicação que usam o motor compartilhado de simulação."""

from __future__ import annotations

import copy
from html import escape
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.dataset.provenance import PROJECT_ROOT, inspect_snapshot
from src.experiments.baselines import create_fixed_baseline_chromosome
from src.game.combat import DungeonRunResult, run_dungeon_simulation
from src.game.dungeon import build_dungeon_100_rooms
from src.genetic.chromosome import Chromosome
from src.genetic.optimizer import GenerationRecord, run_genetic_algorithm
from src.services.journey import journey_report, search_journey, simulate_journey
from src.ui.design import BRASS, GREEN, RED, atlas_html, creature_seal, heading, section_label, strategy_summary
from src.ui.experience import ALLY_OPTIONS, EQUIPMENT_OPTIONS, FOCUS_PRESETS, make_manual_strategy, termination_label
from src.ui.localization import ALLY_CLASS_LABELS, GENE_FRIENDLY_INFO


AUTO_SEARCH_BUDGET = 400
AUTO_POPULATION_SIZE = 16


def _navigate(page: str) -> None:
    st.session_state["page"] = page


def _start_automatically() -> None:
    st.session_state["auto_start_requested"] = True
    _navigate("Aventura")


def _use_demo() -> None:
    st.session_state.pop("journey", None)
    st.session_state["adventure_mode"] = "Treino demonstrativo"
    _navigate("Aventura")


def _champion(payload: dict | None) -> Chromosome | None:
    try:
        return Chromosome(genes=payload["best_champion_strategy"]["best_chromosome"]["genes"])
    except (TypeError, KeyError, ValueError):
        return None


def _heading(kicker: str, title: str, text: str) -> None:
    heading(kicker, title, text)


def home(monsters: pd.DataFrame, manifest: dict) -> None:
    st.html('<div class="folio"><span>Atlas de estratégias / Inteligência Artificial II</span>'
            '<span>FIB · Caderno 07 / 2026</span></div>')
    left, right = st.columns([1.1, 1], gap="large")
    with left:
        st.html('''<div class="eyebrow">Evolução de estratégias em 100 salas</div>
            <h1 class="hero-title">Quem chega à<br><em>centésima sala?</em></h1>
            <p class="hero-copy">Força bruta nem sempre resolve. Decida como evoluir,
            quem levar e onde gastar o ouro. Depois, coloque sua estratégia à prova.</p>''')
        st.button("Treinar e iniciar automaticamente", type="primary", on_click=_start_automatically,
                  use_container_width=True)
        st.button("Montar minha estratégia", on_click=_navigate, args=("Aventura",), use_container_width=True)
        st.html('<div class="hero-meta">O algoritmo testa combinações de atributos, aliados e compras.<br>'
                'Você acompanha o resultado, sala por sala.</div>')
    with right:
        st.html(atlas_html())

    st.html(f'''<div class="fact-strip"><div><strong>100</strong><span>salas para atravessar</span></div>
        <div><strong>{len(monsters)}</strong><span>criaturas no dataset</span></div>
        <div><strong>16</strong><span>genes por estratégia</span></div></div>''')
    section_label("01", "O que vale uma boa estratégia?", "A pergunta do experimento")
    research, paths = st.columns([1.05, 1], gap="large")
    with research:
        st.write("Nosso objetivo é fazer o guerreiro avançar mais. O algoritmo genético procura combinações de escolhas e enfrenta os mesmos cenários que uma regra fixa e uma busca aleatória.")
        st.caption("As criaturas vêm de uma base externa. As batalhas e as regras de adaptação são simulações do grupo.")
        st.button("De onde vêm as criaturas? →", on_click=_navigate, args=("Dados e fonte",))
    with paths:
        st.html('''<div class="research-row"><span>I</span><div><strong>Prepare o guerreiro</strong>
            <p>Escolha o foco dos atributos, um aliado e a prioridade de compra.</p></div></div>
            <div class="research-row"><span>II</span><div><strong>Leia os encontros</strong>
            <p>Veja onde a estratégia resiste e em qual sala ela falha.</p></div></div>
            <div class="research-row"><span>III</span><div><strong>Confira as evidências</strong>
            <p>Compare os métodos e os limites dos resultados em outras masmorras.</p></div></div>''')
    with st.expander("Sobre o projeto e os integrantes"):
        st.write("Trabalho de Inteligência Artificial II das Faculdades Integradas de Bauru (FIB).")
        st.write("Eduardo Coque Corrêa de Lima · Fernando Eduardo Motta Mendes · Matheus Alcântara Pereira · Reuel Vitor Lanzetti · Rogério Tiritan Marcone")
        if manifest.get("collected_at_utc"):
            st.caption(f"Dados coletados em {manifest['collected_at_utc'][:10]} · versão {manifest.get('dataset_version', 'não informada')}")
        st.markdown("[Fonte dos dados: D&D 5e SRD API](https://docs.dnd5eapi.co/) · [SRD 5.1 e atribuição](https://www.dndbeyond.com/srd)")


def adventure(monsters: pd.DataFrame, settings: dict, payload: dict | None) -> None:
    _heading("Caderno de expedição", "Entre na masmorra", "Prepare o guerreiro. As escolhas guiam as compras, a evolução e os combates das 100 salas.")
    champion = _champion(payload)
    if st.session_state.pop("auto_start_requested", False):
        _run_automatic_journey(monsters, settings, champion,
                               int(st.session_state.get("adventure_seed", 201)),
                               bool(st.session_state.get("adventure_chests", True)))
    has_journey = bool(st.session_state.get("journey"))
    with st.expander("Preparar outra jornada" if has_journey else "Configurar uma jornada", expanded=not has_journey):
        modes = ["Minha estratégia", "Estratégia fixa"]
        if champion is not None:
            modes.append("Estratégia do algoritmo")
        if st.session_state.get("demo_result") is not None:
            modes.append("Treino demonstrativo")
        mode = st.radio("Quem escolhe a estratégia?", modes, horizontal=True, key="adventure_mode")

        if mode == "Minha estratégia":
            a, b, c = st.columns(3)
            with a:
                focus = st.selectbox("Evolução do guerreiro", list(FOCUS_PRESETS))
            with b:
                ally = st.selectbox("Aliado preferido", list(ALLY_OPTIONS))
            with c:
                equipment = st.selectbox("Prioridade no mercado", list(EQUIPMENT_OPTIONS))
            strategy = make_manual_strategy(focus, ally, equipment)
            st.caption("O aliado escolhido tem prioridade quando houver nível e ouro suficientes. As compras e os combates são automáticos.")
        elif mode == "Estratégia fixa":
            strategy = create_fixed_baseline_chromosome()
            st.caption("Uma regra equilibrada definida pelo grupo serve de referência para as comparações.")
        elif mode == "Estratégia do algoritmo":
            strategy = champion
            st.caption("Estratégia selecionada pelo desempenho durante o treinamento científico.")
        else:
            strategy = Chromosome(genes=st.session_state["demo_result"].best_chromosome.genes)
            st.caption("Estratégia encontrada na demonstração que você executou nesta sessão.")

        policy = strategy.to_policy_params()
        preferred = max(policy["ally_priorities"], key=policy["ally_priorities"].get)
        strategy_summary(policy["warrior_attr_weights"], ALLY_CLASS_LABELS[preferred]["nome"],
                         "Proteção primeiro" if policy["equip_offense_priority"] <= 0.4 else "Arma primeiro")

        seed_col, chest_col = st.columns(2)
        seed = seed_col.number_input("Número da masmorra", min_value=1, max_value=99999, value=201, step=1, key="adventure_seed",
                                     help="O mesmo número gera as mesmas salas; serve para repetir o teste.")
        chests = chest_col.checkbox("Permitir baús após vitórias", value=True, key="adventure_chests")

        if champion is None:
            st.info("Os resultados científicos atualizados ainda não estão disponíveis. Você pode usar a estratégia manual e a fixa.")

        auto_button, manual_button = st.columns(2)
        automatic = auto_button.button("Treinar e jogar automaticamente", type="primary")
        manual = manual_button.button("Iniciar com esta estratégia")
        if automatic:
            _run_automatic_journey(monsters, settings, champion, int(seed), chests)

        if manual:
            with st.spinner("Preparando as salas e simulando os combates..."):
                st.session_state["journey"] = simulate_journey(monsters, settings, int(seed), chests, strategy, mode, champion)
                st.session_state.pop("attempt_replay", None)
            st.rerun()

    journey = st.session_state.get("journey")
    if not journey:
        notes, map_column = st.columns([1, 1], gap="large")
        with notes:
            st.html('''<div class="field-note"><h3>Antes de abrir a primeira porta</h3>
                <p>A vida é recuperada parcialmente entre combates. O ouro pode virar equipamento
                ou pagar um aliado. Uma escolha que ajuda no começo pode custar caro nas últimas salas.</p></div>''')
            st.caption("Inicie com seu plano ou deixe o algoritmo procurar uma estratégia. O número da masmorra permite repetir os mesmos encontros.")
        with map_column:
            st.html(atlas_html())
        return

    player: DungeonRunResult = journey["player"]
    rooms = journey["rooms"]
    if not player.room_results:
        st.warning("Não há salas registradas para esta tentativa.")
        return

    index = min(journey["index"], len(player.room_results) - 1)
    room_result = player.room_results[index]
    room = rooms[room_result.room_number - 1]
    st.divider()
    st.caption(f"Jornada: {journey['mode']} · masmorra {journey['seed']} · baús {'ativados' if journey['chests'] else 'desativados'}")
    if journey.get("training") is not None:
        training = journey["training"]
        selected_strategy = journey["selected_strategy"]
        genes = selected_strategy.to_named_dict()
        preferred = max(ALLY_OPTIONS, key=lambda name: genes[f"ally_prio_{ALLY_OPTIONS[name]}"])
        score, learned = st.columns(2)
        score.metric("Salas concluídas na jornada", f"{player.rooms_cleared} / 100")
        learned.metric("Média nas masmorras da busca", f"{selected_strategy.mean_rooms_cleared:.1f} / 100")
        if player.completed_all_100:
            st.success(f"Objetivo alcançado: uma estratégia venceu as 100 salas da masmorra {journey['seed']}.")
        else:
            st.warning(f"Após {journey['total_evaluations']} estratégias, ainda não houve uma vitória completa. A melhor tentativa concluiu {player.rooms_cleared} salas; você pode continuar a busca.")
            if st.button("Continuar procurando", type="primary"):
                _run_automatic_journey(monsters, settings, champion, journey["seed"], journey["chests"], previous=journey)
        with st.expander("Como a estratégia foi escolhida"):
            st.write(f"A estratégia prioriza {preferred} e investe {genes['w_weight_str'] * 100:.0f}% em força, {genes['w_weight_vit'] * 100:.0f}% em vida e {genes['w_weight_def'] * 100:.0f}% em defesa.")
            st.write(f"Foram avaliadas {journey['total_evaluations']} estratégias em {journey['search_round']} rodada(s) de busca. A última rodada teve {len(training.history)} gerações.")
            st.caption("A masmorra escolhida participa da busca, junto com as sementes 101 a 105. Vencer esse cenário não garante vitória em todas as masmorras nem prova que a estratégia seja a melhor possível.")
            st.caption("Os experimentos científicos usam avaliação separada e continuam disponíveis em Resultados.")
    st.subheader(f"Sala {room_result.room_number} de 100")
    st.progress(room_result.room_number / 100, text=f"Explorando a sala {room_result.room_number} de 100")
    st.caption("Registro de uma simulação já concluída. Os controles abaixo permitem rever cada encontro.")

    first, previous, next_room, advance, finish = st.columns(5)
    if first.button("Início", disabled=index == 0):
        journey["index"] = 0
        st.rerun()
    if previous.button("← Anterior", disabled=index == 0):
        journey["index"] = max(0, index - 1)
        st.rerun()
    if next_room.button("Próxima sala →", type="primary", disabled=index == len(player.room_results) - 1):
        journey["index"] = index + 1
        st.rerun()
    if advance.button("Avançar 5 salas", disabled=index == len(player.room_results) - 1):
        journey["index"] = min(index + 5, len(player.room_results) - 1)
        st.rerun()
    if finish.button("Ver final", disabled=index == len(player.room_results) - 1):
        journey["index"] = len(player.room_results) - 1
        st.rerun()

    with st.expander("Mapa da expedição · ir direto a uma sala"):
        map_column, note_column = st.columns([1.1, 1])
        with map_column:
            st.html(atlas_html(room_result.room_number, player.failure_room))
        with note_column:
            selected_room = st.select_slider("Ir para uma sala registrada", options=list(range(1, len(player.room_results) + 1)),
                                             value=index + 1)
            if selected_room != index + 1:
                journey["index"] = selected_room - 1
                st.rerun()
            st.caption("O mapa organiza a ordem dos encontros. A posição dos quadrados é esquemática; o personagem percorre as salas em sequência.")

    left, right = st.columns([1, 1], gap="large")
    with left:
        with st.container(border=True):
            st.markdown("#### O encontro")
            for enemy in room.enemies:
                st.html(f'<div class="encounter-creature">{creature_seal(enemy.creature_type)}'
                        f'<strong>{escape(enemy.source_name)}</strong></div>')
                st.caption(f"Desafio {enemy.challenge_rating:g} · Vida adaptada {enemy.max_hp} · Defesa {enemy.defense:.1f}")
                st.markdown(f"[Ver registro de {enemy.source_name} na fonte]({enemy.source_url})")
            st.caption("Os nomes originais das criaturas estão em inglês. Os valores de combate são adaptados pelo projeto.")
    with right:
        with st.container(border=True):
            st.markdown("#### Depois da luta")
            st.write("Vitória" if room_result.victory else termination_label(room_result.termination_reason))
            st.write(f"Vida: **{room_result.warrior_hp_end} / {room_result.warrior_max_hp}** · Nível **{room_result.warrior_level_end}**")
            st.progress(min(1.0, max(0.0, room_result.warrior_hp_end / max(1, room_result.warrior_max_hp))))
            st.write(f"Ouro: **{room_result.gold_end}** · Turnos: **{room_result.turns_taken}**")
            st.caption("Aliados ao fim da sala: " + (", ".join(room_result.active_allies_end) or "nenhum"))
            equipment_names = []
            for category, tier in (("weapons", room_result.weapon_tier_end), ("armors", room_result.armor_tier_end),
                                   ("shields", room_result.shield_tier_end)):
                item = next((item for item in settings["economy"][category] if item["tier"] == tier), None)
                if item:
                    equipment_names.append(item["name"])
            st.caption("Equipamentos: " + ", ".join(equipment_names))
            if room_result.victory:
                st.caption("A vida exibida já considera a recuperação entre salas.")

    events = []
    for tx in room_result.market_transactions:
        if tx.get("action") == "buy_equipment":
            events.append(f"Comprou {tx.get('item_name')} por {tx.get('net_cost')} moedas.")
        elif tx.get("action") == "hire_ally":
            events.append(f"Contratou {tx.get('ally_name')} por {tx.get('cost')} moedas.")
    if room_result.chest_event:
        event = room_result.chest_event
        verb = "equipou" if event.get("event") == "chest_equip" else "vendeu"
        events.append(f"Encontrou {event.get('item_name')} em um baú e {verb} o item.")
    if events:
        st.write("**Decisões e descobertas:** " + " ".join(events))
    with st.expander("Ver os turnos do combate"):
        if room_result.combat_log:
            for line in room_result.combat_log:
                st.write(line)
        else:
            st.write("Não há ações registradas nesta sala.")

    with st.expander("Histórico das salas acompanhadas"):
        history = [{"Sala": item.room_number, "Resultado": "Vitória" if item.victory else "Tentativa encerrada",
                    "Vida após a sala": item.warrior_hp_end, "Ouro": item.gold_end,
                    "Criaturas": ", ".join(item.enemies_faced)} for item in player.room_results[:index + 1]]
        st.dataframe(pd.DataFrame(history), hide_index=True)

    if index == len(player.room_results) - 1:
        if player.completed_all_100:
            st.success("Sua estratégia concluiu as 100 salas.")
        else:
            st.info(f"A jornada terminou na sala {player.failure_room}. {termination_label(player.failure_reason)}")

    with st.expander("Comparar as tentativas", expanded=index == len(player.room_results) - 1):
        st.caption("As estratégias usam a mesma masmorra, número e regras. A sequência de eventos aleatórios pode variar conforme as decisões.")
        comparisons = journey["comparisons"]
        columns = st.columns(1 + len(comparisons))
        columns[0].metric(journey["mode"], f"{player.rooms_cleared} / 100 salas")
        for col, (name, rival) in zip(columns[1:], comparisons):
            col.metric(name, f"{rival.rooms_cleared} / 100 salas")
        if champion is None:
            st.caption("A estratégia científica salva ficará disponível com os resultados atualizados.")
        st.caption("Esta comparação mostra uma tentativa por estratégia; os experimentos avaliam várias masmorras.")

    if journey.get("training") is not None:
        _render_search_history(journey, settings)
    st.download_button("Salvar relatório da jornada", data=journey_report(journey, settings),
                       file_name=f"masmorra-{journey['seed']}-jornada.json", mime="application/json")


def _run_automatic_journey(monsters: pd.DataFrame, settings: dict, champion: Chromosome | None,
                           seed: int, chests: bool, previous: dict | None = None) -> None:
    progress = st.progress(0.0, text="Preparando as masmorras para a busca...")
    details = st.empty()

    def report(status: dict) -> None:
        progress.progress(status["round_evaluations"] / status["budget"],
                          text=f"{status['round_evaluations']} de {status['budget']} estratégias nesta rodada")
        details.caption(f"Melhor avanço: {status['best_rooms']}/100 salas · "
                        f"{status['evaluations']} estratégias no histórico · geração {status['generation']}")

    try:
        journey = search_journey(monsters, settings, seed, chests, champion,
                                 budget=AUTO_SEARCH_BUDGET, population=AUTO_POPULATION_SIZE,
                                 previous=previous, on_progress=report)
    except ValueError as exc:
        progress.empty()
        details.empty()
        st.error(str(exc))
        return
    st.session_state["journey"] = journey
    st.session_state.pop("attempt_replay", None)
    st.rerun()


def _render_search_history(journey: dict, settings: dict) -> None:
    attempts = journey.get("attempts", [])
    if not attempts:
        st.info("O histórico de estratégias aparece quando você inicia uma nova busca automática.")
        return

    with st.expander("Ver tentativas anteriores e evolução", expanded=False):
        st.write("Cada ponto é uma estratégia testada na masmorra escolhida. A linha mostra o melhor resultado encontrado até aquele momento.")
        st.caption("O histórico fica nesta sessão e inclui as rodadas feitas com ‘Continuar procurando’. Uma nova busca começa outro histórico.")
        count, incomplete, best = st.columns(3)
        count.metric("Estratégias avaliadas", len(attempts))
        incomplete.metric("Não concluíram", sum(not item["completed"] for item in attempts))
        best.metric("Maior avanço", f"{attempts[-1]['best_so_far']} / 100")
        fig = go.Figure()
        custom = [[item["round"], item["generation"]] for item in attempts]
        fig.add_scatter(
            x=[item["number"] for item in attempts], y=[item["rooms_cleared"] for item in attempts],
            mode="markers", name="Cada estratégia", marker=dict(color=GREEN, size=8, opacity=0.75),
            customdata=custom,
            hovertemplate="Tentativa %{x}<br>Salas concluídas: %{y}<br>Rodada: %{customdata[0]}<br>Geração: %{customdata[1]}<extra></extra>",
        )
        fig.add_scatter(
            x=[item["number"] for item in attempts], y=[item["best_so_far"] for item in attempts],
            mode="lines", name="Melhor até então", line=dict(color=RED, width=3, shape="hv"),
            hovertemplate="Até a tentativa %{x}<br>Melhor resultado: %{y} salas<extra></extra>",
        )
        fig.update_layout(xaxis_title="Número da tentativa", yaxis_title="Salas concluídas", yaxis_range=[0, 105],
                          margin=dict(l=5, r=5, t=15, b=5))
        st.plotly_chart(fig)
        st.download_button("Baixar histórico das tentativas", pd.DataFrame(attempts).drop(columns="genes").to_csv(index=False).encode("utf-8-sig"),
                           file_name=f"masmorra-{journey['seed']}-tentativas.csv", mime="text/csv")

        if st.checkbox("Mostrar todas as tentativas"):
            rows = [{"Tentativa": item["number"], "Rodada": item["round"], "Geração": item["generation"],
                     "Salas concluídas": item["rooms_cleared"],
                     "Fim": "Concluiu 100 salas" if item["completed"] else f"Sala {item['failure_room']}: {termination_label(item['failure_reason'])}",
                     "Inimigos no fim": ", ".join(item["enemies"])} for item in attempts]
            st.dataframe(pd.DataFrame(rows), hide_index=True)

        st.markdown("#### Compare duas estratégias")
        by_number = {item["number"]: item for item in attempts}
        options = list(by_number)
        first_failure = next((item for item in attempts if not item["completed"]), attempts[0])
        selected_genes = journey["selected_strategy"].genes
        chosen = next((item for item in reversed(attempts) if item["genes"] == selected_genes), attempts[-1])

        def label(number: int) -> str:
            item = by_number[number]
            outcome = "venceu" if item["completed"] else f"parou na sala {item['failure_room']}"
            return f"#{number} · rodada {item['round']}, geração {item['generation']} · {item['rooms_cleared']}/100 · {outcome}"

        left, right = st.columns(2)
        first = left.selectbox("Tentativa anterior", options, index=options.index(first_failure["number"]), format_func=label)
        second = right.selectbox("Comparar com", options, index=options.index(chosen["number"]), format_func=label)
        a, b = by_number[first], by_number[second]

        def ally_name(class_name: str) -> str:
            return ALLY_CLASS_LABELS.get(class_name, {}).get("nome", class_name)

        def points(item: dict) -> str:
            return " / ".join(f"{value * 100:.0f}%" for value in item["warrior_weights"])

        def finish(item: dict) -> str:
            return "Concluiu as 100 salas" if item["completed"] else f"Sala {item['failure_room']} — {termination_label(item['failure_reason'])}"

        def items(item: dict) -> str:
            return f"Arma {item['weapon_tier']} · Armadura {item['armor_tier']} · Escudo {item['shield_tier']}"

        def allies(item: dict) -> str:
            return ", ".join(ally_name(name) for name in item["allies"]) or "Nenhum"

        def market(item: dict) -> str:
            return "Proteção primeiro" if item["equipment_priority"] <= 0.40 else "Arma primeiro"

        rows = [
            ("Salas concluídas", a["rooms_cleared"], b["rooms_cleared"]),
            ("Como terminou", finish(a), finish(b)),
            ("Inimigos no último encontro", ", ".join(a["enemies"]), ", ".join(b["enemies"])),
            ("Nível do guerreiro", a["level"], b["level"]),
            ("Vida ao fim da sala", f"{a['health']} / {a['max_health']}", f"{b['health']} / {b['max_health']}"),
            ("Atributos finais: força / vitalidade / defesa", f"{a['strength']} / {a['vitality']} / {a['defense']}", f"{b['strength']} / {b['vitality']} / {b['defense']}"),
            ("Foco escolhido: força / vida / defesa", points(a), points(b)),
            ("Aliado prioritário", ally_name(a["preferred_ally"]), ally_name(b["preferred_ally"])),
            ("Prioridade no mercado", market(a), market(b)),
            ("Aliados ao final", allies(a), allies(b)),
            ("Equipamentos ao final", items(a), items(b)),
            ("Ouro ao final", a["gold"], b["gold"]),
        ]
        comparison = pd.DataFrame(rows, columns=["O que comparar", f"Anterior (#{first})", f"Comparação (#{second})"])
        st.dataframe(comparison.astype(str), hide_index=True)
        difference = b["rooms_cleared"] - a["rooms_cleared"]
        st.write(f"Diferença: **{difference:+d} salas** da tentativa #{first} para a #{second}.")
        st.caption("Nas salas vencidas, a vida final inclui a recuperação. As diferenças observadas não provam, sozinhas, qual decisão causou o resultado.")

        if st.button("Rever o combate final da tentativa anterior"):
            replay = run_dungeon_simulation(
                journey["rooms"], Chromosome(genes=a["genes"]).to_policy_params(), settings,
                seed=journey["seed"], enable_chests=journey["chests"], record_detailed_logs=True,
            )
            st.session_state["attempt_replay"] = {"seed": journey["seed"], "chests": journey["chests"],
                                                   "genes": a["genes"], "result": replay}
        replay_data = st.session_state.get("attempt_replay")
        if (replay_data and replay_data["seed"] == journey["seed"] and
                replay_data.get("chests") == journey["chests"] and replay_data["genes"] == a["genes"]):
            replay = replay_data["result"]
            if (replay.rooms_cleared != a["rooms_cleared"] or replay.completed_all_100 != a["completed"] or
                    replay.failure_room != a["failure_room"] or replay.failure_reason != a["failure_reason"]):
                st.warning("A reprodução não coincidiu com o resultado registrado, então o combate não será exibido.")
            elif replay.room_results:
                final_room = replay.room_results[-1]
                st.markdown(f"**Combate final da tentativa #{first} · sala {final_room.room_number}**")
                st.write("Inimigos: " + ", ".join(final_room.enemies_faced))
                st.code("\n".join(final_room.combat_log) if final_room.combat_log else "Não há ações registradas.")


def evolution(monsters: pd.DataFrame, settings: dict, payload: dict | None) -> None:
    _heading("A ideia por trás do projeto", "Como uma estratégia evolui?", "O algoritmo testa várias formas de jogar e cria novas combinações a partir das melhores.")
    a, b, c = st.columns(3)
    for col, title, body in [
        (a, "1 · Criar", "Cada estratégia escolhe como evoluir, comprar e contratar."),
        (b, "2 · Testar", "Todas enfrentam as mesmas masmorras de treinamento."),
        (c, "3 · Evoluir", "As melhores são combinadas e recebem pequenas alterações."),
    ]:
        with col:
            with st.container(border=True):
                st.markdown(f"#### {title}")
                st.write(body)
    st.caption("O processo busca boas soluções; ele não garante encontrar a melhor estratégia possível.")

    official, demo = st.tabs(["Experimento do grupo", "Faça uma demonstração"])
    with official:
        if _champion(payload) is None:
            st.info("Os resultados científicos atualizados ainda não estão disponíveis.")
        else:
            recorded = payload["best_champion_strategy"]
            history = pd.DataFrame(recorded["history"])
            st.write("A curva mostra o desempenho no treinamento da estratégia escolhida pelo grupo.")
            m1, m2, m3 = st.columns(3)
            m1.metric("Melhor média no treino", f"{recorded['best_chromosome']['mean_rooms_cleared']:.1f} salas")
            m2.metric("Estratégias avaliadas", recorded["total_objective_evaluations"])
            m3.metric("Masmorras simuladas", recorded["total_simulation_runs"])
            chart = go.Figure()
            chart.add_scatter(x=history["generation"], y=history["best_mean_rooms"], mode="lines+markers", name="Melhor estratégia")
            chart.add_scatter(x=history["generation"], y=history["pop_mean_rooms"], mode="lines+markers", name="Média da população")
            chart.update_layout(xaxis_title="Geração", yaxis_title="Média de salas no treino", yaxis_range=[0, 105])
            st.plotly_chart(chart)
            st.caption("A métrica principal é a média de salas concluídas nas masmorras de treino. A validação é apresentada em Resultados.")
            with st.expander("Ver as decisões da estratégia"):
                _show_genes(_champion(payload))

    with demo:
        st.write("Teste uma execução menor. Ela usa três masmorras e pode produzir uma estratégia diferente do experimento do grupo.")
        p, g, m = st.columns(3)
        population = p.slider("Estratégias por geração", 6, 20, 10, 2)
        generations = g.slider("Número de gerações", 3, 12, 6)
        mutation = m.slider("Chance de alteração", 0.02, 0.30, 0.10, 0.02, format="%.2f")
        st.caption("A chance de alteração é a taxa de mutação: ela controla a frequência de mudanças nos genes.")
        if st.button("Executar demonstração", type="primary"):
            progress = st.progress(0.0, text="Preparando as masmorras...")
            chart_slot = st.empty()
            records: list[dict[str, Any]] = []

            def report(record: GenerationRecord) -> None:
                records.append({"Geração": record.generation, "Melhor média no treino": record.best_mean_rooms})
                progress.progress(min(record.generation / generations, 1.0), text=f"Geração {record.generation} de {generations}")
                chart_slot.line_chart(pd.DataFrame(records).set_index("Geração"))

            suites = {s: build_dungeon_100_rooms(monsters, settings, seed=s) for s in (101, 102, 103)}
            result = run_genetic_algorithm(suites, settings, pop_size=int(population), generations=int(generations),
                                           mutation_rate=float(mutation), seed=42, on_generation=report)
            st.session_state["demo_result"] = result
            progress.empty()
            chart_slot.empty()

        demo_result = st.session_state.get("demo_result")
        if demo_result is not None:
            st.success(f"Demonstração concluída: média de {demo_result.best_chromosome.mean_rooms_cleared:.1f} salas nas três masmorras de treino.")
            hist = pd.DataFrame([record.to_dict() for record in demo_result.history])
            st.line_chart(hist.set_index("generation")[["best_mean_rooms"]].rename(columns={"best_mean_rooms": "Melhor média no treino"}))
            st.caption(f"{demo_result.total_objective_evaluations} estratégias avaliadas · {demo_result.elapsed_seconds:.1f} segundos · sementes 101, 102 e 103")
            st.button("Usar esta estratégia na aventura", on_click=_use_demo)


def _show_genes(chromosome: Chromosome) -> None:
    rows = []
    for name, value in chromosome.to_named_dict().items():
        info = GENE_FRIENDLY_INFO.get(name, {"nome": name, "explicacao": "Parâmetro da estratégia."})
        if "discrete" in name:
            formatted = "Sim" if value >= 0.5 else "Não"
        elif "reserve" in name:
            formatted = f"{value:.0f} moedas"
        elif "threshold" in name:
            formatted = f"{value:.2f} vezes o custo"
        else:
            formatted = f"{value:.2f}"
        rows.append({"Escolha": info["nome"], "Valor": formatted, "Significado": info["explicacao"]})
    st.dataframe(pd.DataFrame(rows), hide_index=True)


def results(payload: dict | None) -> None:
    _heading("O que aconteceu nos testes", "Resultados e limites", "Comparamos estratégias em várias masmorras e observamos onde cada uma funciona ou falha.")
    if not payload:
        st.warning("Os resultados atualizados ainda não foram gerados. Execute o script científico para disponibilizá-los.")
        return
    exp = payload["experiment_3_baselines"]
    methods = exp["methods"]
    fixed, random, genetic = methods["fixed_baseline"], methods["random_search"], methods["genetic_algorithm"]
    comparison = pd.DataFrame([
        {"Método": "Estratégia fixa", "Média de salas": fixed["val_mean_rooms"], "Conclusão (%)": fixed["val_completion_rate"] * 100},
        {"Método": "Busca aleatória", "Média de salas": random["val_rooms_across_repeats"]["mean"], "Conclusão (%)": random["val_completion_rate_mean"] * 100},
        {"Método": "Algoritmo genético", "Média de salas": genetic["val_rooms_across_repeats"]["mean"], "Conclusão (%)": genetic["val_completion_rate_mean"] * 100},
    ])
    st.subheader("Quantas salas cada método concluiu?")
    fig = px.bar(comparison, x="Método", y="Média de salas", text_auto=".1f", color="Método",
                 color_discrete_sequence=["#8e8778", BRASS, RED])
    fig.update_layout(showlegend=False, yaxis_range=[0, 105], margin=dict(l=5, r=5, t=10, b=5))
    st.plotly_chart(fig)
    st.dataframe(comparison.round(2), hide_index=True)
    n_repeats = exp["n_independent_repeats"]
    st.caption(f"Média de validação: {len(exp['validation_seeds'])} masmorras. Busca aleatória e algoritmo genético foram repetidos {n_repeats} vezes; a estratégia fixa foi avaliada uma vez no mesmo conjunto.")
    st.caption(f"Busca aleatória e algoritmo genético: {exp['budget_objective_evaluations_per_run']} avaliações efetivas por repetição. A última geração pode ser parcial.")
    with st.expander("Ver métricas e tempo"):
        details = pd.DataFrame([
            {"Método": "Estratégia fixa", "Mediana por simulação": fixed["val_median_rooms"],
             "Desvio por simulação": fixed["val_std_rooms"], "Avaliações na busca": 1,
             "Tempo médio da busca (s)": None},
            {"Método": "Busca aleatória", "Mediana por simulação": random["pooled_val_rooms_all_seeds"]["median"],
             "Desvio por simulação": random["pooled_val_rooms_all_seeds"]["std"],
             "Avaliações na busca": random["objective_evaluations_per_run"], "Tempo médio da busca (s)": random["mean_elapsed_seconds"]},
            {"Método": "Algoritmo genético", "Mediana por simulação": genetic["pooled_val_rooms_all_seeds"]["median"],
             "Desvio por simulação": genetic["pooled_val_rooms_all_seeds"]["std"],
             "Avaliações na busca": genetic["objective_evaluations_per_run"], "Tempo médio da busca (s)": genetic["mean_elapsed_seconds"]},
        ])
        st.dataframe(details.round(2), hide_index=True)
        st.caption("Mediana e desvio descrevem as simulações de validação reunidas. O tempo mostrado é apenas o de busca; a estratégia fixa não passou por uma busca.")
    st.info("Uma execução pode ter um resultado diferente da média. A busca genética não precisa vencer todas as comparações para que o experimento seja útil.")

    mutation_tab, population_tab, generalization_tab, limits_tab = st.tabs(["Mutação", "População", "Novos cenários", "Limites e falhas"])
    with mutation_tab:
        st.write("Alteramos a chance de mudar os genes para observar desempenho e diversidade.")
        rows = []
        for label, data in payload["experiment_1_mutation"]["results"].items():
            rows.append({"Mutação": label, "Média de salas": data["val_rooms_summary"]["mean"],
                         "Conclusão (%)": data["val_completion_rate_mean"] * 100,
                         "Diversidade final": data["final_diversity_summary"]["mean"]})
        st.dataframe(pd.DataFrame(rows).round(2), hide_index=True)
        st.caption("Resultados médios nas masmorras de validação; diversidade é um índice calculado sobre os genes.")
        fig_mutation = go.Figure()
        for label, data in payload["experiment_1_mutation"]["results"].items():
            curve = data["curves_by_generation"]
            fig_mutation.add_scatter(x=curve["generation"], y=curve["best_rooms_mean"], mode="lines+markers", name=label)
        fig_mutation.update_layout(xaxis_title="Geração", yaxis_title="Melhor média de salas no treino", legend_title="Mutação")
        st.plotly_chart(fig_mutation)
    with population_tab:
        st.write("Variamos o número de estratégias por geração, mantendo a mesma quantidade de avaliações efetivas.")
        rows = []
        for data in payload["experiment_2_population"]["results"].values():
            rows.append({"Estratégias por geração": data["pop_size"], "Gerações avaliadas": data["generations"],
                         "Avaliações": data["budget_evaluations"], "Média de salas": data["val_rooms_summary"]["mean"],
                         "Conclusão (%)": data["val_completion_rate_mean"] * 100})
        st.dataframe(pd.DataFrame(rows).round(2), hide_index=True)
        st.caption("Como as melhores estratégias são preservadas sem nova avaliação, a última geração pode conter menos estratégias novas.")
        fig_population = go.Figure()
        for label, data in payload["experiment_2_population"]["results"].items():
            curve = data["convergence_by_evaluations"]
            fig_population.add_scatter(x=curve["evaluations"], y=curve["best_rooms_mean"], mode="lines+markers", name=label)
        fig_population.update_layout(xaxis_title="Avaliações realizadas", yaxis_title="Melhor média de salas no treino")
        st.plotly_chart(fig_population)
    with generalization_tab:
        st.write("A mesma estratégia escolhida no treino foi testada em condições diferentes, sem novo treinamento.")
        rows = []
        for scenario in payload["experiment_4_generalization"]["scenarios"].values():
            rows.append({"Cenário": scenario["label"], "Algoritmo": scenario["genetic_algorithm"]["mean_rooms"],
                         "Fixa": scenario["fixed_baseline"]["mean_rooms"],
                         "Conclusão do algoritmo (%)": scenario["genetic_algorithm"]["completion_rate"] * 100})
        st.dataframe(pd.DataFrame(rows).round(2), hide_index=True)
        st.caption("As primeiras linhas distinguem treino e validação; os demais cenários alteram composição, dificuldade ou baús.")
    with limits_tab:
        analysis = payload["failure_and_dominance_analysis"]
        gap = analysis["4_overfitting_to_dungeon_seeds"]["generalization_gap_rooms"]
        luck = analysis["3_randomness_dependence"]
        st.write(f"**Treino e validação:** a diferença entre as médias das repetições foi de {gap:.1f} salas. Ela pode indicar adaptação às masmorras de treino, mas não prova a causa.")
        st.write(f"**Variação entre masmorras:** com baús, a estratégia escolhida concluiu entre {luck['validation_min_rooms']:.0f} e {luck['validation_max_rooms']:.0f} salas nas sementes avaliadas.")
        st.write(f"**Dependência das regras:** a média foi de {luck['mean_rooms_with_chests']:.1f} salas com baús e {luck['mean_rooms_without_chests']:.1f} sem baús nos cenários registrados.")
        st.write("Os resultados dependem dos monstros, das regras de combate e das sementes escolhidas. Eles não descrevem jogadores reais nem garantem desempenho em outros jogos.")


def bestiary(monsters: pd.DataFrame, manifest: dict, eda: dict) -> None:
    _heading("Arquivo de criaturas", "Bestiário", "Dos primeiros encontros ao último adversário. Consulte os atributos originais de cada criatura.")
    search, kind = st.columns([2, 1])
    query = search.text_input("Procurar criatura pelo nome", placeholder="Ex.: goblin ou dragon")
    kinds = ["Todos"] + sorted(monsters["tipo_pt"].dropna().unique().tolist())
    selected_kind = kind.selectbox("Tipo", kinds)
    low, high = float(monsters["challenge_rating"].min()), float(monsters["challenge_rating"].max())
    cr_range = st.slider("Faixa de desafio original (CR)", min_value=low, max_value=high,
                         value=(low, high), step=0.125,
                         help="O desafio descreve a criatura no SRD. O simulador adapta seus atributos para cada sala.")
    visible = monsters[monsters["challenge_rating"].between(*cr_range)]
    if query.strip():
        visible = visible[visible["name"].str.contains(query.strip(), case=False, regex=False, na=False)]
    if selected_kind != "Todos":
        visible = visible[visible["tipo_pt"] == selected_kind]
    st.caption(f"{len(visible)} de {len(monsters)} registros encontrados. A busca usa os nomes originais em inglês.")
    if not visible.empty:
        options = visible.sort_values("name")["index"].tolist()
        names = visible.set_index("index")["name"].to_dict()
        selected = st.selectbox("Escolha uma criatura", options, format_func=lambda item: names[item])
        row = visible[visible["index"] == selected].iloc[0]
        st.html(f'<div class="creature-sheet">{creature_seal(str(row["type"]))}<div>'
                f'<div class="eyebrow">Registro {escape(str(row["index"]))}</div>'
                f'<h2>{escape(str(row["name"]))}</h2><p>{escape(str(row["tipo_pt"]))} · '
                f'{escape(str(row["tamanho_pt"]))} · desafio {row["challenge_rating"]:g}</p></div></div>')
        with st.container():
            a, b, c = st.columns(3)
            a.metric("Vida original", int(row["hit_points"]))
            b.metric("Classe de armadura", int(row["armor_class"]))
            c.metric("Experiência original", int(row["xp"]))
            st.markdown(f"[Consultar registro original]({row['source_url']})")
        with st.expander("Ver a tabela dos resultados"):
            table = visible[["name", "tipo_pt", "challenge_rating", "hit_points", "armor_class", "xp"]].rename(
                columns={"name": "Criatura", "tipo_pt": "Tipo", "challenge_rating": "Desafio", "hit_points": "Vida", "armor_class": "Armadura", "xp": "Experiência"})
            st.dataframe(table, hide_index=True)
            st.download_button("Baixar criaturas filtradas", visible.drop(columns=["tipo_pt", "tamanho_pt"]).to_csv(index=False).encode("utf-8-sig"),
                               file_name="bestiario-filtrado.csv", mime="text/csv")
    else:
        st.info("Nenhuma criatura encontrada. Tente outro nome ou tipo.")

    st.divider()
    st.subheader("O que os dados mostram?")
    median = monsters["hit_points"].median()
    corr = eda.get("pair_correlations", {}).get("challenge_rating_vs_hit_points", {}).get("pearson_r")
    st.write(f"Metade dos registros tem até {median:.0f} pontos de vida originais.")
    if corr is not None:
        st.write(f"No conjunto completo, desafio e vida têm correlação de {corr:.2f}. Isso descreve uma relação nos dados, não uma regra para cada criatura.")
    anomaly = eda.get("inconsistencies_and_anomalies", {}).get("monsters_without_direct_damage_actions_count")
    if anomaly is not None:
        st.write(f"A análise encontrou {anomaly} registros sem dano direto identificado nas ações, que precisam de atenção na adaptação.")
    with st.expander("Explorar a relação entre desafio e vida"):
        fig = px.scatter(visible, x="challenge_rating", y="hit_points", color="tipo_pt", hover_name="name",
                         labels={"challenge_rating": "Nível de desafio", "hit_points": "Vida original", "tipo_pt": "Tipo"})
        st.plotly_chart(fig)
    with st.expander("Origem e licença"):
        st.write("Dados do SRD 5.1 fornecidos pela API D&D 5e da 5e-bits. As criaturas são fictícias; os registros e sua coleta são reais.")
        st.write(manifest.get("attribution", "A atribuição da fonte está no manifesto do dataset."))
        st.markdown("[Documentação da API](https://docs.dnd5eapi.co/) · [SRD 5.1 e licença](https://www.dndbeyond.com/srd)")


def data_source(monsters: pd.DataFrame, manifest: dict) -> None:
    _heading("Os dados por trás da aventura", "Dados e fonte", "Dataset é o conjunto de registros usado no projeto. Fonte é de onde esses registros vieram.")
    definition, counts = st.columns([1.55, 1], gap="large")
    with definition:
        st.html('''<div class="field-note"><h3>Neste projeto, cada linha é uma criatura.</h3>
            <p>Nome, tipo, vida, armadura, desafio e ações vêm da base D&D 5e SRD 2014,
            consultada pela API mantida pela comunidade 5e-bits. Guardamos uma cópia local
            para repetir os experimentos e usar a aplicação sem consultar a API.</p></div>''')
        st.markdown("[Abrir a fonte: D&D 5e SRD API](https://www.dnd5eapi.co/api/2014/monsters) · "
                    "[Exemplo de registro: Goblin](https://www.dnd5eapi.co/api/2014/monsters/goblin)")
    with counts:
        st.metric("Registros na cópia local", len(monsters))
        date = str(manifest.get("collected_at_utc", ""))[:10]
        st.caption(f"Coleta: {'/'.join(reversed(date.split('-'))) if date else 'não informada'}")
        st.caption(f"Versão: {manifest.get('dataset_version', 'não informada')}")

    section_label("01", "Da fonte ao combate")
    st.html('''<div class="source-step"><span>1</span><div><h3>Dados externos</h3>
        <p>Os registros originais de criaturas ficam em um arquivo JSON. São dados publicados
        sobre criaturas fictícias, com um endereço de origem para cada registro.</p></div></div>
        <div class="source-step"><span>2</span><div><h3>Dados tratados</h3>
        <p>O grupo organiza campos aninhados em uma tabela, resume ações e danos e registra
        os valores ausentes. A tabela é salva em CSV e Parquet.</p></div></div>
        <div class="source-step"><span>3</span><div><h3>Simulação do grupo</h3>
        <p>As 100 salas, o balanceamento, o ouro e as batalhas são gerados pelo nosso código.
        O algoritmo evolui estratégias no simulador; os registros de monstros fornecem os adversários.</p></div></div>''')
    st.caption("Não há um conjunto de partidas humanas ou rótulos de jogador vencedor. O desempenho de cada estratégia é calculado ao simular as masmorras.")

    section_label("02", "Consulte e leve os dados", "Snapshot usado pelo projeto")
    preview = monsters[["name", "type", "challenge_rating", "hit_points", "armor_class", "source_url"]].head(8)
    st.dataframe(preview.rename(columns={"name": "Criatura", "type": "Tipo original", "challenge_rating": "Desafio",
                                         "hit_points": "Vida", "armor_class": "Armadura", "source_url": "Registro na fonte"}),
                 hide_index=True, column_config={"Registro na fonte": st.column_config.LinkColumn("Registro na fonte")})
    csv_column, raw_column, manifest_column = st.columns(3)
    files = [(csv_column, "Baixar tabela (CSV)", "data/processed/monsters_srd2014_processed.csv", "text/csv"),
             (raw_column, "Baixar dados brutos (JSON)", "data/raw/monsters_raw_srd2014.json", "application/json"),
             (manifest_column, "Baixar manifesto", "data/metadata/collection_manifest.json", "application/json")]
    for column, label, relative, mime in files:
        source = PROJECT_ROOT / relative
        if source.is_file():
            column.download_button(label, source.read_bytes(), file_name=source.name, mime=mime, use_container_width=True)

    with st.expander("Conferência da cópia e atribuição da fonte"):
        snapshot = inspect_snapshot(monsters, manifest)
        if snapshot["verified"]:
            st.success("Arquivo bruto confere com o SHA-256 do manifesto. Quantidade e IDs conferem com a tabela em uso.")
        elif snapshot["available"]:
            st.warning("Há uma diferença entre o arquivo bruto, o manifesto e a tabela em uso. Confira o snapshot antes de reproduzir os experimentos.")
        else:
            st.info("O arquivo bruto não está disponível para conferência nesta instalação.")
        if snapshot.get("sha256"):
            st.code(snapshot["sha256"], language=None)
        st.caption("Essa conferência verifica o arquivo bruto, os IDs e a quantidade de registros. As transformações e os atributos tratados são descritos na análise exploratória.")
        st.write(manifest.get("attribution", "Consulte a atribuição no manifesto."))
        st.markdown("[Documentação da API](https://docs.dnd5eapi.co/) · [SRD e condições de uso](https://www.dndbeyond.com/srd)")
    st.button("Explorar as criaturas no Bestiário →", on_click=_navigate, args=("Bestiário",))


def laboratory(monsters: pd.DataFrame, settings: dict, payload: dict | None) -> None:
    _heading("Teste uma ideia", "Laboratório", "Mude as condições da masmorra e compare a estratégia do algoritmo com a estratégia fixa.")
    champion = _champion(payload)
    if champion is None:
        st.info("Esta comparação ficará disponível depois que os resultados científicos atualizados forem gerados.")
        return
    with st.form("laboratory_form"):
        a, b, c = st.columns(3)
        difficulty = a.slider("Força dos inimigos", 70, 150, 115, 5, format="%d%%")
        healing = a.slider("Recuperação entre salas", 10, 50, 22, 2, format="%d%%")
        composition = b.selectbox("Criaturas", ["Composição padrão", "Composição alternativa"])
        seed = b.number_input("Número da masmorra", min_value=1, max_value=99999, value=505, step=1)
        allies = c.checkbox("Permitir aliados", value=True)
        chests = c.checkbox("Permitir baús", value=False)
        submitted = st.form_submit_button("Comparar neste cenário", type="primary")
    if submitted:
        cfg = copy.deepcopy(settings)
        cfg["warrior"]["post_room_heal_fraction"] = healing / 100
        rooms = build_dungeon_100_rooms(monsters, cfg, seed=int(seed), difficulty_multiplier=difficulty / 100,
                                       composition_mode="alternate_pool" if composition == "Composição alternativa" else "standard")
        with st.spinner("Testando as duas estratégias..."):
            ga = run_dungeon_simulation(rooms, champion.to_policy_params(), cfg, seed=int(seed),
                                        enable_allies=allies, enable_chests=chests, record_detailed_logs=True)
            fixed = run_dungeon_simulation(rooms, create_fixed_baseline_chromosome().to_policy_params(), cfg,
                                           seed=int(seed), enable_allies=allies, enable_chests=chests, record_detailed_logs=True)
        st.session_state["laboratory_result"] = {"ga": ga, "fixed": fixed, "seed": int(seed), "difficulty": difficulty,
                                                  "healing": healing, "composition": composition, "allies": allies, "chests": chests}
    result = st.session_state.get("laboratory_result")
    if result:
        st.divider()
        st.caption(f"Masmorra {result['seed']} · força {result['difficulty']}% · recuperação {result['healing']}% · {result['composition'].lower()} · aliados {'sim' if result['allies'] else 'não'} · baús {'sim' if result['chests'] else 'não'}")
        ga, fixed = result["ga"], result["fixed"]
        a, b = st.columns(2)
        a.metric("Estratégia do algoritmo", f"{ga.rooms_cleared} / 100 salas")
        b.metric("Estratégia fixa", f"{fixed.rooms_cleared} / 100 salas")
        st.caption("Uma tentativa por estratégia, usando a mesma masmorra e as mesmas regras. Eventos aleatórios podem seguir sequências diferentes.")
        series = pd.DataFrame({
            "Algoritmo": pd.Series({r.room_number: r.warrior_hp_end for r in ga.room_results}),
            "Fixa": pd.Series({r.room_number: r.warrior_hp_end for r in fixed.room_results}),
        })
        st.subheader("Vida ao longo da jornada")
        st.line_chart(series)
        st.caption("Nas salas vencidas, a vida exibida inclui a recuperação após o combate.")
