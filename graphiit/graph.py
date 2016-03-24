import networkx as nx
import numpy as np
import pyphi
from pyphi.convert import loli_index2state, holi_index2state
from pyphi.models import Cut
from . import utils
from collections import OrderedDict

class Graph(nx.DiGraph):
    # Edge order NOT preserved!
    node_dict_factory = OrderedDict

    def __init__(self, graph_config=[], state={}, background_nodes=[]):
        super().__init__()
        self._build_from_config(graph_config)
        self.state = state
        self.background_nodes = background_nodes

    def _build_from_config(self, config):
        parsed_config = utils.parse_graph_config(config)

        # add nodes before adding any edges,
        # so that they are added to the graph in config file order
        for label, mechanism, inputs in parsed_config:
            self.add_node(label, mechanism=mechanism)

        # now add edges
        for label, mechanism, inputs in parsed_config:
            for input in inputs:
                self.add_edge(input, label)

    @property
    def foreground_nodes(self):
        return self.complement(self.background_nodes)

    @foreground_nodes.setter
    def foreground_nodes(self, foreground_nodes):
        self.background_nodes = self.complement(foreground_nodes)

    def complement(self, nodes):
        return [node for node in self.nodes if node not in nodes]

    def subgraph(self, subgraph_nodes):
        subgraph = super().subgraph(nodes)
        subgraph_nodes_indices = self.get_indices(subgraph.nodes())
        subgraph.state = self.state[subgraph_node_indices]
        subgraph.background_nodes = [node for node in subgraph.nodes()
                                     if node in self.background_nodes]

        return subgraph

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
        return self.subgraph(blanket)

    def neighborhood(self, node):
        parents = set(self.pred[node])
        children = set(self.succ[node])

        neighborhood = set.union({node}, parents, children)
        neighborhood = self._get_node_ordering(neighborhood)
        return self.subgraph(neighborhood)

    def get_index(self, node):
        return self.nodes().index(node)

    def get_indicies(self, nodes):
        return [self.get_index(node) for node in nodes]

    def predict_next_state(self, current_state=None):
        if not current_state:
            current_state = self.state

        next_state = np.zeros(len(current_state))
        # the following line shouldn't be necessary, but the nx API is broken
        network_mechanisms = nx.get_node_attributes(self, 'mechanism')
        for node in self.nodes():
            node_index = self.get_index(node)
            input_nodes = list(self.pred[node])
            if len(input_nodes):
                input_vector = [current_state[self.get_index(x)] for x in
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

    def pyphi_network(self):
        return pyphi.Network(self.tpm, self.connectivity_matrix)

    def pyphi_subsystem(self):
        net = pyphi.Network(self.tpm, self.connectivity_matrix)
        foreground_node_indices = self.get_indices(self.foreground_nodes)
        return pyphi.Subsystem(net, self.state, foreground_node_indices)

    def all_possible_holi_states(self):
        # unused
        state_index = 0
        number_of_nodes = len(self)
        number_of_states = 2 ** len(self)
        while state_index < number_of_states:
            yield holi_index2state(state_index, number_of_nodes)
            state_index += 1

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        if isinstance(state, list):
            self._state = np.array(state)
        elif isinstance(state, np.ndarray):
            self._state = state
        elif isinstance(state, dict):
            self._state = utils.parse_state_config(self, state)
        else:
            raise("Unrecognized state specification")
