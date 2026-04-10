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
from core.calculations import berechne_kennzahlen, berechne_nachfrage
from core.state import GameState

st.set_page_config(page_title="Factory Planspiel", layout="wide")


# -----------------------------
# SESSION STATE
# -----------------------------

def get_state() -> GameState:
    if "game_state" not in st.session_state:
        st.session_state.game_state = GameState()
    return st.session_state.game_state


def reset_game() -> None:
    st.session_state.game_state = GameState()
    if "active_panel" in st.session_state:
        del st.session_state.active_panel


def run_action(action_func, *args, success_message: str | None = None, **kwargs) -> None:
    """Führt eine Aktion aus, zeigt Erfolg/Fehler an und startet die Seite neu."""
    try:
        action_func(*args, **kwargs)
        if success_message:
            st.success(success_message)
        st.rerun()
    except ValueError as e:
        st.error(str(e))


state = get_state()

# -----------------------------
# TITEL & HEADER
# -----------------------------

st.title("Factory Planspiel")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Jahr", state.jahr)
col2.metric("Quartal", state.quartal)
col3.metric("Runde", state.runde)
col4.metric("Liquide Mittel", f"{state.liquide_mittel:.1f} M")
col5.metric("Eigenkapital", f"{state.eigenkapital:.1f} M")

st.divider()

# -----------------------------
# SPIELFELD
# -----------------------------

left_panel, center_panel, right_panel = st.columns([0.5, 4, 0.5])

