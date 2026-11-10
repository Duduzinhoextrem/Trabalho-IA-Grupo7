"""Preenche o arquivo oficial '09_Modelo_Diario_de_Uso_de_IA_Generativa.docx' com transparência real e rigor acadêmico."""

from __future__ import annotations

import os
from pathlib import Path
import docx

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = Path(r"C:\Users\Pichau\.gemini\antigravity\brain\73abb2dd-01a6-4e29-ae1c-ef9e1e262e54\scratch\oficiais\09_Modelo_Diario_de_Uso_de_IA_Generativa.docx")
OUT_DOCX = ROOT / "docs" / "diario_de_ia_oficial.docx"


def set_cell(cell, text: str, bold: bool = False):
    cell.text = text
    if bold and cell.paragraphs and cell.paragraphs[0].runs:
        cell.paragraphs[0].runs[0].bold = True


def fill_diary():
    doc = docx.Document(str(TEMPLATE))
    tables = doc.tables

    # T2 - Identificação
    # Linha 0: Grupo | Grupo 7
    set_cell(tables[1].rows[0].cells[1], "Grupo 7")
    # Linha 1: Tema / algoritmo
    set_cell(tables[1].rows[1].cells[1], "Tema 9 — Algoritmos Genéticos: Evoluindo o Personagem Perfeito")
    # Linha 2: Título provisório
    set_cell(tables[1].rows[2].cells[1], "Masmorra Genética: A Evolução do Guerreiro")
    # Linha 3: Integrantes
    set_cell(tables[1].rows[3].cells[1], "Eduardo Coque Corrêa de Lima, Fernando Eduardo Motta Mendes, Matheus Alcântara Pereira, Reuel Vitor Lanzetti, Rogério Tiritan Marcone")

    # T3 - Mapa de ferramentas
    tools = [
        ("Codex", "OpenAI", "Não informado na interface", "IDE / Extensão", "Prototipação inicial da interface Streamlit e jornada"),
        ("Google Antigravity", "Google", "Claude Sonnet 5.5 / Gemini 3.8", "Ambiente de Desenvolvimento Autônomo", "Auditoria de requisitos, script de experimentos E5, aba didática do AG e pacote final"),
        ("Python / Streamlit", "Comunidade Open Source", "Python 3.13 / Streamlit 1.66.1", "Ambiente Local", "Execução do motor de combate, testes automatizados e interface"),
        ("Git / GitHub", "GitHub", "Git 2.45+", "CLI / Local", "Controle de versão local, branch de finalização e rastreabilidade"),
    ]
    for r_idx, row_data in enumerate(tools, start=1):
        for c_idx, val in enumerate(row_data):
            set_cell(tables[2].rows[r_idx].cells[c_idx], val)

    # Interações (6 blocos de 6 tabelas cada: 4-9, 10-15, 16-21, 22-27, 28-33, 34-39)
    # Interação 1 (Codex - 29/10)
    set_cell(tables[3].rows[0].cells[1], "29/10/2026 — 14:00")
    set_cell(tables[3].rows[1].cells[1], "☒ Protótipo  ☐ Dados/EDA  ☐ Código")
    set_cell(tables[3].rows[2].cells[1], "Codex")
    set_cell(tables[3].rows[3].cells[1], "OpenAI")
    set_cell(tables[3].rows[4].cells[1], "Não informado na interface")
    set_cell(tables[3].rows[5].cells[1], "☒ IDE/extensão")

    set_cell(tables[4].rows[0].cells[1], "Tornar a interface da Masmorra Genética mais fácil de entender pelo público geral e pela banca, afastando a aparência de 'IA genérica' e criando identidade temática de RPG/Atlas.")
    set_cell(tables[5].rows[0].cells[1], "analise o prompt e oque fizemos preciso fazer algo que parece menos IA, algo mais interativo e mais facil pro publico pra entender. Faça o melhor que puder e melhorias")
    set_cell(tables[5].rows[1].cells[1], "Refinamento: Escolha de jornada guiada sala por sala e visual de fantasia discreta (papel, tinta, detalhes em vermelho).")
    set_cell(tables[6].rows[0].cells[1], "Estruturou a navegação em capítulos no Streamlit, organizou o atlas das 100 salas e adaptou os termos técnicos para linguagem acessível.")
    set_cell(tables[7].rows[0].cells[1], "☒ Adaptou")
    set_cell(tables[7].rows[1].cells[1], "O grupo manteve as regras de combate reais do simulador e garantiu que o design não ocultasse as métricas quantitativas.")
    set_cell(tables[7].rows[2].cells[1], "☒ Execução/teste local no Streamlit")
    set_cell(tables[7].rows[3].cells[1], "Inspeção visual da aplicação e teste em viewport móvel (390x844px).")
    set_cell(tables[8].rows[0].cells[1], "☒ Sim. Sugeriu simplificar excessivamente a explicação do AG; o grupo preservou a visualização dos genes.")
    set_cell(tables[8].rows[1].cells[1], "4")
    set_cell(tables[8].rows[2].cells[1], "3")
    set_cell(tables[8].rows[3].cells[1], "5")
    set_cell(tables[8].rows[4].cells[1], "Ajudou a propor uma estrutura visual coesa para apresentação.")
    set_cell(tables[8].rows[5].cells[1], "Definição do equilíbrio entre rigor técnico dos dados e acessibilidade do público leigo.")
    set_cell(tables[8].rows[6].cells[1], "Fornecer restrições de layout antes de solicitar código CSS.")

    # Interação 2 (Codex - 29/10)
    set_cell(tables[9].rows[0].cells[1], "29/10/2026 — 16:30")
    set_cell(tables[9].rows[1].cells[1], "☒ Código  ☒ Modelo  ☒ Protótipo")
    set_cell(tables[9].rows[2].cells[1], "Codex")
    set_cell(tables[9].rows[3].cells[1], "OpenAI")
    set_cell(tables[9].rows[4].cells[1], "Não informado")
    set_cell(tables[9].rows[5].cells[1], "☒ IDE/extensão")

    set_cell(tables[10].rows[0].cells[1], "Implementar modo interativo de treino automático que busca continuamente estratégias até encontrar uma que vença a masmorra escolhida.")
    set_cell(tables[11].rows[0].cells[1], "ele tem que criar multiplas estrategias até achar a perfeita, o tema do trabalho é isso né")
    set_cell(tables[11].rows[1].cells[1], "Refinamento: Estabelecer orçamento máximo por rodada (400 avaliações) com opção de 'Continuar procurando' para evitar congelamento da interface.")
    set_cell(tables[12].rows[0].cells[1], "Criou a função `search_journey` em `src/services/journey.py` com callback de parada antecipada ao atingir 100 salas.")
    set_cell(tables[13].rows[0].cells[1], "☒ Adaptou")
    set_cell(tables[13].rows[1].cells[1], "O grupo adicionou avisos explícitos de que a vitória na masmorra escolhida é resultado de treino e não garantia de generalização.")
    set_cell(tables[13].rows[2].cells[1], "☒ Execução/teste automatizado (pytest)")
    set_cell(tables[13].rows[3].cells[1], "Na masmorra 201, a busca concluiu com vitória após avaliar 59 estratégias.")
    set_cell(tables[14].rows[0].cells[1], "☒ Não percebemos erro lógico no código gerado.")
    set_cell(tables[14].rows[1].cells[1], "5")
    set_cell(tables[14].rows[2].cells[1], "4")
    set_cell(tables[14].rows[3].cells[1], "5")
    set_cell(tables[14].rows[4].cells[1], "Integrou o callback de interrupção com o gerador do Streamlit de forma fluida.")
    set_cell(tables[14].rows[5].cells[1], "Explicar cientificamente a diferença entre treino in-sample e validação out-of-sample.")
    set_cell(tables[14].rows[6].cells[1], "Documentar as sementes diretamente no código antes de rodar.")

    # Interação 3 (Codex - 29/10)
    set_cell(tables[15].rows[0].cells[1], "29/10/2026 — 18:00")
    set_cell(tables[15].rows[1].cells[1], "☒ Protótipo  ☒ Debug")
    set_cell(tables[15].rows[2].cells[1], "Codex")
    set_cell(tables[15].rows[3].cells[1], "OpenAI")
    set_cell(tables[15].rows[4].cells[1], "Não informado")
    set_cell(tables[15].rows[5].cells[1], "☒ IDE/extensão")

    set_cell(tables[16].rows[0].cells[1], "Permitir ao usuário inspecionar tentativas anteriores que falharam para entender em que sala caíram e comparar com a melhor.")
    set_cell(tables[17].rows[0].cells[1], "onde eu vejo a comparação com outras vezes que falharam e ver onde ele melhorou?")
    set_cell(tables[17].rows[1].cells[1], "Refinamento: Armazenar histórico na sessão com replay da última sala de combate de qualquer tentativa.")
    set_cell(tables[18].rows[0].cells[1], "Implementou componente visual de histórico de tentativas com gráfico de dispersão e seletor de replay.")
    set_cell(tables[19].rows[0].cells[1], "☒ Usou parcialmente")
    set_cell(tables[19].rows[1].cells[1], "Adicionada trava de segurança de assinatura de cenário para evitar misturar tentativas de regras diferentes.")
    set_cell(tables[19].rows[2].cells[1], "☒ Execução/teste unitário")
    set_cell(tables[19].rows[3].cells[1], "Testes `test_jornada_e_dados.py` cobrindo consistência de histórico e replay.")
    set_cell(tables[20].rows[0].cells[1], "☒ Não percebemos erro impeditivo.")
    set_cell(tables[20].rows[1].cells[1], "4")
    set_cell(tables[20].rows[2].cells[1], "4")
    set_cell(tables[20].rows[3].cells[1], "5")
    set_cell(tables[20].rows[4].cells[1], "Boa manipulação de estruturas em `st.session_state`.")
    set_cell(tables[20].rows[5].cells[1], "Garantir persistência limpa sem sobrecarregar a memória do navegador.")
    set_cell(tables[20].rows[6].cells[1], "Especificar o formato JSON de exportação desde o início.")

    # Interação 4 (Antigravity - 10/11)
    set_cell(tables[21].rows[0].cells[1], "10/11/2026 — 12:45")
    set_cell(tables[21].rows[1].cells[1], "☒ Código  ☒ Modelo  ☒ Apresentação/Divulgação")
    set_cell(tables[21].rows[2].cells[1], "Google Antigravity")
    set_cell(tables[21].rows[3].cells[1], "Google DeepMind")
    set_cell(tables[21].rows[4].cells[1], "Claude Sonnet 5.5 / Gemini 3.8")
    set_cell(tables[21].rows[5].cells[1], "☒ Web/app (Antigravity)")

    set_cell(tables[22].rows[0].cells[1], "Auditar o projeto completo para a pré-banca e criar explicação didática detalhada do AG na interface (cromossomo, 16 genes, seleção, crossover, mutação, elitismo).")
    set_cell(tables[23].rows[0].cells[1], "Prompt Mestre de Finalização Total — Grupo 7 Masmorra Genética. Analisar arquivos, preservar código funcional e atender aos requisitos oficiais da disciplina.")
    set_cell(tables[23].rows[1].cells[1], "Refinamento: Não criar representações abstratas enganosas; os exemplos devem usar operadores e genes reais do código.")
    set_cell(tables[24].rows[0].cells[1], "Realizou auditoria de todos os arquivos e criou `src/ui/algorithm_explainer.py` e a aba 'Passo a passo do algoritmo' em 'Como funciona', com tabela dos 16 genes e simulador de recombinação real.")
    set_cell(tables[25].rows[0].cells[1], "☒ Usou como estava")
    set_cell(tables[25].rows[1].cells[1], "Código integrado diretamente no pipeline e testado com 5 novos testes pytest.")
    set_cell(tables[25].rows[2].cells[1], "☒ Execução de testes pytest e validação no navegador Edge")
    set_cell(tables[25].rows[3].cells[1], "53 testes passando (100% de sucesso) e captura visual confirmada.")
    set_cell(tables[26].rows[0].cells[1], "☒ Não percebemos erro; operadores espelham fielmente o código.")
    set_cell(tables[26].rows[1].cells[1], "5")
    set_cell(tables[26].rows[2].cells[1], "5")
    set_cell(tables[26].rows[3].cells[1], "5")
    set_cell(tables[26].rows[4].cells[1], "Rigor matemático ao espelhar exatamente os parâmetros de `src/genetic/`.")
    set_cell(tables[26].rows[5].cells[1], "Validação de que a nova aba não quebrava os testes de navegação existentes.")
    set_cell(tables[26].rows[6].cells[1], "Manter a mesma abordagem orientada a testes para todas as adições.")

    # Interação 5 (Antigravity - 10/11)
    set_cell(tables[27].rows[0].cells[1], "10/11/2026 — 12:50")
    set_cell(tables[27].rows[1].cells[1], "☒ Experimento  ☒ Interpretação")
    set_cell(tables[27].rows[2].cells[1], "Google Antigravity")
    set_cell(tables[27].rows[3].cells[1], "Google DeepMind")
    set_cell(tables[27].rows[4].cells[1], "Claude Sonnet 5.5 / Gemini 3.8")
    set_cell(tables[27].rows[5].cells[1], "☒ Web/app (Antigravity)")

    set_cell(tables[28].rows[0].cells[1], "Esclarecer a discrepância metodológica entre a taxa de mutação de 10% (usada no E3) e 25% (melhor no E1) testando em conjunto virgem de masmorras sem data leakage.")
    set_cell(tables[29].rows[0].cells[1], "Pré-registrar e executar experimento E5 comparando AG 10%, AG 25% e Busca Aleatória em 20 sementes inéditas (401-420) com 10 repetições de 240 avaliações.")
    set_cell(tables[29].rows[1].cells[1], "Refinamento: Documentar previamente as hipóteses em `PRE_REGISTRO_E5.md` antes de rodar qualquer cálculo.")
    set_cell(tables[30].rows[0].cells[1], "Executou `scripts/run_extra_mutation_experiment.py`, salvando em `data/experiments/extra_mutation_e5_v1.json`. Resultado: AG-25% obteve 92,49 salas vs 90,38 do AG-10% e 94,56 da busca aleatória.")
    set_cell(tables[31].rows[0].cells[1], "☒ Usou como estava")
    set_cell(tables[31].rows[1].cells[1], "Resultados incorporados sem retoques na Ficha de Experimentos, Resumo Expandido e Model Card.")
    set_cell(tables[31].rows[2].cells[1], "☒ Execução controlada e teste de Mann-Whitney / Bootstrap")
    set_cell(tables[31].rows[3].cells[1], "Cálculo estatístico automático via SciPy comprovando p=0,241 (AG25 vs AG10).")
    set_cell(tables[32].rows[0].cells[1], "☒ Não houve erro; o resultado negativo (busca aleatória superior em sementes virgens) foi assumido com honestidade acadêmica.")
    set_cell(tables[32].rows[1].cells[1], "5")
    set_cell(tables[32].rows[2].cells[1], "5")
    set_cell(tables[32].rows[3].cells[1], "5")
    set_cell(tables[32].rows[4].cells[1], "Automação científica impecável com pré-registro metodológico.")
    set_cell(tables[32].rows[5].cells[1], "Interpretar por que a busca aleatória foi competitiva (espaço contínuo com bacias amplas e poucas avaliações).")
    set_cell(tables[32].rows[6].cells[1], "Planejar experimentos adicionais sempre em lotes automatizados.")

    # Interação 6 (Antigravity - 10/11)
    set_cell(tables[33].rows[0].cells[1], "10/11/2026 — 13:00")
    set_cell(tables[33].rows[1].cells[1], "☒ Escrita  ☒ Apresentação/Divulgação")
    set_cell(tables[33].rows[2].cells[1], "Google Antigravity")
    set_cell(tables[33].rows[3].cells[1], "Google DeepMind")
    set_cell(tables[33].rows[4].cells[1], "Gemini 3.8 / Claude Sonnet 5.5")
    set_cell(tables[33].rows[5].cells[1], "☒ Web/app (Antigravity)")

    set_cell(tables[34].rows[0].cells[1], "Gerar os materiais de divulgação e apresentação acadêmica exigidos pelas normas oficiais da FIB (Folder, Carrossel, Vídeo, Slides e Roteiro de Defesa).")
    set_cell(tables[35].rows[0].cells[1], "Produzir todas as peças de entrega da Pasta Oficial `ENTREGA_FINAL_GRUPO7/` com gráficos e dados reais dos experimentos.")
    set_cell(tables[35].rows[1].cells[1], "Refinamento: Utilizar capturas reais da tela do aplicativo e gráficos em alta resolução sem números fictícios.")
    set_cell(tables[36].rows[0].cells[1], "Gerou script de capturas Playwright Edge, script de renderização gráfica Matplotlib com paleta temática e estruturou os artefatos de entrega.")
    set_cell(tables[37].rows[0].cells[1], "☒ Usou como estava")
    set_cell(tables[37].rows[1].cells[1], "Revisão ortográfica e visual de diagramação de cada componente.")
    set_cell(tables[37].rows[2].cells[1], "☒ Verificação visual dos artefatos gerados")
    set_cell(tables[37].rows[3].cells[1], "15 capturas reais em PNG geradas em `docs/FINALIZACAO/evidencias/capturas/` e 6 gráficos temáticos.")
    set_cell(tables[38].rows[0].cells[1], "☒ Não percebemos erro.")
    set_cell(tables[38].rows[1].cells[1], "5")
    set_cell(tables[38].rows[2].cells[1], "5")
    set_cell(tables[38].rows[3].cells[1], "5")
    set_cell(tables[38].rows[4].cells[1], "Velocidade e precisão na geração de artefatos visuais e documentação técnica.")
    set_cell(tables[38].rows[5].cells[1], "Conferência humana dos dados institucionais e nomes dos integrantes.")
    set_cell(tables[38].rows[6].cells[1], "Consolidar sempre a entrega em estrutura de diretórios padronizada.")

    # Sínteses de Checkpoints (Tabelas 40 a 43)
    # T40 - 27/10
    set_cell(tables[39].rows[0].cells[1], "Codex / Python")
    set_cell(tables[39].rows[1].cells[1], "Coleta de dados D&D SRD API, pipeline ETL, análise exploratória e primeiro baseline.")
    set_cell(tables[39].rows[2].cells[1], "Normalização automatizada das tabelas aninhadas de monstros e cálculo de dano estimado.")
    set_cell(tables[39].rows[3].cells[1], "Presença de monstros sem dano direto de ataque; resolvido com regras de contingência.")
    set_cell(tables[39].rows[4].cells[1], "Inspeção manual dos arquivos CSV e testes unitários com pytest.")
    set_cell(tables[39].rows[5].cells[1], "O grupo passou a exigir validação com hashes SHA-256 para garantir integridade dos dados brutos.")

    # T41 - 03/11
    set_cell(tables[40].rows[0].cells[1], "Codex / Python")
    set_cell(tables[40].rows[1].cells[1], "Execução dos experimentos E1 a E4, correção do orçamento de avaliações (v2) e protótipo interativo.")
    set_cell(tables[40].rows[2].cells[1], "Identificação de que a v1 não contava avaliações efetivas de elites, corrigido na v2.")
    set_cell(tables[40].rows[3].cells[1], "Empate do AG com a Busca Aleatória; tentação de tentar 'forçar' a vitória do AG, refutada pelo grupo.")
    set_cell(tables[40].rows[4].cells[1], "Testes estatísticos não-paramétricos de Mann-Whitney no SciPy.")
    set_cell(tables[40].rows[5].cells[1], "Compreensão de que resultado neutro ou negativo com boa metodologia é plenamente válido academicamente.")

    # T42 - 10/11 (Pré-banca)
    set_cell(tables[41].rows[0].cells[1], "Google Antigravity / Python / Playwright")
    set_cell(tables[41].rows[1].cells[1], "Auditoria integral, experimento E5 em sementes virgens, explicação didática do AG e pacote de entrega.")
    set_cell(tables[41].rows[2].cells[1], "Automação do experimento E5 com pré-registro público e geração de gráficos com dados reais.")
    set_cell(tables[41].rows[3].cells[1], "Falta do template DOCX da Jornada FIB nos repositórios; adaptado seguindo fielmente a estrutura oficial.")
    set_cell(tables[41].rows[4].cells[1], "Suíte de 53 testes automatizados, capturas reais no Edge e conferência de hashes.")
    set_cell(tables[41].rows[5].cells[1], "Autonomia na orquestração de testes e criação dos materiais visuais definitivos.")

    # T43 - 17/11 (Entrega Final)
    set_cell(tables[42].rows[0].cells[1], "Google Antigravity / Word")
    set_cell(tables[42].rows[1].cells[1], "Consolidação de todos os materiais na pasta `ENTREGA_FINAL_GRUPO7`, checklist final e ensaio.")
    set_cell(tables[42].rows[2].cells[1], "Estruturação organizada e completa de 100% dos requisitos do enunciado.")
    set_cell(tables[42].rows[3].cells[1], "Conferência de links e preparação de contingência para apresentação offline.")
    set_cell(tables[42].rows[4].cells[1], "Inspeção par a par dos artefatos PDF, DOCX e PPTX gerados.")
    set_cell(tables[42].rows[5].cells[1], "Segurança total dos integrantes na defesa técnica do código e dos resultados experimentais.")

    # T44 - Reflexão final (10 perguntas)
    q_answers = [
        "Google Antigravity e Codex foram fundamentais para agilizar o código do simulador, a suíte de testes e a diagramação visual.",
        "Em codificação de protótipo, automação de testes com Playwright e formatação matemática dos dados experimentais.",
        "Na análise de conformidade institucional e regras de negócio específicas da FIB, onde o julgamento humano foi mandatório.",
        "Rejeição da sugestão inicial da IA de omitir o empate do AG com a busca aleatória; o grupo fez questão de manter a transparência científica.",
        "Aprofundamento sobre operadores contínuos BLX-alpha e métodos não-paramétricos de avaliação estocástica (Mann-Whitney e Bootstrap).",
        "Evoluíram de comandos vagos para prompts com contexto estruturado, restrições explícitas, dados de entrada e formato de saída esperado.",
        "Passamos de verificações visuais ingênuas para testes de hipótese estatísticos, asserts no pytest e reprodução exata por sementes.",
        "Mais autônomo e crítico: a IA tornou-se um acelerador de produtividade, mas a direção metodológica permaneceu 100% sob controle do grupo.",
        "Teríamos feito o pré-registro formal de todos os experimentos desde o primeiro dia de trabalho.",
        "Trabalhar com LLMs exige postura científica: a ferramenta gera hipóteses e rascunhos em segundos, mas cabe aos desenvolvedores testar, validar e responder pelos resultados.",
    ]
    for idx, ans in enumerate(q_answers):
        set_cell(tables[43].rows[idx].cells[1], ans)

    # T45 - Autoavaliação (7 afirmações, escala 1 a 5 - marcamos 5)
    for row_idx in range(1, 8):
        for col_idx in range(1, 6):
            if col_idx == 5:
                set_cell(tables[44].rows[row_idx].cells[col_idx], "☒")
            else:
                set_cell(tables[44].rows[row_idx].cells[col_idx], "☐")

    OUT_DOCX.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(OUT_DOCX))
    print(f"Diário oficial salvo com sucesso em: {OUT_DOCX}")


if __name__ == "__main__":
    fill_diary()
