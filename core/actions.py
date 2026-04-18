from data.config import (
    AFA_BGA_PRO_JAHR,
    AFA_GEBAEUDE_PRO_JAHR,
    AFA_MASCHINEN_PRO_JAHR,
    AFA_NEUE_ANLAGE_PRO_JAHR,
    MARKETING_NACHFRAGE_FAKTOR,
    MAX_UNFERTIGE_ERZEUGNISSE,
    SOFORTZAHLUNG_SKONTO,
    STANDARD_GEMEINKOSTEN_AB_JAHR_2_PRO_QUARTAL,
    STANDARD_GEMEINKOSTEN_JAHR_1_PRO_QUARTAL,
    STANDARD_INVESTITION_NEUE_ANLAGE,
    STEUERSATZ,
)
from core.calculations import (
    berechne_fertigungskosten,
    berechne_gewinn,
    berechne_kennzahlen,
    berechne_materialkosten,
    berechne_tatsaechliche_nachfrage,
    berechne_umsatz,
    berechne_zinskosten,
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
    state.log(f"Materialeinkauf: {menge:.0f} Lose für {kosten:.2f} M.")


# =========================================================
# Produktion Stufe 1
# =========================================================

def produktion_stufe_1(state: GameState, menge: float) -> None:
    """Verarbeitet Rohmaterial zu unfertigen Erzeugnissen (Fertigungsstufe 1)."""
    if not ist_positive_menge(menge):
        raise ValueError("Die Produktionsmenge der Stufe 1 muss größer als 0 sein.")
    if not produktionsmenge_im_bereich(menge):
        raise ValueError("Die Produktionsmenge der Stufe 1 liegt außerhalb des erlaubten Bereichs.")
    if not hat_genug_rohmaterial(state.rohmaterial_lager, menge):
        raise ValueError("Nicht genügend Rohmaterial für die Fertigungsstufe 1 vorhanden.")
    if state.unfertige_erzeugnisse + menge > MAX_UNFERTIGE_ERZEUGNISSE:
        raise ValueError("Nicht genügend Lagerkapazität für unfertige Erzeugnisse vorhanden.")

    kosten = berechne_fertigungskosten(menge, state.fertigungskosten_pro_los)

    if not hat_genug_liquiditaet(state.liquide_mittel, kosten):
        raise ValueError("Nicht genügend liquide Mittel für die Fertigungsstufe 1 vorhanden.")

    state.rohmaterial_lager -= menge
    state.unfertige_erzeugnisse += menge
    state.liquide_mittel -= kosten
    state.fertigungskosten += kosten
    state.produktionsmenge = menge
    state.neue_unfertige_dieses_quartal += menge
    state.stufe1_durchgefuehrt = True
    state.log(f"Fertigungsstufe 1: {menge:.0f} Lose, Kosten {kosten:.2f} M.")


# =========================================================
# Endmontage Stufe 2
# =========================================================

def endmontage_stufe_2(state: GameState, menge: float) -> None:
    """Verarbeitet unfertige Erzeugnisse zu fertigen Erzeugnissen (Stufe 2)."""
    if state.neue_anlage_aktiv:
        raise ValueError("Mit der neuen Anlage entfällt Stufe 2 – nutze 'Produktion (neue Anlage)'.")
    if not ist_positive_menge(menge):
        raise ValueError("Die Endmontagemenge der Stufe 2 muss größer als 0 sein.")
    if not produktionsmenge_im_bereich(menge):
        raise ValueError("Die Endmontagemenge der Stufe 2 liegt außerhalb des erlaubten Bereichs.")
    if state.unfertige_erzeugnisse < menge:
        raise ValueError("Nicht genügend unfertige Erzeugnisse für die Endmontage vorhanden.")
    if not fertige_erzeugnisse_lager_ausreichend(state.fertige_erzeugnisse, menge):
        raise ValueError("Nicht genügend Lagerkapazität für fertige Erzeugnisse vorhanden.")

    kosten = berechne_fertigungskosten(menge, state.endmontagekosten_stufe_2_pro_los)

    if not hat_genug_liquiditaet(state.liquide_mittel, kosten):
        raise ValueError("Nicht genügend liquide Mittel für die Endmontage vorhanden.")

    state.unfertige_erzeugnisse -= menge
    state.fertige_erzeugnisse += menge
    state.liquide_mittel -= kosten
    state.fertigungskosten += kosten
    state.produktionsmenge = menge
    state.stufe2_durchgefuehrt = True
    state.log(f"Endmontage Stufe 2: {menge:.0f} Lose, Kosten {kosten:.2f} M.")


# =========================================================
# Produktion mit neuer Anlage (einstufig)
# =========================================================

def produktion_neue_anlage(state: GameState, menge: float) -> None:
    """Einstufige Produktion mit der neuen Anlage (direkt Rohstoff → Fertigprodukt)."""
    if not state.neue_anlage_aktiv:
        raise ValueError("Neue Anlage ist noch nicht aktiv.")
    if not ist_positive_menge(menge):
        raise ValueError("Die Produktionsmenge muss größer als 0 sein.")
    if not produktionsmenge_im_bereich(menge):
        raise ValueError("Die Produktionsmenge liegt außerhalb des erlaubten Bereichs.")
    if not hat_genug_rohmaterial(state.rohmaterial_lager, menge):
        raise ValueError("Nicht genügend Rohmaterial vorhanden.")
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
    state.log(f"Produktion (neue Anlage): {menge:.0f} Lose, Kosten {kosten:.2f} M.")


# =========================================================
# Verkauf
# =========================================================

def produkte_verkaufen(state: GameState, menge_angebot: float, sofortzahlung: bool = False) -> None:
    """Bietet fertige Erzeugnisse zum Verkauf an; tatsächlicher Absatz hängt von der
    gewürfelten Marktnachfrage ab (Normalverteilung um den Erwartungswert).

    Verkauft wird min(Angebot, tatsächliche Nachfrage). Nicht abgenommene Lose
    verbleiben im Fertigwarenlager.
    """
    if not ist_positive_menge(menge_angebot):
        raise ValueError("Das Verkaufsangebot muss größer als 0 sein.")
    if not absatzmenge_im_bereich(menge_angebot):
        raise ValueError("Das Verkaufsangebot liegt außerhalb des erlaubten Bereichs.")
    if not hat_genug_fertige_erzeugnisse(state.fertige_erzeugnisse, menge_angebot):
        raise ValueError("Nicht genügend fertige Erzeugnisse für den Verkauf vorhanden.")

    # Marktnachfrage für dieses Quartal würfeln (einmalig pro Verkauf)
    nachfrage_index = state.marketing_index * state.nachfrage_index
    tatsaechliche_nachfrage = berechne_tatsaechliche_nachfrage(state.verkaufspreis, nachfrage_index)
    tatsaechlich_verkauft = min(int(menge_angebot), tatsaechliche_nachfrage)

    # Ergebnis im State speichern (für UI-Feedback)
    state.letzte_tatsaechliche_nachfrage = tatsaechliche_nachfrage
    state.letzte_verkaufte_menge = tatsaechlich_verkauft
    state.verkauf_durchgefuehrt = True

    if tatsaechlich_verkauft <= 0:
        state.log(
            f"Verkauf: Markt hat keine Erzeugnisse abgenommen "
            f"(Nachfrage: {tatsaechliche_nachfrage}, Angebot: {int(menge_angebot)})."
        )
        return

    umsatz_brutto = berechne_umsatz(tatsaechlich_verkauft, state.verkaufspreis)
    state.fertige_erzeugnisse -= tatsaechlich_verkauft
    state.absatzmenge_ist += tatsaechlich_verkauft

    if sofortzahlung:
        skonto = round(umsatz_brutto * SOFORTZAHLUNG_SKONTO, 2)
        umsatz_netto = umsatz_brutto - skonto
        state.liquide_mittel += umsatz_netto
        state.umsatz += umsatz_netto
        state.log(
            f"Verkauf (Sofortzahlung, −{skonto:.2f} M Skonto): {tatsaechlich_verkauft} Elektromotoren abgenommen "
            f"(Nachfrage: {tatsaechliche_nachfrage}), Umsatz netto {umsatz_netto:.2f} M."
        )
    else:
        state.forderungen += umsatz_brutto
        state.umsatz += umsatz_brutto
        state.log(
            f"Verkauf (auf Ziel): {tatsaechlich_verkauft} Elektromotoren abgenommen "
            f"(Nachfrage: {tatsaechliche_nachfrage}), {umsatz_brutto:.2f} M als Forderung gebucht."
        )


# =========================================================
# Forderungen einziehen
# =========================================================

def forderungen_einziehen(state: GameState) -> None:
    """Kunden zahlen – offene Forderungen werden zu liquiden Mitteln."""
    if state.forderungen <= 0:
        raise ValueError("Keine offenen Forderungen vorhanden.")

    betrag = state.forderungen
    state.liquide_mittel += betrag
    state.forderungen = 0.0
    state.log(f"Forderungen eingezogen: {betrag:.2f} M.")


# =========================================================
# Gemeinkosten zahlen
# =========================================================

def gemeinkosten_zahlen(state: GameState) -> None:
    """Zahlt die quartalsmäßigen Gemeinkosten (6M in Jahr 1, 5M ab Jahr 2)."""
    betrag = (
        STANDARD_GEMEINKOSTEN_JAHR_1_PRO_QUARTAL
        if state.jahr == 1
        else STANDARD_GEMEINKOSTEN_AB_JAHR_2_PRO_QUARTAL
    )

    if not hat_genug_liquiditaet(state.liquide_mittel, betrag):
        raise ValueError(f"Nicht genügend liquide Mittel für Gemeinkosten ({betrag:.1f} M) vorhanden.")

    state.liquide_mittel -= betrag
    state.gemeinkosten += betrag
    state.log(f"Gemeinkosten gezahlt: {betrag:.1f} M (Jahr {state.jahr}).")


# =========================================================
# Marketing
# =========================================================

def marketing_ausgeben(state: GameState, betrag: float) -> None:
    """Gibt Budget für Marketing aus und erhöht dadurch die Marktnachfrage für dieses Quartal."""
    if not ist_positive_menge(betrag):
        raise ValueError("Der Marketingbetrag muss größer als 0 sein.")
    if not hat_genug_liquiditaet(state.liquide_mittel, betrag):
        raise ValueError("Nicht genügend liquide Mittel für Marketing vorhanden.")

    state.liquide_mittel -= betrag
    state.marketingkosten += betrag
    # Nachfrage steigt um 10% pro investierter Million (MARKETING_NACHFRAGE_FAKTOR = 0.10)
    state.marketing_index = 1.0 + betrag * MARKETING_NACHFRAGE_FAKTOR
    state.marketing_durchgefuehrt = True
    state.log(f"Marketing: {betrag:.2f} M investiert → Nachfrage-Index {state.marketing_index:.2f}.")


# =========================================================
# Darlehen tilgen
# =========================================================

def darlehen_tilgen(state: GameState, betrag: float) -> None:
    """Tilgt einen Teil des Darlehens."""
    if not ist_positive_menge(betrag):
        raise ValueError("Der Tilgungsbetrag muss größer als 0 sein.")
    if betrag > state.darlehen:
        raise ValueError(f"Tilgungsbetrag ({betrag:.2f} M) übersteigt das Darlehen ({state.darlehen:.2f} M).")
    if not hat_genug_liquiditaet(state.liquide_mittel, betrag):
        raise ValueError("Nicht genügend liquide Mittel für die Tilgung vorhanden.")

    state.liquide_mittel -= betrag
    state.darlehen -= betrag
    state.log(f"Darlehen getilgt: {betrag:.2f} M, verbleibendes Darlehen: {state.darlehen:.2f} M.")


# =========================================================
# Jahresabschluss
# =========================================================

def jahresabschluss(state: GameState) -> None:
    """Führt den Jahresabschluss durch: Zinsen, Abschreibungen, Steuern, GuV.

    Sollte am Ende von Quartal 4 durchgeführt werden, bevor 'Nächstes Quartal'
    geklickt wird.
    """
    # --- Zinsen ---
    zinsen = berechne_zinskosten(state.darlehen, state.zinssatz)
    if not hat_genug_liquiditaet(state.liquide_mittel, zinsen):
        raise ValueError(
            f"Nicht genügend liquide Mittel für Zinszahlung ({zinsen:.2f} M) vorhanden."
        )
    state.liquide_mittel -= zinsen
    state.zinskosten += zinsen
    state.log(f"Jahresabschluss – Zinsen: {zinsen:.2f} M.")

    # --- Abschreibungen ---
    afa_gebaeude = min(AFA_GEBAEUDE_PRO_JAHR, state.av_gebaeude)
    afa_maschinen = min(AFA_MASCHINEN_PRO_JAHR, state.av_maschinen)
    afa_bga = min(AFA_BGA_PRO_JAHR, state.av_bga)
    afa_neue_anlage = AFA_NEUE_ANLAGE_PRO_JAHR if state.neue_anlage_aktiv else 0.0

    state.av_gebaeude -= afa_gebaeude
    state.av_maschinen -= afa_maschinen
    state.av_bga -= afa_bga
    afa_gesamt = afa_gebaeude + afa_maschinen + afa_bga + afa_neue_anlage
    state.abschreibungen_periode += afa_gesamt
    state.abschreibungen_kumuliert += afa_gesamt
    state.log(f"Jahresabschluss – Abschreibungen: {afa_gesamt:.2f} M.")

    # --- Gewinn vor Steuern ---
    gewinn_vor_steuern = berechne_gewinn(
        umsatz=state.umsatz,
        materialkosten=state.materialkosten,
        fertigungskosten=state.fertigungskosten,
        gemeinkosten=state.gemeinkosten,
        marketingkosten=state.marketingkosten,
        zinskosten=state.zinskosten,
        abschreibungen=state.abschreibungen_periode,
    )

    # --- Steuern (1/3 des positiven Gewinns) ---
    steuern = max(0.0, gewinn_vor_steuern * STEUERSATZ)
    state.steuerverbindlichkeiten += steuern
    state.log(f"Jahresabschluss – Steuern: {steuern:.2f} M.")

    # --- Gewinn nach Steuern und Eigenkapital ---
    state.gewinn = gewinn_vor_steuern - steuern
    state.eigenkapital += state.gewinn
    state.log(f"Jahresabschluss – Gewinn n. St.: {state.gewinn:.2f} M, EK: {state.eigenkapital:.2f} M.")

    # --- Kennzahlen speichern für Verlaufscharts ---
    kz = berechne_kennzahlen(state)
    state.kennzahlen_history.append(kz)

    # --- Periodenwerte für nächstes Jahr zurücksetzen ---
    state.reset_periodenwerte()
    state.jahresabschluss_durchgefuehrt = True
    state.log(f"Jahresabschluss Jahr {state.jahr} abgeschlossen.")


# =========================================================
# Neue Anlage kaufen
# =========================================================

def neue_anlage_kaufen(state: GameState) -> None:
    """Investiert in die neue einstufige Fertigungsanlage (ab Jahr 3, Kosten 20M).

    Die neue Anlage ersetzt die zweistufige Produktion:
    - Einstufig: direkt Rohstoff → Fertigprodukt
    - Kosten: 3M/Los (wie Stufe 1 vorher)
    - Kapazität: bis zu 3 Lose/Quartal
    """
    if state.neue_anlage_aktiv:
        raise ValueError("Die neue Anlage ist bereits aktiv.")
    if state.jahr < 3:
        raise ValueError("Die neue Anlage ist erst ab Jahr 3 verfügbar.")
    if not hat_genug_liquiditaet(state.liquide_mittel, STANDARD_INVESTITION_NEUE_ANLAGE):
        raise ValueError(
            f"Nicht genügend liquide Mittel für die Investition ({STANDARD_INVESTITION_NEUE_ANLAGE:.0f} M) vorhanden."
        )

    state.liquide_mittel -= STANDARD_INVESTITION_NEUE_ANLAGE
    state.av_maschinen += STANDARD_INVESTITION_NEUE_ANLAGE
    state.neue_anlage_aktiv = True
    state.log(f"Neue Anlage gekauft: {STANDARD_INVESTITION_NEUE_ANLAGE:.0f} M investiert.")


# =========================================================
# Alias für Rückwärtskompatibilität
# =========================================================

def produktion_durchfuehren(state: GameState, menge: float) -> None:
    """Alias für die Fertigungsstufe 1."""
    produktion_stufe_1(state, menge)
