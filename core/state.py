from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class GameState:
    # -----------------------------
    # Zeit / Ablauf
    # -----------------------------
    jahr: int = 1
    quartal: int = 1
    runde: int = 1

    # -----------------------------
    # Liquidität / Finanzierung
    # -----------------------------
    liquide_mittel: float = 0.0
    darlehen: float = 0.0
    zinssatz: float = 0.0

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
    gemeinkosten: float = 0.0
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
    einkaufspreis_material: float = 0.0
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
    def log(self, text: str) -> None:
        """Speichert ein Ereignis in der Verlaufsliste."""
        self.verlauf.append(text)

    def naechstes_quartal(self) -> None:
        """Springt ins nächste Quartal; nach Q4 beginnt ein neues Jahr."""
        if self.quartal < 4:
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
        self.gemeinkosten = 0.0
        self.marketingkosten = 0.0
        self.zinskosten = 0.0
        self.abschreibungen_periode = 0.0
        self.gewinn = 0.0
        self.absatzmenge_ist = 0
        self.produktionsmenge = 0
        self.bestellmenge_material = 0
        self.log("Periodenwerte wurden zurückgesetzt.")

    def to_dict(self) -> Dict[str, float]:
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
            "variable_gemeinkosten": self.variable_gemeinkosten,
            "produktionsmenge": self.produktionsmenge,
            "bestellmenge_material": self.bestellmenge_material,
            "nachfrage_index": self.nachfrage_index,
            "marketing_index": self.marketing_index,
        }