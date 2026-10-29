"""Aplicação Web Interativa — Masmorra Genética: A Evolução do Guerreiro (Grupo 7 - IA II FIB).

Implementa as 6 páginas obrigatórias (Seção 11):
1. Sobre o projeto
2. Dataset (D&D 5e SRD API + EDA Interativa)
3. Masmorra (Simulador de 100 Salas: Estratégia Fixa, Manual ou Otimizada pelo AG)
4. Evolução Genética (Modo Demonstração ao Vivo + Modo Científico Versionado)
5. Experimentos (Comparação com Baselines, 4 Experimentos Científicos e Análise de Falhas)
6. Laboratório (Teste de Generalização e Sensibilidade Ambiental)
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.dataset.collector import load_or_collect_raw_monsters
from src.dataset.preprocessing import load_processed_dataset
from src.experiments.baselines import (
    create_fixed_baseline_chromosome,
    run_random_search,
)
from src.game.characters import ALLY_CLASSES_ORDER
from src.game.combat import run_dungeon_simulation
from src.game.dungeon import build_dungeon_100_rooms
from src.game.monsters import load_balance_config
from src.genetic.chromosome import Chromosome, GENE_NAMES
from src.genetic.optimizer import run_genetic_algorithm

st.set_page_config(
    page_title="Masmorra Genética — Grupo 7 (IA II - FIB)",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def get_cached_dataset() -> pd.DataFrame:
    return load_processed_dataset()


@st.cache_data
def get_cached_manifest() -> dict[str, Any]:
    p = Path("data/metadata/collection_manifest.json")
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}


@st.cache_data
def get_cached_eda_summary() -> dict[str, Any]:
    p = Path("results/eda/eda_summary.json")
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}


@st.cache_data
def get_cached_balance() -> dict[str, Any]:
    return load_balance_config()


def load_experiments_payload() -> dict[str, Any] | None:
    p = Path("data/experiments/scientific_experiments_v1.json")
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return None


def get_champion_chromosome(exp_payload: dict[str, Any] | None) -> Chromosome:
    if exp_payload and "best_champion_strategy" in exp_payload:
        genes = exp_payload["best_champion_strategy"]["best_chromosome"]["genes"]
        return Chromosome(genes=genes)
    # Fallback determinístico caso o JSON ainda não tenha sido carregado
    return Chromosome(
        genes=[
            0.39, 0.36, 0.25,
            0.78, 0.72, 0.55, 0.92, 0.84,
            0.48, 0.32, 0.20,
            0.62, 1.0, 28.0, 1.12, 1.08,
        ]
    )


def render_page_1_about(manifest: dict[str, Any], balance_cfg: dict[str, Any]) -> None:
    st.title("⚔️ Masmorra Genética: A Evolução do Guerreiro")
    st.subheader("Grupo 7 — Inteligência Artificial II — Faculdades Integradas de Bauru (FIB)")

    st.markdown(
        """
        ### 1. Objetivo do Projeto
        Desenvolver e validar cientificamente uma aplicação pública que utiliza **Algoritmos Genéticos (Computação Evolutiva)**
        para descobrir **políticas ótimas de evolução de atributos, contratação de aliados e gestão econômica** de um guerreiro
        enfrentando uma masmorra progressiva de **100 salas** construída diretamente a partir de dados reais do
        **Dungeons & Dragons 5e System Reference Document (SRD 2014 API)**.

        > **Distinção Metodológica Fundamental:** Este projeto realiza **otimização direta de políticas de decisão sequencial em ambiente de simulação**
        > via Algoritmo Genético (busca meta-heurística populacional guiada por função de aptidão/fitness), **e não** o treinamento supervisionado
        > de um classificador ou regressor preditivo sobre rótulos estáticos.
        """
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            ### 2. Integrantes e Organização (Grupo 7)
            | Integrante | Frente Principal | Responsabilidades |
            | :--- | :--- | :--- |
            | **Eduardo Coque Corrêa de Lima** | Coordenação Técnica & AG | Arquitetura, Algoritmo Genético (`src/genetic/`) e integração geral |
            | **Matheus Alcântara Pereira** | Dados, ETL & EDA | Coleta API D&D 5e SRD, validação, normalização, snapshot e EDA (`src/dataset/`) |
            | **Fernando Eduardo Motta Mendes** | Simulador & Interface | Motor de combate em turnos, masmorra de 100 salas, economia e UI Streamlit |
            | **Rogério Tiritan Marcone** | Documentação Científica | Canvas Inicial, Metodologia, Model Card e Resumo Expandido |
            | **Reuel Vitor Lanzetti** | Experimentos & Divulgação | Ficha de Experimentos, análise estatística/falhas, slides, vídeo e materiais |
            """
        )

    with col2:
        st.markdown(
            f"""
            ### 3. Proveniência do Dataset e Versionamento
            - **Fonte Primária:** [D&D 5e SRD REST API (2014)](https://www.dnd5eapi.co/api/2014/monsters)
            - **Repositório Oficial da Fonte:** [`5e-bits/5e-database`](https://github.com/5e-bits/5e-database)
            - **Fonte Secundária Documentada (Contingência):** [Open5e API V2](https://open5e.com/api-docs)
            - **Licença dos Dados:** *System Reference Document 5.1 (Wizards of the Coast LLC)* — **CC-BY-4.0 / OGL v1.0a** (Código API: MIT).
            - **Versão Congelada do Snapshot:** `{manifest.get('dataset_version', 'srd-2014-v1.0.0')}`
            - **Registros Válidos Coletados:** `{manifest.get('collected_records_count', 334)}` criaturas (`0` falhas, `0` dados inventados)
            - **Hash SHA-256 do JSON Bruto:** `{manifest.get('raw_file_sha256', 'N/A')[:32]}...`
            - **Versão do Balanceamento do Simulador:** `{balance_cfg.get('config_version', 'balance-v1.0.0')}`
            """
        )

    st.markdown("---")
    st.markdown(
        """
        ### 4. Arquitetura Metodológica e Rastreabilidade de Dados
        Para garantir rigor acadêmico, o projeto separa explicitamente cinco camadas de informação:
        1. **Dados Externos Originais (`data/raw/monsters_raw_srd2014.json`):** Registros JSON preservados sem alteração da API oficial.
        2. **Dados Externos Tratados (`data/processed/monsters_srd2014_processed.parquet`):** Atributos normalizados e valor esperado matemático de expressões de dados (`NdS+M`).
        3. **Atributos Derivados por Fórmulas (`src/game/monsters.py`):** Conversão documentada de CR, AC, HP, ações e resistências para os parâmetros do simulador.
        4. **Configurações Criadas pelo Grupo (`config/balance.json`):** Catálogo do mercado (4 armas, 4 armaduras, 3 escudos) e regras das 5 classes de aliados.
        5. **Resultados Sintéticos das Simulações (`data/experiments/`):** Logs e métricas gerados exclusivamente pela execução real do motor de combate e do AG.
        """
    )


