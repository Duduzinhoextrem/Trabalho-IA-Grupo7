"""Aplicação Web Interativa em Português Claro e Didático.

Masmorra Genética: A Evolução do Guerreiro — Grupo 7 (IA II - FIB).
Projetada para que qualquer pessoa (mesmo sem conhecimento prévio de IA ou RPG)
consiga entender o projeto, a inteligência artificial e as decisões da simulação.
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
from src.experiments.baselines import create_fixed_baseline_chromosome
from src.game.combat import run_dungeon_simulation
from src.game.dungeon import build_dungeon_100_rooms
from src.game.monsters import load_balance_config
from src.genetic.chromosome import Chromosome
from src.genetic.optimizer import run_genetic_algorithm
from src.ui.localization import (
    ALLY_CLASS_LABELS,
    CREATURE_SIZE_TRANSLATIONS,
    CREATURE_TYPE_TRANSLATIONS,
    GENE_FRIENDLY_INFO,
    translate_creature_size,
    translate_creature_type,
    translate_reason,
)

st.set_page_config(
    page_title="Masmorra Genética — IA II (Grupo 7)",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def get_cached_dataset() -> pd.DataFrame:
    df = load_processed_dataset()
    df["tipo_pt"] = df["type"].map(lambda t: CREATURE_TYPE_TRANSLATIONS.get(str(t).lower(), str(t).capitalize()))
    df["tamanho_pt"] = df["size"].map(lambda s: CREATURE_SIZE_TRANSLATIONS.get(str(s), str(s)))
    return df


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
    return Chromosome(
        genes=[
            0.1628, 0.5511, 0.2861,
            0.0788, 0.1887, 0.3096, 0.4657, 0.1828,
            0.6686, 0.0121, 0.3193,
            0.0113, 0.0, 38.8416, 1.4530, 1.1129,
        ]
    )


def format_chromosome_table(chromosome: Chromosome) -> pd.DataFrame:
    """Gera uma tabela amigável em português explicando cada um dos 16 genes."""
    raw_dict = chromosome.to_named_dict()
    rows = []
    for gene_key, val in raw_dict.items():
        info = GENE_FRIENDLY_INFO.get(
            gene_key, {"nome": gene_key, "explicacao": "Configuração da estratégia."}
        )
        if "discrete" in gene_key:
            val_str = "Sim (Aliado Primeiro)" if val >= 0.5 else "Não (Equipamento Primeiro)"
        elif "reserve" in gene_key:
            val_str = f"{val:.1f} moedas de ouro"
        elif "threshold" in gene_key:
            val_str = f"{val:.2f}x do custo"
        elif "weight" in gene_key or "priority" in gene_key or "prio" in gene_key:
            val_str = f"{val * 100:.1f}%"
        else:
            val_str = f"{val:.3f}"

        rows.append(
            {
                "Decisão da IA": info["nome"],
                "Valor Otimizado": val_str,
                "O que isso significa na prática?": info["explicacao"],
            }
        )
    return pd.DataFrame(rows)


# ==============================================================================
# PÁGINA 1 — SOBRE O PROJETO
# ==============================================================================
def render_page_1_about(manifest: dict[str, Any], balance_cfg: dict[str, Any]) -> None:
    st.title("⚔️ Masmorra Genética: A Evolução do Guerreiro")
    st.subheader("Grupo 7 — Inteligência Artificial II — Faculdades Integradas de Bauru (FIB)")

    st.info(
        """
        💡 **O que é este projeto? (Para entender em 1 minuto):**  
        Imagine um guerreiro que entra sozinho em uma masmorra de **100 salas cheias de monstros perigosos**,
        carregando apenas uma espada básica de ferro e sem nenhuma armadura. Conforme ele vence as batalhas, ganha experiência
        para ficar mais forte, junta moedas de ouro para comprar equipamentos no mercado e, nos níveis 5 e 15,
        pode contratar até dois companheiros (como Magos, Arqueiros ou Padres).
        
        **A grande pergunta de Inteligência Artificial é:**  
        *Qual é a combinação perfeita de escolhas para zerar as 100 salas sem morrer?*  
        Em vez de um humano adivinhar as respostas, usamos um **Algoritmo Genético (Computação Evolutiva)**:
        a própria IA testa centenas de estratégias, combina as melhores ideias e descobre sozinha a fórmula do sucesso!
        """
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            ### 👥 Integrantes do Grupo 7 e Responsabilidades
            | Integrante | Frente de Trabalho | O que fez no projeto? |
            | :--- | :--- | :--- |
            | **Eduardo Coque Corrêa de Lima** | Coordenação & Algoritmo Genético | Criou o cérebro evolutivo da IA e a integração geral |
            | **Matheus Alcântara Pereira** | Dados Oficiais & Análise (EDA) | Coletou os 334 monstros reais da API e analisou as estatísticas |
            | **Fernando Eduardo Motta Mendes** | Simulador de Combate & Telas | Criou as 100 salas, o combate em turnos e a interface gráfica |
            | **Rogério Tiritan Marcone** | Metodologia & Documentação | Escreveu o Canvas, Model Card e Resumo Acadêmico |
            | **Reuel Vitor Lanzetti** | Experimentos & Divulgação | Realizou os testes científicos, gráficos, slides e vídeo |
            """
        )

    with col2:
        st.markdown(
            f"""
            ### 📜 De onde vieram os monstros? (Dados 100% Reais)
            - **Zero dados inventados:** Não criamos monstros fictícios. Todos os inimigos vieram da **API oficial de Dungeons & Dragons 5ª Edição (SRD 2014)**.
            - **Fonte Oficial:** [D&D 5e SRD REST API](https://www.dnd5eapi.co/api/2014/monsters) (Wizards of the Coast LLC).
            - **Licença Livre:** Creative Commons Attribution 4.0 (**CC-BY-4.0**) e Open Game License (**OGL v1.0a**).
            - **Total de Criaturas Válidas:** `{manifest.get('collected_records_count', 334)}` criaturas reais.
            - **Cópia Congelada e Auditável:** Salva no repositório com código de segurança SHA-256 `{manifest.get('raw_file_sha256', '')[:20]}...` para garantir que qualquer pessoa no mundo consiga repetir o experimento com os mesmos resultados.
            """
        )

    st.markdown("---")
    st.markdown(
        """
        ### 🧠 Como a IA resolveu o problema? (Metodologia Explicada)
        Diferente de uma IA que tenta apenas prever o futuro ou classificar fotos, nosso sistema usa **Otimização de Políticas por Algoritmos Genéticos**:
        1. **DNA da Estratégia (Cromossomo de 16 Genes):** Criamos uma lista de 16 números que representam a "personalidade" do guerreiro (ex: se ele prefere investir em força ou vida, se compra armadura antes de armas e qual ajudante ele contrata primeiro).
        2. **Simulação Real:** O guerreiro enfrenta as 100 salas seguindo estritamente essas regras, sem saber o que vem pela frente.
        3. **Seleção Natural:** Quem morre na sala 10 é descartado; quem chega na sala 80 ou 90 passa seus "genes" para as próximas gerações.
        4. **Evolução:** Ao cruzar as melhores estratégias e adicionar pequenas mutações, a IA encontrou uma estratégia que alcança **98 salas no treino e 97 salas em masmorras nunca antes vistas!**
        """
    )