with center_panel:
    st.subheader("Spielfeld")

    from pathlib import Path
    image_path = Path(__file__).parent / "assets" / "factory_board.jpeg"
    if image_path.exists():
        st.image(str(image_path), use_container_width=True)

    # Panel-Buttons
    btn_cols = st.columns(5)
    with btn_cols[0]:
        if st.button("🏭 Produktion", use_container_width=True):
            st.session_state.active_panel = "produktion"
    with btn_cols[1]:
        if st.button("📦 Lager", use_container_width=True):
            st.session_state.active_panel = "lager"
    with btn_cols[2]:
        if st.button("🚚 Vertrieb", use_container_width=True):
            st.session_state.active_panel = "vertrieb"
    with btn_cols[3]:
        if st.button("💰 Finanzen", use_container_width=True):
            st.session_state.active_panel = "finanzen"
    with btn_cols[4]:
        label = "🏗️ Neue Anlage ✓" if state.neue_anlage_aktiv else "🏗️ Neue Anlage"
        if st.button(label, use_container_width=True):
            st.session_state.active_panel = "neue_anlage"

    # ------------------------------------------
    # PANELS
    # ------------------------------------------

    if "active_panel" in st.session_state:
        st.divider()

        # ==========================================
        # PANEL: FINANZEN
        # ==========================================
        if st.session_state.active_panel == "finanzen":
            st.markdown("## 💰 Finanzen")

            fin_col1, fin_col2, fin_col3, fin_col4 = st.columns(4)
            fin_col1.metric("Liquide Mittel", f"{state.liquide_mittel:.2f} M")
            fin_col2.metric("Forderungen", f"{state.forderungen:.2f} M")
            fin_col3.metric("Darlehen", f"{state.darlehen:.2f} M")
            fin_col4.metric("Eigenkapital", f"{state.eigenkapital:.2f} M")

            st.markdown("### Periodenübersicht")
            p_col1, p_col2, p_col3 = st.columns(3)
            p_col1.metric("Umsatz", f"{state.umsatz:.2f} M")
            p_col2.metric("Materialkosten", f"{state.materialkosten:.2f} M")
            p_col3.metric("Fertigungskosten", f"{state.fertigungskosten:.2f} M")

            p_col4, p_col5, p_col6 = st.columns(3)
            p_col4.metric("Gemeinkosten", f"{state.gemeinkosten:.2f} M")
            p_col5.metric("Marketingkosten", f"{state.marketingkosten:.2f} M")
            p_col6.metric("Zinskosten", f"{state.zinskosten:.2f} M")

            st.markdown("### Aktionen")
            act_col1, act_col2 = st.columns(2)

            with act_col1:
                st.write("**Forderungen einziehen**")
                st.caption(f"Offen: {state.forderungen:.2f} M")
                if st.button("Forderungen einziehen", disabled=state.forderungen <= 0):
                    run_action(forderungen_einziehen, state,
                               success_message=f"{state.forderungen:.2f} M eingezogen.")

                st.write("**Gemeinkosten zahlen**")
                gk_betrag = 6.0 if state.jahr == 1 else 5.0
                st.caption(f"Fällig: {gk_betrag:.0f} M/Quartal")
                if st.button("Gemeinkosten zahlen"):
                    run_action(gemeinkosten_zahlen, state,
                               success_message=f"{gk_betrag:.0f} M Gemeinkosten gezahlt.")

            with act_col2:
                st.write("**Darlehen tilgen**")
                st.caption(f"Restdarlehen: {state.darlehen:.2f} M (Zinssatz {state.zinssatz*100:.0f}%)")
                tilgung = st.number_input("Tilgungsbetrag (M)", min_value=0.0,
                                          max_value=float(state.darlehen), step=5.0, key="tilgung")
                if st.button("Tilgen"):
                    run_action(darlehen_tilgen, state, tilgung,
                               success_message=f"{tilgung:.2f} M getilgt.")

        # ==========================================
        # PANEL: PRODUKTION
        # ==========================================
        elif st.session_state.active_panel == "produktion":
            st.markdown("## 🏭 Produktion")

            if state.neue_anlage_aktiv:
                st.info("Neue einstufige Anlage aktiv – Rohstoff wird direkt zu Fertigprodukt verarbeitet.")
                st.write("### Produktion (neue Anlage, einstufig)")
                st.caption(f"Rohmaterial: {state.rohmaterial_lager:.0f} Lose | "
                           f"Fertige Erzeugnisse: {state.fertige_erzeugnisse:.0f} Lose | "
                           f"Kosten: {state.fertigungskosten_pro_los:.1f} M/Los")
                menge_neu = st.number_input("Menge (Lose)", min_value=0.0, step=1.0, key="prod_neu")
                if st.button("Produktion starten"):
                    run_action(produktion_neue_anlage, state, menge_neu,
                               success_message=f"{menge_neu:.0f} Lose produziert (neue Anlage).")
            else:
                prod_col1, prod_col2 = st.columns(2)

                with prod_col1:
                    st.write("### Fertigungsstufe 1")
                    st.caption(f"Rohmaterial: {state.rohmaterial_lager:.0f} Lose | "
                               f"Kosten: {state.fertigungskosten_pro_los:.1f} M/Los")
                    menge_stufe_1 = st.number_input(
                        "Menge Stufe 1", min_value=0.0, step=1.0, key="prod1"
                    )
                    if st.button("Produktion Stufe 1 starten"):
                        run_action(produktion_stufe_1, state, menge_stufe_1,
                                   success_message=f"{menge_stufe_1:.0f} Lose in Stufe 1 gefertigt.")

                with prod_col2:
                    st.write("### Endmontage (Stufe 2)")
                    st.caption(f"Unfertige Erzeugnisse: {state.unfertige_erzeugnisse:.0f} Lose | "
                               f"Kosten: {state.endmontagekosten_stufe_2_pro_los:.1f} M/Los")
                    menge_stufe_2 = st.number_input(
                        "Menge Stufe 2", min_value=0.0, step=1.0, key="prod2"
                    )
                    if st.button("Endmontage starten"):
                        run_action(endmontage_stufe_2, state, menge_stufe_2,
                                   success_message=f"{menge_stufe_2:.0f} Lose in Stufe 2 fertiggestellt.")

        # ==========================================
        # PANEL: VERTRIEB
        # ==========================================
        elif st.session_state.active_panel == "vertrieb":
            st.markdown("## 🚚 Vertrieb")

            nachfrage = berechne_nachfrage(state.verkaufspreis, state.marketing_index)
            vert_col1, vert_col2 = st.columns(2)

            with vert_col1:
                st.write("### Verkauf")
                v_col_a, v_col_b, v_col_c = st.columns(3)
                v_col_a.metric("Fertige Erzeugnisse", f"{state.fertige_erzeugnisse:.0f} Lose")
                v_col_b.metric("Marktnachfrage", f"{nachfrage} Lose")
                v_col_c.metric("Marketing-Index", f"{state.marketing_index:.2f}")

                verkaufs_menge = st.number_input(
                    "Menge verkaufen", min_value=0.0, max_value=float(nachfrage),
                    step=1.0, key="vertrieb_menge"
                )
                sofortzahlung = st.checkbox("Sofortzahlung (sonst: auf Ziel)", key="vertrieb_sofort")

                if st.button("Verkauf starten"):
                    zahlungsart = "Sofortzahlung" if sofortzahlung else "auf Ziel"
                    run_action(produkte_verkaufen, state, verkaufs_menge,
                               sofortzahlung=sofortzahlung,
                               success_message=f"{verkaufs_menge:.0f} Lose verkauft ({zahlungsart}).")

            with vert_col2:
                st.write("### Preisstrategie")
                neuer_preis = st.number_input(
                    "Verkaufspreis (M)", value=float(state.verkaufspreis),
                    min_value=1.0, step=1.0, key="vertrieb_preis"
                )
                vorschau_nachfrage = berechne_nachfrage(neuer_preis, state.marketing_index)
                st.caption(f"Erwartete Nachfrage bei {neuer_preis:.0f} M: **{vorschau_nachfrage} Lose/Quartal**")
                vorschau_umsatz = vorschau_nachfrage * neuer_preis
                st.caption(f"Maximaler Quartalsumsatz: **{vorschau_umsatz:.0f} M**")

                if st.button("Preis setzen"):
                    state.verkaufspreis = neuer_preis
                    st.success(f"Verkaufspreis auf {neuer_preis:.2f} M gesetzt.")
                    st.rerun()

                st.write("### Marketing")
                st.caption(f"Nachfrage steigt um 10% pro investierter Million.")
                marketing_betrag = st.number_input(
                    "Marketing-Budget (M)", min_value=0.0, step=0.5, key="marketing_budget"
                )
                vorschau_marketing_index = 1.0 + marketing_betrag * 0.10
                vorschau_nachfrage_marketing = berechne_nachfrage(state.verkaufspreis, vorschau_marketing_index)
                st.caption(f"Nachfrage nach Marketing: **{vorschau_nachfrage_marketing} Lose**")
                if st.button("Marketing buchen"):
                    run_action(marketing_ausgeben, state, marketing_betrag,
                               success_message=f"{marketing_betrag:.1f} M Marketing gebucht.")

        # ==========================================
        # PANEL: LAGER
        # ==========================================
        elif st.session_state.active_panel == "lager":
            st.markdown("## 📦 Lager")

            lag_col1, lag_col2 = st.columns(2)

            with lag_col1:
                st.write("### Bestände")
                st.metric("Rohmaterial", f"{state.rohmaterial_lager:.0f} Lose",
                          help=f"Wert: {state.rohmaterial_lager * state.einkaufspreis_material:.1f} M")
                st.metric("Unfertige Erzeugnisse", f"{state.unfertige_erzeugnisse:.0f} Lose")
                st.metric("Fertige Erzeugnisse", f"{state.fertige_erzeugnisse:.0f} Lose")

            with lag_col2:
                st.write("### Materialbeschaffung")
                st.caption(f"Einkaufspreis: {state.einkaufspreis_material:.1f} M/Los")
                einkauf_menge = st.number_input(
                    "Material einkaufen (Lose)", min_value=0.0, step=1.0, key="lager_einkauf"
                )
                kosten_vorschau = einkauf_menge * state.einkaufspreis_material
                if einkauf_menge > 0:
                    st.caption(f"Kosten: {kosten_vorschau:.1f} M")
                if st.button("Material bestellen"):
                    run_action(material_einkaufen, state, einkauf_menge,
                               success_message=f"{einkauf_menge:.0f} Lose Rohmaterial eingekauft.")

        # ==========================================
        # PANEL: NEUE ANLAGE
        # ==========================================
        elif st.session_state.active_panel == "neue_anlage":
            st.markdown("## 🏗️ Neue Fertigungsanlage")

            if state.neue_anlage_aktiv:
                st.success("Die neue Anlage ist aktiv und in Betrieb.")
            elif state.jahr < 3:
                st.warning(f"Die neue Anlage ist erst ab Jahr 3 verfügbar. Aktuell: Jahr {state.jahr}.")

            st.markdown("### Vergleich: Alte vs. Neue Anlage")

            vergleich_data = {
                "Merkmal": [
                    "Fertigungsstufen",
                    "Kosten pro Los",
                    "Investitionskosten",
                    "Abschreibung/Jahr",
                    "Verfügbar ab",
                ],
                "Alte Anlage (2-stufig)": [
                    "Stufe 1 (3M) + Stufe 2 (1M)",
                    "4M gesamt",
                    "–",
                    "5M (Maschinen)",
                    "Sofort",
                ],
                "Neue Anlage (1-stufig)": [
                    "Einstufig",
                    "3M gesamt",
                    "20M",
                    "5M (alt) + 4M (neu) = 9M",
                    "Jahr 3",
                ],
            }
            st.table(pd.DataFrame(vergleich_data).set_index("Merkmal"))

            st.markdown("### Wirtschaftlichkeit")
            ersparnis_pro_los = 1.0  # 4M → 3M
            st.info(
                f"**Einsparung:** {ersparnis_pro_los:.0f} M/Los durch Wegfall der Endmontage (Stufe 2).  \n"
                f"**Break-Even:** Bei 3 Losen/Quartal ersparen Sie 3M/Q = 12M/Jahr.  \n"
                f"Die Investition von 20M amortisiert sich in ca. **1,7 Jahren**.  \n"
                f"Zusätzliche AfA: 4M/Jahr über 5 Jahre."
            )

            if not state.neue_anlage_aktiv:
                st.markdown("### Investitionsentscheidung")
                st.write(f"**Investitionskosten:** 20M | **Verfügbare Mittel:** {state.liquide_mittel:.2f} M")
                kann_kaufen = state.jahr >= 3 and state.liquide_mittel >= 20.0
                if not kann_kaufen:
                    if state.jahr < 3:
                        st.warning("Noch nicht verfügbar (ab Jahr 3).")
                    else:
                        st.warning("Nicht genügend liquide Mittel (20M benötigt).")
                if st.button("✅ Neue Anlage kaufen (20M)", disabled=not kann_kaufen):
                    run_action(neue_anlage_kaufen, state,
                               success_message="Neue Anlage erfolgreich in Betrieb genommen!")

