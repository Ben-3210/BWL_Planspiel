import io

import pandas as pd
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

from core.actions import (
    endmontage_stufe_2,
    material_einkaufen,
    produktion_stufe_1,
    produkte_verkaufen,
)
from core.state import GameState

st.set_page_config(page_title="Factory Planspiel", layout="wide")


# -----------------------------
# SPIELFELD-OVERLAY
# -----------------------------

# Koordinaten (x, y) der Sechsecke auf dem Bild (1557x957px).
# Jeweils das erste Sechseck im Bereich wird beschriftet.
_OVERLAY_FONT_SIZE = 34
_OVERLAY_COLOR = (0, 0, 0)  # schwarz

_OVERLAY_POSITIONS = {
    "rohmaterial_lager":      (200, 140),   # Materiallager (oben links)
    "unfertige_erzeugnisse":  (490, 140),   # Fertigungsstufe 1
    "fertige_erzeugnisse":    (1095, 140),  # Fertigwarenlager (oben rechts)
    "liquide_mittel":         (385, 730),   # Kasse + Bankguthaben
    "forderungen":            (725, 730),   # Forderungen
}


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
    except OSError:
        return ImageFont.load_default()


def draw_board_overlay(state: "GameState", image_path: str) -> bytes:
    """Öffnet das Spielfeldbild und beschriftet die Sechseck-Felder mit aktuellen Beständen."""
    img = Image.open(image_path).copy()
    draw = ImageDraw.Draw(img)
    font = _load_font(_OVERLAY_FONT_SIZE)

    for field, (x, y) in _OVERLAY_POSITIONS.items():
        value = getattr(state, field, 0)
        text = str(int(value)) if value == int(value) else f"{value:.1f}"
        # Weißer Schatten für Lesbarkeit
        draw.text((x + 1, y + 1), text, fill=(255, 255, 255), font=font)
        draw.text((x, y), text, fill=_OVERLAY_COLOR, font=font)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    buf.seek(0)
    return buf


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
# TITEL
# -----------------------------

