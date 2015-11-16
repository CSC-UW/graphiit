import networkx as nx
from collections import namedtuple, OrderedDict, Iterable
import numpy as np
import pyphi
from pyphi.convert import loli_index2state, holi_index2state, state2holi_index

def convert_holi_tpm_to_loli(holi_tpm):
    # Assumes state by node format
    states, nodes = holi_tpm.shape
    loli_tpm = np.zeros([states, nodes])
    for i in range(states):
        loli_state = loli_index2state(i, nodes)
        holi_tpm_row = state2holi_index(loli_state)
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
        current_state = loli_index2state(state_index, number_of_nodes)
        next_state = tpm[state_index, :]
        pretty_tokens = format_node_tokens_by_state(node_tokens, current_state,
                                                    mode='back')
        pretty_tokens = format_node_tokens_by_state(pretty_tokens, next_state,
                                                    mode='fore')
        print(':'.join(pretty_tokens))


class Network(nx.DiGraph):
    # Edge order NOT preserved!
    node_dict_factory = OrderedDict

    def __init__(self, net_config=[], state_config={}):
        super().__init__()
        self.build_from_config(net_config)
        self.state = self.parse_state_config(state_config)

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

    def subsystem(self, subsystem_nodes):
        subsystem = super().subgraph(subsystem_nodes)
        subsystem.state = tuple([self.state[self.index(node)] for node in
                                subsystem.nodes()])

        return subsystem

    def _get_node_ordering(self, unordered_nodes):
        return [node for node in self.nodes() if node in unordered_nodes]

    def markov_blanket(self, node):
        parents = set(self.pred[node])
        children = set(self.succ[node])
        childrens_parents = set()
        for child in children:
            childrens_parents.update(set(self.pred[child]))

        blanket = set.union({node}, parents, children, childrens_parents)
        blanket = self._get_node_ordering(blanket)
        return self.subsystem(blanket)

    def index(self, node):
        return self.nodes().index(node)

    def predict_next_state(self, current_state=None):
        if not current_state:
            current_state = self.state

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

    def tic(self, current_state=None):
        self.state = self.predict_next_state(current_state)

    @property
    def tpm(self):
        return self.loli_tpm

    @property
    def loli_tpm(self):
        number_of_states = 2 ** len(self)
        number_of_nodes = len(self)
        tpm = np.zeros([number_of_states, number_of_nodes])
        for state_index in range(number_of_states):
            current_state = loli_index2state(state_index, number_of_nodes)
            tpm[state_index] = self.predict_next_state(current_state)

        return tpm

    @property
    def connectivity_matrix(self):
        return nx.to_numpy_matrix(self)

    @property
    def node_tokens(self):
        return [str(node) for node in self.nodes()]

    def net_first_order_concepts(self, just_phi=False):
        nodes = self.nodes()
        concepts = dict()
        for node in nodes:
            concepts[node] = self.node_first_order_concepts(node,
                                                            states='blanket',
                                                            just_phi=just_phi)
        return concepts

    def node_first_order_concepts(self, node, states='blanket', just_phi=False):
        """
        Args:
            states (str): 'all' or 'blanket'
        """
        blanket = self.markov_blanket(node)
        pyphi_blanket = pyphi.Network(blanket.tpm,
                                      blanket.connectivity_matrix)
        if states is 'all':
            concepts = dict()
            for state in self.all_possible_holi_states():
                sub = pyphi.Subsystem(pyphi_blanket, state, range(len(blanket)))
                concept = sub.concept((sub.nodes[blanket.index(node)],))
                concepts[state] = concept.phi if just_phi else concept
            return concepts
        elif states is 'blanket':
            sub = pyphi.Subsystem(pyphi_blanket, blanket.state,
                                                 range(len(blanket)))
            concept = sub.concept((sub.nodes[blanket.index(node)],))
            return concept.phi if just_phi else concept
        else:
            raise("Argument not recognized: %s.", states)

    def all_possible_holi_states(self):
        state_index = 0
        number_of_nodes = len(self)
        number_of_states = 2 ** len(self)
        while state_index < number_of_states:
            yield holi_index2state(state_index, number_of_nodes)
            state_index += 1

    def parse_state_config(self, state_config):
        if not state_config:
            return None
        else:
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