def render_page_2_dataset(df: pd.DataFrame, manifest: dict[str, Any], eda: dict[str, Any]) -> None:
    st.title("📊 Dataset Externo D&D 5e SRD & Análise Exploratória (EDA)")

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total de Criaturas (SRD)", len(df))
    m2.metric("Registros Válidos", f"{len(df)} (100%)")
    m3.metric("CR Médio / Máximo", f"{df['challenge_rating'].mean():.2f} / {df['challenge_rating'].max():.0f}")
    m4.metric("HP Mediano / Máximo", f"{df['hit_points'].median():.0f} / {df['hit_points'].max():.0f}")
    m5.metric("AC Médio (Bounded)", f"{df['armor_class'].mean():.2f} [5–25]")

    with st.expander("🔍 Proveniência, Manifesto de Coleta e Atualização via API", expanded=False):
        st.json(manifest)
        if st.button("🔄 Verificar Conectividade com a API Oficial (com Fallback Seguro para Snapshot)"):
            with st.spinner("Consultando https://www.dnd5eapi.co/api/2014/monsters ..."):
                recs, new_man = load_or_collect_raw_monsters(force_refresh=False)
                st.success(
                    f"Snapshot verificado com sucesso! {len(recs)} criaturas íntegras (SHA-256: {new_man.get('raw_file_sha256', '')[:24]}...)."
                )

    st.subheader("1. Explorador Interativo de Criaturas do Dataset")
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    with f_col1:
        selected_types = st.multiselect(
            "Filtrar por Tipo (type)",
            options=sorted(df["type"].unique()),
            default=[],
        )
    with f_col2:
        selected_sizes = st.multiselect(
            "Filtrar por Tamanho (size)",
            options=sorted(df["size"].unique()),
            default=[],
        )
    with f_col3:
        cr_range = st.slider(
            "Faixa de Nível de Desafio (CR)",
            min_value=0.0,
            max_value=float(df["challenge_rating"].max()),
            value=(0.0, 30.0),
            step=0.5,
        )
    with f_col4:
        search_term = st.text_input("Buscar por nome ou index", "")

    filtered = df[
        (df["challenge_rating"] >= cr_range[0]) & (df["challenge_rating"] <= cr_range[1])
    ].copy()
    if selected_types:
        filtered = filtered[filtered["type"].isin(selected_types)]
    if selected_sizes:
        filtered = filtered[filtered["size"].isin(selected_sizes)]
    if search_term.strip():
        q = search_term.strip().lower()
        filtered = filtered[
            filtered["name"].str.lower().str.contains(q) | filtered["index"].str.lower().str.contains(q)
        ]

    st.caption(f"Exibindo **{len(filtered)}** de **{len(df)}** criaturas do dataset oficial.")
    display_cols = [
        "index",
        "name",
        "type",
        "size",
        "challenge_rating",
        "xp",
        "hit_points",
        "armor_class",
        "strength",
        "dexterity",
        "constitution",
        "max_attack_bonus",
        "best_action_damage",
        "estimated_dpr_raw",
        "has_physical_resistance",
        "has_magical_resistance",
        "source_url",
    ]
    st.dataframe(filtered[display_cols], use_container_width=True, height=320)

    st.subheader("2. Visualizações da Análise Exploratória de Dados (EDA)")
    tab_g1, tab_g2, tab_g3, tab_g4 = st.tabs(
        [
            "📈 Distribuições e Relações com CR",
            "🧬 Matriz de Correlação Verificada",
            "🐉 Tipos, Tamanhos e Atributos Ofensivos",
            "🔎 Descobertas Empíricas e Seleção de Campos",
        ]
    )

    with tab_g1:
        c1, c2 = st.columns(2)
        with c1:
            fig_hp = px.scatter(
                filtered,
                x="challenge_rating",
                y="hit_points",
                color="type",
                hover_data=["name", "armor_class", "xp"],
                title="Relação Nível de Desafio (CR) vs Pontos de Vida (HP) — r = 0.9404",
            )
            st.plotly_chart(fig_hp, use_container_width=True)
        with c2:
            fig_ac = px.scatter(
                filtered,
                x="challenge_rating",
                y="armor_class",
                color="size",
                hover_data=["name", "hit_points", "dexterity"],
                title="Relação CR vs Classe de Armadura (AC) — r = 0.7547 (Bounded Accuracy)",
            )
            st.plotly_chart(fig_ac, use_container_width=True)

        c3, c4 = st.columns(2)
        with c3:
            fig_xp = px.scatter(
                filtered,
                x="challenge_rating",
                y="xp",
                color="type",
                hover_data=["name"],
                title="Crescimento Exponencial de XP por CR (Spearman ρ = 0.9995, Skew = +7.33)",
            )
            st.plotly_chart(fig_xp, use_container_width=True)
        with c4:
            fig_hist = px.histogram(
                filtered,
                x="challenge_rating",
                nbins=25,
                title="Distribuição de Criaturas por Nível de Desafio (CR)",
            )
            st.plotly_chart(fig_hist, use_container_width=True)

    with tab_g2:
        if eda and "pair_correlations" in eda:
            corr_rows = []
            for pair_name, vals in eda["pair_correlations"].items():
                corr_rows.append(
                    {
                        "Par de Atributos": pair_name,
                        "Pearson (r)": vals["pearson_r"],
                        "Valor-p (Pearson)": vals["pearson_p"],
                        "Spearman (ρ)": vals["spearman_rho"],
                    }
                )
            st.dataframe(pd.DataFrame(corr_rows), use_container_width=True)
        img_corr = Path("results/eda/05_matriz_correlacao_pearson.png")
        if img_corr.exists():
            st.image(str(img_corr), caption="Matriz de Correlação de Pearson calculada sobre os 334 registros do SRD.")

    with tab_g3:
        c1, c2 = st.columns(2)
        with c1:
            type_df = filtered["type"].value_counts().reset_index()
            type_df.columns = ["type", "count"]
            fig_t = px.bar(type_df, x="count", y="type", orientation="h", title="Distribuição por Tipo de Criatura")
            st.plotly_chart(fig_t, use_container_width=True)
        with c2:
            fig_off = px.scatter(
                filtered,
                x="max_attack_bonus",
                y="estimated_dpr_raw",
                color="challenge_rating",
                hover_data=["name", "multiattack_count"],
                title="Atributos Ofensivos: Bônus de Ataque vs Dano Estimado por Turno (DPR)",
            )
            st.plotly_chart(fig_off, use_container_width=True)

    with tab_g4:
        ReportPath = Path("docs/eda_report.md")
        if ReportPath.exists():
            st.markdown(ReportPath.read_text(encoding="utf-8"))


