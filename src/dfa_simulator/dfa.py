"""Core DFA logic (no UI dependencies)."""
from dataclasses import dataclass


def parse_list(text: str) -> list[str]:
    """Turn 'q0, q1, q2' into unique trimmed items."""
    seen, items = set(), []
    for raw in text.split(","):
        item = raw.strip()
        if item and item not in seen:
            seen.add(item)
            items.append(item)
    return items


@dataclass
class DFA:
    states: list[str]
    alphabet: list[str]
    transitions: dict[tuple[str, str], str]
    start: str
    accept: set[str]

    def validate(self) -> list[str]:
        """Return a list of validation errors (empty if DFA is valid)."""
        errors = []
        if not self.states:
            errors.append("Add at least one state.")
        if not self.alphabet:
            errors.append("Add at least one input symbol.")
        if self.start not in self.states:
            errors.append(f"Start state '{self.start}' is not in states.")
        for acc in sorted(self.accept - set(self.states)):
            errors.append(f"Accepting state '{acc}' is not in states.")
        for s in self.states:
            for c in self.alphabet:
                target = self.transitions.get((s, c))
                if target is None:
                    errors.append(f"Missing transition for ({s}, {c}).")
                elif target not in self.states:
                    errors.append(f"Transition ({s}, {c}) points to unknown state '{target}'.")
        return errors

    def trace(self, string: str):
        """Simulate the DFA on `string` and return (steps, accepted)."""
        state, steps = self.start, []
        for ch in string:
            nxt = self.transitions.get((state, ch)) if ch in self.alphabet else None
            steps.append((state, ch, nxt))
            if nxt is None:
                return steps, False
            state = nxt
        return steps, state in self.accept

    def accepts(self, string: str) -> bool:
        return self.trace(string)[1]

    def to_dot(self, current: str | None = None, active_edge: tuple[str, str] | None = None) -> str:
        """Build Graphviz DOT graph with current state and active transition highlighted."""
        lines = [
            "digraph DFA {",
            "  rankdir=LR;",
            '  bgcolor="transparent";',
            '  node [fontname="Helvetica", color="#475569"];',
            '  edge [fontname="Helvetica", color="#64748b", fontcolor="#334155"];',
            '  __start [shape=point, color="#2563eb"];',
        ]
        for s in self.states:
            shape = "doublecircle" if s in self.accept else "circle"
            if s == current:
                style = 'style=filled, fillcolor="#2563eb", fontcolor="white", color="#1d4ed8"'
            elif s in self.accept:
                style = 'style=filled, fillcolor="#dcfce7", color="#16a34a"'
            else:
                style = 'style=filled, fillcolor="#f8fafc"'
            lines.append(f'  "{s}" [shape={shape}, {style}];')

        lines.append(f'  __start -> "{self.start}" [color="#2563eb"];')

        grouped: dict[tuple[str, str], list[str]] = {}
        for (s, c), t in self.transitions.items():
            grouped.setdefault((s, t), []).append(c)
        for (s, t), syms in grouped.items():
            edge_style = ', color="#f97316", penwidth=2.4' if active_edge == (s, t) else ""
            lines.append(f'  "{s}" -> "{t}" [label="{",".join(syms)}"{edge_style}];')
        lines.append("}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "states": self.states,
            "alphabet": self.alphabet,
            "start": self.start,
            "accept": sorted(self.accept),
            "transitions": [[s, c, t] for (s, c), t in self.transitions.items()],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DFA":
        return cls(
            states=list(data["states"]),
            alphabet=list(data["alphabet"]),
            transitions={(s, c): t for s, c, t in data["transitions"]},
            start=data["start"],
            accept=set(data["accept"]),
        )
