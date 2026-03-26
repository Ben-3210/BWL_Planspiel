from data.config import (
    MAX_ABSATZMENGE,
    MAX_BESTELLMENGE_MATERIAL,
    MAX_EINKAUFSPREIS_MATERIAL,
    MAX_FERTIGE_ERZEUGNISSE,
    MAX_FERTIGUNGSKOSTEN_PRO_LOS,
    MAX_GEMEINKOSTEN_PRO_QUARTAL,
    MAX_PRODUKTIONSMENGE,
    MAX_ROHMATERIAL_LAGER,
    MAX_VERKAUFSPREIS,
    MIN_ABSATZMENGE,
    MIN_BESTELLMENGE_MATERIAL,
    MIN_EINKAUFSPREIS_MATERIAL,
    MIN_FERTIGUNGSKOSTEN_PRO_LOS,
    MIN_GEMEINKOSTEN_PRO_QUARTAL,
    MIN_PRODUKTIONSMENGE,
    MIN_VERKAUFSPREIS,
)


# =========================================================
# Interne Hilfsfunktion
# =========================================================

def _wert_im_bereich(wert: float, minimum: float, maximum: float) -> bool:
    """Prüft, ob ein Wert innerhalb eines Bereichs liegt."""
    return minimum <= wert <= maximum


# =========================================================
# Allgemeine Mengenprüfungen
# =========================================================

def ist_positive_menge(menge: float) -> bool:
    """Prüft, ob eine Menge größer als null ist."""
    return menge > 0


def ist_nicht_negative_menge(menge: float) -> bool:
    """Prüft, ob eine Menge null oder positiv ist."""
    return menge >= 0


# =========================================================
# Bereichsprüfungen für Mengen
# =========================================================

def absatzmenge_im_bereich(menge: float) -> bool:
    """Prüft, ob die Absatzmenge innerhalb der erlaubten Grenzen liegt."""
    return _wert_im_bereich(menge, MIN_ABSATZMENGE, MAX_ABSATZMENGE)


def bestellmenge_im_bereich(menge: float) -> bool:
    """Prüft, ob die Bestellmenge innerhalb der erlaubten Grenzen liegt."""
    return _wert_im_bereich(menge, MIN_BESTELLMENGE_MATERIAL, MAX_BESTELLMENGE_MATERIAL)


def produktionsmenge_im_bereich(menge: float) -> bool:
    """Prüft, ob die Produktionsmenge innerhalb der erlaubten Grenzen liegt."""
    return _wert_im_bereich(menge, MIN_PRODUKTIONSMENGE, MAX_PRODUKTIONSMENGE)


# =========================================================
# Bereichsprüfungen für Preise und Kosten
# =========================================================

def verkaufspreis_im_bereich(preis: float) -> bool:
    """Prüft, ob der Verkaufspreis innerhalb der erlaubten Grenzen liegt."""
    return _wert_im_bereich(preis, MIN_VERKAUFSPREIS, MAX_VERKAUFSPREIS)


def einkaufspreis_im_bereich(preis: float) -> bool:
    """Prüft, ob der Einkaufspreis innerhalb der erlaubten Grenzen liegt."""
    return _wert_im_bereich(preis, MIN_EINKAUFSPREIS_MATERIAL, MAX_EINKAUFSPREIS_MATERIAL)


def fertigungskosten_im_bereich(kosten: float) -> bool:
    """Prüft, ob die Fertigungskosten pro Los innerhalb der erlaubten Grenzen liegen."""
    return _wert_im_bereich(kosten, MIN_FERTIGUNGSKOSTEN_PRO_LOS, MAX_FERTIGUNGSKOSTEN_PRO_LOS)


def gemeinkosten_im_bereich(kosten: float) -> bool:
    """Prüft, ob die Gemeinkosten innerhalb der erlaubten Grenzen liegen."""
    return _wert_im_bereich(kosten, MIN_GEMEINKOSTEN_PRO_QUARTAL, MAX_GEMEINKOSTEN_PRO_QUARTAL)


# =========================================================
# Ressourcen- und Bestandsprüfungen
# =========================================================

def hat_genug_liquiditaet(liquide_mittel: float, benoetigter_betrag: float) -> bool:
    """Prüft, ob genügend liquide Mittel vorhanden sind."""
    return liquide_mittel >= benoetigter_betrag


def hat_genug_rohmaterial(bestand: float, benoetigte_menge: float) -> bool:
    """Prüft, ob genügend Rohmaterial für eine Aktion vorhanden ist."""
    return bestand >= benoetigte_menge


def hat_genug_fertige_erzeugnisse(bestand: float, benoetigte_menge: float) -> bool:
    """Prüft, ob genügend fertige Erzeugnisse für den Verkauf vorhanden sind."""
    return bestand >= benoetigte_menge


# =========================================================
# Lagerkapazitäten
# =========================================================

def rohmaterial_lager_ausreichend(aktueller_bestand: float, zugang: float) -> bool:
    """Prüft, ob das Rohmateriallager durch den Zugang nicht überfüllt wird."""
    return aktueller_bestand + zugang <= MAX_ROHMATERIAL_LAGER


def fertige_erzeugnisse_lager_ausreichend(aktueller_bestand: float, zugang: float) -> bool:
    """Prüft, ob das Lager fertiger Erzeugnisse durch den Zugang nicht überfüllt wird."""
    return aktueller_bestand + zugang <= MAX_FERTIGE_ERZEUGNISSE