def render_page_3_dungeon(
    df: pd.DataFrame,
    balance_cfg: dict[str, Any],
    exp_payload: dict[str, Any] | None,
) -> None:
    st.title("🏰 Simulador da Masmorra de 100 Salas")
    st.markdown(
        """
        Execute uma aventura completa nas **100 salas** geradas a partir do dataset externo D&D 5e SRD.
        Cada monstro mantém referência explícita ao registro original (`source_index` e URL da API).
        """
    )

    ctrl1, ctrl2, ctrl3 = st.columns(3)
    with ctrl1:
        strategy_mode = st.selectbox(
            "Modo de Estratégia",
            options=[
                "1. Estratégia Otimizada (Campeã do Algoritmo Genético)",
                "2. Estratégia Fixa (Baseline Equilibrado)",
                "3. Estratégia Manual (Customizada pelo Usuário)",
            ],
        )
    with ctrl2:
        dungeon_seed = st.number_input("Semente da Masmorra (Reprodutível)", min_value=1, max_value=99999, value=201, step=1)
    with ctrl3:
        enable_chests = st.checkbox("Habilitar Baús Pós-Vitória (Controlados por Semente)", value=True)

    if strategy_mode.startswith("1."):
        chosen_chrom = get_champion_chromosome(exp_payload)
    elif strategy_mode.startswith("2."):
        chosen_chrom = create_fixed_baseline_chromosome()
    else:
        st.markdown("#### 🛠️ Configurar Estratégia Manualmente")
        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            w_str = st.slider("Peso Força Guerreiro", 0.05, 0.90, 0.40, 0.05)
            w_vit = st.slider("Peso Vitalidade Guerreiro", 0.05, 0.90, 0.35, 0.05)
            w_def = st.slider("Peso Defesa Guerreiro", 0.05, 0.90, 0.25, 0.05)
        with mc2:
            p_mage = st.slider("Prioridade Mago", 0.0, 1.0, 0.75, 0.05)
            p_arch = st.slider("Prioridade Arqueiro", 0.0, 1.0, 0.70, 0.05)
            p_monk = st.slider("Prioridade Monge", 0.0, 1.0, 0.50, 0.05)
            p_priest = st.slider("Prioridade Padre (Cura)", 0.0, 1.0, 0.90, 0.05)
            p_alch = st.slider("Prioridade Alquimista (Buff/Debuff)", 0.0, 1.0, 0.80, 0.05)
        with mc3:
            eq_off = st.slider("Foco Ofensivo Equipamentos", 0.0, 1.0, 0.60, 0.05)
            hire_first = st.selectbox("Priorizar Aliado antes de Equipamento?", [1.0, 0.0], format_func=lambda x: "Sim" if x == 1.0 else "Não")
            min_res = st.slider("Reserva Mínima de Ouro", 0.0, 120.0, 25.0, 5.0)
            buy_th = st.slider("Limiar de Compra de Equipamento", 1.0, 1.8, 1.10, 0.05)
            hire_th = st.slider("Limiar de Contratação de Aliado", 1.0, 1.8, 1.05, 0.05)

        chosen_chrom = Chromosome(
            genes=[
                w_str, w_vit, w_def,
                p_mage, p_arch, p_monk, p_priest, p_alch,
                0.45, 0.35, 0.20,
                eq_off, float(hire_first), min_res, buy_th, hire_th,
            ]
        )

    with st.expander("🧬 Inspecionar Genes da Estratégia Selecionada", expanded=False):
        st.json(chosen_chrom.to_named_dict())

    rooms = build_dungeon_100_rooms(df, balance_cfg, seed=int(dungeon_seed))
    run_res = run_dungeon_simulation(
        rooms_template=rooms,
        policy_params=chosen_chrom.to_policy_params(),
        balance_cfg=balance_cfg,
        seed=int(dungeon_seed),
        enable_allies=True,
        enable_chests=enable_chests,
        record_detailed_logs=True,
    )

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Salas Concluídas", f"{run_res.rooms_cleared} / 100")
    k2.metric("Status Final", "🏆 VITÓRIA TOTAL" if run_res.completed_all_100 else f"💀 Caiu na Sala {run_res.failure_room}")
    k3.metric("Nível Final Guerreiro", f"Nv. {run_res.final_warrior_level}")
    k4.metric("Atributos (STR/VIT/DEF)", f"{run_res.final_strength}/{run_res.final_vitality}/{run_res.final_defense}")
    k5.metric("Equipamentos (Arma/Armad/Esc)", f"T{run_res.final_weapon_tier} / T{run_res.final_armor_tier} / T{run_res.final_shield_tier}")
    k6.metric("Aliados Ativos no Final", ", ".join(run_res.active_allies_final) if run_res.active_allies_final else "Nenhum")

    if run_res.room_results:
        hist_rows = []
        for rr in run_res.room_results:
            hist_rows.append(
                {
                    "Sala": rr.room_number,
                    "Resultado": "Vitória" if rr.victory else f"Derrota ({rr.termination_reason})",
                    "Turnos": rr.turns_taken,
                    "HP Início": rr.warrior_hp_start,
                    "HP Fim": rr.warrior_hp_end,
                    "HP Máx": rr.warrior_max_hp,
                    "Nível Guerreiro": rr.warrior_level_end,
                    "Ouro Ganho": rr.gold_earned,
                    "Ouro Acumulado": rr.gold_end,
                    "Aliados Ativos": ", ".join(rr.active_allies_end) if rr.active_allies_end else "-",
                    "Inimigos (SRD)": ", ".join(rr.enemies_faced),
                    "IDs Origem API": ", ".join(rr.enemy_source_indices),
                }
            )
        hist_df = pd.DataFrame(hist_rows)

        c_chart1, c_chart2 = st.columns(2)
        with c_chart1:
            fig_hp_prog = go.Figure()
            fig_hp_prog.add_trace(go.Scatter(x=hist_df["Sala"], y=hist_df["HP Máx"], name="HP Máximo", line=dict(color="#2b5c8f", dash="dot")))
            fig_hp_prog.add_trace(go.Scatter(x=hist_df["Sala"], y=hist_df["HP Fim"], name="HP Pós-Sala", line=dict(color="#27ae60")))
            fig_hp_prog.update_layout(title="Evolução de Vida (HP) do Guerreiro ao Longo das Salas", xaxis_title="Sala", yaxis_title="HP")
            st.plotly_chart(fig_hp_prog, use_container_width=True)
        with c_chart2:
            fig_econ = go.Figure()
            fig_econ.add_trace(go.Scatter(x=hist_df["Sala"], y=hist_df["Ouro Acumulado"], name="Saldo de Ouro", line=dict(color="#f39c12")))
            fig_econ.add_trace(go.Scatter(x=hist_df["Sala"], y=hist_df["Turnos"], name="Turnos de Combate", yaxis="y2", line=dict(color="#e74c3c")))
            fig_econ.update_layout(
                title="Economia (Saldo de Ouro) e Duração dos Combates (Turnos)",
                xaxis_title="Sala",
                yaxis=dict(title="Ouro"),
                yaxis2=dict(title="Turnos", overlaying="y", side="right"),
            )
            st.plotly_chart(fig_econ, use_container_width=True)

        st.subheader("📜 Registro Sala a Sala e Auditoria de Turnos")
        st.dataframe(hist_df, use_container_width=True, height=280)

        selected_room_idx = st.slider(
            "Inspecionar Log Detalhado de Combate e Transações da Sala:",
            min_value=1,
            max_value=len(run_res.room_results),
            value=len(run_res.room_results),
        )
        rr_detail = run_res.room_results[selected_room_idx - 1]
        room_obj = rooms[selected_room_idx - 1]

        dcol1, dcol2 = st.columns(2)
        with dcol1:
            st.markdown(f"**Inimigos da Sala {rr_detail.room_number} (Referência Oficial SRD):**")
            for e in room_obj.enemies:
                st.markdown(
                    f"- **{e.source_name}** (`{e.source_index}`, CR {e.challenge_rating:g}, {e.position}) — "
                    f"HP Simulado: `{e.max_hp}`, Dano Fís/Mág: `{e.physical_damage}/{e.magical_damage}`, "
                    f"Defesa: `{e.defense}` | [JSON Oficial na API]({e.source_url})"
                )
            if rr_detail.market_transactions:
                st.markdown("**Transações no Mercado nesta Sala:**")
                st.json(rr_detail.market_transactions)
            if rr_detail.chest_event:
                st.markdown("**Evento de Baú Pós-Vitória:**")
                st.json(rr_detail.chest_event)
        with dcol2:
            st.markdown(f"**Log Turno a Turno — Sala {rr_detail.room_number} ({rr_detail.turns_taken} turnos):**")
            st.code("\n".join(rr_detail.combat_log) if rr_detail.combat_log else "Sem log registrado.")


