from dfa import DFA, parse_list

ENDS_IN_1 = DFA(
    states=["q0", "q1"],
    alphabet=["0", "1"],
    transitions={("q0", "0"): "q0", ("q0", "1"): "q1",
                 ("q1", "0"): "q0", ("q1", "1"): "q1"},
    start="q0",
    accept={"q1"},
)

EVEN_ZEROS = DFA(
    states=["q0", "q1"],
    alphabet=["0", "1"],
    transitions={("q0", "0"): "q1", ("q0", "1"): "q0",
                 ("q1", "0"): "q0", ("q1", "1"): "q1"},
    start="q0",
    accept={"q0"},
)


def test_ends_in_1():
    assert ENDS_IN_1.accepts("1")
    assert ENDS_IN_1.accepts("0101")
    assert not ENDS_IN_1.accepts("10")
    assert not ENDS_IN_1.accepts("")


def test_even_zeros():
    assert EVEN_ZEROS.accepts("")
    assert EVEN_ZEROS.accepts("1010")
    assert not EVEN_ZEROS.accepts("0")


def test_unknown_symbol_rejected():
    steps, accepted = ENDS_IN_1.trace("1x1")
    assert not accepted
    assert steps[-1] == ("q1", "x", None)


def test_trace_and_active_edge():
    steps, _ = ENDS_IN_1.trace("01")
    assert steps == [("q0", "0", "q0"), ("q0", "1", "q1")]
    dot = ENDS_IN_1.to_dot(current="q1", active_edge=("q0", "q1"))
    assert 'color="#f97316"' in dot


def test_validation_errors():
    broken = DFA(["a"], ["0", "1"], {("a", "0"): "a"}, "z", {"y"})
    errors = broken.validate()
    assert any("Missing transition" in e for e in errors)
    assert any("Start state" in e for e in errors)
    assert any("Accepting state" in e for e in errors)


def test_json_round_trip():
    assert DFA.from_dict(ENDS_IN_1.to_dict()) == ENDS_IN_1


def test_parse_list():
    assert parse_list(" q0, q1 ,,q0, q2 ") == ["q0", "q1", "q2"]
