@echo off
chcp 65001 > nul
title BWL Planspiel Factory

:: Sicherstellen dass das Arbeitsverzeichnis korrekt ist
cd /d "%~dp0"

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
    echo WICHTIG: Bei der Installation "Add Python to PATH" anhaken!
    pause
    exit /b 1
)

echo Python gefunden.

:: Virtuelle Umgebung anlegen (nur beim ersten Start)
if not exist ".venv" (
    echo Erstelle virtuelle Umgebung...
    python -m venv .venv
    if errorlevel 1 (
        echo FEHLER: Virtuelle Umgebung konnte nicht erstellt werden.
        pause
        exit /b 1
    )
)

:: Umgebung aktivieren
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo FEHLER: Virtuelle Umgebung konnte nicht aktiviert werden.
    pause
    exit /b 1
)

:: Pakete installieren (nur wenn noetig)
echo Pruefe Abhaengigkeiten...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo FEHLER: Pakete konnten nicht installiert werden.
    pause
    exit /b 1
)

echo.
echo Starte Anwendung im Browser...
echo Fenster offen lassen - Schliessen beendet die App
echo.

:: Streamlit starten
streamlit run app.py

if errorlevel 1 (
    echo.
    echo FEHLER: Streamlit ist abgestuerzt oder konnte nicht starten.
    pause
)

deactivate