# ------------------------------------------
# JAHRESABSCHLUSS
# ------------------------------------------

st.divider()

with st.expander("📋 Jahresabschluss durchführen", expanded=(state.quartal == 4)):
    st.markdown(
        "Der Jahresabschluss schließt das Geschäftsjahr ab: "
        "Zinszahlung, Abschreibungen, Steuerermittlung und GuV-Erstellung. "
        "**Erst nach dem Jahresabschluss ins nächste Quartal wechseln.**"
    )
    if state.quartal != 4:
        st.info(f"Jahresabschluss ist in Quartal 4 fällig. Aktuell: Q{state.quartal}.")

    ja_col1, ja_col2 = st.columns(2)
    with ja_col1:
        zinsen_vorschau = state.darlehen * state.zinssatz
        afa_vorschau = min(1.0, state.av_gebaeude) + min(5.0, state.av_maschinen)
        if state.neue_anlage_aktiv:
            afa_vorschau += 4.0
        st.metric("Zinsen (fällig)", f"{zinsen_vorschau:.2f} M")
        st.metric("Abschreibungen", f"{afa_vorschau:.2f} M")
    with ja_col2:
        from core.calculations import berechne_gewinn as _bgv, berechne_zinskosten as _bzk
        gwv = _bgv(
            state.umsatz, state.materialkosten, state.fertigungskosten,
            state.gemeinkosten, state.marketingkosten,
            state.zinskosten + zinsen_vorschau, state.abschreibungen_periode + afa_vorschau
        )
        steuern_vorschau = max(0.0, gwv / 3)
        st.metric("Gewinn vor Steuern (Vorschau)", f"{gwv:.2f} M")
        st.metric("Steuern (1/3, Vorschau)", f"{steuern_vorschau:.2f} M")

    if st.button("📋 Jahresabschluss jetzt durchführen", type="primary"):
        run_action(jahresabschluss, state, success_message=f"Jahresabschluss Jahr {state.jahr} abgeschlossen.")

