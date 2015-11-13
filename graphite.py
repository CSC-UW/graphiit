import networkx as nx
from collections import namedtuple, OrderedDict
import numpy as np
import pyphi


class OrderedNodeDiGraph(nx.DiGraph):
    node_dict_factory = OrderedDict


def parse_config(net_config):
    NodeSpec = namedtuple('NodeSpec', ['node', 'mechanism', 'inputs'],
                          verbose=False)
    nodes = list()
    for node_config in net_config:
        nodes.append(NodeSpec(node_config[0], node_config[1], node_config[2:]))

    return nodes


def build_network(node_specs):
    net = OrderedNodeDiGraph()

    # add nodes before adding edges, so that they are added in config file order
    for node, mechanism, inputs in node_specs:
        net.add_node(node, mechanism=mechanism)

    # now add edges
    for node, mechanism, inputs in node_specs:
        for input in inputs:
            net.add_edge(input, node)

    return net


def markov_blanket(net, node):
    parents = set(net.pred[node])
    children = set(net.succ[node])
    childrens_parents = set()
    for child in children:
        childrens_parents.update(set(net.pred[child]))

    blanket = set.union(set(node), parents, children, childrens_parents)
    return net.subgraph(sorted(blanket)) # TODO: preserve ordering


def next_state(inet, current_state):
    next_state = np.zeros(len(inet))
    # the following line shouldn't be necessary, but the nx API is broken
    network_mechanisms = nx.get_node_attributes(inet, 'mechanism')
    for node in inet.nodes():
        input_nodes = list(inet.pred[node])
        if len(input_nodes):
            input_vector = [current_state[x] for x in input_nodes]
            next_state[node] = network_mechanisms[node](input_vector)
        else:
            next_state[node] = current_state[node]

    return next_state


def build_tpm(net):
    inet = nx.convert_node_labels_to_integers(net, label_attribute='name')
    number_of_states = 2 ** len(net)
    number_of_nodes = len(net)
    tpm = np.zeros([number_of_states, number_of_nodes])
    for state_index in range(number_of_states):
        current_state = pyphi.convert.loli_index2state(state_index,
                                                       number_of_nodes)
        tpm[state_index] = next_state(inet, current_state)

    print("Mapping of node indicies to node labels")
    print(nx.get_node_attributes(inet, 'name'))
    print("TPM")
    print(tpm)
    return tpm


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


