import pandas as pd
import streamlit as st

from core.state import GameState


st.set_page_config(page_title="Planspiel Test-App", layout="wide")


def get_state() -> GameState:
    if "game_state" not in st.session_state:
        st.session_state.game_state = GameState()
        st.session_state.game_state.log("Test-App gestartet.")
    return st.session_state.game_state


def reset_game() -> None:
    st.session_state.game_state = GameState()
    st.session_state.game_state.log("Spiel wurde zurückgesetzt.")


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
        state.naechstes_quartal()

with action_col2:
    if st.button("Periodenwerte zurücksetzen"):
        state.reset_periodenwerte()

with action_col3:
    if st.button("Test: +100 liquide Mittel"):
        state.liquide_mittel += 100
        state.log("100 liquide Mittel hinzugefügt.")

with action_col4:
    if st.button("Spiel komplett zurücksetzen"):
        reset_game()
        state = st.session_state.game_state

st.divider()
st.subheader("Direkte Testeingaben")

input_col1, input_col2, input_col3 = st.columns(3)

with input_col1:
    neues_geld = st.number_input("Liquide Mittel setzen", value=float(state.liquide_mittel), step=10.0)
    if st.button("Liquide Mittel übernehmen"):
        state.liquide_mittel = neues_geld
        state.log(f"Liquide Mittel auf {neues_geld} gesetzt.")

with input_col2:
    neuer_preis = st.number_input("Verkaufspreis setzen", value=float(state.verkaufspreis), step=1.0)
    if st.button("Verkaufspreis übernehmen"):
        state.verkaufspreis = neuer_preis
        state.log(f"Verkaufspreis auf {neuer_preis} gesetzt.")

with input_col3:
    neues_material = st.number_input("Rohmateriallager setzen", value=float(state.rohmaterial_lager), step=1.0)
    if st.button("Rohmaterial übernehmen"):
        state.rohmaterial_lager = neues_material
        state.log(f"Rohmateriallager auf {neues_material} gesetzt.")

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