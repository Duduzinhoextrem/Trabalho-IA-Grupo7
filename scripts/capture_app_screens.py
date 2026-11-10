"""Captura telas reais do aplicativo Streamlit com um navegador automatizado (Microsoft Edge).

Uso: python scripts/capture_app_screens.py [URL] [PASTA_DE_SAIDA]
Requer: playwright (pip install playwright). Usa o Edge instalado (canal "msedge"), sem baixar navegadores.
Gera os PNG e `capturas_log.json` com tempos e erros de console observados.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
import time

from playwright.sync_api import Page, sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8599"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("docs/FINALIZACAO/evidencias/capturas")
OUT.mkdir(parents=True, exist_ok=True)
LOG: dict = {"url": URL, "capturas": [], "console_errors": [], "tempos_s": {}}


def settle(page: Page, pause: float = 1.2) -> None:
    page.wait_for_load_state("networkidle")
    page.wait_for_selector('[data-testid="stApp"]')
    time.sleep(0.6)  # dá tempo para o Streamlit iniciar a execução disparada pelo clique
    # aguarda o fim da execução em andamento do script Streamlit
    page.wait_for_function(
        '() => document.querySelector(\'[data-testid="stApp"]\').getAttribute("data-test-script-state") === "notRunning"',
        timeout=300000,
    )
    time.sleep(pause)


def shot(page: Page, name: str, full: bool = True) -> None:
    path = OUT / f"{name}.png"
    if full:
        # O conteúdo do Streamlit rola dentro de um contêiner; amplia a janela para mostrar a página inteira.
        height = page.evaluate('() => document.querySelector(\'[data-testid="stMain"]\').scrollHeight')
        page.set_viewport_size({"width": 1440, "height": int(min(max(height, 900), 5200))})
        time.sleep(0.8)
    page.screenshot(path=str(path))
    if full:
        page.set_viewport_size({"width": 1440, "height": 900})
    LOG["capturas"].append(path.name)
    print("capturado", path.name)


def goto(page: Page, label: str) -> None:
    page.locator('[data-testid="stSidebar"] label', has_text=label).first.click()
    settle(page)


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, locale="pt-BR")
        page = ctx.new_page()
        page.on("console", lambda m: LOG["console_errors"].append(m.text) if m.type == "error" else None)
        t0 = time.time()
        page.goto(URL)
        settle(page, 2.0)
        LOG["tempos_s"]["abertura_inicial"] = round(time.time() - t0, 2)
        shot(page, "01_inicio")

        goto(page, "Aventura")
        page.get_by_role("button", name="Iniciar com esta estratégia").click()
        settle(page)
        shot(page, "02_aventura_sala1")
        page.get_by_role("button", name="Ver final").click()
        settle(page)
        shot(page, "03_aventura_final_e_comparacao")

        goto(page, "Como funciona")
        shot(page, "04_como_funciona_experimento")
        page.get_by_role("tab", name="Passo a passo do algoritmo").click()
        time.sleep(1)
        page.get_by_text("7 · Elitismo").click()
        time.sleep(1)
        shot(page, "05_como_funciona_passo_a_passo")
        page.get_by_role("tab", name="Faça uma demonstração").click()
        time.sleep(1)
        t1 = time.time()
        page.get_by_role("button", name="Executar demonstração").click()
        settle(page, 2.0)
        LOG["tempos_s"]["demonstracao_ag_padrao"] = round(time.time() - t1, 2)
        shot(page, "06_como_funciona_demonstracao")

        goto(page, "Resultados")
        shot(page, "07_resultados")
        for tab, name in (("População", "08_resultados_populacao"), ("Novos cenários", "09_resultados_cenarios"),
                          ("Limites e falhas", "10_resultados_limites")):
            page.get_by_role("tab", name=tab).click()
            time.sleep(1.5)
            shot(page, name)

        goto(page, "Bestiário")
        shot(page, "11_bestiario")
        goto(page, "Dados e fonte")
        shot(page, "12_dados_e_fonte")

        goto(page, "Laboratório")
        t2 = time.time()
        page.get_by_role("button", name="Comparar neste cenário").click()
        settle(page, 2.0)
        LOG["tempos_s"]["laboratorio_comparacao"] = round(time.time() - t2, 2)
        shot(page, "13_laboratorio")

        goto(page, "Início")
        t3 = time.time()
        page.get_by_role("button", name="Treinar e iniciar automaticamente").click()
        settle(page, 3.0)
        LOG["tempos_s"]["treino_automatico_masmorra_201"] = round(time.time() - t3, 2)
        shot(page, "14_treino_automatico")
        ctx.close()

        mobile = browser.new_context(viewport={"width": 390, "height": 844}, locale="pt-BR", device_scale_factor=2)
        mp = mobile.new_page()
        mp.goto(URL)
        settle(mp, 2.0)
        LOG["largura_documento_mobile"] = mp.evaluate("document.documentElement.scrollWidth")
        shot(mp, "15_inicio_mobile", full=False)
        mobile.close()
        browser.close()
    (OUT / "capturas_log.json").write_text(json.dumps(LOG, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(LOG["tempos_s"], indent=2), "erros de console:", len(LOG["console_errors"]))


if __name__ == "__main__":
    main()
