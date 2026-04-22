import random

from data.config import (
    AFA_BGA_PRO_JAHR,
    AFA_GEBAEUDE_PRO_JAHR,
    AFA_MASCHINEN_PRO_JAHR,
    AFA_NEUE_ANLAGE_PRO_JAHR,
    BASISNACHFRAGE_PRO_QUARTAL,
    BASISPREIS,
    EINKAUFSPREIS_ERWARTUNGSWERT,
    EINKAUFSPREIS_MIN,
    EINKAUFSPREIS_STANDARDABWEICHUNG,
    NACHFRAGE_STANDARDABWEICHUNG,
    PREISELASTIZITAET,
)


def berechne_materialkosten(menge: float, preis_pro_los: float) -> float:
    """Berechnet die gesamten Materialkosten."""
    return menge * preis_pro_los


def berechne_fertigungskosten(menge: float, kosten_pro_los: float) -> float:
    """Berechnet die gesamten Fertigungskosten."""
    return menge * kosten_pro_los


def berechne_umsatz(menge: float, verkaufspreis: float) -> float:
    """Berechnet den Umsatz aus Absatzmenge und Verkaufspreis."""
    return menge * verkaufspreis


def berechne_zinskosten(darlehen: float, zinssatz: float) -> float:
    """Berechnet die Zinskosten auf Basis von Darlehen und Zinssatz."""
    return darlehen * zinssatz


def berechne_variable_gesamtkosten(
    menge: float,
    materialpreis_pro_los: float,
    fertigungskosten_pro_los: float,
) -> float:
    """Berechnet die gesamten variablen Kosten einer Produktionsmenge."""
    return berechne_materialkosten(menge, materialpreis_pro_los) + berechne_fertigungskosten(menge, fertigungskosten_pro_los)


def berechne_deckungsbeitrag(
    umsatz: float,
    materialkosten: float,
    fertigungskosten: float,
) -> float:
    """Berechnet den Deckungsbeitrag vor Fixkosten."""
    return umsatz - materialkosten - fertigungskosten


def berechne_gewinn(
    umsatz: float,
    materialkosten: float,
    fertigungskosten: float,
    gemeinkosten: float,
    marketingkosten: float,
    zinskosten: float,
    abschreibungen: float,
) -> float:
    """Berechnet den Periodengewinn vor Steuern."""
    return (
        umsatz
        - materialkosten
        - fertigungskosten
        - gemeinkosten
        - marketingkosten
        - zinskosten
        - abschreibungen
    )


def berechne_afa_vorschau(state) -> float:
    """Berechnet die erwarteten Jahres-Abschreibungen (für Q4-Vorschau vor Jahresabschluss)."""
    afa = (
        min(AFA_GEBAEUDE_PRO_JAHR, state.av_gebaeude)
        + min(AFA_MASCHINEN_PRO_JAHR, state.av_maschinen)
        + min(AFA_BGA_PRO_JAHR, state.av_bga)
    )
    if state.neue_anlage_aktiv:
        afa += AFA_NEUE_ANLAGE_PRO_JAHR
    return afa


def berechne_cashflow(gewinn: float, abschreibungen: float) -> float:
    """Berechnet einen einfachen Cashflow aus Gewinn und Abschreibungen."""
    return gewinn + abschreibungen


def wuerfle_einkaufspreis() -> float:
    """Zieht einen neuen Einkaufspreis aus einer Normalverteilung (µ=3M, σ=0.4M)."""
    preis = random.gauss(EINKAUFSPREIS_ERWARTUNGSWERT, EINKAUFSPREIS_STANDARDABWEICHUNG)
    return round(max(EINKAUFSPREIS_MIN, preis), 2)


def berechne_nachfrage(preis: float, marketing_index: float = 1.0) -> int:
    """Berechnet die *erwartete* Quartalsnachfrage (Planungswert, ohne Zufallselement).

    Formel: Nachfrage = BASIS * (BASISPREIS / Preis)^ELASTIZITAET * Marketing-Index
    Bei Basispreis 11M → 3 Lose/Quartal (entspricht ~99M Jahresumsatz).
    """
    if preis <= 0:
        return BASISNACHFRAGE_PRO_QUARTAL
    raw = BASISNACHFRAGE_PRO_QUARTAL * (BASISPREIS / preis) ** PREISELASTIZITAET * marketing_index
    return max(0, int(raw))


def berechne_nachfrage_spanne(preis: float, marketing_index: float = 1.0) -> tuple[int, int]:
    """Gibt die realistische Nachfragespanne zurück (µ ± 2σ, 95%-Konfidenzintervall).

    Dient der Anzeige im UI damit Spieler die Unsicherheit einschätzen können.
    """
    mu = berechne_nachfrage(preis, marketing_index)
    sigma = max(0.5, mu * NACHFRAGE_STANDARDABWEICHUNG)
    low = max(0, int(mu - 2 * sigma))
    high = int(mu + 2 * sigma) + 1
    return low, high


