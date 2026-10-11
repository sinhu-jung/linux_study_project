@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  py -3 -X utf8 start-study.py --offline
  if errorlevel 1 pause
  exit /b
)
set "STUDY_PY=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%STUDY_PY%" (
  "%STUDY_PY%" -X utf8 start-study.py --offline
  if errorlevel 1 pause
  exit /b
)
python -X utf8 start-study.py --offline
if errorlevel 1 (
  echo Python 3.9 이상이 필요합니다. README.md를 확인하세요.
  pause
)
