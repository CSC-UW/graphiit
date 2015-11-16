import networkx as nx
from collections import namedtuple, OrderedDict, Iterable
import numpy as np
import pyphi


def convert_holi_tpm_to_loli(holi_tpm):
    # Assumes state by node format
    states, nodes = holi_tpm.shape
    loli_tpm = np.zeros([states, nodes])
    for i in range(states):
        loli_state = pyphi.convert.loli_index2state(i, nodes)
        holi_tpm_row = pyphi.convert.state2holi_index(loli_state)
        loli_tpm[i, :] = holi_tpm[holi_tpm_row, :]

    return loli_tpm


def parse_network_config(net_config):
    NodeConfig = namedtuple('NodeConfig', ['label', 'mechanism', 'inputs'],
                            verbose=False)
    parsed_config = list()
    for node_config in net_config:
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
        current_state = pyphi.convert.loli_index2state(state_index,
                                                       number_of_nodes)
        next_state = tpm[state_index, :]
        pretty_tokens = format_node_tokens_by_state(node_tokens, current_state,
                                                    mode='back')
        pretty_tokens = format_node_tokens_by_state(pretty_tokens, next_state,
                                                    mode='fore')
        print(':'.join(pretty_tokens))


class Network(nx.DiGraph):
    # Edge order NOT preserved!
    node_dict_factory = OrderedDict

    def __init__(self, config=[], label=None):
        super().__init__()
        self.label = label
        self.build_from_config(config)

    def build_from_config(self, config):
        parsed_config = parse_network_config(config)

        # add nodes before adding any edges,
        # so that they are added to the graph in config file order
        for label, mechanism, inputs in parsed_config:
            self.add_node(label, mechanism=mechanism)

        # now add edges
        for label, mechanism, inputs in parsed_config:
            for input in inputs:
                self.add_edge(input, label)

    def _get_node_ordering(self, unordered_nodes):
        return [node for node in self.nodes() if node in unordered_nodes]

    def markov_blanket(self, node):
        parents = set(self.pred[node])
        children = set(self.succ[node])
        childrens_parents = set()
        for child in children:
            childrens_parents.update(set(self.pred[child]))

        blanket = set.union(set(node), parents, children, childrens_parents)
        blanket = self._get_node_ordering(blanket)
        return self.subgraph(blanket)

    def index(self, node):
        return self.nodes().index(node)

    def next_state(self, current_state):
        next_state = np.zeros(len(current_state))
        # the following line shouldn't be necessary, but the nx API is broken
        network_mechanisms = nx.get_node_attributes(self, 'mechanism')
        for node in self.nodes():
            node_index = self.index(node)
            input_nodes = list(self.pred[node])
            if len(input_nodes):
                input_vector = [current_state[self.index(x)] for x in
                                input_nodes]
                node_mechanism = network_mechanisms[node]
                next_state[node_index] = node_mechanism(input_vector)
            else:
                # TODO: Is this right?
                next_state[node_index] = current_state[node_index]

        return next_state

    @property
    def tpm(self):
        return self.loli_tpm

    @property
    def loli_tpm(self):
        number_of_states = 2 ** len(self)
        number_of_nodes = len(self)
        tpm = np.zeros([number_of_states, number_of_nodes])
        for state_index in range(number_of_states):
            current_state = pyphi.convert.loli_index2state(state_index,
                                                           number_of_nodes)
            tpm[state_index] = self.next_state(current_state)

        return tpm

    @property
    def connectivity_matrix(self):
        return nx.to_numpy_matrix(self)

    @property
    def node_tokens(self):
        return [str(node) for node in self.nodes()]

    def subsystem_state(self, subsystem, my_state):
        subsystem_state = list()
        for node in subsystem:
            subsystem_state.append(my_state[self.index(node)])

        return tuple(subsystem_state)

    def net_first_order_concepts(self, state, just_phi=False):
        nodes = self.nodes()
        concepts = dict()
        for node in nodes:
            blanket = self.markov_blanket(node)
            pyphi_blanket = pyphi.Network(blanket.tpm,
                                          blanket.connectivity_matrix)
            blanket_state = self.subsystem_state(blanket, state)
            pyphi_sub = pyphi.Subsystem(pyphi_blanket, blanket_state,
                                        range(len(blanket)))
            concept = pyphi_sub.concept((pyphi_sub.nodes[blanket.index(node)],))
            concepts[node] = concept.phi if just_phi else concept

        return concepts

    def node_first_order_concepts(self, node, states='all', just_phi=False):
        # states are blanket states
        # TODO: accept system states
        # states must be in holi format
        blanket = self.markov_blanket(node)
        pyphi_blanket = pyphi.Network(blanket.tpm,
                                      blanket.connectivity_matrix)
        if states is 'all':
            states = [pyphi.convert.holi_index2state(i, len(blanket))
                      for i in range(pyphi_blanket.num_states)]
        else:
            assert type(states) is list, "states must be a list of states"
            assert all([isinstance(state, Iterable) for state in states]), \
                "each state must be iterable"

        concepts = dict()
        for state in states:
            pyphi_sub = pyphi.Subsystem(pyphi_blanket, state,
                                        range(len(blanket)))
            concept = pyphi_sub.concept((pyphi_sub.nodes[blanket.index(node)],))
            concepts[state] = concept.phi if just_phi else concept

        return concepts

    def parse_state_config(self, state_config):
        if ('on' in state_config) and not ('off' in state_config):
            on_nodes = set(state_config['on'])
        elif ('off' in state_config) and not ('on' in state_config):
            off_nodes = set(state_config['off'])
            all_nodes = set(self.nodes())
            on_nodes = all_nodes - off_nodes
        else:
            raise("State config cannot expliticly specifiy both on and off \
                  nodes")

        global_state = np.zeros(len(self))
        for node in on_nodes:
            global_state[self.index(node)] = 1

        return global_state
