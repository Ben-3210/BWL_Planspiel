"""
Zentrale Konfiguration für das digitale Planspiel.

Hier stehen nur:
- feste Rahmenbedingungen
- Basiswerte
- Grenzwerte
- Feature-Schalter

Hier stehen NICHT:
- aktueller Spielstand
- laufende Quartalswerte
- konkrete Aktionen
- Berechnungslogik
"""

# =========================================================
# 1) Allgemeine Spielstruktur
# =========================================================

QUARTALE_PRO_JAHR = 4
SPIELDAUER_JAHRE = 5
START_JAHR = 1
START_QUARTAL = 1

# =========================================================
# 2) Basiswerte des Planspiels
# =========================================================

# Finanzierung
STANDARD_ZINSSATZ = 0.10

# Material / Produktion
STANDARD_EINKAUFSPREIS_MATERIAL_PRO_LOS = 3.0
STANDARD_FERTIGUNGSKOSTEN_STUFE_1_PRO_LOS = 3.0
STANDARD_ENDMONTAGEKOSTEN_STUFE_2_PRO_LOS = 1.0

# Gemeinkosten
STANDARD_GEMEINKOSTEN_JAHR_1_PRO_QUARTAL = 6.0
STANDARD_GEMEINKOSTEN_AB_JAHR_2_PRO_QUARTAL = 5.0

# Erweiterungen / spätere Ausbaustufen
STANDARD_MARKETINGKOSTEN = 1.0
STANDARD_INVESTITION_NEUE_ANLAGE = 20.0
STANDARD_KAPAZITAET_NEUE_ANLAGE_PRO_QUARTAL = 3

# =========================================================
# 3) Grenzen für variable Parameter
# =========================================================

# Verkauf
MIN_VERKAUFSPREIS = 0.0
MAX_VERKAUFSPREIS = 100.0

# Absatz / Einkauf / Produktion
MIN_ABSATZMENGE = 0
MAX_ABSATZMENGE = 10

MIN_BESTELLMENGE_MATERIAL = 0
MAX_BESTELLMENGE_MATERIAL = 10

MIN_PRODUKTIONSMENGE = 0
MAX_PRODUKTIONSMENGE = 10

# Einkaufspreise
MIN_EINKAUFSPREIS_MATERIAL = 1.0
MAX_EINKAUFSPREIS_MATERIAL = 10.0

# Fertigungskosten
MIN_FERTIGUNGSKOSTEN_PRO_LOS = 1.0
MAX_FERTIGUNGSKOSTEN_PRO_LOS = 10.0

# Gemeinkosten
MIN_GEMEINKOSTEN_PRO_QUARTAL = 0.0
MAX_GEMEINKOSTEN_PRO_QUARTAL = 20.0

# =========================================================
# 4) Lager- und Finanzgrenzen
# =========================================================

MIN_BESTAND = 0

MAX_ROHMATERIAL_LAGER = 20
MAX_UNFERTIGE_ERZEUGNISSE = 20
MAX_FERTIGE_ERZEUGNISSE = 20

MIN_LIQUIDE_MITTEL = 0.0
MIN_DARLEHEN = 0.0
MAX_DARLEHEN = 1000.0

MIN_ZINSSATZ = 0.0
MAX_ZINSSATZ = 1.0

NEGATIVE_BESTAENDE_ERLAUBT = False
NEGATIVE_LIQUIDITAET_ERLAUBT = False

# =========================================================
# 5) Feature-Schalter für eure Erweiterung
# =========================================================

FEATURE_VARIABLE_VERKAUFSPREISE = True
FEATURE_VARIABLE_ABSATZMENGEN = True
FEATURE_MARKETING_EINFLUSS = True
FEATURE_VARIABLE_FERTIGUNGSKOSTEN = True
FEATURE_VARIABLE_EINKAUFSPREISE = True
FEATURE_VARIABLE_GEMEINKOSTEN = True

# =========================================================
# 6) Einflussfaktoren / Modellparameter
# =========================================================

# Diese Werte sind bewusst Modellannahmen für eure digitale Erweiterung.
MARKETING_NACHFRAGE_FAKTOR = 0.10

# Einkaufspreis Rohmaterial (normalverteilt)
EINKAUFSPREIS_ERWARTUNGSWERT = 3.0
EINKAUFSPREIS_STANDARDABWEICHUNG = 0.4   # ± ~13% Schwankung
EINKAUFSPREIS_MIN = 1.0                  # Untergrenze
MARKETING_PREIS_FAKTOR = 0.05

# =========================================================
# 7) Technische Hilfswerte
# =========================================================

GELD_RUNDUNG = 2
DEFAULT_WAEHRUNG = "M"
ENABLE_LOGGING = True

# =========================================================
# 8) Nachfragekurve
# =========================================================

# Isoelastische Nachfragefunktion: Nachfrage = BASIS * (BASIS_PREIS / Preis)^ELASTIZITAET
# Bei Basispreis 11M → 3 Lose/Quartal ≈ 99M/Jahr (passt zu den Referenzwerten)
BASISPREIS = 11.0
BASISNACHFRAGE_PRO_QUARTAL = 3
PREISELASTIZITAET = 1.2              # > 1 = elastisch (realistisch für Industrieprodukte)

# Marktschwankung: Standardabweichung als Anteil der erwarteten Nachfrage
# 0.30 → ±30% Schwankung (68%-Konfidenzintervall)
NACHFRAGE_STANDARDABWEICHUNG = 0.30

# =========================================================
# 9) Abschreibungen (AfA)
# =========================================================

AFA_GEBAEUDE_PRO_JAHR = 1.0          # Nutzungsdauer 20 Jahre
AFA_MASCHINEN_PRO_JAHR = 5.0         # Nutzungsdauer 6 Jahre
AFA_NEUE_ANLAGE_PRO_JAHR = 4.0       # 20M Investition über 5 Jahre
AFA_BGA_PRO_JAHR = 0.4               # 2M Startwert über 5 Jahre

# =========================================================
# 10) Jahresabschluss
# =========================================================

STEUERSATZ = 1 / 3                   # 1/3 des Gewinns vor Steuern
