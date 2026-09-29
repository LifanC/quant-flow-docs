@echo off
cd /d "%~dp0"
set "watchlist=watchlist.csv"
if exist "watchlist.xlsx" set "watchlist=watchlist.xlsx"
".venv\Scripts\python.exe" -m quant_flow.main --symbols-file "%watchlist%" --screen trend
pause
