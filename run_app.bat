@echo off
echo ========================================
echo  Analise de Faturamento - COMPULAB vs SIMUS
echo ========================================
echo.
echo Verificando instalacao...
py -m pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo Streamlit nao encontrado. Instalando dependencias...
    py -m pip install -r requirements.txt
    echo.
)
echo.
echo Iniciando aplicativo...
echo O navegador abrira automaticamente em alguns segundos...
echo.
py -m streamlit run app.py
pause

