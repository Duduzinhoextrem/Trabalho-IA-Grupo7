"""Script executável de ETL, Validação, Pré-processamento e EDA do Dataset D&D 5e SRD."""

from __future__ import annotations

import json
import logging
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.dataset.collector import load_or_collect_raw_monsters
from src.dataset.exploration import run_full_eda
from src.dataset.preprocessing import preprocess_and_export_dataset
from src.dataset.validation import validate_raw_dataset


def main(force_refresh: bool = False) -> None:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    raw_records, manifest = load_or_collect_raw_monsters(force_refresh=force_refresh)
    logging.info(
        "Coleta concluída: %d registros brutos (SHA256: %s)",
        len(raw_records),
        manifest.get("raw_file_sha256"),
    )

    valid_records, val_report = validate_raw_dataset(raw_records)
    val_dict = val_report.to_dict()
    val_path = Path("data/metadata/validation_report.json")
    val_path.parent.mkdir(parents=True, exist_ok=True)
    val_path.write_text(json.dumps(val_dict, ensure_ascii=False, indent=2), encoding="utf-8")

    logging.info(
        "Validação concluída: %d válidos, %d inválidos, %d duplicados.",
        val_report.valid_records_count,
        val_report.invalid_records_count,
        len(val_report.duplicate_indices),
    )

    df_processed = preprocess_and_export_dataset(valid_records)
    logging.info(
        "Pré-processamento concluído: DataFrame %s exportado para CSV e Parquet.",
        df_processed.shape,
    )

    eda_metrics = run_full_eda(df_processed, validation_report=val_dict)
    logging.info("EDA concluída com sucesso. Gráficos gerados: %d", len(eda_metrics["generated_charts"]))


if __name__ == "__main__":
    refresh = "--refresh" in sys.argv
    main(force_refresh=refresh)
