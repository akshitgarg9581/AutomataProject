# DFA Simulator — CSET302

## Overview
An interactive web-based Deterministic Finite Automaton (DFA) simulator built with Python and Streamlit for the **CSET302 – Automata Theory and Computability** project.

## Supported Features
- Define states ($Q$), alphabet ($\Sigma$), start state ($q_0$), accepting states ($F$), and transition table ($\delta$)
- Built-in **Quick Presets** (*Ends with '1'*, *Even number of 0s*, *Divisible by 3*)
- Step-by-step string simulation with an execution slider and trace table
- Live **Graphviz State Diagram** highlighting the current state (blue), accepting states (green), and active transition arrow (orange)
- Import / Export DFA definitions as JSON

## Technology Stack
- Python `>= 3.10`
- `streamlit`
- `pytest`

## Installation
```bash
pip install streamlit pytest
```

## How to Run
```bash
cd src/dfa_simulator
python -m streamlit run app.py
```

## Project Structure
| File | Purpose |
| --- | --- |
| `src/dfa_simulator/dfa.py` | Core DFA logic: validation, trace, Graphviz DOT generation, JSON serialization. |
| `src/dfa_simulator/app.py` | Streamlit web interface (2-tab layout, presets, sidebar controls). |
| `src/dfa_simulator/test_dfa.py` | Automated `pytest` unit tests. |
| `src/dfa_simulator/.streamlit/config.toml` | Custom dark-blue UI theme. |

## Testing
```bash
cd src/dfa_simulator
python -m pytest -v
```

## Known Limitations
- DFAs must be complete (no implicit trap state).
- Alphabet symbols must be single characters.
- Symbols outside $\Sigma$ immediately halt and reject the string.
