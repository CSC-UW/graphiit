import numpy as np
import pyphi
import pytest

from graphiit import Graph


def test_connectivity_matrix(fig4_graph):
    true_connectivity_matrix = np.array(
        [[0, 1, 1], [1, 0, 1], [1, 1, 0]]
    )  # Big Endian format
    assert np.all(fig4_graph.connectivity_matrix == true_connectivity_matrix)


def test_graph_instantiation():
    return Graph()


def test_add_from_config(fig4_config):
    graph = test_graph_instantiation()
    graph._add_from_config(config=fig4_config)
    assert graph.nodes() == ["A", "B", "C"], "Nodes out of order"


def test_node_tokens(fig4_graph):
    assert fig4_graph.node_tokens == ["A", "B", "C"]


def test_pyphi_integration(fig4_graph):
    state = (1, 0, 0)
    fig4_graph.state = (1, 0, 0)

    computed_net = fig4_graph.pyphi_network()
    computed_sub = fig4_graph.pyphi_subsystem()

    true_net = pyphi.examples.fig4()
    true_sub = pyphi.Subsystem(true_net, state, true_net.node_indices)

    assert computed_net == true_net
    assert np.array_equal(computed_net.node_labels, ["A", "B", "C"])
    assert computed_sub == true_sub


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
