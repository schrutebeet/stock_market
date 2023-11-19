@echo off

REM Set working directory
cd C:\Users\Ricky\Documents\Gitlab\stock_market

REM Set log directory
set LOGS_PATH=C:\Users\Ricky\Documents\Gitlab\cronjobs\logs_stock

REM Set the path to virtual environment
set VIRTUAL_ENV_PATH=.\stock_venv\Scripts\activate

REM Activate the virtual environment
call %VIRTUAL_ENV_PATH%

REM Run Stocks project
.\stock_venv\Scripts\python.exe -m src.main
