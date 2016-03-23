import pytest
import pyphi
from graphiit import Network
from graphiit.example_networks import oizumi2014_fig4
from graphiit.utils import * # TODO : name imports explicitly
# TODO : Split testing of utils into its own file

@pytest.fixture
def fig4_graph():
    return Network(oizumi2014_fig4.net_conf)


def test_connectivity_matrix(fig4_graph):
    true_connectivity_matrix = np.array([
        [0, 1, 1],
        [1, 0, 1],
        [1, 1, 0]
    ])  # Holi format
    assert np.all(fig4_graph.connectivity_matrix == true_connectivity_matrix)


def test_network_instantiation():
    return Network()


def test_build_from_config():
    net = test_network_instantiation()
    net.build_from_config(config=oizumi2014_fig4.net_conf)
    assert net.nodes() == ['A', 'B', 'C'], "Nodes out of order"


def test_node_tokens(fig4_graph):
    assert fig4_graph.node_tokens == ['A', 'B', 'C']


def test_format_node_tokens_by_state(fig4_graph):
    state = (1, 0, 0)
    fore = format_node_tokens_by_state(fig4_graph.node_tokens, state, mode='fore')
    print("Tokens formatted by foreground color, should be cyan:red:red")
    print(':'.join(fore))
    back = format_node_tokens_by_state(fig4_graph.node_tokens, state, mode='back')
    print("Tokens formatted by background color, should be white:black:black")
    print(':'.join(back))
    fore_and_back = format_node_tokens_by_state(fore, state, mode='back')
    print("Tokens formatter by both FG and BG.")
    print(':'.join(fore_and_back))


def test_pretty_print_tpm(fig4_graph):
    print("Pretty printing figure 4 TPM")
    pretty_print_tpm(fig4_graph.node_tokens, fig4_graph.tpm)


def test_pyphi_integration(fig4_graph):
    current_state = (1, 0, 0)  # holi format

    computed_net = pyphi.Network(fig4_graph.tpm, fig4_graph.connectivity_matrix)
    computed_sub = pyphi.Subsystem(computed_net, current_state,
                                   range(computed_net.size))

    true_net = pyphi.examples.fig4()
    true_sub = pyphi.Subsystem(true_net, current_state, range(true_net.size))

    assert computed_net == true_net
    assert computed_sub == true_sub


def test_holi_tpm_to_loli():
    holi_tpm = np.array([
        [0, 0, 0],
        [1, 0, 0],
        [1, 0, 1],
        [1, 0, 1],
        [0, 0, 1],
        [1, 1, 1],
        [1, 0, 0],
        [1, 1, 0]
    ])
    true_loli_tpm = np.array([
        [0, 0, 0],
        [0, 0, 1],
        [1, 0, 1],
        [1, 0, 0],
        [1, 0, 0],
        [1, 1, 1],
        [1, 0, 1],
        [1, 1, 0]
    ])
    computed_loli_tpm = convert_holi_tpm_to_loli(holi_tpm)
    assert np.all(computed_loli_tpm == true_loli_tpm)


def test_tpm(fig4_graph):
    true_loli_tpm = np.array([
        [0, 0, 0],
        [0, 0, 1],
        [1, 0, 1],
        [1, 0, 0],
        [1, 0, 0],
        [1, 1, 1],
        [1, 0, 1],
        [1, 1, 0]
    ])
    assert np.all(fig4_graph.tpm == true_loli_tpm)
