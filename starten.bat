@echo off
chcp 65001 > nul
title BWL Planspiel Factory

echo ============================================
echo   BWL Planspiel Factory - wird gestartet...
echo ============================================
echo.

:: Python pruefen
python --version > nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python ist nicht installiert oder nicht im PATH.
    echo.
    echo Bitte Python herunterladen und installieren:
    echo   https://www.python.org/downloads/
    echo.
    echo WICHTIG: Bei der Installation "Add Python to PATH" anhakenl
    pause
    exit /b 1
)

echo Python gefunden.

:: Virtuelle Umgebung anlegen (nur beim ersten Start)
if not exist ".venv" (
    echo Erstelle virtuelle Umgebung (nur beim ersten Start)...
    python -m venv .venv
)

:: Umgebung aktivieren
call .venv\Scripts\activate.bat

:: Pakete installieren (nur wenn noetig)
echo Pruefe Abhaengigkeiten...
pip install -q -r requirements.txt

echo.
echo Starte Anwendung im Browser...
echo (Fenster offen lassen - Schliessen beendet die App)
echo.

:: Streamlit starten (Browser oeffnet sich automatisch)
streamlit run app.py --server.headless false

deactivate
