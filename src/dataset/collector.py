"""Coleta de dados da API D&D 5e SRD (2014).

Etapas da coleta:
1. Consultar a listagem oficial de monstros em https://www.dnd5eapi.co/api/2014/monsters
2. Obter os registros completos de cada criatura e manter a referência original
3. Tratar erros HTTP, tempo limite e limites de requisições, com novas tentativas e espera exponencial
4. Preservar os dados brutos (JSON) em `data/raw/monsters_raw_srd2014.json`
5. Registrar a origem, a licença, a versão e o hash SHA-256 no manifesto
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import logging
from pathlib import Path
import time
from typing import Any, Callable

import requests

logger = logging.getLogger(__name__)

PRIMARY_BASE_URL = "https://www.dnd5eapi.co"
PRIMARY_LIST_ENDPOINT = f"{PRIMARY_BASE_URL}/api/2014/monsters"
SECONDARY_LIST_ENDPOINT = "https://api.open5e.com/v2/creatures/?document__slug=wotc-srd&limit=500"
SOURCE_REPO_URL = "https://github.com/5e-bits/5e-database"
DATASET_VERSION = "srd-2014-v1.0.0"

DEFAULT_RAW_PATH = Path("data/raw/monsters_raw_srd2014.json")
DEFAULT_MANIFEST_PATH = Path("data/metadata/collection_manifest.json")


class DataCollectionError(RuntimeError):
    """Erro de coleta quando não há uma cópia local válida disponível."""


def fetch_json_with_retry(
    url: str,
    session: requests.Session | None = None,
    timeout: float = 15.0,
    max_retries: int = 3,
    backoff_base: float = 0.75,
) -> dict[str, Any]:
    """Faz uma requisição HTTP GET e trata erros e tempo limite com espera entre tentativas."""
    http = session or requests
    last_error: Exception | None = None

    for attempt in range(1, max_retries + 1):
        try:
            response = http.get(
                url,
                timeout=timeout,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "MasmorraGenetica-Grupo7-FIB-IA2/1.0 (Academic Research)",
                },
            )
            if response.status_code == 429:
                wait_time = backoff_base * (2**attempt)
                logger.warning("Rate limit (429) em %s. Aguardando %.2fs...", url, wait_time)
                time.sleep(wait_time)
                continue
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                raise ValueError(f"Resposta JSON inválida (esperado dict) em {url}")
            return data
        except (requests.RequestException, ValueError) as exc:
            last_error = exc
            if attempt < max_retries:
                wait_time = backoff_base * (2 ** (attempt - 1))
                logger.warning(
                    "Tentativa %d/%d falhou para %s (%s). Retentando em %.2fs...",
                    attempt,
                    max_retries,
                    url,
                    exc,
                    wait_time,
                )
                time.sleep(wait_time)

    raise DataCollectionError(f"Falha ao consultar {url} após {max_retries} tentativas: {last_error}")


def collect_monsters_from_api(
    list_endpoint: str = PRIMARY_LIST_ENDPOINT,
    base_url: str = PRIMARY_BASE_URL,
    raw_output_path: Path = DEFAULT_RAW_PATH,
    manifest_output_path: Path = DEFAULT_MANIFEST_PATH,
    max_workers: int = 12,
    timeout: float = 15.0,
    max_retries: int = 3,
    http_get_fn: Callable[..., dict[str, Any]] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Coleta a listagem completa e os registros detalhados da D&D 5e SRD API.

    Preserva os registros brutos e gera o manifesto de metadados e integridade.
    """
    fetch_fn = http_get_fn or fetch_json_with_retry
    started_at = datetime.now(timezone.utc).isoformat()
    session = requests.Session()

    logger.info("Consultando listagem principal de monstros em %s", list_endpoint)
    listing_payload = fetch_fn(list_endpoint, session=session, timeout=timeout, max_retries=max_retries)

    results_summary = listing_payload.get("results", [])
    expected_count = listing_payload.get("count", len(results_summary))
    if not results_summary:
        raise DataCollectionError(f"Listagem vazia retornada por {list_endpoint}")

    records: list[dict[str, Any]] = []
    failed_urls: list[dict[str, str]] = []
    incomplete_records: list[str] = []

    def _fetch_single(item: dict[str, Any]) -> tuple[str, dict[str, Any] | None, str | None]:
        idx = str(item.get("index", "")).strip()
        rel_url = str(item.get("url", f"/api/2014/monsters/{idx}")).strip()
        full_url = rel_url if rel_url.startswith("http") else f"{base_url.rstrip('/')}/{rel_url.lstrip('/')}"
        try:
            detail = fetch_fn(full_url, session=session, timeout=timeout, max_retries=max_retries)
            detail["_source_api_url"] = full_url
            detail["_source_list_endpoint"] = list_endpoint
            detail["_collected_at_utc"] = started_at
            return idx, detail, None
        except Exception as exc:  # noqa: BLE001
            return idx, None, str(exc)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_fetch_single, item): item for item in results_summary}
        for future in as_completed(futures):
            idx, detail, error_msg = future.result()
            if error_msg is not None or detail is None:
                failed_urls.append({"index": idx, "error": error_msg or "Unknown error"})
                continue
            # Verifica se o registro coletado está incompleto.
            required_minimal = ("index", "name", "hit_points", "challenge_rating")
            if any(detail.get(k) is None for k in required_minimal):
                incomplete_records.append(idx)
            records.append(detail)

    # Ordena pelo campo index para reproduzir o hash SHA-256.
    records.sort(key=lambda r: str(r.get("index", "")))

    if not records:
        raise DataCollectionError("Nenhum registro completo de monstro pôde ser coletado.")

    finished_at = datetime.now(timezone.utc).isoformat()
    raw_output_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_output_path.parent.mkdir(parents=True, exist_ok=True)

    raw_bytes = json.dumps(records, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
    raw_sha256 = hashlib.sha256(raw_bytes).hexdigest()
    raw_output_path.write_bytes(raw_bytes)

    manifest: dict[str, Any] = {
        "dataset_name": "D&D 5e SRD Monsters Dataset (2014 Edition)",
        "dataset_version": DATASET_VERSION,
        "source_api_name": "5e-bits D&D 5e SRD API",
        "source_list_endpoint": list_endpoint,
        "source_example_endpoint": f"{base_url}/api/2014/monsters/goblin",
        "source_repository": SOURCE_REPO_URL,
        "fallback_documented_api": SECONDARY_LIST_ENDPOINT,
        "license_data": (
            "System Reference Document 5.1 (SRD 5.1) by Wizards of the Coast LLC — "
            "disponibilizado sob Creative Commons Attribution 4.0 International (CC-BY-4.0) "
            "e Open Game License (OGL) v1.0a. Código da API sob licença MIT (5e-bits)."
        ),
        "attribution": (
            "This work includes material taken from the System Reference Document 5.1 ('SRD 5.1') "
            "by Wizards of the Coast LLC, available at https://dnd.wizards.com/resources/systems-reference-document. "
            "The SRD 5.1 is licensed under the Creative Commons Attribution 4.0 International License."
        ),
        "collected_at_utc": started_at,
        "completed_at_utc": finished_at,
        "expected_count_from_api": expected_count,
        "collected_records_count": len(records),
        "failed_requests_count": len(failed_urls),
        "failed_requests": failed_urls,
        "incomplete_records_count": len(incomplete_records),
        "incomplete_records": incomplete_records,
        "raw_file_path": str(raw_output_path.as_posix()),
        "raw_file_sha256": raw_sha256,
        "raw_file_size_bytes": len(raw_bytes),
        "integrity_status": "VERIFIED" if len(records) == expected_count and not failed_urls else "PARTIAL",
    }

    manifest_output_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return records, manifest


def load_or_collect_raw_monsters(
    raw_path: Path = DEFAULT_RAW_PATH,
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
    force_refresh: bool = False,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Carrega a cópia dos dados brutos ou consulta a API se ela estiver ausente ou houver pedido de atualização.

    Se a API falhar na atualização, usa a cópia local versionada e registra a falha.
    Os registros vêm da API ou dessa cópia.
    """
    if not force_refresh and raw_path.exists() and manifest_path.exists():
        records = json.loads(raw_path.read_text(encoding="utf-8"))
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        return records, manifest

    try:
        return collect_monsters_from_api(raw_output_path=raw_path, manifest_output_path=manifest_path)
    except Exception as exc:
        logger.error("Erro ao consultar a API principal (%s).", exc)
        if raw_path.exists() and manifest_path.exists():
            logger.warning("Utilizando snapshot congelado versionado em %s.", raw_path)
            records = json.loads(raw_path.read_text(encoding="utf-8"))
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["fallback_used"] = True
            manifest["last_api_error"] = str(exc)
            return records, manifest
        raise DataCollectionError(
            f"API indisponível ({exc}) e nenhum snapshot local encontrado em {raw_path}."
        ) from exc
