

from core.calculations import (
    berechne_fertigungskosten,
    berechne_materialkosten,
    berechne_umsatz,
)
from core.rules import (
    absatzmenge_im_bereich,
    bestellmenge_im_bereich,
    fertige_erzeugnisse_lager_ausreichend,
    hat_genug_fertige_erzeugnisse,
    hat_genug_liquiditaet,
    hat_genug_rohmaterial,
    ist_positive_menge,
    produktionsmenge_im_bereich,
    rohmaterial_lager_ausreichend,
)
from core.state import GameState


# =========================================================
# Materialeinkauf
# =========================================================

def material_einkaufen(state: GameState, menge: float) -> None:
    """Kauft Rohmaterial ein und aktualisiert Lager, Liquidität und Materialkosten."""
    if not ist_positive_menge(menge):
        raise ValueError("Die Bestellmenge muss größer als 0 sein.")

    if not bestellmenge_im_bereich(menge):
        raise ValueError("Die Bestellmenge liegt außerhalb des erlaubten Bereichs.")

    if not rohmaterial_lager_ausreichend(state.rohmaterial_lager, menge):
        raise ValueError("Nicht genügend Lagerkapazität für den Materialeinkauf vorhanden.")

    kosten = berechne_materialkosten(menge, state.einkaufspreis_material)

    if not hat_genug_liquiditaet(state.liquide_mittel, kosten):
        raise ValueError("Nicht genügend liquide Mittel für den Materialeinkauf vorhanden.")

    state.rohmaterial_lager += menge
    state.liquide_mittel -= kosten
    state.materialkosten += kosten
    state.bestellmenge_material = menge
    state.log(f"Materialeinkauf durchgeführt: {menge} Lose für {kosten:.2f}.")


# =========================================================
# Produktion
# =========================================================

def produktion_durchfuehren(state: GameState, menge: float) -> None:
    """Verarbeitet Rohmaterial zu fertigen Erzeugnissen und bucht die Fertigungskosten pro Los."""
    if not ist_positive_menge(menge):
        raise ValueError("Die Produktionsmenge muss größer als 0 sein.")

    if not produktionsmenge_im_bereich(menge):
        raise ValueError("Die Produktionsmenge liegt außerhalb des erlaubten Bereichs.")

    if not hat_genug_rohmaterial(state.rohmaterial_lager, menge):
        raise ValueError("Nicht genügend Rohmaterial für die Produktion vorhanden.")

    if not fertige_erzeugnisse_lager_ausreichend(state.fertige_erzeugnisse, menge):
        raise ValueError("Nicht genügend Lagerkapazität für fertige Erzeugnisse vorhanden.")

    kosten = berechne_fertigungskosten(menge, state.fertigungskosten_pro_los)

    if not hat_genug_liquiditaet(state.liquide_mittel, kosten):
        raise ValueError("Nicht genügend liquide Mittel für die Produktion vorhanden.")

    state.rohmaterial_lager -= menge
    state.fertige_erzeugnisse += menge
    state.liquide_mittel -= kosten
    state.fertigungskosten += kosten
    state.produktionsmenge = menge
    state.log(f"Produktion durchgeführt: {menge} Lose, Kosten {kosten:.2f}.")


# =========================================================
# Verkauf
# =========================================================

def produkte_verkaufen(state: GameState, menge: float, sofortzahlung: bool = False) -> None:
    """Verkauft fertige Erzeugnisse und bucht Umsatz sowie Zahlung oder Forderung."""
    if not ist_positive_menge(menge):
        raise ValueError("Die Absatzmenge muss größer als 0 sein.")

    if not absatzmenge_im_bereich(menge):
        raise ValueError("Die Absatzmenge liegt außerhalb des erlaubten Bereichs.")

    if not hat_genug_fertige_erzeugnisse(state.fertige_erzeugnisse, menge):
        raise ValueError("Nicht genügend fertige Erzeugnisse für den Verkauf vorhanden.")

    umsatz = berechne_umsatz(menge, state.verkaufspreis)

    state.fertige_erzeugnisse -= menge
    state.umsatz += umsatz
    state.absatzmenge_ist += int(menge)

    if sofortzahlung:
        state.liquide_mittel += umsatz
        state.log(f"Verkauf mit Sofortzahlung: {menge} Lose, Umsatz {umsatz:.2f}.")
    else:
        state.forderungen += umsatz
        state.log(f"Verkauf auf Ziel: {menge} Lose, Umsatz {umsatz:.2f} als Forderung gebucht.")