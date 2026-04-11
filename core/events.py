"""
Quartalsereignisse – zufällige Marktentwicklungen die das Spielgeschehen beeinflussen.

Jedes Ereignis modifiziert genau ein State-Feld für die Dauer eines Quartals.
Die Originalwerte werden gespeichert und am Quartalsende automatisch wiederhergestellt.
"""

import random
from typing import Optional


EREIGNISSE_NACHTEIL = [
    {
        "id": "rohstoffknappheit",
        "titel": "Rohstoffknappheit",
        "beschreibung": "Lieferengpässe auf dem Weltmarkt – Einkaufspreise steigen dieses Quartal um 50%.",
        "effekt_feld": "einkaufspreis_material",
        "effekt_faktor": 1.5,
        "kategorie": "nachteil",
        "emoji": "⛏️",
    },
    {
        "id": "konjunkturdelle",
        "titel": "Konjunkturdelle",
        "beschreibung": "Wirtschaftliche Unsicherheit dämpft die Kauflust – Marktnachfrage sinkt um 25%.",
        "effekt_feld": "nachfrage_index",
        "effekt_faktor": 0.75,
        "kategorie": "nachteil",
        "emoji": "📉",
    },
    {
        "id": "personalengpass",
        "titel": "Personalengpass",
        "beschreibung": "Grippe-Welle legt Teile der Belegschaft lahm – Fertigungskosten steigen um 20%.",
        "effekt_feld": "fertigungskosten_pro_los",
        "effekt_faktor": 1.2,
        "kategorie": "nachteil",
        "emoji": "🤒",
    },
    {
        "id": "maschinenstoerung",
        "titel": "Ungeplante Maschinenstörung",
        "beschreibung": "Maschinenausfall erzwingt Notfallreparatur – Fertigungskosten steigen um 30%.",
        "effekt_feld": "fertigungskosten_pro_los",
        "effekt_faktor": 1.3,
        "kategorie": "nachteil",
        "emoji": "🔧",
    },
    {
        "id": "kundenstornierung",
        "titel": "Großkundenabgang",
        "beschreibung": "Ein Schlüsselkunde wechselt zur Konkurrenz – Nachfrage bricht um 30% ein.",
        "effekt_feld": "nachfrage_index",
        "effekt_faktor": 0.70,
        "kategorie": "nachteil",
        "emoji": "😤",
    },
]

EREIGNISSE_VORTEIL = [
    {
        "id": "lieferantenrabatt",
        "titel": "Lieferantensonderangebot",
        "beschreibung": "Jahresendverkauf beim Lieferanten – Einkaufspreise sinken dieses Quartal um 20%.",
        "effekt_feld": "einkaufspreis_material",
        "effekt_faktor": 0.8,
        "kategorie": "vorteil",
        "emoji": "🎁",
    },
    {
        "id": "wirtschaftsboom",
        "titel": "Wirtschaftsboom",
        "beschreibung": "Starke Konjunktur befeuert den Markt – Nachfrage steigt um 30%.",
        "effekt_feld": "nachfrage_index",
        "effekt_faktor": 1.3,
        "kategorie": "vorteil",
        "emoji": "📈",
    },
    {
        "id": "lean_offensive",
        "titel": "Lean-Offensive erfolgreich",
        "beschreibung": "Prozessverbesserungen zeigen Wirkung – Fertigungskosten sinken um 15%.",
        "effekt_feld": "fertigungskosten_pro_los",
        "effekt_faktor": 0.85,
        "kategorie": "vorteil",
        "emoji": "⚙️",
    },
    {
        "id": "grossauftrag",
        "titel": "Großauftrag eingegangen",
        "beschreibung": "Neukunde mit Großbestellung – Marktnachfrage steigt um 50%!",
        "effekt_feld": "nachfrage_index",
        "effekt_faktor": 1.5,
        "kategorie": "vorteil",
        "emoji": "🏆",
    },
    {
        "id": "rohstoffpreisfall",
        "titel": "Rohstoffpreise im Keller",
        "beschreibung": "Überangebot auf dem Weltmarkt drückt die Preise – Einkaufskosten sinken um 25%.",
        "effekt_feld": "einkaufspreis_material",
        "effekt_faktor": 0.75,
        "kategorie": "vorteil",
        "emoji": "💎",
    },
]

ALLE_EREIGNISSE = EREIGNISSE_NACHTEIL + EREIGNISSE_VORTEIL

# Wahrscheinlichkeit, dass überhaupt ein Ereignis eintritt (pro Quartal)
EREIGNIS_WAHRSCHEINLICHKEIT = 0.45


def wuerfle_ereignis() -> Optional[dict]:
    """Würfelt ein zufälliges Quartalsereignis. Gibt None zurück bei ruhigem Quartal."""
    if random.random() > EREIGNIS_WAHRSCHEINLICHKEIT:
        return None
    return random.choice(ALLE_EREIGNISSE)


def wende_ereignis_an(state, ereignis: dict) -> None:
    """Wendet Ereigniseffekt auf den State an; speichert Originalwert zur Rücksetzung."""
    feld = ereignis["effekt_feld"]
    faktor = ereignis["effekt_faktor"]
    original = getattr(state, feld)
    state.ereignis_original_werte[feld] = original
    setattr(state, feld, round(original * faktor, 4))
    state.log(f"Ereignis '{ereignis['titel']}': {feld} × {faktor:.2f} (war {original:.2f})")


def setze_ereignis_zurueck(state) -> None:
    """Stellt alle durch das Ereignis veränderten Felder auf ihre Originalwerte zurück."""
    for feld, original in state.ereignis_original_werte.items():
        setattr(state, feld, original)
    state.ereignis_original_werte = {}
    state.aktuelles_ereignis = None
