import networkx as nx
from collections import namedtuple, OrderedDict
import numpy as np
import pyphi


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
    node_dict_factory = OrderedDict

    def __init__(self, config=None, label=None):
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
        number_of_states = 2 ** len(self)
        number_of_nodes = len(self)
        tpm = np.zeros([number_of_states, number_of_nodes])
        for state_index in range(number_of_states):
            current_state = pyphi.convert.loli_index2state(state_index,
                                                           number_of_nodes)
            tpm[state_index] = self.next_state(current_state)

        return tpm

    @property
    def node_tokens(self):
        return [str(node) for node in self.nodes()]


def net_first_order_concepts(global_net, global_state):
    global_net_nodes = global_net.nodes()
    concepts = dict()
    for concept_node in global_net_nodes:
        blanket = markov_blanket(global_net, concept_node)
        concept_node_blanket_index = blanket.nodes().index(concept_node)
        print("Node | Blanket | Node Index in Blanket")
        print(concept_node, blanket.nodes(), concept_node_blanket_index)

        tpm = build_tpm(blanket)
        cm = nx.to_numpy_matrix(blanket)
        print ("Connectivity matrix")
        print(cm)
        pyphi_blanket = pyphi.Network(tpm, connectivity_matrix=cm)

        blanket_state = list()
        for node in blanket.nodes():
            node_global_index = global_net_nodes.index(node)
            node_state = global_state[node_global_index]
            blanket_state.append(node_state)
        blanket_state = tuple(blanket_state)

        pyphi_sub = pyphi.Subsystem(pyphi_blanket, blanket_state,
                                    range(len(blanket)))
        concept = pyphi_sub.concept((pyphi_sub.nodes[concept_node_blanket_index],))

        concepts[concept_node] = concept
        print("Cumulative set of concepts")
        print(concepts)

    return concepts


def node_first_order_concepts(net, node):
    blanket = markov_blanket(net, node)

    tpm = build_tpm(blanket)
    cm = nx.to_numpy_matrix(blanket)
    pyphi_net = pyphi.Network(tpm, connectivity_matrix=cm)

    node_index = blanket.nodes().index(node)
    concepts = dict()
    for state_index in range(pyphi_net.num_states):
        current_state = pyphi.convert.holi_index2state(state_index,
                                                       len(blanket))
        pyphi_sub = pyphi.Subsystem(pyphi_net, current_state,
                                    range(len(blanket)))
        concept = pyphi_sub.concept((pyphi_sub.nodes[node_index],))
        if current_state == (0, 0, 0, 0, 0):
            print(concept)
        concepts[current_state] = concept.phi

    print(blanket.nodes())
    return concepts


def global_state(state_config, net):
    if ('on' in state_config) and not ('off' in state_config):
        on_nodes = set(state_config['on'])
    elif ('off' in state_config) and not ('on' in state_config):
        off_nodes = set(state_config['off'])
        all_nodes = set(net.nodes())
        on_nodes = all_nodes - off_nodes
    else:
        raise("State config cannot expliticly specifiy both on and off nodes")

    global_state = np.zeros(len(net))
    for node in on_nodes:
        node_index = net.nodes().index(node)
        global_state[node_index] = 1

    return global_state


