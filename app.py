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


# ─── INTRO-SCREEN ──────────────────────────────────────────────────────────────

def zeige_intro() -> None:
    st.title("🏭 Factory AG – Planspiel")
    st.markdown("#### Ostfalia Hochschule · Fakultät Maschinenbau · SoSe 2026")
    st.divider()

    # ── Kontext ────────────────────────────────────────────────────────────────
    st.markdown("## Das Unternehmen")

    k1, k2 = st.columns([2, 1])

    with k1:
        st.markdown(
            """
            Du übernimmst die Geschäftsführung der **Factory AG** – einem mittelständischen
            deutschen Maschinenbauunternehmen, spezialisiert auf die Fertigung von
            **Elektromotoren für den Industriemarkt**.

            Das Unternehmen produziert in zwei Fertigungsstufen:

            - **Teilefertigung:** Motorkomponenten (Rotor, Stator, Wicklungen) werden gefertigt
            - **Endmontage:** Die Komponenten werden zum fertigen Elektromotor zusammengesetzt und geprüft

            Deine Aufgabe: Führe die Factory AG über **5 Jahre (20 Quartale)** möglichst
            profitabel. Triff kluge Entscheidungen zu Preisen, Produktion, Einkauf und
            Marketing – und reagiere auf unvorhergesehene Marktereignisse.
            """
        )

    with k2:
        st.markdown("**📊 Ausgangslage der Factory AG**")
        st.markdown(
            """
            | Position | Wert |
            |---|---|
            | Eigenkapital | 67 M |
            | Darlehen | 100 M |
            | Kassenbestand | 45 M |
            | Zinssatz | 10 % p.a. |
            | Steuersatz | 33 % |
            """
        )

    st.divider()

    # ── Spielanleitung ─────────────────────────────────────────────────────────
    st.markdown("## Spielanleitung")

    tab1, tab2, tab3, tab4 = st.tabs(["📅 Spielablauf", "🎛️ Deine Stellschrauben", "📊 Ziel & Kennzahlen", "⚡ Ereignisse"])

    with tab1:
        st.markdown(
            """
            Das Spiel ist in **Quartale** unterteilt. Jedes Quartal läuft in **6 geführten Schritten** ab:

            | Schritt | Aktion | Was passiert |
            |---|---|---|
            | 1 | 💰 **Forderungen einziehen** | Kunden begleichen ihre offenen Rechnungen aus dem Vorquartal |
            | 2 | 🚚 **Elektromotoren verkaufen** | Verkaufspreis festlegen, optional Marketing buchen, Angebot aufgeben |
            | 3 | 🏭 **Produktion** | Teilefertigung und/oder Endmontage durchführen |
            | 4 | 📦 **Materialeinkauf** | Rohmaterial für die nächste Produktion bestellen |
            | 5 | 📋 **Gemeinkosten zahlen** | Laufende Betriebskosten begleichen |
            | 6 | ✅ **Quartal abschließen** | Im 4. Quartal: Jahresabschluss mit Zinsen, Abschreibungen und Steuern |

            > **Wichtig:** Verkaufte Elektromotoren werden erst **im Folgequartal bezahlt** (Lieferung auf Ziel),
            > außer du wählst die Option "Sofortzahlung" mit Abzug.
            """
        )

    with tab2:
        st.markdown("Du hast folgende Hebel, um das Unternehmen zu steuern:")

        s1, s2 = st.columns(2)

        with s1:
            st.markdown(
                """
                **💰 Verkaufspreis**
                Höherer Preis bedeutet weniger Nachfrage – das klassische Preis-Mengen-Dilemma.
                Die Nachfrage schwankt außerdem zufällig um ±30%.

                **📣 Marketing**
                Mehr Marketingbudget schiebt die Nachfragekurve für dieses Quartal nach oben.
                Kosten laufen aber sofort durch die GuV.

                **🏭 Produktionsmenge**
                Zu viel produzieren bindet Kapital im Lager. Zu wenig produzieren bedeutet
                entgangenen Umsatz. Geschickte Planung ist entscheidend.
                """
            )

        with s2:
            st.markdown(
                """
                **📦 Einkaufsmenge**
                Du entscheidest, wie viel Rohmaterial du pro Quartal bestellst.
                Puffer aufbauen oder just-in-time? Beides hat Vor- und Nachteile.

                **🏗️ Neue Anlage (ab Jahr 3)**
                Für 20 M kannst du eine moderne einstufige Anlage kaufen, die Teilefertigung
                und Endmontage zusammenführt und die Stückkosten senkt.

                **🏦 Darlehen tilgen**
                Jeder zurückgezahlte Euro spart 10% Zinsen im Jahr – aber bindet Liquidität.
                """
            )

    with tab3:
        st.markdown(
            """
            **Dein Ziel:** Baue das Eigenkapital der Factory AG über 5 Jahre möglichst stark aus.
            Am Ende jedes Jahres werden folgende Kennzahlen berechnet und verfolgt:
            """
        )

        z1, z2 = st.columns(2)

        with z1:
            st.markdown(
                """
                | Kennzahl | Formel | Richtwert |
                |---|---|---|
                | **ROS** (Umsatzrendite) | EBIT / Umsatz | ≥ 8% gut |
                | **ROE** (EK-Rendite) | Gewinn / Eigenkapital | ≥ 10% gut |
                | **ROI** | ROS × Kapitalumschlag | ≥ 6% gut |
                | **GKR** | EBIT / Gesamtkapital | ≥ 6% gut |
                """
            )

        with z2:
            st.markdown(
                """
                | Kennzahl | Was sie zeigt | Richtwert |
                |---|---|---|
                | **Liquidität I** | Kasse / kurzfr. Verbindlichkeiten | ≥ 20% |
                | **Liquidität II** | (Kasse + Ford.) / kurzfr. Verbindl. | ≥ 100% |
                | **Working Capital** | UV − kurzfr. Verbindlichkeiten | positiv |
                | **Cash Flow** | Gewinn + Abschreibungen | positiv |
                """
            )

        st.info(
            "💡 **Merke:** Das Unternehmen darf nie zahlungsunfähig werden. "
            "Halte immer genügend Kasse – Zinsen und Gemeinkosten fallen unabhängig vom Umsatz an."
        )

    with tab4:
        st.markdown(
            """
            Jedes Quartal kann ein **zufälliges Ereignis** eintreten, das einen Spielparameter
            für genau dieses Quartal verändert. Das Ereignis wird zu Beginn des Quartals als
            Banner angezeigt.
            """
        )

        e1, e2 = st.columns(2)

        with e1:
            st.markdown("**📉 Mögliche Nachteile**")
            st.markdown(
                """
                - ⛏️ **Rohstoffknappheit** – Einkaufspreise steigen um 50%
                - 📉 **Konjunkturdelle** – Marktnachfrage sinkt um 25%
                - 🤒 **Personalengpass** – Fertigungskosten steigen um 20%
                - 🔧 **Maschinenstörung** – Fertigungskosten steigen um 30%
                - 😤 **Großkundenabgang** – Nachfrage bricht um 30% ein
                """
            )

        with e2:
            st.markdown("**📈 Mögliche Vorteile**")
            st.markdown(
                """
                - 🚀 **Nachfrageboom** – Marktnachfrage steigt um 30%
                - 💰 **Rohstoff-Sonderangebot** – Einkaufspreise sinken um 25%
                - ⚙️ **Prozessoptimierung** – Fertigungskosten sinken um 15%
                - 🏆 **Exportauftrag** – Einmaliger Umsatzbonus
                - ☀️ **Ruhiges Quartal** – Kein Ereignis
                """
            )

        st.markdown(
            "> Ereignisse laufen automatisch aus – du musst nichts zurücksetzen."
        )

    st.divider()

    col_l, col_m, col_r = st.columns([1, 1, 1])
    with col_m:
        if st.button("▶ Spiel starten", type="primary", use_container_width=True):
            st.session_state.intro_gesehen = True
            st.rerun()