st.title("Factory Planspiel")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Jahr", state.jahr)
col2.metric("Quartal", state.quartal)
col3.metric("Runde", state.runde)
col4.metric("Liquide Mittel", f"{state.liquide_mittel:.2f} M")

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
        st.image(draw_board_overlay(state, str(image_path)), use_container_width=True)

    col_a, col_b, col_c, col_d = st.columns(4)

    with col_a:
        if st.button("🏭 Produktion", use_container_width=True):
            st.session_state.active_panel = "produktion"

    with col_b:
        if st.button("📦 Lager", use_container_width=True):
            st.session_state.active_panel = "lager"

    with col_c:
        if st.button("🚚 Vertrieb", use_container_width=True):
            st.session_state.active_panel = "vertrieb"

    with col_d:
        if st.button("💰 Finanzen", use_container_width=True):
            st.session_state.active_panel = "finanzen"

    # -----------------------------
    # PANELS
    # -----------------------------

    if "active_panel" in st.session_state:
        st.divider()

        if st.session_state.active_panel == "finanzen":
            st.markdown("## 💰 Finanzübersicht")

            fin_col1, fin_col2, fin_col3, fin_col4 = st.columns(4)
            fin_col1.metric("Liquide Mittel", f"{state.liquide_mittel:.2f} M")
            fin_col2.metric("Darlehen", f"{state.darlehen:.2f} M")
            fin_col3.metric("Forderungen", f"{state.forderungen:.2f} M")
            fin_col4.metric("Gewinn", f"{state.gewinn:.2f} M")

            st.markdown("### Periodenübersicht")
            p_col1, p_col2, p_col3 = st.columns(3)
            p_col1.metric("Umsatz", f"{state.umsatz:.2f} M")
            p_col2.metric("Materialkosten", f"{state.materialkosten:.2f} M")
            p_col3.metric("Fertigungskosten", f"{state.fertigungskosten:.2f} M")

            p_col4, p_col5, p_col6 = st.columns(3)
            p_col4.metric("Gemeinkosten", f"{state.gemeinkosten:.2f} M")
            p_col5.metric("Marketingkosten", f"{state.marketingkosten:.2f} M")
            p_col6.metric("Zinskosten", f"{state.zinskosten:.2f} M")

        elif st.session_state.active_panel == "produktion":
            st.markdown("## 🏭 Produktion")

            prod_col1, prod_col2 = st.columns(2)

            with prod_col1:
                st.write("### Fertigungsstufe 1")
                st.caption(f"Rohmaterial verfügbar: {state.rohmaterial_lager:.0f} Lose")
                menge_stufe_1 = st.number_input(
                    "Menge Stufe 1", min_value=0.0, step=1.0, key="prod1"
                )
                if st.button("Produktion Stufe 1 starten"):
                    run_action(
                        produktion_stufe_1,
                        state,
                        menge_stufe_1,
                        success_message=f"Stufe 1: {menge_stufe_1:.0f} Lose produziert.",
                    )

            with prod_col2:
                st.write("### Endmontage (Stufe 2)")
                st.caption(f"Unfertige Erzeugnisse: {state.unfertige_erzeugnisse:.0f} Lose")
                menge_stufe_2 = st.number_input(
                    "Menge Stufe 2", min_value=0.0, step=1.0, key="prod2"
                )
                if st.button("Endmontage starten"):
                    run_action(
                        endmontage_stufe_2,
                        state,
                        menge_stufe_2,
                        success_message=f"Stufe 2: {menge_stufe_2:.0f} Lose fertiggestellt.",
                    )

        elif st.session_state.active_panel == "vertrieb":
            st.markdown("## 🚚 Vertrieb")

            vertrieb_col1, vertrieb_col2 = st.columns(2)

            with vertrieb_col1:
                st.write("### Verkauf")
                st.caption(f"Fertige Erzeugnisse: {state.fertige_erzeugnisse:.0f} Lose")
                verkaufs_menge = st.number_input(
                    "Menge verkaufen", min_value=0.0, step=1.0, key="vertrieb_menge"
                )
                sofortzahlung = st.checkbox("Sofortzahlung", key="vertrieb_sofort")

                if st.button("Verkauf starten"):
                    zahlungsart = "mit Sofortzahlung" if sofortzahlung else "auf Ziel"
                    run_action(
                        produkte_verkaufen,
                        state,
                        verkaufs_menge,
                        sofortzahlung=sofortzahlung,
                        success_message=f"{verkaufs_menge:.0f} Lose {zahlungsart} verkauft.",
                    )

            with vertrieb_col2:
                st.write("### Preisstrategie")
                neuer_preis = st.number_input(
                    "Verkaufspreis (M)", value=float(state.verkaufspreis), step=1.0, key="vertrieb_preis"
                )
                if st.button("Preis setzen"):
                    state.verkaufspreis = neuer_preis
                    st.success(f"Verkaufspreis auf {neuer_preis:.2f} M gesetzt.")
                    st.rerun()

        elif st.session_state.active_panel == "lager":
            st.markdown("## 📦 Lager")

            lag_col1, lag_col2 = st.columns(2)

            with lag_col1:
                st.write("### Bestände")
                st.metric("Rohmaterial", f"{state.rohmaterial_lager:.0f} Lose")
                st.metric("Unfertige Erzeugnisse", f"{state.unfertige_erzeugnisse:.0f} Lose")
                st.metric("Fertige Erzeugnisse", f"{state.fertige_erzeugnisse:.0f} Lose")

            with lag_col2:
                st.write("### Materialbeschaffung")
                einkauf_menge = st.number_input(
                    "Material einkaufen (Lose)", min_value=0.0, step=1.0, key="lager_einkauf"
                )
                if st.button("Material bestellen"):
                    run_action(
                        material_einkaufen,
                        state,
                        einkauf_menge,
                        success_message=f"{einkauf_menge:.0f} Lose Rohmaterial eingekauft.",
                    )

# -----------------------------
# SPIELSTEUERUNG
# -----------------------------

st.divider()

ctrl_col1, ctrl_col2 = st.columns([1, 5])

with ctrl_col1:
    if st.button("▶ Nächstes Quartal", use_container_width=True):
        run_action(state.naechstes_quartal)

with ctrl_col2:
    if st.button("↺ Spiel zurücksetzen", use_container_width=True):
        reset_game()
        st.rerun()

# -----------------------------
# VERLAUF
# -----------------------------

if state.verlauf:
    with st.expander("Verlauf anzeigen"):
        for eintrag in reversed(state.verlauf):
            st.write(f"- {eintrag}")
