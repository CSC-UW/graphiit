import networkx as nx
import numpy as np
from pyphi.convert import le_index2state, state2be_index
from collections import namedtuple

from . import micro_mechanisms


def predict_next_state(graph, current_state):
    # TODO: Allow current_state to be specified using a config.
    """Yield the next state of a graph, given a current state.
       Memory friendly: doesn't require a TPM."""

    next_state = np.zeros(len(current_state))
    # the following line shouldn't be necessary, but the nx API is broken
    network_mechanisms = nx.get_node_attributes(graph, 'mechanism')
    for node in graph.nodes():
        node_index = graph.get_index(node)
        input_nodes = list(graph.pred[node])
        if len(input_nodes):
            input_vector = [current_state[graph.get_index(x)] for x in
                            input_nodes]
            node_mechanism = network_mechanisms[node]
            next_state[node_index] = node_mechanism(input_vector)
        else:
            # Here we define the state of an inputless node as persistent.
            #   This may not be your intented behavior!
            next_state[node_index] = current_state[node_index]

    return next_state


def parse_state_config(graph, state_config):
    """Parse a state configuration into an actual state."""
    if not state_config:
        return None

    if isinstance(state_config, (tuple, list, np.ndarray)):
        if len(graph) != len(state_config):
            raise ValueError(
                "Mis-sized state config. States passed in tuple form must "
                "specify the state of every node in the graph, no more.")
        return np.array(state_config)

    if ('on' in state_config) and not ('off' in state_config):
        on_nodes = set(state_config['on'])
    elif ('off' in state_config) and not ('on' in state_config):
        off_nodes = set(state_config['off'])
        all_nodes = set(graph.nodes())
        on_nodes = all_nodes - off_nodes
    else:
        raise ValueError(
            "State config cannot specifiy both on and off nodes")

    global_state = np.zeros(len(graph))
    global_state[graph.get_indices(on_nodes)] = 1

    return global_state


NodeConfig = namedtuple('NodeConfig', ['label', 'mechanism', 'inputs'])


def parse_graph_config(graph_config):
    """Parse a graph configuration list.

    Returns:
        list[NodeConfig]
    """
    all_labels = []
    all_inputs = set()

    parsed_config = []
    for node_config in graph_config:

        label = node_config[0]
        inputs = node_config[2:]

        all_labels.append(label)
        all_inputs.update(inputs)

        if isinstance(node_config[1], str):
            mechanism = micro_mechanisms.MAP[node_config[1]]
        else:
            mechanism = node_config[1]

        parsed_config.append(NodeConfig(label, mechanism, inputs))

    if all_inputs - set(all_labels):
        raise ValueError(
            'Nodes {} are given as inputs but are not specified as nodes in '
            'the graph'.format(all_inputs - set(all_labels)))

    if len(all_labels) != len(set(all_labels)):
        raise ValueError('Duplicate node labels provided')

    return parsed_config


def format_node_tokens_by_state(tokens, states, mode='fore'):
    assert len(tokens) is len(states)
    assert mode is 'fore' or 'back'

    CYAN_FORE = '\033[36m'
    RED_FORE = '\033[31m'
    WHITE_BACK = '\033[47m'
    BLACK_BACK = '\033[40m'
    END = '\033[0m'

    new_tokens = list()
    for token, state in zip(tokens, states):
        if state and mode is 'fore':
            new_tokens.append(CYAN_FORE + token + END)
        if state and mode is 'back':
            new_tokens.append(WHITE_BACK + token + END)
        if not state and mode is 'fore':
            new_tokens.append(RED_FORE + token + END)
        if not state and mode is 'back':
            new_tokens.append(BLACK_BACK + token + END)

    return new_tokens


def pretty_print_tpm(node_tokens, tpm):
    number_of_states, number_of_nodes = tpm.shape
    for state_index in range(number_of_states):
        current_state = le_index2state(state_index, number_of_nodes)
        next_state = tpm[state_index, :]
        pretty_tokens = format_node_tokens_by_state(node_tokens, current_state,
                                                    mode='back')
        pretty_tokens = format_node_tokens_by_state(pretty_tokens, next_state,
                                                    mode='fore')
        print(':'.join(pretty_tokens))


def convert_be_tpm_to_le(be_tpm):
    # Assumes state by node format
    states, nodes = be_tpm.shape
    le_tpm = np.zeros([states, nodes])
    for i in range(states):
        le_state = le_index2state(i, nodes)
        be_tpm_row = state2be_index(le_state)
        le_tpm[i, :] = be_tpm[be_tpm_row, :]

    return le_tpm
