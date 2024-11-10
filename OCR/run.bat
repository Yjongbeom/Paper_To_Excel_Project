@ECHO OFF

for /f "tokens=* delims=" %%i in (.env) do set %%i

REM 환경변수설정
set QT_PLUGIN_PATH=%~dp0\OCR\.runtime\Python311\Lib\site-packages\PyQt5\Qt5\plugins
set QT_QPA_PLATFORM_PLUGIN_PATH=%~dp0\OCR\.runtime\Python311\Lib\site-packages\PyQt5\Qt5\plugins\platforms
".\.runtime\Python311\python.exe" -m pip install -r ./requirements.txt
".\.runtime\Python311\python.exe" ".\application\app.py"
pause