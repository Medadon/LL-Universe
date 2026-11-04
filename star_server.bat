@echo off
cd /d "%~dp0"

"%~dp0.venv\Scripts\python.exe" -m uvicorn api.main:app --reload

pause
