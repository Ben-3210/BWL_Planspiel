# Startzustand der Factory AG
# Quelle: CLAUDE.md – Unternehmensstruktur
#
# Bilanzprüfung Startzustand:
#   AV (62M) + UV (105M) = 167M = EK (67M) + FK (100M) ✓

# =========================================================
# Liquidität / Finanzierung
# =========================================================
START_LIQUIDE_MITTEL = 45.0          # Kasse + Bank
START_DARLEHEN = 100.0               # Langfristiges Darlehen
START_FORDERUNGEN = 33.0             # Offene Forderungen aus Vorquartal
START_EIGENKAPITAL = 67.0            # Gezeichnetes Kapital + Rücklagen

# =========================================================
# Vorräte (in Losen, nicht Geldwert)
# =========================================================
START_ROHMATERIAL_LAGER = 2          # 2 Lose à 3M = 6M Buchwert
START_UNFERTIGE_ERZEUGNISSE = 2      # 2 Lose (Stufe 1 abgeschlossen)
START_FERTIGE_ERZEUGNISSE = 1        # 1 Los zur Auslieferung bereit

# =========================================================
# Anlagevermögen (Buchwerte in M)
#   Summe = 10 + 20 + 30 + 2 = 62M
# =========================================================
START_AV_GRUNDSTUECKE = 10.0         # Grundstücke (keine AfA)
START_AV_GEBAEUDE = 20.0             # Gebäude (AfA 1M/Jahr → 20 Jahre)
START_AV_MASCHINEN = 30.0            # Maschinen (AfA 5M/Jahr → 6 Jahre)
START_AV_BGA = 2.0                   # Betriebs- und Geschäftsausstattung
