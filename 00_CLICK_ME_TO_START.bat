@echo off
cd /d "%~dp0"

:: Look for .venv folder specifically
call .venv\Scripts\activate

:: Run the app
python -m streamlit run app.py
pause