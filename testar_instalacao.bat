@echo off
echo ========================================
echo  Teste de Instalacao
echo ========================================
echo.

echo [1/4] Verificando Python...
py --version
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Tente usar: python --version
    pause
    exit /b 1
)
echo OK: Python encontrado!
echo.

echo [2/4] Verificando pip...
py -m pip --version
if errorlevel 1 (
    echo ERRO: pip nao encontrado!
    pause
    exit /b 1
)
echo OK: pip encontrado!
echo.

echo [3/4] Verificando dependencias...
py -m pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo AVISO: Streamlit nao instalado. Instalando agora...
    py -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ERRO: Falha ao instalar dependencias!
        pause
        exit /b 1
    )
) else (
    echo OK: Streamlit ja instalado!
)
echo.

echo [4/4] Verificando arquivo app.py...
if exist app.py (
    echo OK: app.py encontrado!
) else (
    echo ERRO: app.py nao encontrado!
    pause
    exit /b 1
)
echo.

echo ========================================
echo  TUDO PRONTO! 
echo ========================================
echo.
echo Para iniciar o aplicativo, execute:
echo   py -m streamlit run app.py
echo.
echo Ou clique duas vezes em: run_app.bat
echo.
pause