# ------------------------------------------
# SPIELSTEUERUNG
# ------------------------------------------

st.divider()

ctrl_col1, ctrl_col2 = st.columns([1, 5])

with ctrl_col1:
    if st.button("▶ Nächstes Quartal", use_container_width=True):
        run_action(state.naechstes_quartal)

with ctrl_col2:
    if st.button("↺ Spiel zurücksetzen", use_container_width=True):
        reset_game()
        st.rerun()

# ------------------------------------------
# KENNZAHLEN & CHARTS
# ------------------------------------------

if state.kennzahlen_history:
    with st.expander("📊 Kennzahlen & Verlauf"):
        df = pd.DataFrame(state.kennzahlen_history)

        tab1, tab2 = st.tabs(["Kennzahlentabelle", "Charts"])

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
            chart_col1, chart_col2 = st.columns(2)
            with chart_col1:
                st.markdown("**Umsatz & Gewinn (M)**")
                if "Umsatz" in df.columns and "Gewinn n. St." in df.columns:
                    st.line_chart(df.set_index("Jahr")[["Umsatz", "EBIT", "Gewinn n. St."]])

            with chart_col2:
                st.markdown("**Eigenkapital & Gesamtkapital (M)**")
                if "Eigenkapital" in df.columns:
                    st.line_chart(df.set_index("Jahr")[["Eigenkapital", "Gesamtkapital", "Fremdkapital (Darlehen)"]])

