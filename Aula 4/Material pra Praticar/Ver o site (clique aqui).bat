@echo off
title Tergon - Visualizar Site
cd /d "%~dp0site-final"

echo Iniciando o site local...
start /min "Servidor Tergon" cmd /c "py -3 -m http.server 8888 || python -m http.server 8888"
timeout /t 2 /nobreak >nul

start "" http://localhost:8888/index.html

echo.
echo ============================================================
echo  O site esta rodando em http://localhost:8888
echo.
echo  Deixe esta janela aberta enquanto estiver olhando o site.
echo  Quando terminar, so fechar esta janela.
echo ============================================================
echo.
pause >nul