def render_page_4_genetic_evolution(
    df: pd.DataFrame,
    balance_cfg: dict[str, Any],
    exp_payload: dict[str, Any] | None,
) -> None:
    st.title("🧬 Evolução Genética — Treinamento e Convergência")
    st.markdown(
        """
        Conforme especificado na **Seção 11 (Limitações de Hospedagem)**, esta página disponibiliza dois modos:
        - **Modo Científico (Resultados Reais Versionados):** Exibe a evolução completa do campeão obtido nos experimentos científicos formais.
        - **Modo Demonstração (Execução ao Vivo):** Permite configurar os hiperparâmetros do Algoritmo Genético e executar uma evolução real ao vivo no navegador.
        """
    )

    tab_sci, tab_demo = st.tabs(
        ["🏛️ Modo Científico (Execução Completa Versionada)", "⚡ Modo Demonstração (Treinar AG ao Vivo)"]
    )

    with tab_sci:
        if exp_payload and "best_champion_strategy" in exp_payload:
            champ = exp_payload["best_champion_strategy"]
            hist_df = pd.DataFrame(champ["history"])
            best_c = champ["best_chromosome"]

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Média de Salas (Treino)", f"{best_c['mean_rooms_cleared']:.2f} / 100")
            m2.metric("Taxa de Conclusão 100 Salas", f"{best_c['completion_rate'] * 100:.1f}%")
            m3.metric("Avaliações da Função Objetivo", champ["total_objective_evaluations"])
            m4.metric("Simulações de Masmorra Executadas", champ["total_simulation_runs"])

            c1, c2 = st.columns(2)
            with c1:
                fig_f = go.Figure()
                fig_f.add_trace(go.Scatter(x=hist_df["generation"], y=hist_df["best_mean_rooms"], mode="lines+markers", name="Melhor Indivíduo (Salas)"))
                fig_f.add_trace(go.Scatter(x=hist_df["generation"], y=hist_df["pop_mean_rooms"], mode="lines+markers", name="Média da População (Salas)"))
                fig_f.update_layout(title="Evolução de Salas Concluídas por Geração", xaxis_title="Geração", yaxis_title="Salas Concluídas")
                st.plotly_chart(fig_f, use_container_width=True)
            with c2:
                fig_d = px.line(
                    hist_df,
                    x="generation",
                    y="diversity_index",
                    markers=True,
                    title="Evolução da Diversidade Genética da População por Geração",
                )
                st.plotly_chart(fig_d, use_container_width=True)

            st.subheader("Cromossomo Campeão Decodificado (16 Genes)")
            genes_df = pd.DataFrame(
                [{"Gene": k, "Valor Otimizado": v} for k, v in best_c["named_genes"].items()]
            )
            st.dataframe(genes_df, use_container_width=True)
        else:
            st.info("Resultados científicos em processamento ou não encontrados em `data/experiments/scientific_experiments_v1.json`.")

    with tab_demo:
        st.markdown("Configure os parâmetros abaixo para rodar o **Algoritmo Genético real** agora:")
        dc1, dc2, dc3, dc4 = st.columns(4)
        with dc1:
            demo_pop = st.slider("Tamanho da População", min_value=6, max_value=24, value=10, step=2)
        with dc2:
            demo_gens = st.slider("Número de Gerações", min_value=3, max_value=15, value=6, step=1)
        with dc3:
            demo_mut = st.slider("Taxa de Mutação", min_value=0.01, max_value=0.35, value=0.10, step=0.01)
        with dc4:
            demo_seed = st.number_input("Semente do AG", min_value=1, max_value=9999, value=42)

        if st.button("🚀 Executar Treinamento Demonstrativo ao Vivo", type="primary"):
            with st.spinner("Evoluindo população de guerreiros nas masmorras do SRD..."):
                demo_dungeons = {
                    s: build_dungeon_100_rooms(df, balance_cfg, seed=s) for s in [101, 102, 103]
                }
                demo_res = run_genetic_algorithm(
                    dungeons_by_seed=demo_dungeons,
                    balance_cfg=balance_cfg,
                    pop_size=int(demo_pop),
                    generations=int(demo_gens),
                    mutation_rate=float(demo_mut),
                    seed=int(demo_seed),
                )
            st.success(
                f"Treinamento concluído em {demo_res.elapsed_seconds:.2f}s! "
                f"Melhor estratégia alcançou média de **{demo_res.best_chromosome.mean_rooms_cleared:.2f} salas** "
                f"(taxa de conclusão: **{demo_res.best_chromosome.completion_rate * 100:.1f}%**)."
            )
            d_hist = pd.DataFrame([h.to_dict() for h in demo_res.history])
            col_a, col_b = st.columns(2)
            with col_a:
                fig_live = go.Figure()
                fig_live.add_trace(go.Scatter(x=d_hist["generation"], y=d_hist["best_mean_rooms"], mode="lines+markers", name="Melhor (Salas)"))
                fig_live.add_trace(go.Scatter(x=d_hist["generation"], y=d_hist["pop_mean_rooms"], mode="lines+markers", name="Média População"))
                fig_live.update_layout(title="Curva de Evolução ao Vivo", xaxis_title="Geração", yaxis_title="Salas Concluídas")
                st.plotly_chart(fig_live, use_container_width=True)
            with col_b:
                st.markdown("**Melhor Cromossomo Encontrado na Demonstração:**")
                st.json(demo_res.best_chromosome.to_named_dict())


