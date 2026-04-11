from pathlib import Path

import pandas as pd
import streamlit as st

from core.actions import (
    darlehen_tilgen,
    endmontage_stufe_2,
    forderungen_einziehen,
    gemeinkosten_zahlen,
    jahresabschluss,
    marketing_ausgeben,
    material_einkaufen,
    neue_anlage_kaufen,
    produktion_neue_anlage,
    produktion_stufe_1,
    produkte_verkaufen,
)
from core.calculations import (
    berechne_gewinn,
    berechne_kennzahlen,
    berechne_nachfrage,
    berechne_nachfrage_spanne,
    berechne_zinskosten,
)
from core.state import GameState

st.set_page_config(page_title="Factory Planspiel", layout="wide")


# ─── SESSION STATE ─────────────────────────────────────────────────────────────

def get_state() -> GameState:
    if "game_state" not in st.session_state:
        st.session_state.game_state = GameState()
    return st.session_state.game_state


def reset_game() -> None:
    st.session_state.game_state = GameState()


state = get_state()


# ─── HILFSFUNKTIONEN ───────────────────────────────────────────────────────────

def run_action(action_func, *args, success_message: str | None = None, **kwargs) -> None:
    """Führt eine Aktion aus, zeigt Erfolg/Fehler und lädt die Seite neu."""
    try:
        action_func(*args, **kwargs)
        if success_message:
            st.success(success_message)
        st.rerun()
    except ValueError as e:
        st.error(str(e))


def run_action_and_advance(action_func, *args, success_message: str | None = None, **kwargs) -> None:
    """Führt eine Aktion aus und rückt automatisch zum nächsten Schritt vor."""
    try:
        action_func(*args, **kwargs)
        state.quartalsschritt += 1
        if success_message:
            st.success(success_message)
        st.rerun()
    except ValueError as e:
        st.error(str(e))


def advance_schritt() -> None:
    state.quartalsschritt += 1
    st.rerun()


def kombinierter_nachfrage_index() -> float:
    """Marketing-Index des Spielers × Quartalsereignis-Index."""
    return state.marketing_index * state.nachfrage_index


# ─── HEADER ────────────────────────────────────────────────────────────────────

st.title("🏭 Factory Planspiel")

h1, h2, h3, h4, h5 = st.columns(5)
h1.metric("Jahr", state.jahr)
h2.metric("Quartal", state.quartal)
h3.metric("Runde", state.runde)
h4.metric("Liquide Mittel", f"{state.liquide_mittel:.1f} M")
h5.metric("Eigenkapital", f"{state.eigenkapital:.1f} M")

st.divider()

# ─── EREIGNIS-BANNER ───────────────────────────────────────────────────────────

if state.aktuelles_ereignis:
    e = state.aktuelles_ereignis
    msg = f"{e['emoji']} **Quartalsereignis: {e['titel']}** — {e['beschreibung']}"
    if e["kategorie"] == "nachteil":
        st.warning(msg)
    else:
        st.success(msg)
elif state.runde > 1:
    st.info("☀️ Ruhiges Quartal – keine besonderen Ereignisse.")

st.divider()

# ─── FORTSCHRITTSANZEIGE ───────────────────────────────────────────────────────

SCHRITT_NAMEN = ["Forderungen", "Verkauf", "Produktion", "Einkauf", "Gemeinkosten", "Abschluss"]
SCHRITT_ICONS = ["💰", "🚚", "🏭", "📦", "📋", "✅"]

schritt = state.quartalsschritt

st.subheader(f"Q{state.quartal} / Jahr {state.jahr}  –  Schritt {min(schritt, 6)} von 6")
st.progress((schritt - 1) / 6)

