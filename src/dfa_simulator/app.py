"""Streamlit UI for the DFA Simulator (CSET302)."""
import json
import streamlit as st
from dfa import DFA, parse_list

st.set_page_config(page_title="DFA Simulator | CSET302", page_icon="⚙️", layout="wide")

PRESETS = {
    "Ends with '1'": DFA(["q0", "q1"], ["0", "1"], {("q0", "0"): "q0", ("q0", "1"): "q1", ("q1", "0"): "q0", ("q1", "1"): "q1"}, "q0", {"q1"}),
    "Even number of 0s": DFA(["q0", "q1"], ["0", "1"], {("q0", "0"): "q1", ("q0", "1"): "q0", ("q1", "0"): "q0", ("q1", "1"): "q1"}, "q0", {"q0"}),
    "Divisible by 3": DFA(["q0", "q1", "q2"], ["0", "1"], {("q0", "0"): "q0", ("q0", "1"): "q1", ("q1", "0"): "q2", ("q1", "1"): "q0", ("q2", "0"): "q1", ("q2", "1"): "q2"}, "q0", {"q0"}),
}


def state_sig(states):
    return "|".join(states)


def table_sig(states, alphabet):
    return state_sig(states) + "::" + "|".join(alphabet)


def load_into_state(dfa: DFA):
    st.session_state["states_text"] = ", ".join(dfa.states)
    st.session_state["alphabet_text"] = ", ".join(dfa.alphabet)
    st.session_state[f"start::{state_sig(dfa.states)}"] = dfa.start
    st.session_state[f"accept::{state_sig(dfa.states)}"] = sorted(dfa.accept)
    tsig = table_sig(dfa.states, dfa.alphabet)
    for (s, c), t in dfa.transitions.items():
        st.session_state[f"t::{tsig}::{s}::{c}"] = t


if "states_text" not in st.session_state:
    load_into_state(PRESETS["Ends with '1'"])

# ------------------------------------------------------------------ Sidebar
with st.sidebar:
    st.title("⚙️ DFA Simulator")
    st.caption("CSET302 • Automata Theory")

    preset = st.selectbox("Quick Preset", list(PRESETS.keys()))
    if st.button("Load Preset", use_container_width=True):
        load_into_state(PRESETS[preset])
        st.rerun()

    st.divider()
    states = parse_list(st.text_input("States Q (comma-separated)", key="states_text"))
    alphabet = parse_list(st.text_input("Alphabet Σ (single chars)", key="alphabet_text"))

    if not states or not alphabet:
        st.error("Enter at least one state and one symbol.")
        st.stop()
    if any(len(c) != 1 for c in alphabet):
        st.error("Each symbol in Σ must be a single character.")
        st.stop()

    ssig = state_sig(states)
    st.session_state.setdefault(f"start::{ssig}", states[0])
    st.session_state.setdefault(f"accept::{ssig}", [])
    start = st.selectbox("Start state (q₀)", states, key=f"start::{ssig}")
    accept = st.multiselect("Accepting states (F)", states, key=f"accept::{ssig}")

    st.divider()
    uploaded = st.file_uploader("Import DFA (JSON)", type="json")
    if uploaded is not None:
        try:
            loaded = DFA.from_dict(json.loads(uploaded.getvalue()))
            problems = loaded.validate()
        except Exception:
            loaded, problems = None, ["Invalid DFA JSON file."]
        if problems:
            st.error("\n".join(problems))
        elif st.session_state.get("loaded_marker") != (uploaded.name, uploaded.size):
            load_into_state(loaded)
            st.session_state["loaded_marker"] = (uploaded.name, uploaded.size)
            st.rerun()

# Ensure transition defaults exist
tsig = table_sig(states, alphabet)
for s in states:
    for c in alphabet:
        st.session_state.setdefault(f"t::{tsig}::{s}::{c}", s)

# ------------------------------------------------------------------ Main UI
st.title("Deterministic Finite Automaton (DFA) Simulator")
tab_sim, tab_table = st.tabs(["▶ Simulator & Diagram", "📋 Transition Table (δ)"])

with tab_table:
    st.caption("`→` = Start state (q₀) | `*` = Accepting state (F)")
    header = st.columns(len(alphabet) + 1)
    header[0].markdown("**State**")
    for col, c in zip(header[1:], alphabet):
        col.markdown(f"**`{c}`**")

    transitions = {}
    for s in states:
        row = st.columns(len(alphabet) + 1)
        row[0].markdown(f"`{'→' if s == start else ''}{'*' if s in accept else ''}{s}`")
        for col, c in zip(row[1:], alphabet):
            key = f"t::{tsig}::{s}::{c}"
            transitions[(s, c)] = col.selectbox(
                f"δ({s},{c})", states, key=key, label_visibility="collapsed"
            )

dfa = DFA(states, alphabet, transitions, start, set(accept))
if errors := dfa.validate():
    st.error("\n".join(errors))
    st.stop()

st.sidebar.download_button(
    "Export DFA (JSON)",
    json.dumps(dfa.to_dict(), indent=2),
    file_name="dfa.json",
    mime="application/json",
    use_container_width=True,
)

with tab_sim:
    text = st.text_input("Input string (blank = ε)", "0101")
    steps, accepted = dfa.trace(text)
    step = st.slider("Step", 0, len(steps), len(steps)) if steps else 0

    if step == 0:
        current, active_edge = dfa.start, None
    else:
        prev, _, nxt = steps[step - 1]
        current = nxt if nxt is not None else prev
        active_edge = (prev, nxt) if nxt is not None else None

    bad = next((s for s in steps[:step] if s[2] is None), None)
    left, right = st.columns([3, 2])

    with left:
        st.caption("Blue = Current state | Green = Accepting | Orange = Active transition")
        st.graphviz_chart(dfa.to_dot(current, active_edge), use_container_width=True)

    with right:
        if bad:
            st.warning(f"Symbol `{bad[1]}` is not in Σ — rejected.")
        elif step == len(steps):
            if accepted:
                st.success(f"ACCEPTED — ended in `{current}`.")
            else:
                st.error(f"REJECTED — ended in `{current}`.")
        else:
            st.info(f"Step {step} of {len(steps)} — at `{current}`.")

        if steps[:step]:
            st.dataframe(
                [{"Step": i + 1, "From": a, "Symbol": b, "To": c or "Invalid"}
                 for i, (a, b, c) in enumerate(steps[:step])],
                hide_index=True,
                use_container_width=True,
            )
