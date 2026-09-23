@echo off
title Tergon - Atualizar Site
cd /d "%~dp0Editar o Site"

echo Gerando o site a partir dos arquivos em "Editar o Site"...
echo.
py -3 gerar-site.py
if errorlevel 1 (
  python gerar-site.py
)

echo.
echo ============================================================
echo  Pronto. As paginas em site-final foram atualizadas.
echo  Use "Ver o site (clique aqui).bat" pra conferir.
echo ============================================================
echo.
pause