prog_cols = st.columns(6)
for i, (col, name, icon) in enumerate(zip(prog_cols, SCHRITT_NAMEN, SCHRITT_ICONS), 1):
    if i < schritt:
        col.markdown(
            f"<div style='text-align:center; color:#28a745'>{icon}<br><small>✓ {name}</small></div>",
            unsafe_allow_html=True,
        )
    elif i == schritt:
        col.markdown(
            f"<div style='text-align:center'><b>{icon}<br>{name}</b></div>",
            unsafe_allow_html=True,
        )
    else:
        col.markdown(
            f"<div style='text-align:center; color:gray'>{icon}<br><small>{name}</small></div>",
            unsafe_allow_html=True,
        )

st.divider()

# ─── SCHRITT 1: FORDERUNGEN EINZIEHEN ─────────────────────────────────────────

if schritt == 1:
    st.markdown("## 💰 Schritt 1: Forderungen einziehen")
    st.caption("Kunden begleichen ihre offenen Rechnungen aus dem Vorquartal.")

    c1, c2 = st.columns(2)
    c1.metric("Offene Forderungen", f"{state.forderungen:.2f} M")
    c2.metric("Liquide Mittel", f"{state.liquide_mittel:.2f} M")

    if state.forderungen > 0:
        if st.button("💸 Forderungen einziehen", type="primary"):
            run_action_and_advance(
                forderungen_einziehen, state,
                success_message=f"{state.forderungen:.2f} M erfolgreich eingezogen.",
            )
    else:
        st.info("Keine offenen Forderungen vorhanden.")
        if st.button("Weiter →", type="primary"):
            advance_schritt()

    with st.expander("Optionale Aktion: Darlehen tilgen"):
        st.caption(f"Restschuld: {state.darlehen:.2f} M | Zinssatz: {state.zinssatz * 100:.0f}%")
        tilgung = st.number_input(
            "Tilgungsbetrag (M)", min_value=0.0, max_value=float(state.darlehen), step=5.0, key="s1_tilgung"
        )
        if st.button("Tilgen", disabled=tilgung <= 0):
            run_action(darlehen_tilgen, state, tilgung, success_message=f"{tilgung:.2f} M getilgt.")

elif schritt > 1:
    with st.expander("✅ Schritt 1: Forderungen einziehen"):
        st.success("Erledigt.")

# ─── SCHRITT 2: PRODUKTE VERKAUFEN ────────────────────────────────────────────