# Aktuelle Kennzahlen (immer sichtbar)
with st.expander("🔢 Aktuelle Kennzahlen"):
    kz = berechne_kennzahlen(state)
    kz_col1, kz_col2, kz_col3 = st.columns(3)
    kz_col1.metric("Umsatzrendite ROS", f"{kz['Umsatzrendite ROS (%)']:.1f} %")
    kz_col1.metric("Eigenkapitalrendite ROE", f"{kz['Eigenkapitalrendite ROE (%)']:.1f} %")
    kz_col1.metric("ROI", f"{kz['ROI (%)']:.1f} %")
    kz_col2.metric("Anlagevermögen", f"{kz['Anlagevermögen']:.1f} M")
    kz_col2.metric("Umlaufvermögen", f"{kz['Umlaufvermögen']:.1f} M")
    kz_col2.metric("Gesamtkapital", f"{kz['Gesamtkapital']:.1f} M")
    kz_col3.metric("Working Capital", f"{kz['Working Capital']:.1f} M")
    kz_col3.metric("Cash Flow", f"{kz['Cash Flow']:.1f} M")
    kz_col3.metric("EBIT", f"{kz['EBIT']:.1f} M")

# ------------------------------------------
# VERLAUF
# ------------------------------------------

if state.verlauf:
    with st.expander("🗒️ Verlauf anzeigen"):
        for eintrag in reversed(state.verlauf):
            st.write(f"- {eintrag}")