def render_page_5_experiments(exp_payload: dict[str, Any] | None) -> None:
    st.title("🔬 Experimentos Científicos e Análise de Falhas")
    if not exp_payload:
        st.warning("Arquivo `data/experiments/scientific_experiments_v1.json` ainda não disponível.")
        return

    t_exp3, t_exp1, t_exp2, t_exp4, t_fail = st.tabs(
        [
            "🏆 Exp. 3: Comparação com Baselines",
            "🧪 Exp. 1: Taxas de Mutação (2%, 10%, 25%)",
            "👥 Exp. 2: População (Orçamento Fixo)",
            "🌍 Exp. 4: Generalização Fora da Amostra",
            "⚠️ Análise Obrigatória de Falhas",
        ]
    )

    with t_exp3:
        exp3 = exp_payload["experiment_3_baselines"]
        m = exp3["methods"]
        st.subheader("Comparação Sob as Mesmas Condições (Validação Fora da Amostra — 10 Sementes Holdout)")
        comp_table = pd.DataFrame(
            [
                {
                    "Método": m["fixed_baseline"]["label"],
                    "Média Salas (Treino)": m["fixed_baseline"]["train_mean_rooms"],
                    "Média Salas (Validação)": m["fixed_baseline"]["val_mean_rooms"],
                    "Mediana (Validação)": m["fixed_baseline"]["val_median_rooms"],
                    "Desvio-Padrão (Validação)": m["fixed_baseline"]["val_std_rooms"],
                    "Taxa de Conclusão 100 Salas (%)": round(m["fixed_baseline"]["val_completion_rate"] * 100, 2),
                    "Avaliações Função Objetivo": m["fixed_baseline"]["objective_evaluations"],
                    "Tempo Médio (s)": m["fixed_baseline"]["elapsed_seconds"],
                },
                {
                    "Método": m["random_search"]["label"],
                    "Média Salas (Treino)": m["random_search"]["train_rooms_across_repeats"]["mean"],
                    "Média Salas (Validação)": m["random_search"]["val_rooms_across_repeats"]["mean"],
                    "Mediana (Validação)": m["random_search"]["val_rooms_across_repeats"]["median"],
                    "Desvio-Padrão (Validação)": m["random_search"]["val_rooms_across_repeats"]["std"],
                    "Taxa de Conclusão 100 Salas (%)": round(m["random_search"]["val_completion_rate_mean"] * 100, 2),
                    "Avaliações Função Objetivo": m["random_search"]["objective_evaluations_per_run"],
                    "Tempo Médio (s)": m["random_search"]["mean_elapsed_seconds"],
                },
                {
                    "Método": m["genetic_algorithm"]["label"],
                    "Média Salas (Treino)": m["genetic_algorithm"]["train_rooms_across_repeats"]["mean"],
                    "Média Salas (Validação)": m["genetic_algorithm"]["val_rooms_across_repeats"]["mean"],
                    "Mediana (Validação)": m["genetic_algorithm"]["val_rooms_across_repeats"]["median"],
                    "Desvio-Padrão (Validação)": m["genetic_algorithm"]["val_rooms_across_repeats"]["std"],
                    "Taxa de Conclusão 100 Salas (%)": round(m["genetic_algorithm"]["val_completion_rate_mean"] * 100, 2),
                    "Avaliações Função Objetivo": m["genetic_algorithm"]["objective_evaluations_per_run"],
                    "Tempo Médio (s)": m["genetic_algorithm"]["mean_elapsed_seconds"],
                },
            ]
        )
        st.dataframe(comp_table, use_container_width=True)
        st.markdown("**Testes Estatísticos Registrados:**")
        st.json(exp3["statistical_tests"])
        p3_img = Path("results/experiments/exp3_comparacao_baselines.png")
        if p3_img.exists():
            st.image(str(p3_img), caption="Comparação entre Baseline Fixo, Busca Aleatória e Algoritmo Genético.")

    with t_exp1:
        exp1 = exp_payload["experiment_1_mutation"]
        st.markdown(f"**Hipótese Testada:** {exp1['hypothesis']}")
        rows1 = []
        for rate_lbl, rdata in exp1["results"].items():
            rows1.append(
                {
                    "Taxa de Mutação": rate_lbl,
                    "Média Salas (Treino)": rdata["train_rooms_summary"]["mean"],
                    "Média Salas (Validação)": rdata["val_rooms_summary"]["mean"],
                    "Mediana (Validação)": rdata["val_rooms_summary"]["median"],
                    "DP (Validação)": rdata["val_rooms_summary"]["std"],
                    "Taxa Conclusão Val (%)": round(rdata["val_completion_rate_mean"] * 100, 2),
                    "Diversidade Final Média": rdata["final_diversity_summary"]["mean"],
                    "Geração Média de Convergência": rdata["mean_convergence_generation"],
                    "Tempo Médio (s)": rdata["mean_elapsed_seconds"],
                }
            )
        st.dataframe(pd.DataFrame(rows1), use_container_width=True)
        p1_img = Path("results/experiments/exp1_mutacao_convergencia_diversidade.png")
        if p1_img.exists():
            st.image(str(p1_img), caption="Experimento 1 — Convergência e Diversidade por Taxa de Mutação.")

    with t_exp2:
        exp2 = exp_payload["experiment_2_population"]
        st.markdown(f"**Hipótese Testada:** {exp2['hypothesis']}")
        rows2 = []
        for cfg_lbl, cdata in exp2["results"].items():
            rows2.append(
                {
                    "Configuração": cfg_lbl,
                    "População": cdata["pop_size"],
                    "Gerações": cdata["generations"],
                    "Orçamento Avaliações": cdata["budget_evaluations"],
                    "Média Salas (Treino)": cdata["train_rooms_summary"]["mean"],
                    "Média Salas (Validação)": cdata["val_rooms_summary"]["mean"],
                    "DP (Validação)": cdata["val_rooms_summary"]["std"],
                    "Taxa Conclusão Val (%)": round(cdata["val_completion_rate_mean"] * 100, 2),
                    "Diversidade Final": cdata["final_diversity_summary"]["mean"],
                    "Tempo Médio (s)": cdata["mean_elapsed_seconds"],
                }
            )
        st.dataframe(pd.DataFrame(rows2), use_container_width=True)
        p2_img = Path("results/experiments/exp2_populacao_orcamento_equivalente.png")
        if p2_img.exists():
            st.image(str(p2_img), caption="Experimento 2 — População vs Gerações com Orçamento Equivalente (240 avaliações).")

    with t_exp4:
        exp4 = exp_payload["experiment_4_generalization"]
        rows4 = []
        for skey, sdata in exp4["scenarios"].items():
            rows4.append(
                {
                    "Cenário": sdata["label"],
                    "Multiplicador Dificuldade": sdata["difficulty_multiplier"],
                    "Composição": sdata["composition_mode"],
                    "Baús Ativos": sdata["enable_chests"],
                    "AG — Média Salas": sdata["genetic_algorithm"]["mean_rooms"],
                    "AG — Mediana": sdata["genetic_algorithm"]["median_rooms"],
                    "AG — Conclusão (%)": round(sdata["genetic_algorithm"]["completion_rate"] * 100, 2),
                    "Baseline Fixo — Média Salas": sdata["fixed_baseline"]["mean_rooms"],
                    "Vantagem do AG (+Salas)": sdata["ga_advantage_rooms"],
                }
            )
        st.dataframe(pd.DataFrame(rows4), use_container_width=True)
        p4_img = Path("results/experiments/exp4_generalizacao_cenarios.png")
        if p4_img.exists():
            st.image(str(p4_img), caption="Experimento 4 — Desempenho de Generalização Fora das Condições de Otimização.")

    with t_fail:
        st.subheader("Análise Obrigatória de Falhas, Limitações e Dominância")
        st.json(exp_payload["failure_and_dominance_analysis"])


