import pandas as pd
import streamlit as st

from core.state import GameState

from core.actions import (
    endmontage_stufe_2,
    material_einkaufen,
    produktion_stufe_1,
    produkte_verkaufen,
)


st.set_page_config(page_title="Planspiel Test-App", layout="wide")


def get_state() -> GameState:
    if "game_state" not in st.session_state:
        st.session_state.game_state = GameState()
        st.session_state.game_state.log("Test-App gestartet.")
    return st.session_state.game_state


def reset_game() -> None:
    st.session_state.game_state = GameState()
    st.session_state.game_state.log("Spiel wurde zurückgesetzt.")


def run_action(action_func, *args, success_message: str | None = None, **kwargs) -> None:
    """Führt eine Aktion aus, zeigt Erfolg/Fehler an und startet die Seite neu."""
    try:
        action_func(*args, **kwargs)
        if success_message:
            st.success(success_message)
        st.rerun()
    except ValueError as e:
        st.error(str(e))


def add_liquide_mittel(state: GameState, betrag: float) -> None:
    """Erhöht die liquiden Mittel testweise um einen festen Betrag."""
    state.liquide_mittel += betrag
    state.log(f"{betrag} liquide Mittel hinzugefügt.")


def setze_liquide_mittel(state: GameState, betrag: float) -> None:
    """Setzt die liquiden Mittel auf einen neuen Wert."""
    state.liquide_mittel = betrag
    state.log(f"Liquide Mittel auf {betrag} gesetzt.")


def setze_verkaufspreis(state: GameState, preis: float) -> None:
    """Setzt den Verkaufspreis auf einen neuen Wert."""
    state.verkaufspreis = preis
    state.log(f"Verkaufspreis auf {preis} gesetzt.")


def setze_rohmateriallager(state: GameState, menge: float) -> None:
    """Setzt den Rohmaterialbestand auf einen neuen Wert."""
    state.rohmaterial_lager = menge
    state.log(f"Rohmateriallager auf {menge} gesetzt.")


state = get_state()

st.title("Planspiel – Testoberfläche")
st.write("Diese Seite dient zur Prüfung des aktuellen GameState und der ersten Logik.")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Jahr", state.jahr)
col2.metric("Quartal", state.quartal)
col3.metric("Runde", state.runde)
col4.metric("Liquide Mittel", f"{state.liquide_mittel:.2f}")

st.subheader("Schnellübersicht")

overview_col1, overview_col2, overview_col3 = st.columns(3)

with overview_col1:
    st.write("**Lagerbestände**")
    st.write(f"Rohmaterial: {state.rohmaterial_lager}")
    st.write(f"Unfertige Erzeugnisse: {state.unfertige_erzeugnisse}")
    st.write(f"Fertige Erzeugnisse: {state.fertige_erzeugnisse}")

with overview_col2:
    st.write("**Finanzierung**")
    st.write(f"Darlehen: {state.darlehen}")
    st.write(f"Forderungen: {state.forderungen}")
    st.write(f"Lieferantenverbindlichkeiten: {state.verbindlichkeiten_lieferanten}")

with overview_col3:
    st.write("**Periode**")
    st.write(f"Umsatz: {state.umsatz}")
    st.write(f"Materialkosten: {state.materialkosten}")
    st.write(f"Fertigungskosten: {state.fertigungskosten}")
    st.write(f"Gemeinkosten: {state.gemeinkosten}")
    st.write(f"Gewinn: {state.gewinn}")

st.divider()
st.subheader("Testaktionen")

action_col1, action_col2, action_col3, action_col4 = st.columns(4)

with action_col1:
    if st.button("Nächstes Quartal"):
        run_action(state.naechstes_quartal)

with action_col2:
    if st.button("Periodenwerte zurücksetzen"):
        run_action(state.reset_periodenwerte)

with action_col3:
    if st.button("Test: +100 liquide Mittel"):
        run_action(add_liquide_mittel, state, 100, success_message="100 liquide Mittel hinzugefügt.")

with action_col4:
    if st.button("Spiel komplett zurücksetzen"):
        run_action(reset_game, success_message="Spiel wurde komplett zurückgesetzt.")

st.divider()
st.subheader("Spielaktionen")

spiel_col1, spiel_col2, spiel_col3, spiel_col4 = st.columns(4)

with spiel_col1:
    einkauf_menge = st.number_input("Material einkaufen", min_value=0.0, step=1.0)
    if st.button("Material kaufen"):
        run_action(
            material_einkaufen,
            state,
            einkauf_menge,
            success_message=f"Materialeinkauf erfolgreich: {einkauf_menge} Lose eingekauft.",
        )

with spiel_col2:
    produktions_menge_stufe_1 = st.number_input("Fertigungsstufe 1", min_value=0.0, step=1.0)
    if st.button("Stufe 1 ausführen"):
        run_action(
            produktion_stufe_1,
            state,
            produktions_menge_stufe_1,
            success_message=f"Fertigungsstufe 1 erfolgreich: {produktions_menge_stufe_1} Lose verarbeitet.",
        )

with spiel_col3:
    endmontage_menge_stufe_2 = st.number_input("Endmontage Stufe 2", min_value=0.0, step=1.0)
    if st.button("Stufe 2 ausführen"):
        run_action(
            endmontage_stufe_2,
            state,
            endmontage_menge_stufe_2,
            success_message=f"Endmontage Stufe 2 erfolgreich: {endmontage_menge_stufe_2} Lose fertiggestellt.",
        )

with spiel_col4:
    verkaufs_menge = st.number_input("Produkte verkaufen", min_value=0.0, step=1.0)
    sofortzahlung = st.checkbox("Sofortzahlung", value=False)
    if st.button("Verkaufen"):
        zahlungsart = "mit Sofortzahlung" if sofortzahlung else "auf Ziel"
        run_action(
            produkte_verkaufen,
            state,
            verkaufs_menge,
            sofortzahlung=sofortzahlung,
            success_message=f"Verkauf erfolgreich: {verkaufs_menge} Lose {zahlungsart} verkauft.",
        )

st.divider()
st.subheader("Direkte Testeingaben")

input_col1, input_col2, input_col3 = st.columns(3)

with input_col1:
    neues_geld = st.number_input("Liquide Mittel setzen", value=float(state.liquide_mittel), step=10.0)
    if st.button("Liquide Mittel übernehmen"):
        run_action(setze_liquide_mittel, state, neues_geld, success_message=f"Liquide Mittel auf {neues_geld} gesetzt.")

with input_col2:
    neuer_preis = st.number_input("Verkaufspreis setzen", value=float(state.verkaufspreis), step=1.0)
    if st.button("Verkaufspreis übernehmen"):
        run_action(setze_verkaufspreis, state, neuer_preis, success_message=f"Verkaufspreis auf {neuer_preis} gesetzt.")

with input_col3:
    neues_material = st.number_input("Rohmateriallager setzen", value=float(state.rohmaterial_lager), step=1.0)
    if st.button("Rohmaterial übernehmen"):
        run_action(setze_rohmateriallager, state, neues_material, success_message=f"Rohmateriallager auf {neues_material} gesetzt.")

st.divider()
st.subheader("Vollständiger GameState")

state_dict = state.to_dict()
df = pd.DataFrame(
    [{"Feld": key, "Wert": value} for key, value in state_dict.items()]
)
st.dataframe(df, width="stretch")

st.divider()
st.subheader("Verlauf / Log")

if state.verlauf:
    for eintrag in reversed(state.verlauf):
        st.write(f"- {eintrag}")
else:
    st.info("Noch keine Einträge vorhanden.")