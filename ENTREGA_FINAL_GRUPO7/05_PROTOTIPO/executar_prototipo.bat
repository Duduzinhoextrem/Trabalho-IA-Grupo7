@echo off
chcp 65001 > nul
echo =======================================================================
echo   MASMORRA GENETICA - GRUPO 7 ^| IA II - FIB 2026
echo   Iniciando Prototipo Interativo em Streamlit...
echo =======================================================================
echo.

REM Navega para a raiz do repositorio
cd /d "%~dp0..\.."

REM Verifica se existe ambiente virtual na raiz ou em pastas comuns
if exist "venv\Scripts\activate.bat" (
    echo [OK] Ativando ambiente virtual venv...
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo [OK] Ativando ambiente virtual .venv...
    call .venv\Scripts\activate.bat
) else (
    echo [AVISO] Executando com o interpretador Python padrao do sistema...
)

echo [OK] Iniciando Streamlit na porta 8501 a partir da raiz...
echo Abrindo navegador em http://localhost:8501 ...
echo Pressione Ctrl+C nesta janela para encerrar a aplicacao.
echo.

python -m streamlit run app.py
pause
