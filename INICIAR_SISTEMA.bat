@echo off
chcp 65001 >nul
echo ==================================================
echo  🚀 Iniciando Biodiagnóstico App (Versão Nova)
echo  --------------------------------------
echo  1. Fechando processos antigos...
taskkill /F /IM python.exe >nul 2>&1
echo  2. Preparando ambiente...
cd biodiagnostico_app
echo  3. Iniciando servidor Reflex...
echo.
echo     Acesse no navegador: http://localhost:3000
echo.
echo ==================================================
py -m reflex run
pause
