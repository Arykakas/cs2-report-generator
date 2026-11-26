@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_CMD="
set "PYTHON_ARGS="
for /f "delims=" %%P in ('where python 2^>nul') do (
	"%%P" -c "import streamlit" >nul 2>&1
	if not errorlevel 1 (
		set "PYTHON_CMD=%%P"
		goto python_found
	)
)

where py >nul 2>&1
if not errorlevel 1 (
	py -3 -c "import streamlit" >nul 2>&1
	if not errorlevel 1 (
		set "PYTHON_CMD=py"
		set "PYTHON_ARGS=-3"
	)
)
if not defined PYTHON_CMD goto no_streamlit

:python_found
"%PYTHON_CMD%" %PYTHON_ARGS% -m streamlit run app.py
if errorlevel 1 (
	echo.
	echo Streamlit exited with an error. Review the message above.
	pause
)
exit /b %errorlevel%

:no_streamlit
echo No available Python interpreter has Streamlit installed.
echo Install it for the intended environment with: python -m pip install streamlit
pause
exit /b 1