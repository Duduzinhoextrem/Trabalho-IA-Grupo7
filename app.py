"""Masmorra Genética: interface da demonstração do Grupo 7."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from src.dataset.preprocessing import load_processed_dataset
from src.game.monsters import load_balance_config
from src.ui import pages
from src.ui.design import apply_theme, footer, sidebar_brand
from src.ui.localization import translate_creature_size, translate_creature_type


st.set_page_config(
    page_title="Masmorra Genética",
    page_icon=":material/explore:",
    layout="wide",
    initial_sidebar_state="auto",
)

PROJECT_ROOT = Path(__file__).resolve().parent


@st.cache_data(show_spinner=False)
def dataset() -> pd.DataFrame:
    frame = load_processed_dataset(
        parquet_path=PROJECT_ROOT / "data/processed/monsters_srd2014_processed.parquet",
        csv_path=PROJECT_ROOT / "data/processed/monsters_srd2014_processed.csv",
    ).copy()
    frame["tipo_pt"] = frame["type"].map(translate_creature_type)
    frame["tamanho_pt"] = frame["size"].map(translate_creature_size)
    return frame


@st.cache_data(show_spinner=False)
def balance() -> dict:
    return load_balance_config(PROJECT_ROOT / "config/balance.json")


def read_json(path: str) -> dict | None:
    source = PROJECT_ROOT / path
    if not source.exists():
        return None
    try:
        result = json.loads(source.read_text(encoding="utf-8"))
        return result if isinstance(result, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def main() -> None:
    apply_theme()

    try:
        monsters = dataset()
        settings = balance()
    except (FileNotFoundError, OSError, ValueError) as exc:
        st.error(f"Não foi possível abrir os dados do projeto: {exc}")
        st.stop()

    manifest = read_json("data/metadata/collection_manifest.json") or {}
    eda = read_json("results/eda/eda_summary.json") or {}
    # A versão anterior tinha orçamentos desiguais e fica guardada como histórico.
    experiments = read_json("data/experiments/scientific_experiments_v2.json")

    with st.sidebar:
        sidebar_brand()
    selected = st.sidebar.radio(
        "Explore o projeto",
        ["Início", "Aventura", "Como funciona", "Resultados", "Bestiário", "Dados e fonte", "Laboratório"],
        key="page",
        label_visibility="collapsed",
    )
    st.sidebar.divider()
    st.sidebar.caption("100 salas. Evolução de atributos, aliados e equipamentos.")
    st.sidebar.caption("Inteligência Artificial II · FIB · 2026")

    if selected == "Início":
        pages.home(monsters, manifest)
    elif selected == "Aventura":
        pages.adventure(monsters, settings, experiments)
    elif selected == "Como funciona":
        pages.evolution(monsters, settings, experiments)
    elif selected == "Resultados":
        pages.results(experiments)
    elif selected == "Bestiário":
        pages.bestiary(monsters, manifest, eda)
    elif selected == "Dados e fonte":
        pages.data_source(monsters, manifest)
    else:
        pages.laboratory(monsters, settings, experiments)
    footer()


if __name__ == "__main__":
    main()