# ==============================================================================
# PÁGINA 2 — DATASET E ANÁLISE EXPLORATÓRIA
# ==============================================================================
def render_page_2_dataset(df: pd.DataFrame, manifest: dict[str, Any], eda: dict[str, Any]) -> None:
    st.title("📊 O Bestiário Oficial: 334 Monstros de D&D 5e")
    st.markdown(
        """
        Antes de criar o algoritmo, analisamos a fundo todos os monstros oficiais do jogo.
        Aqui você pode pesquisar qualquer criatura, ver suas estatísticas originais e conferir o que a matemática revelou sobre o balanceamento do D&D.
        """
    )

    st.info(
        """
        💡 **Dica de Navegação:** Use os filtros abaixo para encontrar monstros clássicos como o **Goblin**, o **Dragão Vermelho** ou o **Tarrasque**
        e veja como os atributos deles foram convertidos para o combate da nossa masmorra.
        """
    )

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Monstros Reais Coletados", len(df))
    m2.metric("Registros Íntegros", "100% (Sem Faltas)")
    m3.metric("Nível de Desafio (CR)", "0 a 30")
    m4.metric("Pontos de Vida (HP)", "1 a 676")
    m5.metric("Defesa de Armadura (CA)", "5 a 25")

    f1, f2, f3, f4 = st.columns(4)
    with f1:
        tipos_disp = sorted(df["tipo_pt"].unique())
        filtro_tipo = st.multiselect("Filtrar por Tipo de Monstro", options=tipos_disp, default=[])
    with f2:
        tam_disp = sorted(df["tamanho_pt"].unique())
        filtro_tam = st.multiselect("Filtrar por Porte / Tamanho", options=tam_disp, default=[])
    with f3:
        filtro_cr = st.slider("Nível de Desafio (CR)", 0.0, 30.0, (0.0, 30.0), 0.5)
    with f4:
        busca_nome = st.text_input("Buscar por nome do monstro", placeholder="Ex: goblin, dragon, skeleton...")

    df_view = df[(df["challenge_rating"] >= filtro_cr[0]) & (df["challenge_rating"] <= filtro_cr[1])].copy()
    if filtro_tipo:
        df_view = df_view[df_view["tipo_pt"].isin(filtro_tipo)]
    if filtro_tam:
        df_view = df_view[df_view["tamanho_pt"].isin(filtro_tam)]
    if busca_nome.strip():
        termo = busca_nome.strip().lower()
        df_view = df_view[df_view["name"].str.lower().str.contains(termo) | df_view["index"].str.lower().str.contains(termo)]

    st.caption(f"Exibindo **{len(df_view)}** de **{len(df)}** criaturas cadastradas.")

    # Tabela com nomes de colunas 100% em português
    tabela_pt = df_view[
        [
            "name",
            "tipo_pt",
            "tamanho_pt",
            "challenge_rating",
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
    ].rename(
        columns={
            "name": "Nome da Criatura",
            "tipo_pt": "Tipo",
            "tamanho_pt": "Porte",
            "challenge_rating": "Nível de Desafio (CR)",
            "hit_points": "Vida (HP)",
            "armor_class": "Classe de Armadura (CA)",
            "strength": "Força",
            "dexterity": "Destreza",
            "constitution": "Constituição",
            "max_attack_bonus": "Bônus de Acerto",
            "best_action_damage": "Dano do Golpe Principal",
            "estimated_dpr_raw": "Dano Estimado / Turno",
            "has_physical_resistance": "Resiste a Dano Físico?",
            "has_magical_resistance": "Resiste a Dano Mágico?",
            "source_url": "Link Oficial na API",
        }
    )
    st.dataframe(tabela_pt, use_container_width=True, height=320)

    st.subheader("🔍 As 4 Grandes Descobertas da Análise de Dados (EDA)")
    d1, d2 = st.columns(2)
    with d1:
        st.markdown(
            """
            **1. Vida cresce em linha reta, mas Experiência dispara como um foguete:**  
            - A vida dos monstros tem uma correlação linear quase perfeita com o perigo ($r = 0,94$). Um monstro fraco tem 12 de vida e um chefe tem cerca de 400.
            - Porém, o XP salta de 50 para mais de 150.000 (crescimento exponencial!). Se usássemos o XP direto sem freio matemático, o guerreiro ganharia 30 níveis em uma única sala final! Por isso, criamos uma fórmula de XP ajustada e justa.
            
            **2. Destreza não aumenta com o perigo do monstro ($r = -0,01$):**  
            - Em videogames comuns, monstros fortes são mais rápidos e ágeis. No D&D 5e oficial, a estatística provou que dragões e gigantes têm a mesma destreza média (12 a 13) que um goblin comum! O que torna monstros fortes perigosos é sua Força e Constituição brutais.
            """
        )
    with d2:
        st.markdown(
            """
            **3. Monstros estranhos que precisavam de cuidado especial:**  
            - Descobrimos 5 criaturas oficiais no dataset que não têm golpes diretos de arma: o sapo (*frog*), o cavalo-marinho (*sea-horse*), o fungo estridente (*shrieker*) e a forma de névoa do vampiro (*vampire-mist*, CR 13 mas sem ataque!).
            - Se não tivéssemos tratado isso, a masmorra poderia colocar um vampiro inofensivo na sala 60!
            
            **4. A armadilha das Resistências (Física vs Mágica):**  
            - 25,4% dos monstros resistem a cortes e flechas, e 39,8% resistem a magias.
            - Isso provou matematicamente que montar um grupo só com guerreiros físicos ou só com magos é garantia de fracasso nas salas avançadas!
            """
        )

    with st.expander("📈 Ver Gráficos Interativos da Distribuição", expanded=False):
        c_a, c_b = st.columns(2)
        with c_a:
            fig1 = px.scatter(
                df_view,
                x="challenge_rating",
                y="hit_points",
                color="tipo_pt",
                hover_name="name",
                labels={"challenge_rating": "Nível de Desafio (CR)", "hit_points": "Pontos de Vida (HP)", "tipo_pt": "Tipo"},
                title="Relação: Nível de Desafio vs. Pontos de Vida (Correlação r = 0,9404)",
            )
            st.plotly_chart(fig1, use_container_width=True)
        with c_b:
            fig2 = px.scatter(
                df_view,
                x="challenge_rating",
                y="armor_class",
                color="tamanho_pt",
                hover_name="name",
                labels={"challenge_rating": "Nível de Desafio (CR)", "armor_class": "Classe de Armadura (CA)", "tamanho_pt": "Porte"},
                title="Relação: Nível de Desafio vs. Defesa de Armadura (5 a 25)",
            )
            st.plotly_chart(fig2, use_container_width=True)


# ==============================================================================
# PÁGINA 3 — MASMORRA DE 100 SALAS
# ==============================================================================
def render_page_3_dungeon(
    df: pd.DataFrame,
    balance_cfg: dict[str, Any],
    exp_payload: dict[str, Any] | None,
) -> None:
    st.title("🏰 A Masmorra das 100 Salas")
    st.markdown(
        """
        Nesta tela você assiste à jornada do guerreiro sala por sala.
        Ele começa fraco na **Sala 1**, enfrenta monstros progressivamente mais difíceis e tenta alcançar a **Sala 100** para vencer o Chefe Final!
        """
    )

    st.info(
        """
        💡 **Como testar:**
        1. Escolha a **Estratégia Campeã da IA** para ver até onde ela chega.
        2. Mude para a **Estratégia Fixa Tradicional** e veja onde o guerreiro comete erros e é derrotado.
        3. Ou monte uma **Estratégia Manual** com as suas próprias preferências de atributos e aliados!
        """
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        modo_estrategia = st.selectbox(
            "Quem comanda o guerreiro?",
            options=[
                "1. Estratégia Otimizada (Campeã do Algoritmo Genético)",
                "2. Estratégia Fixa Tradicional (Regras Equilibradas)",
                "3. Minha Própria Estratégia (Configuração Manual)",
            ],
        )
    with c2:
        semente_masmorra = st.number_input(
            "Semente da Masmorra (Gera as salas de forma idêntica)",
            min_value=1,
            max_value=99999,
            value=201,
            step=1,
        )
    with c3:
        habilitar_baus = st.checkbox("Permitir Baús com Equipamentos após vitórias?", value=True)

    if modo_estrategia.startswith("1."):
        cromossomo_atual = get_champion_chromosome(exp_payload)
        st.success("✅ Usando a **Estratégia Campeã descoberta pelo Algoritmo Genético**.")
    elif modo_estrategia.startswith("2."):
        cromossomo_atual = create_fixed_baseline_chromosome()
        st.warning("⚠️ Usando a **Estratégia Fixa Tradicional** (divide pontos igualmente e contrata Arqueiro + Mago).")
    else:
        st.markdown("#### 🛠️ Ajuste os Botões da Sua Estratégia:")
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.markdown("**Atributos do Guerreiro:**")
            peso_forca = st.slider("Foco em Força (Dano de Espada)", 0.05, 0.90, 0.20, 0.05)
            peso_vida = st.slider("Foco em Vida (HP)", 0.05, 0.90, 0.55, 0.05)
            peso_defesa = st.slider("Foco em Defesa (Proteção)", 0.05, 0.90, 0.25, 0.05)
        with col_m2:
            st.markdown("**Preferência de Ajudantes (Aliados):**")
            prio_mago = st.slider("Mago (Magias à distância)", 0.0, 1.0, 0.10, 0.05)
            prio_arq = st.slider("Arqueiro (Flechas à distância)", 0.0, 1.0, 0.20, 0.05)
            prio_monge = st.slider("Monge (Corpo a corpo resistente)", 0.0, 1.0, 0.30, 0.05)
            prio_padre = st.slider("Padre (Cura o grupo durante a luta)", 0.0, 1.0, 0.90, 0.05)
            prio_alquimista = st.slider("Alquimista (Poções e enfraquecimento)", 0.0, 1.0, 0.20, 0.05)
        with col_m3:
            st.markdown("**Economia no Mercado:**")
            foco_equip = st.slider("Prioridade de Itens (0=Armadura primeiro | 1=Arma primeiro)", 0.0, 1.0, 0.05, 0.05)
            contratar_primeiro = st.selectbox("Contratar Aliado antes de Comprar Itens?", [1.0, 0.0], format_func=lambda x: "Sim" if x == 1.0 else "Não")
            reserva_ouro = st.slider("Reserva de Ouro 'Pé-de-Meia' (Não gastar)", 0.0, 120.0, 40.0, 5.0)
            limiar_compra = st.slider("Paciência para economizar por itens melhores", 1.0, 1.8, 1.45, 0.05)
            limiar_ajudante = st.slider("Paciência para contratar aliados", 1.0, 1.8, 1.10, 0.05)

        cromossomo_atual = Chromosome(
            genes=[
                peso_forca, peso_vida, peso_defesa,
                prio_mago, prio_arq, prio_monge, prio_padre, prio_alquimista,
                0.60, 0.10, 0.30,
                foco_equip, float(contratar_primeiro), reserva_ouro, limiar_compra, limiar_ajudante,
            ]
        )

    with st.expander("🧬 Ver os 16 Genes Decodificados em Linguagem Simples", expanded=False):
        st.dataframe(format_chromosome_table(cromossomo_atual), use_container_width=True)

    salas = build_dungeon_100_rooms(df, balance_cfg, seed=int(semente_masmorra))
    resultado = run_dungeon_simulation(
        rooms_template=salas,
        policy_params=cromossomo_atual.to_policy_params(),
        balance_cfg=balance_cfg,
        seed=int(semente_masmorra),
        enable_allies=True,
        enable_chests=habilitar_baus,
        record_detailed_logs=True,
    )

    st.markdown("### 🏁 Placar da Tentativa")
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Salas Concluídas", f"{resultado.rooms_cleared} de 100")
    if resultado.completed_all_100:
        k2.metric("Resultado", "🏆 ZEROU AS 100 SALAS!", delta="Vitória Épica")
    else:
        k2.metric("Resultado", f"💀 Morreu na Sala {resultado.failure_room}")
    k3.metric("Nível do Guerreiro", f"Nível {resultado.final_warrior_level}")
    k4.metric("Atributos (FOR / VID / DEF)", f"{resultado.final_strength} / {resultado.final_vitality} / {resultado.final_defense}")
    k5.metric("Itens (Arma / Armadura / Escudo)", f"Nível {resultado.final_weapon_tier} / {resultado.final_armor_tier} / {resultado.final_shield_tier}")
    
    aliados_traduzidos = [ALLY_CLASS_LABELS.get(a, {}).get("nome", a) for a in resultado.active_allies_final]
    k6.metric("Aliados no Final", ", ".join(aliados_traduzidos) if aliados_traduzidos else "Nenhum (Lutou só)")

    if resultado.room_results:
        lista_salas = []
        for r in resultado.room_results:
            al_str = ", ".join([ALLY_CLASS_LABELS.get(a.split()[0].lower(), {}).get("nome", a) for a in r.active_allies_end])
            lista_salas.append(
                {
                    "Sala": r.room_number,
                    "Resultado": "Vitória" if r.victory else "Derrota",
                    "Duração (Turnos)": r.turns_taken,
                    "Vida Inicial": r.warrior_hp_start,
                    "Vida Final": r.warrior_hp_end,
                    "Vida Máxima": r.warrior_max_hp,
                    "Nível": r.warrior_level_end,
                    "Ouro na Sala": r.gold_earned,
                    "Cofre de Ouro": r.gold_end,
                    "Aliados Presentes": al_str if al_str else "Nenhum",
                    "Monstros Enfrentados": ", ".join(r.enemies_faced),
                    "Código Oficial SRD": ", ".join(r.enemy_source_indices),
                }
            )
        df_salas = pd.DataFrame(lista_salas)

        st.subheader("📈 Gráficos de Sobrevivência e Economia")
        g1, g2 = st.columns(2)
        with g1:
            fig_hp = go.Figure()
            fig_hp.add_trace(go.Scatter(x=df_salas["Sala"], y=df_salas["Vida Máxima"], name="Vida Máxima Total", line=dict(color="#2980b9", dash="dot")))
            fig_hp.add_trace(go.Scatter(x=df_salas["Sala"], y=df_salas["Vida Final"], name="Vida Restante no Fim da Sala", line=dict(color="#27ae60", width=2)))
            fig_hp.update_layout(title="Reserva de Vida do Guerreiro ao Longo das Salas", xaxis_title="Número da Sala", yaxis_title="Pontos de Vida (HP)")
            st.plotly_chart(fig_hp, use_container_width=True)
        with g2:
            fig_gold = go.Figure()
            fig_gold.add_trace(go.Scatter(x=df_salas["Sala"], y=df_salas["Cofre de Ouro"], name="Moedas de Ouro Acumuladas", line=dict(color="#f39c12", width=2)))
            fig_gold.add_trace(go.Scatter(x=df_salas["Sala"], y=df_salas["Duração (Turnos)"], name="Turnos de Combate", yaxis="y2", line=dict(color="#e74c3c", dash="dash")))
            fig_gold.update_layout(
                title="Evolução do Dinheiro (Ouro) e Duração dos Combates",
                xaxis_title="Número da Sala",
                yaxis=dict(title="Moedas de Ouro"),
                yaxis2=dict(title="Turnos Gastos", overlaying="y", side="right"),
            )
            st.plotly_chart(fig_gold, use_container_width=True)

        st.subheader("📜 Diário da Aventura (Tabela Sala por Sala)")
        st.dataframe(df_salas, use_container_width=True, height=260)

        num_sel = st.slider("Escolha uma sala para ver o combate golpe a golpe:", 1, len(resultado.room_results), len(resultado.room_results))
        detalhe_sala = resultado.room_results[num_sel - 1]
        obj_sala = salas[num_sel - 1]

        c_info1, c_info2 = st.columns(2)
        with c_info1:
            st.markdown(f"**Monstros Oficiais na Sala {detalhe_sala.room_number}:**")
            for m in obj_sala.enemies:
                st.markdown(
                    f"- 👾 **{m.source_name}** (`{m.source_index}`, Nível de Desafio CR {m.challenge_rating:g})  \n"
                    f"  Vida: `{m.max_hp}` | Defesa: `{m.defense:.1f}` | Dano Físico: `{m.physical_damage:.1f}` | Dano Mágico: `{m.magical_damage:.1f}`  \n"
                    f"  🔗 [Ver Ficha Original na API Oficial do D&D]({m.source_url})"
                )
            if detalhe_sala.market_transactions:
                st.markdown("**🛒 Compras e Contratações Feitas Nesta Sala:**")
                for tx in detalhe_sala.market_transactions:
                    if tx.get("action") == "buy_equipment":
                        st.write(f"- Comprou **{tx.get('item_name')}** (Nível {tx.get('new_tier')}) por **{tx.get('net_cost')} moedas**.")
                    elif tx.get("action") == "hire_ally":
                        nome_a = ALLY_CLASS_LABELS.get(tx.get('ally_class', ''), {}).get('nome', tx.get('ally_class'))
                        st.write(f"- Contratou o companheiro **{nome_a}** por **{tx.get('cost')} moedas**.")
        with c_info2:
            st.markdown(f"**⚔️ Relato da Luta — Sala {detalhe_sala.room_number} ({detalhe_sala.turns_taken} turnos):**")
            st.code("\n".join(detalhe_sala.combat_log) if detalhe_sala.combat_log else "Sem golpes registrados.")


# ==============================================================================
# PÁGINA 4 — EVOLUÇÃO GENÉTICA
# ==============================================================================
def render_page_4_genetic_evolution(
    df: pd.DataFrame,
    balance_cfg: dict[str, Any],
    exp_payload: dict[str, Any] | None,
) -> None:
    st.title("🧬 Como a Inteligência Artificial Aprendeu?")
    st.markdown(
        """
        Nesta tela você entende e pode assistir ao vivo ao funcionamento do **Algoritmo Genético**.
        """
    )

    st.info(
        """
        💡 **O que é um Algoritmo Genético em termos simples?**  
        É uma técnica inspirada na teoria da evolução de Charles Darwin:
        1. Criamos uma população de guerreiros, cada um com uma estratégia diferente gerada aleatoriamente.
        2. Todos tentam vencer a masmorra.
        3. Os guerreiros que morrem nas primeiras salas são eliminados (**Seleção Natural**).
        4. Os que avançam mais longe "têm filhos": misturamos as melhores partes de suas estratégias (**Cruzamento**)
           e adicionamos pequenas variações criativas (**Mutação**).
        5. Repetimos isso ao longo de várias gerações até a IA encontrar a estratégia perfeita!
        """
    )

    aba_sci, aba_demo = st.tabs(
        ["🏆 Campeão dos Experimentos Oficiais (Modo Científico)", "⚡ Ver a IA Aprendendo ao Vivo (Modo Demonstração)"]
    )

    with aba_sci:
        if exp_payload and "best_champion_strategy" in exp_payload:
            champ = exp_payload["best_champion_strategy"]
            hist_df = pd.DataFrame(champ["history"])
            best_c = champ["best_chromosome"]

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Média de Salas Vencidas", f"{best_c['mean_rooms_cleared']:.1f} de 100")
            c2.metric("Taxa de Sucesso Total (Zerar)", f"{best_c['completion_rate'] * 100:.0f}% das vezes")
            c3.metric("Estratégias Avaliadas", champ["total_objective_evaluations"])
            c4.metric("Masmorras Simuladas no Treino", champ["total_simulation_runs"])

            col_g1, col_g2 = st.columns(2)
            with col_g1:
                fig_f = go.Figure()
                fig_f.add_trace(go.Scatter(x=hist_df["generation"], y=hist_df["best_mean_rooms"], mode="lines+markers", name="Melhor Guerreiro da Geração", line=dict(color="#27ae60", width=2.5)))
                fig_f.add_trace(go.Scatter(x=hist_df["generation"], y=hist_df["pop_mean_rooms"], mode="lines+markers", name="Média de Todos os Guerreiros", line=dict(color="#2980b9", dash="dot")))
                fig_f.update_layout(title="Curva de Aprendizado: Quantas salas o guerreiro vence a cada geração?", xaxis_title="Geração da IA", yaxis_title="Salas Vencidas")
                st.plotly_chart(fig_f, use_container_width=True)
            with col_g2:
                fig_d = px.line(
                    hist_df,
                    x="generation",
                    y="diversity_index",
                    markers=True,
                    labels={"generation": "Geração", "diversity_index": "Grau de Diversidade das Ideias"},
                    title="Variedade Genética: A IA continuou testando ideias novas ou viciou?",
                )
                st.plotly_chart(fig_d, use_container_width=True)

            st.subheader("📋 O DNA da Estratégia Campeã (Explicado Item por Item)")
            st.dataframe(format_chromosome_table(Chromosome(genes=best_c["genes"])), use_container_width=True)
        else:
            st.warning("Resultados oficiais em processamento.")

    with aba_demo:
        st.markdown("### 🧪 Experimente treinar a sua própria IA agora:")
        st.write("Escolha abaixo o tamanho da população e quantas gerações deseja rodar:")

        d1, d2, d3 = st.columns(3)
        with d1:
            pop_demo = st.slider("Quantidade de Guerreiros por Geração (População)", 6, 20, 10, 2)
        with d2:
            gen_demo = st.slider("Quantas Gerações Evoluir?", 3, 12, 6, 1)
        with d3:
            mut_demo = st.slider("Taxa de Mutação (Criatividade da IA)", 0.02, 0.30, 0.10, 0.02)

        if st.button("🚀 Iniciar Treinamento ao Vivo", type="primary"):
            with st.spinner("Os guerreiros estão batalhando nas masmorras..."):
                dungeons_demo = {s: build_dungeon_100_rooms(df, balance_cfg, seed=s) for s in [101, 102, 103]}
                res_demo = run_genetic_algorithm(
                    dungeons_by_seed=dungeons_demo,
                    balance_cfg=balance_cfg,
                    pop_size=int(pop_demo),
                    generations=int(gen_demo),
                    mutation_rate=float(mut_demo),
                    seed=42,
                )
            st.success(
                f"Treinamento finalizado em {res_demo.elapsed_seconds:.2f} segundos! "
                f"A melhor estratégia alcançou **{res_demo.best_chromosome.mean_rooms_cleared:.1f} salas** "
                f"com taxa de conclusão de **{res_demo.best_chromosome.completion_rate * 100:.0f}%**."
            )
            df_hist_demo = pd.DataFrame([h.to_dict() for h in res_demo.history])
            fig_demo = px.line(
                df_hist_demo,
                x="generation",
                y="best_mean_rooms",
                markers=True,
                labels={"generation": "Geração", "best_mean_rooms": "Salas Vencidas"},
                title="Progresso da Sua IA ao Longo das Gerações",
            )
            st.plotly_chart(fig_demo, use_container_width=True)


# ==============================================================================
# PÁGINA 5 — EXPERIMENTOS CIENTÍFICOS
# ==============================================================================
def render_page_5_experiments(exp_payload: dict[str, Any] | None) -> None:
    st.title("🔬 Experimentos Científicos e Comparações")
    st.markdown(
        """
        Para provar cientificamente que o Algoritmo Genético realmente funciona, comparamos a nossa IA
        com duas estratégias de referência:
        1. **Estratégia Fixa (Baseline):** O que um jogador humano faria com regras comuns e equilibradas.
        2. **Busca Aleatória (Sorte Pura):** Gerar 240 estratégias totalmente ao acaso e pegar a melhor.
        """
    )

    if not exp_payload:
        st.warning("Arquivo de evidências ainda não carregado.")
        return

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "🏆 Quem venceu? (Comparação com Baselines)",
            "🧬 Experimento 1: Taxas de Mutação",
            "👥 Experimento 2: Tamanho da População",
            "🌍 Experimento 4: Teste de Generalização",
            "⚠️ Análise de Falhas e O Que a IA Aprendeu",
        ]
    )

    with tab1:
        st.subheader("O Algoritmo Genético é Melhor Que Jogar com Regras Fixas ou no Sorteio?")
        exp3 = exp_payload["experiment_3_baselines"]["methods"]
        
        comp_df = pd.DataFrame(
            [
                {
                    "Estratégia": "1. Estratégia Fixa Tradicional",
                    "Como funciona?": "Distribui pontos igualmente (1/3 força, vida e defesa) e contrata Arqueiro + Mago",
                    "Salas Vencidas no Treino": f"{exp3['fixed_baseline']['train_mean_rooms']:.1f}",
                    "Salas em Masmorras Novas (Validação)": f"{exp3['fixed_baseline']['val_mean_rooms']:.1f} ± {exp3['fixed_baseline']['val_std_rooms']:.1f}",
                    "Taxa de Vitória Total (100 Salas)": f"{exp3['fixed_baseline']['val_completion_rate'] * 100:.1f}% (Nunca zerou)",
                },
                {
                    "Estratégia": "2. Busca Aleatória (Sorte)",
                    "Como funciona?": "Testa 240 estratégias sorteadas ao acaso e escolhe a melhor delas",
                    "Salas Vencidas no Treino": f"{exp3['random_search']['train_rooms_across_repeats']['mean']:.1f}",
                    "Salas em Masmorras Novas (Validação)": f"{exp3['random_search']['val_rooms_across_repeats']['mean']:.1f} ± {exp3['random_search']['val_rooms_across_repeats']['std']:.1f}",
                    "Taxa de Vitória Total (100 Salas)": f"{exp3['random_search']['val_completion_rate_mean'] * 100:.1f}%",
                },
                {
                    "Estratégia": "3. Algoritmo Genético (Nossa IA)",
                    "Como funciona?": "Evolui 240 estratégias ao longo de gerações com seleção, cruzamento e elitismo",
                    "Salas Vencidas no Treino": f"{exp3['genetic_algorithm']['train_rooms_across_repeats']['mean']:.1f} (Campeão: 98,2)",
                    "Salas em Masmorras Novas (Validação)": f"{exp3['genetic_algorithm']['val_rooms_across_repeats']['mean']:.1f} (Campeão: 96,9 ± 2,7)",
                    "Taxa de Vitória Total (100 Salas)": f"{exp3['genetic_algorithm']['val_completion_rate_mean'] * 100:.1f}% (Maior taxa de conclusão)",
                },
            ]
        )
        st.dataframe(comp_df, use_container_width=True)

        st.success(
            f"🎯 **Conclusão Estatística Comprovada:** O Algoritmo Genético superou a Estratégia Fixa tradicional em "
            f"**mais de 27 salas de vantagem** na validação (96,9 vs 69,0 salas, com p-valor = 0,000166, altamente significativo!)."
        )

        img_p3 = Path("results/experiments/exp3_comparacao_baselines.png")
        if img_p3.exists():
            st.image(str(img_p3), caption="Comparação Científica: Baseline Fixo vs Busca Aleatória vs Algoritmo Genético.")

    with tab2:
        st.subheader("Experimento 1: Quanta Mutação a IA Precisa Ter?")
        st.write(
            "Testamos três taxas de mutação (2%, 10% e 25%) para ver se a IA precisava ser mais conservadora ou mais ousada:"
        )
        exp1_res = exp_payload["experiment_1_mutation"]["results"]
        t_mut = []
        for taxa, dados in exp1_res.items():
            t_mut.append(
                {
                    "Taxa de Mutação": taxa,
                    "Salas em Masmorras Novas (Validação)": f"{dados['val_rooms_summary']['mean']:.2f} salas",
                    "Taxa de Sucesso das 100 Salas": f"{dados['val_completion_rate_mean'] * 100:.1f}%",
                    "Variedade de Ideias Mantida": f"{dados['final_diversity_summary']['mean']:.3f}",
                    "Geração em que Aprendeu": f"Geração {dados['mean_convergence_generation']:.1f}",
                }
            )
        st.dataframe(pd.DataFrame(t_mut), use_container_width=True)
        st.info(
            "💡 **O que aprendemos:** A taxa de **10%** foi a mais equilibrada e confiável, vencendo em média 92,5 salas na validação. "
            "A taxa de 2% viciou muito cedo em ideias velhas, e a de 25% foi criativa, mas instável."
        )

    with tab3:
        st.subheader("Experimento 2: É melhor ter muitos guerreiros ou muitas gerações?")
        st.write(
            "Com um orçamento fixo de 240 avaliações, comparamos 3 maneiras de dividir o tempo do computador:"
        )
        exp2_res = exp_payload["experiment_2_population"]["results"]
        t_pop = []
        for cfg_nome, dados in exp2_res.items():
            t_pop.append(
                {
                    "Configuração Testada": cfg_nome,
                    "População": dados["pop_size"],
                    "Gerações": dados["generations"],
                    "Salas em Masmorras Novas": f"{dados['val_rooms_summary']['mean']:.2f} salas",
                    "Taxa de Sucesso": f"{dados['val_completion_rate_mean'] * 100:.1f}%",
                    "Diversidade": f"{dados['final_diversity_summary']['mean']:.3f}",
                }
            )
        st.dataframe(pd.DataFrame(t_pop), use_container_width=True)
        st.info(
            "💡 **O que aprendemos:** A configuração com **População 40 e 6 Gerações** generalizou melhor (89,56 salas), "
            "provando que ter uma população inicial grande com muitas ideias diferentes evita que a IA fique viciada nas mesmas salas."
        )

    with tab4:
        st.subheader("Experimento 4: Teste de Resistência em Condições Extremas")
        st.write("Colocamos o campeão da IA para lutar em 5 cenários totalmente diferentes sem nenhum treino novo:")
        exp4_scen = exp_payload["experiment_4_generalization"]["scenarios"]
        t_scen = []
        for skey, sdata in exp4_scen.items():
            t_scen.append(
                {
                    "Cenário de Teste": sdata["label"],
                    "Salas Vencidas pela IA": f"{sdata['genetic_algorithm']['mean_rooms']:.1f} salas",
                    "Zerou as 100 salas?": f"{sdata['genetic_algorithm']['completion_rate'] * 100:.0f}%",
                    "Salas Vencidas pelo Baseline Humano": f"{sdata['fixed_baseline']['mean_rooms']:.1f} salas",
                    "Vantagem da IA": f"+{sdata['ga_advantage_rooms']:.1f} salas",
                }
            )
        st.dataframe(pd.DataFrame(t_scen), use_container_width=True)
        st.success("✅ Em TODOS os cenários adversos, a IA manteve entre **+18,9 e +27,9 salas de vantagem** sobre as regras tradicionais!")

    with tab5:
        st.subheader("🧠 As 2 Grandes Lições que a IA Nos Ensinou")
        st.markdown(
            """
            1. **O Padre é o Melhor Companheiro de Todos (100% de Presença):**  
               Enquanto jogadores humanos costumam escolher Arqueiro e Mago para dar muito dano, a IA descobriu que dano não adianta se o guerreiro morrer no meio do caminho.
               Nas 7 execuções independentes do AG, o **Padre** foi contratado em **100% das vezes** porque sua cura salva a equipe do desgaste!
            
            2. **Armadura e Escudo Valem Mais que Espadas Caras:**  
               O gene de prioridade de compra (`equip_offense_priority`) convergiu para valores baixos (0,12 na média e 0,01 no campeão).
               A IA percebeu que gastar ouro comprando armadura completa e escudo protege a vida muito mais do que gastar tudo em uma espada gigante!
            """
        )