if schritt == 2:
    st.markdown("## 🚚 Schritt 2: Produkte verkaufen")
    st.caption("Preis festlegen, Marketing einsetzen und fertige Erzeugnisse anbieten. Der Markt entscheidet selbst wie viel er abnimmt.")

    idx = kombinierter_nachfrage_index()
    erwartete_nachfrage = berechne_nachfrage(state.verkaufspreis, idx)
    spanne_low, spanne_high = berechne_nachfrage_spanne(state.verkaufspreis, idx)

    # Ergebnis des letzten Verkaufs anzeigen (einmalig nach rerun)
    letztes_ergebnis = st.session_state.pop("verkauf_ergebnis", None)
    if letztes_ergebnis:
        vk = letztes_ergebnis["verkauft"]
        an = letztes_ergebnis["angebot"]
        nf = letztes_ergebnis["nachfrage"]
        if vk == 0:
            st.error(f"Kein Absatz – der Markt hatte dieses Quartal eine Nachfrage von {nf} Losen, aber Ihr Angebot kam nicht an.")
        elif vk < an:
            st.warning(
                f"Markt hat nur **{nf} Lose** nachgefragt – **{vk} von {an} Losen** verkauft. "
                f"{an - vk} Lose verbleiben im Lager."
            )
        else:
            st.success(
                f"Alle **{vk} Lose** verkauft! Markt hätte sogar **{nf} Lose** abgenommen."
                + (" Mehr Lagerbestand wäre vorteilhaft gewesen." if nf > vk else "")
            )

    m1, m2, m3 = st.columns(3)
    m1.metric("Fertige Erzeugnisse", f"{state.fertige_erzeugnisse:.0f} Lose")
    m2.metric("Erwartete Nachfrage", f"~{erwartete_nachfrage} Lose",
              help=f"Realistische Spanne (95%): {spanne_low}–{spanne_high} Lose")
    m3.metric("Aktueller Preis", f"{state.verkaufspreis:.1f} M/Los")

    st.caption(f"Marktschwankung: realistisch **{spanne_low}–{spanne_high} Lose** dieses Quartal (95%-Spanne)")

    v_col1, v_col2 = st.columns(2)

    with v_col1:
        st.write("**Preisstrategie**")
        neuer_preis = st.number_input(
            "Verkaufspreis (M)", value=float(state.verkaufspreis), min_value=1.0, step=1.0, key="s2_preis"
        )
        vorschau_erwartet = berechne_nachfrage(neuer_preis, idx)
        vorschau_low, vorschau_high = berechne_nachfrage_spanne(neuer_preis, idx)
        st.caption(
            f"Erwartete Nachfrage: **~{vorschau_erwartet} Lose** (Spanne: {vorschau_low}–{vorschau_high})  \n"
            f"Max. Umsatz (Erwartung): **{vorschau_erwartet * neuer_preis:.0f} M**"
        )
        if st.button("Preis setzen"):
            state.verkaufspreis = neuer_preis
            st.rerun()

        st.write("**Marketing (optional)**")
        marketing_betrag = st.number_input("Budget (M)", min_value=0.0, step=0.5, key="s2_marketing")
        if marketing_betrag > 0:
            idx_vorschau = (1.0 + marketing_betrag * 0.10) * state.nachfrage_index
            nf_mit_mkt = berechne_nachfrage(state.verkaufspreis, idx_vorschau)
            low_mkt, high_mkt = berechne_nachfrage_spanne(state.verkaufspreis, idx_vorschau)
            st.caption(f"Mit Marketing: **~{nf_mit_mkt} Lose** (Spanne: {low_mkt}–{high_mkt})")
        if st.button("Marketing buchen", disabled=marketing_betrag <= 0):
            run_action(
                marketing_ausgeben, state, marketing_betrag,
                success_message=f"{marketing_betrag:.1f} M Marketing gebucht.",
            )

    with v_col2:
        st.write("**Verkaufsangebot**")
        st.caption(
            "Gib an wie viele Lose du anbietest. Der Markt nimmt ab was er will – "
            "überschüssige Ware bleibt im Lager."
        )
        max_angebot = int(state.fertige_erzeugnisse)
        verkaufs_menge = st.number_input(
            "Angebot (Lose)", min_value=0.0, max_value=float(max_angebot), step=1.0, key="s2_menge"
        )
        sofortzahlung = st.checkbox("Sofortzahlung (sonst auf Ziel)", key="s2_sofort")

        if verkaufs_menge > 0:
            art = "sofort" if sofortzahlung else "als Forderung"
            umsatz_max = verkaufs_menge * state.verkaufspreis
            st.caption(f"Maximaler Umsatz bei Vollabsatz: **{umsatz_max:.1f} M** ({art})")
            if verkaufs_menge > spanne_high:
                st.warning(f"Angebot ({int(verkaufs_menge)} Lose) liegt über der erwarteten Spanne – wahrscheinlich bleibt Ware übrig.")

        if st.button("🚚 Angebot aufgeben", disabled=verkaufs_menge <= 0, type="primary"):
            try:
                produkte_verkaufen(state, verkaufs_menge, sofortzahlung=sofortzahlung)
                st.session_state.verkauf_ergebnis = {
                    "verkauft": state.letzte_verkaufte_menge,
                    "angebot": int(verkaufs_menge),
                    "nachfrage": state.letzte_tatsaechliche_nachfrage,
                }
                st.rerun()
            except ValueError as e:
                st.error(str(e))

    st.divider()
    if st.button("Schritt abschließen →", type="primary", key="s2_done"):
        advance_schritt()

elif schritt > 2:
    with st.expander("✅ Schritt 2: Produkte verkaufen"):
        st.success("Erledigt.")

# ─── SCHRITT 3: PRODUKTION ────────────────────────────────────────────────────

