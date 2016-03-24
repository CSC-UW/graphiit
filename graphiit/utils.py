import networkx as nx
import numpy as np
from itertools import chain, combinations
from pyphi.convert import loli_index2state, holi_index2state, state2holi_index
from collections import namedtuple

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
    if not state_config:
        return None
    else:
        if ('on' in state_config) and not ('off' in state_config):
            on_nodes = set(state_config['on'])
        elif ('off' in state_config) and not ('on' in state_config):
            off_nodes = set(state_config['off'])
            all_nodes = set(graph.nodes())
            on_nodes = all_nodes - off_nodes
        else:
            raise("State config cannot expliticly specifiy both on and off \
                  nodes")

    global_state = np.zeros(len(graph))
    global_state[graph.get_indicies(on_nodes)] = 1

    return global_state

def parse_graph_config(graph_config):
    NodeConfig = namedtuple('NodeConfig', ['label', 'mechanism', 'inputs'],
                            verbose=False)
    parsed_config = list()
    for node_config in graph_config:
        parsed_config.append(NodeConfig(node_config[0],     # label
                                        node_config[1],     # mechanism
                                        node_config[2:]))   # labels of inputs

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
        current_state = loli_index2state(state_index, number_of_nodes)
        next_state = tpm[state_index, :]
        pretty_tokens = format_node_tokens_by_state(node_tokens, current_state,
                                                    mode='back')
        pretty_tokens = format_node_tokens_by_state(pretty_tokens, next_state,
                                                    mode='fore')
        print(':'.join(pretty_tokens))


def convert_holi_tpm_to_loli(holi_tpm):
    # Assumes state by node format
    states, nodes = holi_tpm.shape
    loli_tpm = np.zeros([states, nodes])
    for i in range(states):
        loli_state = loli_index2state(i, nodes)
        holi_tpm_row = state2holi_index(loli_state)
        loli_tpm[i, :] = holi_tpm[holi_tpm_row, :]

    return loli_tpm

def all_possible_holi_states(graph):
    # unused
    state_index = 0
    number_of_nodes = len(graph)
    number_of_states = 2 ** len(graph)
    while state_index < number_of_states:
        yield holi_index2state(state_index, number_of_nodes)
        state_index += 1

def powerset(iterable):
    # unused
    # https://docs.python.org/2/library/itertools.html
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


def bit(boolean):
    # unused
    return int(boolean)
