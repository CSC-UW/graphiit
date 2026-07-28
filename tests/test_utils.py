import numpy as np
import pytest

from graphiit import Graph
from graphiit.example_graphs import oizumi2014_fig4
from graphiit.node_functions import NOT, XOR
from graphiit.utils import (
    NodeConfig,
    parse_graph_config,
    format_node_labels_by_state,
    pretty_print_tpm,
)


def test_format_node_labels_by_state(fig4_graph):
    state = (1, 0, 0)
    fore = format_node_labels_by_state(fig4_graph.node_labels, state, mode="fore")
    print("Tokens formatted by foreground color, should be cyan:red:red")
    print(":".join(fore))
    back = format_node_labels_by_state(fig4_graph.node_labels, state, mode="back")
    print("Tokens formatted by background color, should be white:black:black")
    print(":".join(back))
    fore_and_back = format_node_labels_by_state(fore, state, mode="back")
    print("Tokens formatter by both FG and BG.")
    print(":".join(fore_and_back))


def test_pretty_print_tpm(fig4_graph):
    print("Pretty printing figure 4 TPM")
    pretty_print_tpm(fig4_graph.node_labels, fig4_graph.tpm)


def test_parse_graph_config():
    config = [["A", "XOR", "B", "A"], ["B", "NOT", "A"]]
    assert parse_graph_config(config) == [
        NodeConfig("A", XOR, ["B", "A"]),
        NodeConfig("B", NOT, ["A"]),
    ]

    # Input 'D' is not actually specified as a node
    config = [["A", "XOR", "B", "C"], ["B", "NOT", "D"]]
    with pytest.raises(ValueError):
        parse_graph_config(config)

    # Duplicate specification of node 'A'
    config = [["A", "NOT", "A"], ["A", "COPY", "A"]]
    with pytest.raises(ValueError):
        parse_graph_config(config)


def test_parse_state():
    graph = Graph(oizumi2014_fig4.graph_config)

    # State too large
    with pytest.raises(ValueError):
        graph.parse_state((0, 1, 0, 1))

    expected = {"A": 0, "B": 1, "C": 0}
    assert graph.parse_state((0, 1, 0)) == expected
    assert graph.parse_state([0, 1, 0]) == expected
    assert graph.parse_state({"on": ["B"]}) == expected
    assert graph.parse_state({"off": ["A", "C"]}) == expected

    # Set-and-read-back round trip
    graph.set_state({"on": ["B"]})
    assert np.array_equal(graph.get_state_array(dtype=int), (0, 1, 0))

    # Can't specify both on and off states
    with pytest.raises(ValueError):
        graph.parse_state({"off": ["A", "C"], "on": ["B"]})