if schritt == 3:
    st.markdown("## 🏭 Schritt 3: Produktion")
    st.caption("Endmontage abschließen und neue Fertigungsaufträge starten.")

    if state.neue_anlage_aktiv:
        st.info("Neue einstufige Anlage aktiv – direkt Rohstoff → Fertigprodukt.")
        p1, p2, p3 = st.columns(3)
        p1.metric("Rohmaterial", f"{state.rohmaterial_lager:.0f} Lose")
        p2.metric("Fertige Erzeugnisse", f"{state.fertige_erzeugnisse:.0f} Lose")
        p3.metric("Kosten/Los", f"{state.fertigungskosten_pro_los:.2f} M")
        menge_neu = st.number_input("Produktionsmenge (Lose)", min_value=0.0, step=1.0, key="s3_neu")
        if st.button("Produktion starten", disabled=menge_neu <= 0):
            run_action(
                produktion_neue_anlage, state, menge_neu,
                success_message=f"{menge_neu:.0f} Lose produziert.",
            )
    else:
        p_col1, p_col2 = st.columns(2)

        with p_col1:
            st.write("**Endmontage (Stufe 2)**")
            st.caption(
                f"Unfertige Erzeugnisse: {state.unfertige_erzeugnisse:.0f} Lose | "
                f"Kosten: {state.endmontagekosten_stufe_2_pro_los:.2f} M/Los"
            )
            menge_s2 = st.number_input("Menge Stufe 2", min_value=0.0, step=1.0, key="s3_s2")
            if st.button("Endmontage starten", disabled=menge_s2 <= 0):
                run_action(
                    endmontage_stufe_2, state, menge_s2,
                    success_message=f"{menge_s2:.0f} Lose fertiggestellt.",
                )

        with p_col2:
            st.write("**Fertigungsstufe 1**")
            st.caption(
                f"Rohmaterial: {state.rohmaterial_lager:.0f} Lose | "
                f"Kosten: {state.fertigungskosten_pro_los:.2f} M/Los"
            )
            menge_s1 = st.number_input("Menge Stufe 1", min_value=0.0, step=1.0, key="s3_s1")
            if st.button("Stufe 1 starten", disabled=menge_s1 <= 0):
                run_action(
                    produktion_stufe_1, state, menge_s1,
                    success_message=f"{menge_s1:.0f} Lose in Stufe 1 gefertigt.",
                )

    if not state.neue_anlage_aktiv and state.jahr >= 3:
        with st.expander("Strategische Option: Neue Anlage kaufen (20M)"):
            st.markdown(
                "**Neue einstufige Anlage:** 3M/Los | Einsparung 1M/Los gegenüber alter Anlage  \n"
                "Break-Even bei 3 Losen/Quartal: ~1,7 Jahre | Zusatz-AfA: 4M/Jahr"
            )
            kann_kaufen = state.liquide_mittel >= 20.0
            if not kann_kaufen:
                st.warning(f"Nicht genug Mittel (benötigt: 20M, verfügbar: {state.liquide_mittel:.1f} M)")
            if st.button("✅ Neue Anlage kaufen (20M)", disabled=not kann_kaufen):
                run_action(neue_anlage_kaufen, state, success_message="Neue Anlage in Betrieb genommen!")

    st.divider()
    if st.button("Schritt abschließen →", type="primary", key="s3_done"):
        advance_schritt()

elif schritt > 3:
    with st.expander("✅ Schritt 3: Produktion"):
        st.success("Erledigt.")

# ─── SCHRITT 4: MATERIALEINKAUF ───────────────────────────────────────────────

