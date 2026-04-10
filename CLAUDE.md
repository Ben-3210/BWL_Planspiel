# BWL Planspiel Factory – Projektkontext für Claude Code

## Projektübersicht
Digitale Umsetzung des Planspiels "Factory" (BTI Business Training International) 
als interaktive Streamlit-App. Universitätsprojekt an der Ostfalia Hochschule, 
Fakultät Maschinenbau, SoSe 2026.

## Aufgabenstellung
Das klassische Factory-Planspiel soll digital erweitert werden mit:
- Variablen Verkaufspreisen / Absatzmengen (inkl. Marketing-Ausgaben)
- Variablen Fertigungskosten (wie Runde 3: neue Fertigungsanlage)
- Variablen Einkaufspreisen
- Variablen Gemeinkosten
- IT-Unterstützung zur Berechnung und Verfolgung aller Werte

## Das Original-Planspiel – Spiellogik

### Unternehmensstruktur: Factory AG
- Rechtsform: Aktiengesellschaft
- Startzustand: Anlagevermögen 62M, Umlaufvermögen 105M, Eigenkapital 67M, Fremdkapital 100M
- Zinssatz: 10% auf Darlehen
- Steuerquote: 1/3 des Gewinns vor Steuern

### Produktionsprozess (ursprünglich 2-stufig)
- Fertigungsstufe 1: Vorfertigung, Kosten 3M pro Los
- Fertigungsstufe 2 (Endmontage): Kosten 1M pro Los
- Materialeinkauf: 3M pro Los (2 Lose pro Quartal)
- Ab Jahr 3: neue einstufige Anlage möglich (20M Investition, 3M/Los, 3 Lose/Quartal)

### Quartalsablauf (Checkliste A)
1. Kunden zahlen (Forderungen → Kasse)
2. Fertige Produkte ausliefern (gemäß Auftrag)
3. Rechnung stellen (Erlös → Forderungen)
4. Endmontage Stufe 2 durchführen + bezahlen
5. Neue Produktionsaufträge Stufe 1 starten + bezahlen
6. Rohmaterial annehmen + bezahlen
7. Rohmaterial für nächstes Quartal bestellen
8. Gemeinkosten bezahlen (6M/Quartal Jahr 1, 5M/Quartal ab Jahr 2)

### Jahresabschluss (Checkliste B)
- Zinsen zahlen (10% auf Kreditvolumen)
- Abschreibungen buchen: Gebäude 1M/Jahr, Maschinen 5M/Jahr, BGA variabel
- Steuerverbindlichkeiten buchen
- GuV und Bilanz erstellen

### Kennzahlen die berechnet werden
- Umsatzrendite (ROS) = EBIT * 100 / Umsatz
- Eigenkapitalrendite (ROE) = Gewinn * 100 / Eigenkapital
- Gesamtkapitalrendite = EBIT * 100 / Gesamtkapital
- Kapitalumschlagshäufigkeit = Umsatz / Gesamtkapital
- ROI = ROS * Kapitalumschlagshäufigkeit
- Working Capital = Vorräte + Forderungen - Verbindlichkeiten L&L
- Liquiditätsgrad I/II/III
- Cash Flow / Kapitalflussrechnung

### Referenzwerte aus dem Original (3 Jahre)
| Kennzahl         | Jahr 0 | Jahr 1 | Jahr 2 | Jahr 3 |
|-----------------|--------|--------|--------|--------|
| Umsatz          | 99M    | 99M    | 109M   | 109M   |
| EBIT            | 10M    | 10M    | 13M    | 15M    |
| Gewinn n. St.   | 0M     | 0M     | 2M     | 6M     |
| Gesamtkapital   | 167M   | 167M   | 170M   | 138M   |
| Eigenkapital    | 67M    | 67M    | 69M    | 75M    |

## Technische Architektur

### Stack
- Python 3.x
- Streamlit als UI-Framework
- Zentrales GameState-Objekt im Session State
- Modulare Struktur: core/actions

### GameState (zentrale Datenstruktur)
```python
{
  # Finanzen
  "liquide_mittel": float,
  "darlehen": float,
  "forderungen": float,
  "umsatz": float,
  "gewinn": float,
  
  # Kosten
  "kosten_material": float,
  "kosten_fertigung": float,
  "kosten_gemeinkosten": float,
  "abschreibungen": float,
  "zinsen": float,
  
  # Lager
  "lager_rohmaterial": int,      # Anzahl Lose
  "lager_unfertig": int,         # Anzahl Lose
  "lager_fertig": int,           # Anzahl Lose
  
  # Preise (variabel – Kernfeature)
  "verkaufspreis": float,
  "einkaufspreis": float,        # pro Los
  "fertigungskosten_stufe1": float,
  "fertigungskosten_stufe2": float,
  "gemeinkosten_pro_quartal": float,
  
  # Anlagevermögen
  "av_grundstuecke": float,
  "av_gebaeude": float,
  "av_maschinen": float,
  "av_bga": float,
  
  # Periodenlogik
  "jahr": int,                   # 1-3
  "quartal": int,                # 1-4
  "runde": int,
  
  # Flags
  "jit_aktiv": bool,
  "neue_anlage_aktiv": bool,
}
```

### Aktionen (core/actions)
- `material_einkaufen(state, menge)`
- `produktion_stufe_1(state, menge)`
- `endmontage_stufe_2(state, menge)`
- `produkte_verkaufen(state, menge, preis)`
- `jahresabschluss(state)`
- `darlehen_tilgen(state, betrag)`
- `gemeinkosten_zahlen(state)`

## Geplante Erweiterungen (Aufgabenstellung)
1. Variable Verkaufspreise mit Nachfragekurve (Preis → Absatzmenge)
2. Marketing-Ausgaben beeinflussen Nachfrage
3. Variable Einkaufspreise (Mengenrabatte, Lieferantenwahl)
4. Variable Gemeinkosten (Prozessoptimierung)
5. Variable Fertigungskosten (alte vs. neue Anlage)
6. Diagramme: Gewinnverlauf, Kennzahlenentwicklung über Jahre
7. Klickbare Hotspots im Spielfeld
8. Dashboard-Ansicht

## Coding-Prinzipien
- Sauber, modular, erweiterbar
- Keine Duplikate
- Klare Struktur und Verständlichkeit
- Streamlit Best Practices
- Deutsche Variablennamen (passend zum BWL-Kontext)