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
    materialkosten = berechne_materialkosten(menge, materialpreis_pro_los)
    fertigungskosten = berechne_fertigungskosten(menge, fertigungskosten_pro_los)
    return materialkosten + fertigungskosten


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
    """Berechnet den Periodengewinn nach allen Kostenarten."""
    return (
        umsatz
        - materialkosten
        - fertigungskosten
        - gemeinkosten
        - marketingkosten
        - zinskosten
        - abschreibungen
    )


def berechne_cashflow(
    gewinn: float,
    abschreibungen: float,
) -> float:
    """Berechnet einen einfachen Cashflow aus Gewinn und Abschreibungen."""
    return gewinn + abschreibungen
