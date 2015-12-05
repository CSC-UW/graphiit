import networkx as nx
from collections import namedtuple, OrderedDict, Iterable
import numpy as np
import pyphi
from pyphi.convert import loli_index2state, holi_index2state
from pyphi.models import Cut


def parse_network_config(net_config):
    NodeConfig = namedtuple('NodeConfig', ['label', 'mechanism', 'inputs'],
                            verbose=False)
    parsed_config = list()
    for node_config in net_config:
        parsed_config.append(NodeConfig(node_config[0],     # label
                                        node_config[1],     # mechanism
                                        node_config[2:]))   # labels of inputs

    return parsed_config


class Network(nx.DiGraph):
    # Edge order NOT preserved!
    node_dict_factory = OrderedDict

    def __init__(self, net_config=[], state_config={}, roi=[]):
        super().__init__()
        self.build_from_config(net_config)
        self.state = self.parse_state_config(state_config)
        self.roi = roi

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
        subsystem.roi = [node for node in subsystem.nodes() if node in self.roi]

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

    def neighborhood(self, node):
        parents = set(self.pred[node])
        children = set(self.succ[node])

        neighborhood = set.union({node}, parents, children)
        neighborhood = self._get_node_ordering(neighborhood)
        return self.subsystem(neighborhood)

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

    def net_first_order_concepts(self, just_phi=False, use_roi=False):
        nodes = self.roi if use_roi else self.nodes()
        concepts = dict()
        for node in nodes:
            concepts[node] = self.node_first_order_concepts(node,
                                                            just_phi=just_phi,
                                                            use_roi=use_roi)
        return concepts

    def node_first_order_concepts(self, node, just_phi=False, use_roi=False):
        blanket = self.markov_blanket(node)
        pyphi_blanket = pyphi.Network(blanket.tpm, blanket.connectivity_matrix)

        if use_roi:
            pyphi_submask = [blanket.index(x) for x in blanket.roi]
        else:
            pyphi_submask = range(len(blanket))

        sub = pyphi.Subsystem(pyphi_blanket, blanket.state, pyphi_submask)
        concept = sub.concept((sub.nodes[blanket.index(node)],))
        return concept.phi if just_phi else concept

    def net_first_order_mip(self):
        cut_effects = dict()
        for cut_node in self.nodes():
            altered_concepts = self.node_first_order_mip(cut_node)
            total_phi_destroyed_by_cut = sum(altered_concepts.values())
            cut_effects[cut_node] = total_phi_destroyed_by_cut

        minimum_loss = min(cut_effects.values())
        for cut_node, loss in cut_effects.items():
            if loss == minimum_loss:
                return (cut_node, loss)

    def node_first_order_mip(self, cut_node):
        "max effect on first order concepts of uniparitioning out a single node"

        neighborhood = self.neighborhood(cut_node)
        altered_concepts = dict()
        for concept_node in neighborhood.nodes():
            blanket = self.markov_blanket(concept_node)
            pyphi_blanket = pyphi.Network(blanket.tpm,
                                          blanket.connectivity_matrix)

            pyphi_concept_node_idx = blanket.index(concept_node)
            pyphi_cut_node_idx = blanket.index(cut_node)
            pyphi_cut_complement_idx = [blanket.index(x) for x in
                                        blanket.nodes() if x is not cut_node]
            outgoing_cut = Cut((pyphi_cut_node_idx,),
                               tuple(pyphi_cut_complement_idx))
            incoming_cut = Cut(tuple(pyphi_cut_complement_idx),
                               (pyphi_cut_node_idx,))

            outgoing_cut_sub = pyphi.Subsystem(pyphi_blanket, blanket.state,
                                               range(len(blanket)),
                                               cut=outgoing_cut)
            incoming_cut_sub = pyphi.Subsystem(pyphi_blanket, blanket.state,
                                               range(len(blanket)),
                                               cut=incoming_cut)
            uncut_sub = pyphi.Subsystem(pyphi_blanket, blanket.state,
                                        range(len(blanket)))

            outgoing_cut_phi = outgoing_cut_sub.phi_max((outgoing_cut_sub.nodes[pyphi_concept_node_idx],))
            incoming_cut_phi = incoming_cut_sub.phi_max((incoming_cut_sub.nodes[pyphi_concept_node_idx],))
            uncut_phi = uncut_sub.phi_max((uncut_sub.nodes[pyphi_concept_node_idx],))

            phi_destroyed = uncut_phi - max(outgoing_cut_phi, incoming_cut_phi)
            if phi_destroyed > 0:
                altered_concepts[concept_node] = phi_destroyed

        return altered_concepts

    def all_possible_holi_states(self):
        # unused
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