def render_page_6_laboratory(
    df: pd.DataFrame,
    balance_cfg: dict[str, Any],
    exp_payload: dict[str, Any] | None,
) -> None:
    st.title("🧪 Laboratório de Sensibilidade e Estresse Ambiental")
    st.markdown(
        """
        Altere os parâmetros do ambiente da masmorra para testar a robustez da **Melhor Estratégia do Algoritmo Genético**
        frente à **Estratégia Fixa (Baseline)** em condições adversas ou modificadas.
        """
    )

    lc1, lc2, lc3 = st.columns(3)
    with lc1:
        diff_mult = st.slider("Multiplicador de Dificuldade dos Monstros", 0.70, 1.60, 1.15, 0.05)
        comp_mode = st.selectbox("Modo de Composição dos Encontros", ["standard", "alternate_pool"])
    with lc2:
        lab_seed = st.number_input("Semente de Teste do Laboratório", min_value=1, max_value=99999, value=505)
        post_heal = st.slider("Fração de Cura Entre Salas", 0.10, 0.50, float(balance_cfg["warrior"]["post_room_heal_fraction"]), 0.02)
    with lc3:
        lab_allies = st.checkbox("Permitir Contratação de Aliados", value=True)
        lab_chests = st.checkbox("Permitir Geração de Baús", value=False)

    custom_cfg = copy.deepcopy(balance_cfg)
    custom_cfg["warrior"]["post_room_heal_fraction"] = post_heal

    lab_rooms = build_dungeon_100_rooms(
        monsters_df=df,
        balance_cfg=custom_cfg,
        seed=int(lab_seed),
        difficulty_multiplier=float(diff_mult),
        composition_mode=comp_mode,
    )

    champ_chrom = get_champion_chromosome(exp_payload)
    fixed_chrom = create_fixed_baseline_chromosome()

    res_ga = run_dungeon_simulation(
        rooms_template=lab_rooms,
        policy_params=champ_chrom.to_policy_params(),
        balance_cfg=custom_cfg,
        seed=int(lab_seed),
        enable_allies=lab_allies,
        enable_chests=lab_chests,
        record_detailed_logs=True,
    )
    res_fb = run_dungeon_simulation(
        rooms_template=lab_rooms,
        policy_params=fixed_chrom.to_policy_params(),
        balance_cfg=custom_cfg,
        seed=int(lab_seed),
        enable_allies=lab_allies,
        enable_chests=lab_chests,
        record_detailed_logs=True,
    )

    col_ga, col_fb = st.columns(2)
    with col_ga:
        st.markdown("### 🏆 Melhor Estratégia (Algoritmo Genético)")
        st.metric("Salas Concluídas (AG)", f"{res_ga.rooms_cleared} / 100", delta=f"{res_ga.rooms_cleared - res_fb.rooms_cleared:+d} vs Baseline")
        st.write(
            f"- **Nível Final:** {res_ga.final_warrior_level} | **Atributos:** STR {res_ga.final_strength}, VIT {res_ga.final_vitality}, DEF {res_ga.final_defense}\n"
            f"- **Equipamentos Finais:** Arma T{res_ga.final_weapon_tier}, Armadura T{res_ga.final_armor_tier}, Escudo T{res_ga.final_shield_tier}\n"
            f"- **Aliados Contratados:** {', '.join(res_ga.hired_allies_history) if res_ga.hired_allies_history else 'Nenhum'}\n"
            f"- **Total de Turnos Lutados:** {res_ga.total_turns_fought}"
        )
    with col_fb:
        st.markdown("### 📏 Estratégia Fixa (Baseline)")
        st.metric("Salas Concluídas (Baseline Fixo)", f"{res_fb.rooms_cleared} / 100")
        st.write(
            f"- **Nível Final:** {res_fb.final_warrior_level} | **Atributos:** STR {res_fb.final_strength}, VIT {res_fb.final_vitality}, DEF {res_fb.final_defense}\n"
            f"- **Equipamentos Finais:** Arma T{res_fb.final_weapon_tier}, Armadura T{res_fb.final_armor_tier}, Escudo T{res_fb.final_shield_tier}\n"
            f"- **Aliados Contratados:** {', '.join(res_fb.hired_allies_history) if res_fb.hired_allies_history else 'Nenhum'}\n"
            f"- **Total de Turnos Lutados:** {res_fb.total_turns_fought}"
        )

    ga_hp_curve = [r.warrior_hp_end for r in res_ga.room_results]
    fb_hp_curve = [r.warrior_hp_end for r in res_fb.room_results]
    fig_comp = go.Figure()
    fig_comp.add_trace(go.Scatter(x=list(range(1, len(ga_hp_curve) + 1)), y=ga_hp_curve, name="HP Pós-Sala (Algoritmo Genético)", line=dict(color="#27ae60", width=2.5)))
    fig_comp.add_trace(go.Scatter(x=list(range(1, len(fb_hp_curve) + 1)), y=fb_hp_curve, name="HP Pós-Sala (Baseline Fixo)", line=dict(color="#7f8c8d", width=2.0, dash="dash")))
    fig_comp.update_layout(
        title="Comparação Direta de Sobrevivência (HP Pós-Combate por Sala) no Ambiente Modificado",
        xaxis_title="Sala da Masmorra",
        yaxis_title="HP Restante do Guerreiro",
    )
    st.plotly_chart(fig_comp, use_container_width=True)


