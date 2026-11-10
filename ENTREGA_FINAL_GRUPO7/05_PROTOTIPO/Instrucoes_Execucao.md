# INSTRUÇÕES DE EXECUÇÃO DO PROTÓTIPO
## Masmorra Genética — Grupo 7 | Inteligência Artificial II (FIB 2026)

Este documento contém o guia completo para instalação, configuração, execução e demonstração da aplicação interativa **Masmorra Genética**.

---

## 1. Requisitos do Sistema

- **Sistema Operacional:** Windows 10/11, Linux (Ubuntu/Debian) ou macOS.
- **Python:** Versão 3.10 ou superior (testado e homologado em Python 3.11, 3.12 e 3.13).
- **Memória RAM:** Mínimo de 4 GB (recomendado: 8 GB).
- **Espaço em Disco:** ~250 MB (incluindo dependências e dataset local).
- **Rede / Internet:** **100% Desnecessária em tempo de execução.** Todo o pipeline, simulador, dataset SRD 2014 e gráficos funcionam offline.

---

## 2. Instalação Passo a Passo

### Passo 2.1 — Clonar ou Abrir o Diretório Raiz
Abra o terminal (PowerShell, CMD ou Bash) na pasta raiz do repositório:
```bash
cd Trabalho-IA-Grupo7
```

### Passo 2.2 — Criar Ambiente Virtual (Recomendado)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### Passo 2.3 — Instalar Dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

As dependências principais são:
- `streamlit>=1.35.0`: Interface visual web interativa.
- `pandas>=2.1.0` e `numpy>=1.26.0`: Manipulação de dados e operações matriciais.
- `altair>=5.3.0` e `matplotlib>=3.8.0`: Visualização de dados e gráficos analíticos.
- `scipy>=1.12.0`: Testes estatísticos (Mann-Whitney U).
- `pytest>=8.0.0`: Bateria de testes automatizados.

---

## 3. Execução da Aplicação Interativa

### Opção A — Execução Rápida (Windows)
Basta dar dois cliques no arquivo:
`executar_prototipo.bat` (localizado nesta pasta ou na raiz do projeto).

### Opção B — Execução via Linha de Comando
Execute no terminal:
```bash
python -m streamlit run app.py
```

Por padrão, o Streamlit iniciará na porta **8501** e abrirá seu navegador padrão em:
👉 **`http://localhost:8501`**

Para fixar uma porta específica ou rodar em modo headless:
```bash
python -m streamlit run app.py --server.port 8599 --server.headless true
```

---

## 4. Navegação pelas Páginas do Protótipo

A barra lateral esquerda do Streamlit disponibiliza 7 seções completas:

1. **Início:** Visão geral do projeto, equipe do Grupo 7, objetivos acadêmicos e arquitetura do trabalho.
2. **Aventura:** Simulador gráfico da masmorra em tempo real (100 salas). Permite testar a estratégia campeã do AG contra baselines sala a sala, com log de combate, vida do guerreiro, companheiros ativos e inventário.
3. **Como Funciona:** Explicação do algoritmo genético, do cromossomo de 16 genes, da função de aptidão, da seleção por torneio, do cruzamento BLX-α, da mutação e do elitismo.
4. **Resultados:** Comparativo científico entre Métodos (Estratégia Fixa vs Busca Aleatória vs AG), análise de convergência, boxplots de dispersão e significância estatística ($p = 0.748$).
5. **Bestiário:** Catálogo interativo dos 334 monstros extraídos do D&D 5e SRD 2014, com filtros por ND (Desafio), PV, CA, tipo de criatura e ataques.
6. **Dados e Fonte:** Proveniência do dataset externo (D&D 5e SRD 2014, OGL v1.0a), pipeline de tratamento, balanceamento de dados e verificação de integridade (Hash SHA-256).
7. **Laboratório:** Painel interativo para experimentação em tempo real. Permite alterar sementes, taxas de mutação (10%, 25%), tamanho populacional (10, 20, 50), número de gerações e rodar o AG ao vivo na banca.

---

## 5. Resolução de Problemas Comuns (Troubleshooting)

- **Erro de porta ocupada (`Port 8501 is already in use`):**
  Defina outra porta com a flag `--server.port 8599`.
- **Navegador não abre automaticamente:**
  Copie a URL informada no terminal (`http://localhost:8501` ou `http://localhost:8599`) e cole no Chrome, Edge ou Firefox.
- **Falha de permissão de script no PowerShell:**
  Execute `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` antes de ativar a venv.
- **Execução dos Testes Automatizados:**
  Para validar a integridade total do código a qualquer momento, execute:
  ```bash
  python -m pytest tests -v
  ```
  Resultado esperado: **53 passed**.