if not st.session_state.get("intro_gesehen", False):
    zeige_intro()
    st.stop()


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


def _farbe_metrik(wert: float, schwelle_gut: float, schwelle_ok: float, hoeher_ist_besser: bool = True) -> str:
    """Gibt eine CSS-Farbe zurück abhängig davon ob der Wert gut/ok/schlecht ist."""
    if hoeher_ist_besser:
        if wert >= schwelle_gut:
            return "#28a745"
        elif wert >= schwelle_ok:
            return "#ffc107"
        else:
            return "#dc3545"
    else:
        if wert <= schwelle_gut:
            return "#28a745"
        elif wert <= schwelle_ok:
            return "#ffc107"
        else:
            return "#dc3545"


def _kpi_box(label: str, wert: str, farbe: str = "#1e2a3a") -> None:
    """Rendert eine kompakte KPI-Box mit Hintergrundfarbe."""
    st.markdown(
        f"""<div style="background:{farbe};border-radius:6px;padding:6px 10px;margin-bottom:6px;">
        <div style="font-size:0.72rem;color:#aaa;line-height:1.2">{label}</div>
        <div style="font-size:1.05rem;font-weight:700;color:#f0f0f0;line-height:1.4">{wert}</div>
        </div>""",
        unsafe_allow_html=True,
    )


