import numpy as np
import pyphi
import pytest

from graphiit import Graph


def test_connectivity_matrix(fig4_graph):
    true_connectivity_matrix = np.array(
        [[0, 1, 1], [1, 0, 1], [1, 1, 0]]
    )  # Big Endian format
    assert np.all(fig4_graph.cm == true_connectivity_matrix)


def test_graph_instantiation():
    return Graph()


def test_add_from_config(fig4_config):
    graph = test_graph_instantiation()
    graph._add_from_config(config=fig4_config)
    assert list(graph.nodes()) == ["A", "B", "C"], "Nodes out of order"


def test_node_labels(fig4_graph):
    assert fig4_graph.node_labels == ["A", "B", "C"]


def test_pyphi_integration(fig4_graph):
    fig4_graph.state = (1, 0, 0)

    computed_substrate = fig4_graph.pyphi_substrate()

    true_substrate = pyphi.examples.fig4_substrate()

    assert computed_substrate == true_substrate
    assert np.array_equal(computed_substrate.node_labels, ["A", "B", "C"])


def test_tpm(fig4_graph):
    true_le_tpm = np.array(
        [
            [0, 0, 0],
            [0, 0, 1],
            [1, 0, 1],
            [1, 0, 0],
            [1, 0, 0],
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 0],
        ]
    )
    assert np.all(fig4_graph.tpm == true_le_tpm)