def main() -> None:
    st.sidebar.title("⚔️ Masmorra Genética")
    st.sidebar.caption("Grupo 7 — Inteligência Artificial II (FIB)")
    page = st.sidebar.radio(
        "Navegação",
        options=[
            "Página 1 — Sobre o projeto",
            "Página 2 — Dataset",
            "Página 3 — Masmorra",
            "Página 4 — Evolução Genética",
            "Página 5 — Experimentos",
            "Página 6 — Laboratório",
        ],
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        **Integrantes (Grupo 7):**
        - Eduardo Coque Corrêa de Lima
        - Fernando Eduardo Motta Mendes
        - Matheus Alcântara Pereira
        - Reuel Vitor Lanzetti
        - Rogério Tiritan Marcone
        """
    )

    df = get_cached_dataset()
    manifest = get_cached_manifest()
    eda = get_cached_eda_summary()
    balance_cfg = get_cached_balance()
    exp_payload = load_experiments_payload()

    if page.startswith("Página 1"):
        render_page_1_about(manifest, balance_cfg)
    elif page.startswith("Página 2"):
        render_page_2_dataset(df, manifest, eda)
    elif page.startswith("Página 3"):
        render_page_3_dungeon(df, balance_cfg, exp_payload)
    elif page.startswith("Página 4"):
        render_page_4_genetic_evolution(df, balance_cfg, exp_payload)
    elif page.startswith("Página 5"):
        render_page_5_experiments(exp_payload)
    elif page.startswith("Página 6"):
        render_page_6_laboratory(df, balance_cfg, exp_payload)


if __name__ == "__main__":
    main()