# ==============================================================================
# PÁGINA 6 — LABORATÓRIO DE ESTRESSE
# ==============================================================================
def render_page_6_laboratory(
    df: pd.DataFrame,
    balance_cfg: dict[str, Any],
    exp_payload: dict[str, Any] | None,
) -> None:
    st.title("🧪 Laboratório de Estresse Ambiental")
    st.markdown(
        """
        Nesta tela qualquer pessoa pode fazer simulações do tipo:  
        *"E se os monstros tivessem 20% mais de vida e dano? A estratégia da IA ainda aguentaria o tranco?"*
        """
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        mult_dif = st.slider("Aumentar/Diminuir Força dos Monstros", 0.70, 1.50, 1.15, 0.05, format="%.2fx")
        modo_comp = st.selectbox("Composição dos Monstros", ["standard (Padrão)", "alternate_pool (Mistura Inédita)"])
    with col2:
        semente_lab = st.number_input("Semente de Teste", 1, 99999, 505)
        cura_lab = st.slider("Cura Automática Entre Salas", 0.10, 0.50, 0.22, 0.02, format="%.0f%% da vida")
    with col3:
        permite_aliados = st.checkbox("Permitir Ajudantes (Aliados)", value=True)
        permite_baus = st.checkbox("Permitir Baús com Itens", value=False)

    cfg_mod = copy.deepcopy(balance_cfg)
    cfg_mod["warrior"]["post_room_heal_fraction"] = cura_lab
    comp_real = "alternate_pool" if "alternate" in modo_comp else "standard"

    salas_lab = build_dungeon_100_rooms(
        monsters_df=df,
        balance_cfg=cfg_mod,
        seed=int(semente_lab),
        difficulty_multiplier=float(mult_dif),
        composition_mode=comp_real,
    )

    c_ia = get_champion_chromosome(exp_payload)
    c_base = create_fixed_baseline_chromosome()

    r_ia = run_dungeon_simulation(salas_lab, c_ia.to_policy_params(), cfg_mod, seed=int(semente_lab), enable_allies=permite_aliados, enable_chests=permite_baus, record_detailed_logs=True)
    r_base = run_dungeon_simulation(salas_lab, c_base.to_policy_params(), cfg_mod, seed=int(semente_lab), enable_allies=permite_aliados, enable_chests=permite_baus, record_detailed_logs=True)

    c_res1, c_res2 = st.columns(2)
    with c_res1:
        st.markdown("### 🏆 Melhor Estratégia da IA")
        st.metric("Salas Concluídas", f"{r_ia.rooms_cleared} de 100", delta=f"{r_ia.rooms_cleared - r_base.rooms_cleared:+d} salas a mais")
        st.write(
            f"- **Nível Alcançado:** Nível {r_ia.final_warrior_level}\n"
            f"- **Atributos:** Força {r_ia.final_strength} | Vida {r_ia.final_vitality} | Defesa {r_ia.final_defense}\n"
            f"- **Status Final:** {'Venceu tudo!' if r_ia.completed_all_100 else f'Caiu na Sala {r_ia.failure_room}'}"
        )
    with c_res2:
        st.markdown("### 📏 Estratégia Fixa Tradicional")
        st.metric("Salas Concluídas", f"{r_base.rooms_cleared} de 100")
        st.write(
            f"- **Nível Alcançado:** Nível {r_base.final_warrior_level}\n"
            f"- **Atributos:** Força {r_base.final_strength} | Vida {r_base.final_vitality} | Defesa {r_base.final_defense}\n"
            f"- **Status Final:** {'Venceu tudo!' if r_base.completed_all_100 else f'Caiu na Sala {r_base.failure_room}'}"
        )

    hp_ia = [r.warrior_hp_end for r in r_ia.room_results]
    hp_base = [r.warrior_hp_end for r in r_base.room_results]
    fig_lab = go.Figure()
    fig_lab.add_trace(go.Scatter(x=list(range(1, len(hp_ia) + 1)), y=hp_ia, name="Vida do Guerreiro (IA)", line=dict(color="#27ae60", width=2.5)))
    fig_lab.add_trace(go.Scatter(x=list(range(1, len(hp_base) + 1)), y=hp_base, name="Vida do Guerreiro (Tradicional)", line=dict(color="#7f8c8d", dash="dash", width=2)))
    fig_lab.update_layout(title="Duelo de Sobrevivência no Ambiente Modificado", xaxis_title="Sala da Masmorra", yaxis_title="Vida Restante do Guerreiro")
    st.plotly_chart(fig_lab, use_container_width=True)


# ==============================================================================
# MENU PRINCIPAL
# ==============================================================================
def main() -> None:
    st.sidebar.title("⚔️ Masmorra Genética")
    st.sidebar.caption("Grupo 7 — Inteligência Artificial II (FIB)")

    pagina = st.sidebar.radio(
        "Navegue pelas Telas do Projeto:",
        options=[
            "Página 1 — Sobre o Projeto (O que é e quem fez)",
            "Página 2 — O Bestiário (334 Monstros Oficiais)",
            "Página 3 — A Masmorra (100 Salas em Ação)",
            "Página 4 — A Evolução (Como a IA Aprende)",
            "Página 5 — Experimentos Científicos (Quem Venceu?)",
            "Página 6 — Laboratório de Testes (Mude as Regras)",
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

    if pagina.startswith("Página 1"):
        render_page_1_about(manifest, balance_cfg)
    elif pagina.startswith("Página 2"):
        render_page_2_dataset(df, manifest, eda)
    elif pagina.startswith("Página 3"):
        render_page_3_dungeon(df, balance_cfg, exp_payload)
    elif pagina.startswith("Página 4"):
        render_page_4_genetic_evolution(df, balance_cfg, exp_payload)
    elif pagina.startswith("Página 5"):
        render_page_5_experiments(exp_payload)
    elif pagina.startswith("Página 6"):
        render_page_6_laboratory(df, balance_cfg, exp_payload)


if __name__ == "__main__":
    main()