# ─── SIDEBAR: LIVE-DASHBOARD ────────────────────────────────────────────────────

kz = berechne_kennzahlen(state)

with st.sidebar:
    st.markdown("## 🏭 Factory AG")

    # ── Zeit ──────────────────────────────────────────────────────────────────
    t1, t2, t3 = st.columns(3)
    t1.metric("Jahr", state.jahr)
    t2.metric("Quartal", state.quartal)
    t3.metric("Runde", state.runde)

    st.divider()

    # ── Finanzen ──────────────────────────────────────────────────────────────
    st.markdown("**💰 Finanzen**")
    f1, f2 = st.columns(2)

    lm_farbe = _farbe_metrik(state.liquide_mittel, 15, 5)
    f1.markdown(
        f"<div style='font-size:0.72rem;color:#aaa'>Liquide Mittel</div>"
        f"<div style='font-size:1.0rem;font-weight:700;color:{lm_farbe}'>{state.liquide_mittel:.1f} M</div>",
        unsafe_allow_html=True,
    )
    f2.markdown(
        f"<div style='font-size:0.72rem;color:#aaa'>Eigenkapital</div>"
        f"<div style='font-size:1.0rem;font-weight:700'>{state.eigenkapital:.1f} M</div>",
        unsafe_allow_html=True,
    )
    f1.markdown(
        f"<div style='font-size:0.72rem;color:#aaa'>Forderungen</div>"
        f"<div style='font-size:1.0rem;font-weight:700'>{state.forderungen:.1f} M</div>",
        unsafe_allow_html=True,
    )
    f2.markdown(
        f"<div style='font-size:0.72rem;color:#aaa'>Darlehen</div>"
        f"<div style='font-size:1.0rem;font-weight:700;color:#dc3545'>{state.darlehen:.1f} M</div>",
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Lagerbestand ──────────────────────────────────────────────────────────
    st.markdown("**📦 Lagerbestand (Lose)**")
    st.markdown(
        f"""<div style="display:flex;align-items:center;gap:4px;font-size:0.85rem;">
          <div style="background:#1a3a5c;border-radius:6px;padding:6px 8px;text-align:center;flex:1">
            <div style="font-size:0.65rem;color:#90b8d8">Rohmat.</div>
            <div style="font-weight:700;color:#e0f0ff">{state.rohmaterial_lager:.0f}</div>
          </div>
          <div style="color:#aaa">→</div>
          <div style="background:#4a3200;border-radius:6px;padding:6px 8px;text-align:center;flex:1">
            <div style="font-size:0.65rem;color:#d4a843">Unfertig</div>
            <div style="font-weight:700;color:#ffe0a0">{state.unfertige_erzeugnisse:.0f}</div>
          </div>
          <div style="color:#aaa">→</div>
          <div style="background:#0d3320;border-radius:6px;padding:6px 8px;text-align:center;flex:1">
            <div style="font-size:0.65rem;color:#5cb87a">Fertig</div>
            <div style="font-weight:700;color:#a8f0be">{state.fertige_erzeugnisse:.0f}</div>
          </div>
        </div>""",
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Erfolgsgrößen (laufendes Jahr) ────────────────────────────────────────
    st.markdown("**📈 Erfolgsrechnung (lfd. Jahr)**")
    _kpi_box("Umsatz", f"{kz['Umsatz']:.1f} M")

    e1, e2 = st.columns(2)
    ebit_farbe = "#28a745" if kz["EBIT"] >= 0 else "#dc3545"
    gwn_farbe = "#28a745" if kz["Gewinn n. St."] >= 0 else "#dc3545"
    e1.markdown(
        f"<div style='font-size:0.72rem;color:#aaa'>EBIT</div>"
        f"<div style='font-size:1.0rem;font-weight:700;color:{ebit_farbe}'>{kz['EBIT']:.1f} M</div>",
        unsafe_allow_html=True,
    )
    e2.markdown(
        f"<div style='font-size:0.72rem;color:#aaa'>Gewinn n. St.</div>"
        f"<div style='font-size:1.0rem;font-weight:700;color:{gwn_farbe}'>{kz['Gewinn n. St.']:.1f} M</div>",
        unsafe_allow_html=True,
    )

    # Kosten-Breakdown
    with st.expander("Kosten-Details"):
        st.caption(
            f"Material: **{state.materialkosten:.1f} M**  \n"
            f"Fertigung: **{state.fertigungskosten:.1f} M**  \n"
            f"Gemeinkosten: **{state.gemeinkosten:.1f} M**  \n"
            f"Marketing: **{state.marketingkosten:.1f} M**  \n"
            f"Zinsen: **{state.zinskosten:.1f} M**  \n"
            f"AfA: **{state.abschreibungen_periode:.1f} M**"
        )

    st.divider()

    # ── Renditekennzahlen ─────────────────────────────────────────────────────
    st.markdown("**📊 Renditekennzahlen**")
    r1, r2 = st.columns(2)
    ros_farbe = _farbe_metrik(kz["Umsatzrendite ROS (%)"], 8, 3)
    roe_farbe = _farbe_metrik(kz["Eigenkapitalrendite ROE (%)"], 10, 4)
    roi_farbe = _farbe_metrik(kz["ROI (%)"], 6, 2)
    gkr_farbe = _farbe_metrik(kz["Gesamtkapitalrendite (%)"], 6, 2)

    r1.markdown(
        f"<div style='font-size:0.72rem;color:#aaa'>ROS (Umsatzrendite)</div>"
        f"<div style='font-size:1.0rem;font-weight:700;color:{ros_farbe}'>{kz['Umsatzrendite ROS (%)']:.1f} %</div>",
        unsafe_allow_html=True,
    )
    r2.markdown(
        f"<div style='font-size:0.72rem;color:#aaa'>ROE (EK-Rendite)</div>"
        f"<div style='font-size:1.0rem;font-weight:700;color:{roe_farbe}'>{kz['Eigenkapitalrendite ROE (%)']:.1f} %</div>",
        unsafe_allow_html=True,
    )
    r1.markdown(
        f"<div style='font-size:0.72rem;color:#aaa'>ROI</div>"
        f"<div style='font-size:1.0rem;font-weight:700;color:{roi_farbe}'>{kz['ROI (%)']:.1f} %</div>",
        unsafe_allow_html=True,
    )
    r2.markdown(
        f"<div style='font-size:0.72rem;color:#aaa'>GKR</div>"
        f"<div style='font-size:1.0rem;font-weight:700;color:{gkr_farbe}'>{kz['Gesamtkapitalrendite (%)']:.1f} %</div>",
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Working Capital & Cash Flow ───────────────────────────────────────────
    st.markdown("**⚙️ Liquidität & Kapitalfluss**")
    wc_farbe = _farbe_metrik(kz["Working Capital"], 20, 5)
    cf_farbe = _farbe_metrik(kz["Cash Flow"], 5, 0)

    w1, w2 = st.columns(2)
    w1.markdown(
        f"<div style='font-size:0.72rem;color:#aaa'>Working Capital</div>"
        f"<div style='font-size:1.0rem;font-weight:700;color:{wc_farbe}'>{kz['Working Capital']:.1f} M</div>",
        unsafe_allow_html=True,
    )
    w2.markdown(
        f"<div style='font-size:0.72rem;color:#aaa'>Cash Flow</div>"
        f"<div style='font-size:1.0rem;font-weight:700;color:{cf_farbe}'>{kz['Cash Flow']:.1f} M</div>",
        unsafe_allow_html=True,
    )

    # Liquiditätsgrade
    st.caption("Liquiditätsgrade (Richtwert: I ≥ 20%, II ≥ 100%, III ≥ 120%)")
    liq1 = kz["Liquidität I (%)"]
    liq2 = kz["Liquidität II (%)"]
    liq3 = kz["Liquidität III (%)"]
    l1c, l2c, l3c = st.columns(3)

    def _liq_html(label: str, wert, gut: float, ok: float) -> str:
        if wert == "–":
            return f"<div style='font-size:0.65rem;color:#aaa'>{label}</div><div style='font-weight:700'>–</div>"
        farbe = _farbe_metrik(float(wert), gut, ok)
        return (
            f"<div style='font-size:0.65rem;color:#aaa'>{label}</div>"
            f"<div style='font-weight:700;color:{farbe}'>{wert}%</div>"
        )

    l1c.markdown(_liq_html("Liq. I", liq1, 20, 10), unsafe_allow_html=True)
    l2c.markdown(_liq_html("Liq. II", liq2, 100, 70), unsafe_allow_html=True)
    l3c.markdown(_liq_html("Liq. III", liq3, 120, 100), unsafe_allow_html=True)

    st.divider()

    # ── Mini-Bilanz ───────────────────────────────────────────────────────────
    st.markdown("**⚖️ Bilanz (Kurzform)**")
    av = kz["Anlagevermögen"]
    uv = kz["Umlaufvermögen"]
    ek = kz["Eigenkapital"]
    fk = kz["Fremdkapital (Darlehen)"]
    gk = kz["Gesamtkapital"]

    b1, b2 = st.columns(2)
    b1.markdown(
        f"<div style='font-size:0.72rem;color:#aaa;font-weight:600'>Aktiva {gk:.0f} M</div>"
        f"<div style='font-size:0.72rem'>AV: {av:.1f} M</div>"
        f"<div style='font-size:0.72rem'>UV: {uv:.1f} M</div>",
        unsafe_allow_html=True,
    )
    b2.markdown(
        f"<div style='font-size:0.72rem;color:#aaa;font-weight:600'>Passiva {gk:.0f} M</div>"
        f"<div style='font-size:0.72rem'>EK: {ek:.1f} M</div>"
        f"<div style='font-size:0.72rem'>FK: {fk:.1f} M</div>",
        unsafe_allow_html=True,
    )

    # Kapitalumschlag
    st.caption(f"Kapitalumschlag: **{kz['Kapitalumschlag']:.2f}x**")

    # ── Verlaufschart ─────────────────────────────────────────────────────────
    if state.kennzahlen_history:
        st.divider()
        st.markdown("**📉 Jahresverlauf**")
        df_hist = pd.DataFrame(state.kennzahlen_history)
        st.line_chart(
            df_hist.set_index("Jahr")[["Umsatz", "EBIT", "Gewinn n. St."]],
            height=160,
        )

    st.divider()
    if st.button("↺ Spiel zurücksetzen", use_container_width=True):
        reset_game()
        st.session_state.intro_gesehen = False
        st.rerun()


# ─── HAUPTBEREICH ──────────────────────────────────────────────────────────────

st.title("🏭 Factory Planspiel")

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

# ─── FORTSCHRITTSANZEIGE ───────────────────────────────────────────────────────

SCHRITT_NAMEN = ["Forderungen", "Verkauf", "Produktion", "Einkauf", "Gemeinkosten", "Abschluss"]
SCHRITT_ICONS = ["💰", "🚚", "🏭", "📦", "📋", "✅"]

schritt = state.quartalsschritt

st.subheader(f"Q{state.quartal} / Jahr {state.jahr}")
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
    st.markdown("## 💰 Forderungen einziehen")

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
    with st.expander("✅ Forderungen einziehen"):
        st.success("Erledigt.")

# ─── SCHRITT 2: PRODUKTE VERKAUFEN ────────────────────────────────────────────

if schritt == 2:
    st.markdown("## 🚚 Produkte verkaufen")

    idx = kombinierter_nachfrage_index()
    preis_aktuell = st.session_state.get("s2_preis", state.verkaufspreis)
    erwartete_nachfrage = berechne_nachfrage(preis_aktuell, idx)
    spanne_low, spanne_high = berechne_nachfrage_spanne(preis_aktuell, idx)

    # Ergebnis des letzten Verkaufs anzeigen (einmalig nach rerun)
    letztes_ergebnis = st.session_state.pop("verkauf_ergebnis", None)
    if letztes_ergebnis:
        vk = letztes_ergebnis["verkauft"]
        an = letztes_ergebnis["angebot"]
        los_str = lambda n: f"{n} Los" if n == 1 else f"{n} Lose"
        if vk == 0:
            st.error("Kein Absatz – kein Los wurde verkauft.")
        elif vk < an:
            st.warning(f"**{los_str(vk)}** verkauft – {an - vk} {'Los verbleibt' if an - vk == 1 else 'Lose verbleiben'} im Lager.")
        else:
            st.success(f"**{los_str(vk)}** verkauft.")

    m1, m2, m3 = st.columns(3)
    m1.metric("Fertige Erzeugnisse", f"{state.fertige_erzeugnisse:.0f} Lose")
    m2.metric("Erwartete Nachfrage", f"~{erwartete_nachfrage} Lose",
              help=f"Realistische Spanne (95%): {spanne_low}–{spanne_high} Lose")
    m3.metric("Aktueller Preis", f"{preis_aktuell:.1f} M/Los")

    if not state.verkauf_durchgefuehrt:
        if state.fertige_erzeugnisse <= 0:
            st.info("Kein Fertigwarenbestand – kein Verkauf möglich.")
        else:
            v_col1, v_col2 = st.columns(2)

            with v_col1:
                st.write("**Preisstrategie**")
                neuer_preis = st.number_input(
                    "Verkaufspreis (M)", value=float(state.verkaufspreis), min_value=1.0, step=1.0, key="s2_preis"
                )
                state.verkaufspreis = neuer_preis

                st.write("**Marketing (optional)**")
                if state.marketing_durchgefuehrt:
                    st.success(f"{state.marketingkosten:.1f} M investiert.")
                else:
                    marketing_betrag = st.number_input("Budget (M)", min_value=0.0, step=0.5, key="s2_marketing")
                    if st.button("Marketing buchen", disabled=marketing_betrag <= 0):
                        run_action(
                            marketing_ausgeben, state, marketing_betrag,
                            success_message=f"{marketing_betrag:.1f} M Marketing gebucht.",
                        )

            with v_col2:
                st.write("**Verkaufsangebot**")
                max_angebot = int(state.fertige_erzeugnisse)
                verkaufs_menge = st.number_input(
                    "Angebot (Lose)", min_value=0.0, max_value=float(max_angebot), step=1.0, key="s2_menge"
                )
                sofortzahlung = st.checkbox("Sofortzahlung (sonst auf Ziel)", key="s2_sofort")

                if verkaufs_menge > 0:
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
    with st.expander("✅ Produkte verkaufen"):
        st.success("Erledigt.")

# ─── SCHRITT 3: PRODUKTION ────────────────────────────────────────────────────

if schritt == 3:
    st.markdown("## 🏭 Produktion")

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
        verfuegbar_s2 = max(0.0, state.unfertige_erzeugnisse - state.neue_unfertige_dieses_quartal)
        p_col1, p_col2 = st.columns(2)

        with p_col1:
            st.write("**Fertigungsstufe 1**")
            if state.stufe1_durchgefuehrt:
                st.success("Fertigung erfolgt.")
                menge_s1 = 0.0
            elif state.rohmaterial_lager <= 0:
                st.info("Kein Rohmaterial vorhanden.")
                menge_s1 = 0.0
            else:
                if st.session_state.pop("s3_reset", False):
                    st.session_state["s3_s1"] = 0.0
                menge_s1 = st.number_input("Menge (Lose)", min_value=0.0, max_value=float(state.rohmaterial_lager), step=1.0, key="s3_s1")
                st.caption(f"Rohmaterial danach: **{state.rohmaterial_lager - menge_s1:.0f} Lose** | {state.fertigungskosten_pro_los:.2f} M/Los")

        with p_col2:
            st.write("**Endmontage (Stufe 2)**")
            if state.stufe2_durchgefuehrt:
                st.success("Fertigung erfolgt.")
                menge_s2 = 0.0
            elif verfuegbar_s2 <= 0:
                st.info("Keine unfertigen Erzeugnisse verfügbar.")
                menge_s2 = 0.0
            else:
                if st.session_state.pop("s3_reset", False):
                    st.session_state["s3_s2"] = 0.0
                menge_s2 = st.number_input("Menge (Lose)", min_value=0.0, max_value=verfuegbar_s2, step=1.0, key="s3_s2")
                st.caption(f"Unfertige danach: **{state.unfertige_erzeugnisse - menge_s2:.0f} Lose** | {state.endmontagekosten_stufe_2_pro_los:.2f} M/Los")

        if st.button("🏭 Produktion starten", disabled=(menge_s1 <= 0 and menge_s2 <= 0), type="primary"):
            try:
                if menge_s1 > 0:
                    produktion_stufe_1(state, menge_s1)
                if menge_s2 > 0:
                    endmontage_stufe_2(state, menge_s2)
                st.session_state["s3_reset"] = True
                st.rerun()
            except ValueError as e:
                st.error(str(e))

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
    with st.expander("✅ Produktion"):
        st.success("Erledigt.")

# ─── SCHRITT 4: MATERIALEINKAUF ───────────────────────────────────────────────

if schritt == 4:
    st.markdown("## 📦 Materialeinkauf")

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
    with st.expander("✅ Materialeinkauf"):
        st.success("Erledigt.")

# ─── SCHRITT 5: GEMEINKOSTEN ZAHLEN ───────────────────────────────────────────

if schritt == 5:
    st.markdown("## 📋 Gemeinkosten zahlen")

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
    with st.expander("✅ Gemeinkosten zahlen"):
        st.success("Erledigt.")

# ─── SCHRITT 6: QUARTAL ABSCHLIESSEN ──────────────────────────────────────────

if schritt >= 6:
    st.markdown("## ✅ Quartal abschließen")

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

st.divider()

# ─── HISTORISCHE KENNZAHLEN & CHARTS ──────────────────────────────────────────

if state.kennzahlen_history:
    with st.expander("📊 Historische Kennzahlen & Jahresvergleich"):
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

# ─── VERLAUF ───────────────────────────────────────────────────────────────────

if state.verlauf:
    with st.expander("🗒️ Aktionsprotokoll"):
        for eintrag in reversed(state.verlauf):
            st.write(f"- {eintrag}")