def berechne_tatsaechliche_nachfrage(preis: float, marketing_index: float = 1.0) -> int:
    """Würfelt die tatsächliche Quartalsnachfrage aus einer Normalverteilung.

    Der Erwartungswert folgt der isoelastischen Kurve; die Streuung (σ = 30% des µ)
    bildet reale Marktschwankungen ab. Wird einmalig pro Verkaufsvorgang gezogen.
    """
    mu = berechne_nachfrage(preis, marketing_index)
    sigma = max(0.5, mu * NACHFRAGE_STANDARDABWEICHUNG)
    tatsaechlich = int(round(random.gauss(mu, sigma)))
    return max(0, tatsaechlich)


def berechne_kennzahlen(state) -> dict:
    """Berechnet alle relevanten Kennzahlen aus dem aktuellen GameState.

    Gibt ein Dictionary mit Kennzahl-Name → Wert zurück.
    """
    # Anlagevermögen
    av = state.av_grundstuecke + state.av_gebaeude + state.av_maschinen + state.av_bga

    # Umlaufvermögen (Vorräte zu Herstellungskosten bewertet)
    rohstoffe_wert = state.rohmaterial_lager * state.einkaufspreis_material
    kosten_stufe1 = state.einkaufspreis_material + state.fertigungskosten_pro_los
    kosten_fertig = kosten_stufe1 + state.endmontagekosten_stufe_2_pro_los
    unfertige_wert = state.unfertige_erzeugnisse * kosten_stufe1
    fertige_wert = state.fertige_erzeugnisse * kosten_fertig
    uv = rohstoffe_wert + unfertige_wert + fertige_wert + state.forderungen + state.liquide_mittel

    gesamtkapital = av + uv

    # EBIT (Ergebnis vor Zinsen und Steuern)
    ebit = (
        state.umsatz
        - state.materialkosten
        - state.fertigungskosten
        - state.gemeinkosten
        - state.marketingkosten
        - state.abschreibungen_periode
    )

    # Verbindlichkeiten gesamt (kurzfristig)
    verbindlichkeiten = (
        state.verbindlichkeiten_lieferanten
        + state.sonstige_verbindlichkeiten
        + state.steuerverbindlichkeiten
    )

    # Renditenkennzahlen
    ros = (ebit / state.umsatz * 100) if state.umsatz > 0 else 0.0
    roe = (state.gewinn / state.eigenkapital * 100) if state.eigenkapital > 0 else 0.0
    gkr = (ebit / gesamtkapital * 100) if gesamtkapital > 0 else 0.0
    kapitalumschlag = (state.umsatz / gesamtkapital) if gesamtkapital > 0 else 0.0
    roi = ros * kapitalumschlag / 100

    # Working Capital
    vorraete = rohstoffe_wert + unfertige_wert + fertige_wert
    working_capital = vorraete + state.forderungen - verbindlichkeiten

    # Liquiditätsgrade
    liq1 = (state.liquide_mittel / verbindlichkeiten * 100) if verbindlichkeiten > 0 else None
    liq2 = ((state.liquide_mittel + state.forderungen) / verbindlichkeiten * 100) if verbindlichkeiten > 0 else None
    liq3 = (uv / verbindlichkeiten * 100) if verbindlichkeiten > 0 else None

    cashflow = berechne_cashflow(state.gewinn, state.abschreibungen_periode)

    return {
        "Jahr": state.jahr,
        "Quartal": state.quartal,
        "Umsatz": state.umsatz,
        "EBIT": ebit,
        "Gewinn n. St.": state.gewinn,
        "Umsatzrendite ROS (%)": round(ros, 2),
        "Eigenkapitalrendite ROE (%)": round(roe, 2),
        "Gesamtkapitalrendite (%)": round(gkr, 2),
        "Kapitalumschlag": round(kapitalumschlag, 2),
        "ROI (%)": round(roi * 100, 2),
        "Working Capital": round(working_capital, 2),
        "Liquidität I (%)": round(liq1, 1) if liq1 is not None else "–",
        "Liquidität II (%)": round(liq2, 1) if liq2 is not None else "–",
        "Liquidität III (%)": round(liq3, 1) if liq3 is not None else "–",
        "Cash Flow": round(cashflow, 2),
        "Gesamtkapital": round(gesamtkapital, 2),
        "Anlagevermögen": round(av, 2),
        "Umlaufvermögen": round(uv, 2),
        "Eigenkapital": round(state.eigenkapital, 2),
        "Fremdkapital (Darlehen)": round(state.darlehen, 2),
    }
