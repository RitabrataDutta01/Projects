@echo off
:: Go to the folder where this .bat file is
cd /d "%~dp0"

:: Activate virtual environment
call webdev\Scripts\activate.bat

:: Set Flask environment variables
set FLASK_APP=app.py
set FLASK_ENV=development

:: Run Flask on all network interfaces (0.0.0.0)
python -m flask run --host=0.0.0.0

pause
