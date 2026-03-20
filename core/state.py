from dataclasses import dataclass, field
from typing import Dict, List

from data.config import (
    ENABLE_LOGGING,
    QUARTALE_PRO_JAHR,
    START_JAHR,
    START_QUARTAL,
    STANDARD_EINKAUFSPREIS_MATERIAL_PRO_LOS,
    STANDARD_FERTIGUNGSKOSTEN_PRO_LOS,
    STANDARD_GEMEINKOSTEN_JAHR_1_PRO_QUARTAL,
    STANDARD_ZINSSATZ,
)


@dataclass
class GameState:
    # -----------------------------
    # Zeit / Ablauf
    # -----------------------------
    jahr: int = START_JAHR
    quartal: int = START_QUARTAL
    runde: int = 1

    # -----------------------------
    # Liquidität / Finanzierung
    # -----------------------------
    liquide_mittel: float = 0.0
    darlehen: float = 0.0
    zinssatz: float = STANDARD_ZINSSATZ

    # -----------------------------
    # Umlaufvermögen
    # -----------------------------
    rohmaterial_lager: float = 0.0
    unfertige_erzeugnisse: float = 0.0
    fertige_erzeugnisse: float = 0.0
    forderungen: float = 0.0

    # -----------------------------
    # Anlagevermögen
    # -----------------------------
    maschinenwert: float = 0.0
    abschreibungen_kumuliert: float = 0.0

    # -----------------------------
    # Verbindlichkeiten
    # -----------------------------
    verbindlichkeiten_lieferanten: float = 0.0
    sonstige_verbindlichkeiten: float = 0.0

    # -----------------------------
    # Erfolgsgrößen / Periodenwerte
    # -----------------------------
    umsatz: float = 0.0
    materialkosten: float = 0.0
    fertigungskosten: float = 0.0
    gemeinkosten: float = STANDARD_GEMEINKOSTEN_JAHR_1_PRO_QUARTAL
    marketingkosten: float = 0.0
    zinskosten: float = 0.0
    abschreibungen_periode: float = 0.0
    gewinn: float = 0.0

    # -----------------------------
    # Variable Steuerungsgrößen
    # Erweiterungen für euer Projekt
    # -----------------------------
    verkaufspreis: float = 0.0
    absatzmenge_plan: int = 0
    absatzmenge_ist: int = 0
    einkaufspreis_material: float = STANDARD_EINKAUFSPREIS_MATERIAL_PRO_LOS
    fertigungskosten_pro_los: float = STANDARD_FERTIGUNGSKOSTEN_PRO_LOS
    variable_gemeinkosten: float = 0.0

    # -----------------------------
    # Sonstige Spielparameter
    # -----------------------------
    produktionsmenge: int = 0
    bestellmenge_material: int = 0
    nachfrage_index: float = 1.0
    marketing_index: float = 1.0

    # -----------------------------
    # Historie / Log
    # -----------------------------
    verlauf: List[str] = field(default_factory=list)

    # -----------------------------
    # Hilfsmethoden
    # -----------------------------
    def __post_init__(self) -> None:
        """Setzt abgeleitete Startwerte nach der Initialisierung."""
        if self.gemeinkosten == 0.0:
            self.gemeinkosten = STANDARD_GEMEINKOSTEN_JAHR_1_PRO_QUARTAL
        if self.einkaufspreis_material == 0.0:
            self.einkaufspreis_material = STANDARD_EINKAUFSPREIS_MATERIAL_PRO_LOS
        if self.fertigungskosten_pro_los == 0.0:
            self.fertigungskosten_pro_los = STANDARD_FERTIGUNGSKOSTEN_PRO_LOS
        if self.zinssatz == 0.0:
            self.zinssatz = STANDARD_ZINSSATZ

    def log(self, text: str) -> None:
        """Speichert ein Ereignis in der Verlaufsliste, falls Logging aktiviert ist."""
        if ENABLE_LOGGING:
            self.verlauf.append(text)

    def naechstes_quartal(self) -> None:
        """Springt ins nächste Quartal; nach dem letzten Quartal beginnt ein neues Jahr."""
        if self.quartal < QUARTALE_PRO_JAHR:
            self.quartal += 1
        else:
            self.quartal = 1
            self.jahr += 1

        self.runde += 1
        self.log(f"Fortschritt: Jahr {self.jahr}, Quartal {self.quartal}, Runde {self.runde}")

    def reset_periodenwerte(self) -> None:
        """Setzt Erfolgsgrößen der aktuellen Periode zurück."""
        self.umsatz = 0.0
        self.materialkosten = 0.0
        self.fertigungskosten = 0.0
        self.gemeinkosten = STANDARD_GEMEINKOSTEN_JAHR_1_PRO_QUARTAL
        self.marketingkosten = 0.0
        self.zinskosten = 0.0
        self.abschreibungen_periode = 0.0
        self.gewinn = 0.0
        self.absatzmenge_ist = 0
        self.produktionsmenge = 0
        self.bestellmenge_material = 0
        self.log("Periodenwerte wurden zurückgesetzt.")

    def to_dict(self) -> Dict[str, int | float]:
        """Gibt den aktuellen Zustand als Dictionary zurück."""
        return {
            "jahr": self.jahr,
            "quartal": self.quartal,
            "runde": self.runde,
            "liquide_mittel": self.liquide_mittel,
            "darlehen": self.darlehen,
            "zinssatz": self.zinssatz,
            "rohmaterial_lager": self.rohmaterial_lager,
            "unfertige_erzeugnisse": self.unfertige_erzeugnisse,
            "fertige_erzeugnisse": self.fertige_erzeugnisse,
            "forderungen": self.forderungen,
            "maschinenwert": self.maschinenwert,
            "abschreibungen_kumuliert": self.abschreibungen_kumuliert,
            "verbindlichkeiten_lieferanten": self.verbindlichkeiten_lieferanten,
            "sonstige_verbindlichkeiten": self.sonstige_verbindlichkeiten,
            "umsatz": self.umsatz,
            "materialkosten": self.materialkosten,
            "fertigungskosten": self.fertigungskosten,
            "gemeinkosten": self.gemeinkosten,
            "marketingkosten": self.marketingkosten,
            "zinskosten": self.zinskosten,
            "abschreibungen_periode": self.abschreibungen_periode,
            "gewinn": self.gewinn,
            "verkaufspreis": self.verkaufspreis,
            "absatzmenge_plan": self.absatzmenge_plan,
            "absatzmenge_ist": self.absatzmenge_ist,
            "einkaufspreis_material": self.einkaufspreis_material,
            "fertigungskosten_pro_los": self.fertigungskosten_pro_los,
            "variable_gemeinkosten": self.variable_gemeinkosten,
            "produktionsmenge": self.produktionsmenge,
            "bestellmenge_material": self.bestellmenge_material,
            "nachfrage_index": self.nachfrage_index,
            "marketing_index": self.marketing_index,
        }