from dataclasses import dataclass, field
from typing import Dict, List

from data.config import (
    ENABLE_LOGGING,
    QUARTALE_PRO_JAHR,
    START_JAHR,
    START_QUARTAL,
    STANDARD_EINKAUFSPREIS_MATERIAL_PRO_LOS,
    STANDARD_ENDMONTAGEKOSTEN_STUFE_2_PRO_LOS,
    STANDARD_FERTIGUNGSKOSTEN_STUFE_1_PRO_LOS,
    STANDARD_GEMEINKOSTEN_JAHR_1_PRO_QUARTAL,
    STANDARD_ZINSSATZ,
)
from data.defaults import (
    START_AV_BGA,
    START_AV_GEBAEUDE,
    START_AV_GRUNDSTUECKE,
    START_AV_MASCHINEN,
    START_DARLEHEN,
    START_EIGENKAPITAL,
    START_FERTIGE_ERZEUGNISSE,
    START_FORDERUNGEN,
    START_LIQUIDE_MITTEL,
    START_ROHMATERIAL_LAGER,
    START_UNFERTIGE_ERZEUGNISSE,
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
    liquide_mittel: float = START_LIQUIDE_MITTEL
    darlehen: float = START_DARLEHEN
    zinssatz: float = STANDARD_ZINSSATZ

    # -----------------------------
    # Umlaufvermögen
    # -----------------------------
    rohmaterial_lager: float = START_ROHMATERIAL_LAGER
    unfertige_erzeugnisse: float = START_UNFERTIGE_ERZEUGNISSE
    fertige_erzeugnisse: float = START_FERTIGE_ERZEUGNISSE
    forderungen: float = START_FORDERUNGEN

    # -----------------------------
    # Anlagevermögen
    # -----------------------------
    av_grundstuecke: float = START_AV_GRUNDSTUECKE
    av_gebaeude: float = START_AV_GEBAEUDE
    av_maschinen: float = START_AV_MASCHINEN
    av_bga: float = START_AV_BGA
    abschreibungen_kumuliert: float = 0.0

    # -----------------------------
    # Eigenkapital / Verbindlichkeiten
    # -----------------------------
    eigenkapital: float = START_EIGENKAPITAL
    verbindlichkeiten_lieferanten: float = 0.0
    sonstige_verbindlichkeiten: float = 0.0
    steuerverbindlichkeiten: float = 0.0

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
    # -----------------------------
    verkaufspreis: float = 11.0
    absatzmenge_plan: int = 0
    absatzmenge_ist: int = 0
    einkaufspreis_material: float = STANDARD_EINKAUFSPREIS_MATERIAL_PRO_LOS
    fertigungskosten_pro_los: float = STANDARD_FERTIGUNGSKOSTEN_STUFE_1_PRO_LOS
    endmontagekosten_stufe_2_pro_los: float = STANDARD_ENDMONTAGEKOSTEN_STUFE_2_PRO_LOS
    variable_gemeinkosten: float = 0.0

    # -----------------------------
    # Sonstige Spielparameter
    # -----------------------------
    produktionsmenge: int = 0
    bestellmenge_material: int = 0
    nachfrage_index: float = 1.0
    marketing_index: float = 1.0
    neue_anlage_aktiv: bool = False

    # -----------------------------
    # Quartalsschritte (geführter Modus)
    # -----------------------------
    quartalsschritt: int = 1                              # 1–6: aktueller Schritt im Quartal
    jahresabschluss_durchgefuehrt: bool = False

    # -----------------------------
    # Letztes Verkaufsergebnis (für UI-Feedback)
    # -----------------------------
    letzte_tatsaechliche_nachfrage: int = 0
    letzte_verkaufte_menge: int = 0

    # -----------------------------
    # Quartalsereignisse
    # -----------------------------
    aktuelles_ereignis: dict | None = None
    ereignis_original_werte: dict = field(default_factory=dict)

    # -----------------------------
    # Kennzahlen-Verlauf (für Charts)
    # -----------------------------
    kennzahlen_history: List[Dict] = field(default_factory=list)

    # -----------------------------
    # Historie / Log
    # -----------------------------
    verlauf: List[str] = field(default_factory=list)

    # -----------------------------
    # Hilfsmethoden
    # -----------------------------
    def __post_init__(self) -> None:
        """Setzt abgeleitete Startwerte nach der Initialisierung."""
        if self.einkaufspreis_material == 0.0:
            self.einkaufspreis_material = STANDARD_EINKAUFSPREIS_MATERIAL_PRO_LOS
        if self.fertigungskosten_pro_los == 0.0:
            self.fertigungskosten_pro_los = STANDARD_FERTIGUNGSKOSTEN_STUFE_1_PRO_LOS
        if self.endmontagekosten_stufe_2_pro_los == 0.0:
            self.endmontagekosten_stufe_2_pro_los = STANDARD_ENDMONTAGEKOSTEN_STUFE_2_PRO_LOS
        if self.zinssatz == 0.0:
            self.zinssatz = STANDARD_ZINSSATZ

    def log(self, text: str) -> None:
        """Speichert ein Ereignis in der Verlaufsliste, falls Logging aktiviert ist."""
        if ENABLE_LOGGING:
            self.verlauf.append(text)

    def naechstes_quartal(self) -> None:
        """Springt ins nächste Quartal, würfelt ein neues Ereignis und setzt Schritte zurück."""
        from core.events import setze_ereignis_zurueck, wuerfle_ereignis, wende_ereignis_an

        # Laufendes Ereignis zurücksetzen (Originalwerte wiederherstellen)
        setze_ereignis_zurueck(self)

        # Zeit weiterzählen
        if self.quartal < QUARTALE_PRO_JAHR:
            self.quartal += 1
        else:
            self.quartal = 1
            self.jahr += 1

        self.runde += 1

        # Marketing- und Schrittstate zurücksetzen
        self.marketing_index = 1.0
        self.quartalsschritt = 1
        self.jahresabschluss_durchgefuehrt = False

        # Neues Quartalsereignis würfeln und anwenden
        neues_ereignis = wuerfle_ereignis()
        if neues_ereignis:
            self.aktuelles_ereignis = neues_ereignis
            wende_ereignis_an(self, neues_ereignis)

        self.log(f"Fortschritt: Jahr {self.jahr}, Quartal {self.quartal}, Runde {self.runde}")

    def reset_periodenwerte(self) -> None:
        """Setzt Erfolgsgrößen für die neue Jahresperiode zurück."""
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

    def to_dict(self) -> Dict[str, int | float | bool]:
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
            "av_grundstuecke": self.av_grundstuecke,
            "av_gebaeude": self.av_gebaeude,
            "av_maschinen": self.av_maschinen,
            "av_bga": self.av_bga,
            "abschreibungen_kumuliert": self.abschreibungen_kumuliert,
            "eigenkapital": self.eigenkapital,
            "verbindlichkeiten_lieferanten": self.verbindlichkeiten_lieferanten,
            "sonstige_verbindlichkeiten": self.sonstige_verbindlichkeiten,
            "steuerverbindlichkeiten": self.steuerverbindlichkeiten,
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
            "endmontagekosten_stufe_2_pro_los": self.endmontagekosten_stufe_2_pro_los,
            "variable_gemeinkosten": self.variable_gemeinkosten,
            "produktionsmenge": self.produktionsmenge,
            "bestellmenge_material": self.bestellmenge_material,
            "nachfrage_index": self.nachfrage_index,
            "marketing_index": self.marketing_index,
            "neue_anlage_aktiv": self.neue_anlage_aktiv,
        }
