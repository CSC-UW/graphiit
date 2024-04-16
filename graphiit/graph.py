from __future__ import annotations
from collections import OrderedDict
from typing import Callable

import networkx as nx
import numpy as np
import pyphi

from . import utils


class Graph(nx.DiGraph):
    """A malleable IIT graph object supporting easy PyPhi calls.

    Keyword Args:
        graph_config (list(tuple)): Config specifying nodes, labels, and edges.
        state (np.array, list, or dict): The state of the graph.
        background_nodes (list): A list of nodes to treat as background.

    Attributes:
        state (np.array): Current state of the graph.
        background_nodes (list): Nodes currently treated as background.
        foreground_nodes (list): All nodes not currently treated as background.
        tpm (np.array): State-by-node TPM of the full system. Not conditioned on background nodes!
        cm (np.array): Connectivity matrix of full system.
        node_labels (list): Node IDs
    """

    # Nodes will be in Graph.nodes() in the same order as they were added to the
    #   graph. Order will be preserved by all networkx methods. NO guarantees
    #   are made about edge order.
    node_dict_factory = OrderedDict

    def __init__(self, graph_config=None, state=None, background_nodes=None):
        """Construct a graph."""
        super().__init__()
        graph_config = graph_config or []
        self.config = graph_config
        self._add_from_config(self.config)
        self.state = state or {}
        self.background_nodes = background_nodes or []

    def _add_from_config(self, config):
        """Enlarge this graph with nodes and edges specified in a Python
        configuration object.

        Args:
            config (list(tuple)): Specifies nodes, edges, and labels to add.
        """
        parsed_config = utils.parse_graph_config(config)

        # add nodes before adding any edges,
        # so that they are added to the graph in config file order
        for index, (label, node_fn, inputs) in enumerate(parsed_config):
            self.add_node(label, function=node_fn, index=index)

        # now add edges
        for label, node_fn, inputs in parsed_config:
            for input in inputs:
                self.add_edge(input, label)

    def __repr__(self):
        return f"Graph({self.config})"

    def __str__(self):
        return repr(self)

    def parents(self, node) -> list:
        """Return the parents of the given node.j"""
        return list(self.pred[node])

    def children(self, node) -> list:
        """Return the children of the given node."""
        return list(self.succ[node])

    @property
    def foreground_nodes(self) -> list:
        """All nodes not treated as background."""
        return self.complement(self.background_nodes)

    @foreground_nodes.setter
    def foreground_nodes(self, foreground_nodes):
        self.background_nodes = self.complement(foreground_nodes)

    def complement(self, nodes) -> list:
        """Return all nodes not in the list provided."""
        return [node for node in self.nodes() if node not in nodes]

    def subgraph(self, subgraph_nodes) -> Graph:
        """Create a subgraph containing only the nodes provided and edges
        between them. Background nodes and state are inherited."""
        subgraph = super().subgraph(subgraph_nodes)
        subgraph_node_indices = self.get_indices(subgraph.nodes())
        subgraph.state = self.state[subgraph_node_indices]
        subgraph.background_nodes = [
            node for node in subgraph.nodes() if node in self.background_nodes
        ]

        return subgraph

    def _get_node_ordering(self, unordered_nodes) -> list:
        """Sort the provided nodes according to their order in the graph."""
        return [node for node in self.nodes() if node in unordered_nodes]

    def markov_blanket(self, node) -> Graph:
        """Yield a subgraph induced on the node, its parents, children, and
        children's parents."""
        parents = set(self.pred[node])
        children = set(self.succ[node])
        childrens_parents = set()
        for child in children:
            childrens_parents.update(set(self.pred[child]))

        blanket = set.union({node}, parents, children, childrens_parents)
        blanket = self._get_node_ordering(blanket)
        return self.subgraph(blanket)

    def neighborhood(self, node) -> Graph:
        """Yield a subgraph induced on the node, its parents, and children."""
        parents = set(self.pred[node])
        children = set(self.succ[node])

        neighborhood = set.union({node}, parents, children)
        neighborhood = self._get_node_ordering(neighborhood)
        return self.subgraph(neighborhood)

    def get_index(self, node):
        """Get the index of a single node, according to the graph's node order."""
        return self.nodes[node]["index"]

    def get_indices(self, nodes: list = None) -> list[int]:
        """Get a a list of node indices according to graph order. The ith entry
        in the returned list is the index of the ith node in the input list.
        PyPhi networks spawned using Graph methods maintain these node
        indices."""
        if nodes is None:
            nodes = self.nodes()
        return [self.get_index(node) for node in nodes]

    def get_node_functions(self) -> list[Callable]:
        """Return the functions of the graph nodes."""
        return nx.get_node_attributes(self, "function")

    def tic(self, timesteps: int = 1) -> np.ndarray:
        """Evolve the system's state according to its node functions.

        Keyword Args:
            timesteps (int): The number of iterations to evolve. Default is 1.
        """
        for t in range(timesteps):
            self.state = self.predict_next_state(current_state=self.state)

    @property
    def tpm(self) -> np.ndarray:
        """Yield the State-by-Node TPM for the full system.

        Not conditioned on background nodes. Can piped directly into PyPhi
        """
        n = len(self)
        tpm = np.zeros([2**n, n])

        for i, state in enumerate(pyphi.utils.all_states(n)):
            tpm[i] = self.predict_next_state(current_state=state)

        return tpm

    @property
    def cm(self) -> np.ndarray:
        """Yields a connectivity matrix. Can be piped right into PyPhi."""
        return nx.adjacency_matrix(self).todense()

    @property
    def node_labels(self) -> list:
        "Not guaranteed to be strings."
        return [node for node in self.nodes()]

    def pyphi_network(self) -> pyphi.Network:
        """Yield a PyPhi network corresponding to the graph. PyPhi node indices
        will match graph node indices."""
        return pyphi.Network(self.tpm, self.cm, self.node_labels)

    def pyphi_subsystem(self) -> pyphi.Subsystem:
        """Yield a PyPhi subsystem corresponding to the graph in its current
        state. Background nodes are frozen in PyPhi. PyPhi node indicies
        match graph node indices."""
        net = self.pyphi_network()
        foreground_node_indices = self.get_indices(self.foreground_nodes)
        raise NotImplementedError("This method is not yet implemented for IIT 4.0")

    @property
    def state(self) -> np.ndarray:
        """The current state of the system.

        Getting this property always yields a numpy array for easy calls to
        PyPhi, but setting is flexible.
        Example 1: graph.state = np.array([0, 0, 1])
        Example 2: graph.state = [0, 0, 1]
        Example 3: graph.state = {'on' : ['C']}
        """
        return self._state.astype(int)

    def get_state(self, nodes: list = None) -> np.ndarray:
        return self.state[self.get_indices(nodes)]

    @state.setter
    def state(self, state):
        self._state = self.parse_state_config(state)

    # TODO: Allow current_state to be specified using a config.
    def predict_next_state(self, current_state: np.ndarray = None) -> np.ndarray:
        """Yield the next state of the graph, given a current state.

        Memory friendly: doesn't require a TPM.
        """
        if current_state is None:
            current_state = self.state
        next_state = np.zeros(len(current_state))
        network_mechanisms = self.get_node_functions()
        for node in self.nodes():
            node_index = self.get_index(node)
            input_nodes = self.parents(node)
            if input_nodes:
                input_vector = [current_state[self.get_index(x)] for x in input_nodes]
                node_mechanism = network_mechanisms[node]
                next_state[node_index] = node_mechanism(input_vector)
            else:
                # Here we define the state of an inputless node as persistent.
                #   This may not be your intented behavior!
                next_state[node_index] = current_state[node_index]

        return next_state

    def parse_state_config(self, state_config) -> np.ndarray:
        """Parse a state configuration into an actual state."""
        if isinstance(state_config, np.ndarray) and state_config.size == 0:
            return None

        if isinstance(state_config, (tuple, list, dict)) and not state_config:
            return None

        if isinstance(state_config, (tuple, list, np.ndarray)):
            if len(self) != len(state_config):
                raise ValueError(
                    "Mis-sized state config. States passed in tuple form must "
                    "specify the state of every node in the graph, no more."
                )
            return np.array(state_config)

        if ("on" in state_config) and not ("off" in state_config):
            on_nodes = set(state_config["on"])
        elif ("off" in state_config) and not ("on" in state_config):
            off_nodes = set(state_config["off"])
            all_nodes = set(self.nodes())
            on_nodes = all_nodes - off_nodes
        else:
            raise ValueError("State config cannot specifiy both on and off nodes")

        global_state = np.zeros(len(self))
        global_state[self.get_indices(on_nodes)] = 1

        return global_state