if schritt == 4:
    st.markdown("## 📦 Schritt 4: Materialeinkauf")
    st.caption("Rohmaterial für die nächsten Produktionsläufe bestellen.")

    e1, e2, e3 = st.columns(3)
    e1.metric("Rohmaterial auf Lager", f"{state.rohmaterial_lager:.0f} Lose")
    e2.metric("Einkaufspreis", f"{state.einkaufspreis_material:.2f} M/Los")
    e3.metric("Liquide Mittel", f"{state.liquide_mittel:.1f} M")

    if state.aktuelles_ereignis and state.aktuelles_ereignis["effekt_feld"] == "einkaufspreis_material":
        faktor = state.aktuelles_ereignis["effekt_faktor"]
        if faktor > 1:
            st.warning(f"Ereigniseffekt aktiv: Preis ist {faktor:.0%} des Normalpreises.")
        else:
            st.success(f"Ereigniseffekt aktiv: Sonderangebot – nur {faktor:.0%} des Normalpreises!")

    einkauf_menge = st.number_input("Bestellmenge (Lose)", min_value=0.0, step=1.0, key="s4_menge")
    if einkauf_menge > 0:
        st.caption(f"Gesamtkosten: **{einkauf_menge * state.einkaufspreis_material:.1f} M**")

    b_col1, b_col2 = st.columns(2)
    with b_col1:
        if st.button("📦 Bestellen", type="primary", disabled=einkauf_menge <= 0):
            run_action_and_advance(
                material_einkaufen, state, einkauf_menge,
                success_message=f"{einkauf_menge:.0f} Lose Rohmaterial eingekauft.",
            )
    with b_col2:
        if st.button("Kein Material bestellen →"):
            advance_schritt()

elif schritt > 4:
    with st.expander("✅ Schritt 4: Materialeinkauf"):
        st.success("Erledigt.")

# ─── SCHRITT 5: GEMEINKOSTEN ZAHLEN ───────────────────────────────────────────

if schritt == 5:
    st.markdown("## 📋 Schritt 5: Gemeinkosten zahlen")
    st.caption("Laufende Betriebskosten (Miete, Verwaltung, Energie) begleichen.")

    gk_betrag = 6.0 if state.jahr == 1 else 5.0
    g1, g2 = st.columns(2)
    g1.metric("Fällige Gemeinkosten", f"{gk_betrag:.0f} M")
    g2.metric("Liquide Mittel", f"{state.liquide_mittel:.1f} M")

    if state.liquide_mittel < gk_betrag:
        st.error(f"Achtung: Nur {state.liquide_mittel:.1f} M verfügbar – nicht ausreichend!")

    if st.button("📋 Gemeinkosten zahlen", type="primary"):
        run_action_and_advance(
            gemeinkosten_zahlen, state,
            success_message=f"{gk_betrag:.0f} M Gemeinkosten bezahlt.",
        )

elif schritt > 5:
    with st.expander("✅ Schritt 5: Gemeinkosten zahlen"):
        st.success("Erledigt.")

# ─── SCHRITT 6: QUARTAL ABSCHLIESSEN ──────────────────────────────────────────

if schritt >= 6:
    st.markdown("## ✅ Schritt 6: Quartal abschließen")

    if state.quartal == 4:
        st.warning("**Q4:** Führe zuerst den Jahresabschluss durch, bevor du ins neue Jahr wechselst.")

        zinsen_vorschau = berechne_zinskosten(state.darlehen, state.zinssatz)
        afa_vorschau = min(1.0, state.av_gebaeude) + min(5.0, state.av_maschinen) + min(0.4, state.av_bga)
        if state.neue_anlage_aktiv:
            afa_vorschau += 4.0

        ja_col1, ja_col2 = st.columns(2)
        ja_col1.metric("Zinsen (fällig)", f"{zinsen_vorschau:.2f} M")
        ja_col1.metric("Abschreibungen", f"{afa_vorschau:.2f} M")

        gwv = berechne_gewinn(
            state.umsatz, state.materialkosten, state.fertigungskosten,
            state.gemeinkosten, state.marketingkosten,
            state.zinskosten + zinsen_vorschau,
            state.abschreibungen_periode + afa_vorschau,
        )
        steuern_vorschau = max(0.0, gwv / 3)
        ja_col2.metric("Gewinn vor Steuern (Vorschau)", f"{gwv:.2f} M")
        ja_col2.metric("Steuern (Vorschau, 1/3)", f"{steuern_vorschau:.2f} M")

        if not state.jahresabschluss_durchgefuehrt:
            if st.button("📋 Jahresabschluss durchführen", type="primary"):
                run_action(
                    jahresabschluss, state,
                    success_message=f"Jahresabschluss Jahr {state.jahr} erfolgreich abgeschlossen.",
                )
        else:
            st.success(f"Jahresabschluss Jahr {state.jahr} abgeschlossen.")

    kann_weiter = state.quartal != 4 or state.jahresabschluss_durchgefuehrt

    if st.button("▶ Nächstes Quartal", type="primary", disabled=not kann_weiter):
        run_action(state.naechstes_quartal)

