import streamlit as st

st.set_page_config(layout="wide")

# -----------------------------
# SESSION STATE INITIALISIEREN
# -----------------------------
if "round" not in st.session_state:
    st.session_state.round = 1

if "profit" not in st.session_state:
    st.session_state.profit = 0

if "revenue" not in st.session_state:
    st.session_state.revenue = 0

if "cost" not in st.session_state:
    st.session_state.cost = 0

# -----------------------------
# TITEL
# -----------------------------
st.title("Factory Planspiel")

st.subheader(f"Runde {st.session_state.round}")

# -----------------------------
# LAYOUT
# -----------------------------
left, center, right = st.columns([1,2,1])

# -----------------------------
# LINKES PANEL - AKTIONEN
# -----------------------------
with left:

    st.header("Aktionen")

    price = st.slider("Verkaufspreis", 50, 200, 120)
    marketing = st.slider("Marketing Budget", 0, 5000, 1000)
    production = st.slider("Produktionsmenge", 0, 1000, 500)

    start_round = st.button("Runde starten")

# -----------------------------
# SPIELLOGIK
# -----------------------------
base_demand = 500

demand = base_demand + marketing * 0.05 - price * 2

if demand < 0:
    demand = 0

sold = min(production, demand)

revenue = sold * price

production_cost = production * 60
fixed_cost = 10000

cost = production_cost + marketing + fixed_cost

profit = revenue - cost

# -----------------------------
# RUNDE STARTEN
# -----------------------------
if start_round:

    st.session_state.revenue = revenue
    st.session_state.cost = cost
    st.session_state.profit = profit

    st.session_state.round += 1


# -----------------------------
# MITTE - SPIELFELD
# -----------------------------
with center:

    st.header("Factory")

    st.markdown("""
    ### Produktionssystem

    🏭 Produktion  
    📦 Lager  
    🚚 Verkauf  
    💰 Markt
    """)

    st.metric("Nachfrage", int(demand))
    st.metric("Absatz", int(sold))


# -----------------------------
# RECHTES PANEL - UNTERNEHMENSDATEN
# -----------------------------
with right:

    st.header("Unternehmensdaten")

    st.metric("Umsatz", int(st.session_state.revenue))
    st.metric("Kosten", int(st.session_state.cost))
    st.metric("Gewinn", int(st.session_state.profit))