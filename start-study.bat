@echo off
setlocal
cd /d "%~dp0"
if defined STUDY_PYTHON (
    "%STUDY_PYTHON%" -X utf8 "%~dp0start-study.py" %*
    exit /b
)
py -3 --version >nul 2>&1
if not errorlevel 1 (
    py -3 -X utf8 "%~dp0start-study.py" %*
    exit /b
)
python --version >nul 2>&1
if not errorlevel 1 (
    python -X utf8 "%~dp0start-study.py" %*
    exit /b
)
echo Python 3.9+ is required. Install Python and see README.md.
exit /b 1
