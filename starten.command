#!/bin/bash
cd "$(dirname "$0")"

echo "============================================"
echo "  BWL Planspiel Factory - wird gestartet..."
echo "============================================"
echo ""

# Python pruefen
if ! command -v python3 &> /dev/null; then
    echo "FEHLER: Python ist nicht installiert."
    echo ""
    echo "Bitte Python herunterladen: https://www.python.org/downloads/"
    read -p "Druecke Enter zum Beenden..."
    exit 1
fi

echo "Python gefunden."

# Virtuelle Umgebung anlegen (nur beim ersten Start)
if [ ! -d ".venv" ]; then
    echo "Erstelle virtuelle Umgebung (nur beim ersten Start)..."
    python3 -m venv .venv
fi

# Umgebung aktivieren
source .venv/bin/activate

# Pakete installieren
echo "Pruefe Abhaengigkeiten..."
pip install -q -r requirements.txt

echo ""
echo "Starte Anwendung im Browser..."
echo "(Fenster offen lassen - Schliessen beendet die App)"
echo ""

streamlit run app.py --server.headless false

deactivate
