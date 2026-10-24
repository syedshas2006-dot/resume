@echo off
echo Running Automated Test Suite for AI Resume Analyzer...
call .venv\Scripts\activate.bat
python tests\run_tests.py
pause