# ─── SPIELFELD-BILD ────────────────────────────────────────────────────────────

image_path = Path(__file__).parent / "assets" / "factory_board.jpeg"
if image_path.exists():
    with st.expander("🗺️ Spielfeld anzeigen"):
        st.image(str(image_path), use_container_width=True)

st.divider()

# ─── KENNZAHLEN & CHARTS ───────────────────────────────────────────────────────

if state.kennzahlen_history:
    with st.expander("📊 Kennzahlen & Verlauf"):
        df = pd.DataFrame(state.kennzahlen_history)
        tab1, tab2 = st.tabs(["Tabelle", "Charts"])

        with tab1:
            anzeige_cols = [
                "Jahr", "Umsatz", "EBIT", "Gewinn n. St.",
                "Umsatzrendite ROS (%)", "Eigenkapitalrendite ROE (%)",
                "ROI (%)", "Working Capital", "Cash Flow",
                "Eigenkapital", "Fremdkapital (Darlehen)", "Gesamtkapital",
            ]
            vorhandene_cols = [c for c in anzeige_cols if c in df.columns]
            st.dataframe(df[vorhandene_cols].set_index("Jahr"), use_container_width=True)

        with tab2:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Umsatz & Gewinn (M)**")
                if "Umsatz" in df.columns:
                    st.line_chart(df.set_index("Jahr")[["Umsatz", "EBIT", "Gewinn n. St."]])
            with c2:
                st.markdown("**Kapitalstruktur (M)**")
                if "Eigenkapital" in df.columns:
                    st.line_chart(df.set_index("Jahr")[["Eigenkapital", "Gesamtkapital", "Fremdkapital (Darlehen)"]])

with st.expander("🔢 Aktuelle Kennzahlen"):
    kz = berechne_kennzahlen(state)
    kz1, kz2, kz3 = st.columns(3)
    kz1.metric("Umsatzrendite ROS", f"{kz['Umsatzrendite ROS (%)']:.1f} %")
    kz1.metric("Eigenkapitalrendite ROE", f"{kz['Eigenkapitalrendite ROE (%)']:.1f} %")
    kz1.metric("ROI", f"{kz['ROI (%)']:.1f} %")
    kz2.metric("Anlagevermögen", f"{kz['Anlagevermögen']:.1f} M")
    kz2.metric("Umlaufvermögen", f"{kz['Umlaufvermögen']:.1f} M")
    kz2.metric("Gesamtkapital", f"{kz['Gesamtkapital']:.1f} M")
    kz3.metric("Working Capital", f"{kz['Working Capital']:.1f} M")
    kz3.metric("Cash Flow", f"{kz['Cash Flow']:.1f} M")
    kz3.metric("EBIT", f"{kz['EBIT']:.1f} M")

# ─── VERLAUF ───────────────────────────────────────────────────────────────────

if state.verlauf:
    with st.expander("🗒️ Verlauf"):
        for eintrag in reversed(state.verlauf):
            st.write(f"- {eintrag}")

# ─── SPIELSTEUERUNG ────────────────────────────────────────────────────────────

st.divider()
if st.button("↺ Spiel zurücksetzen"):
    reset_game()
    st.rerun()
