import networkx as nx
import numpy as np
import pyphi
from pyphi.convert import loli_index2state
from pyphi.models import Cut
from . import utils
from collections import OrderedDict

class Graph(nx.DiGraph):
    """ A malleable IIT graph object supporting easy PyPhi calls.

    Keyword Args:
        graph_config (list(tuple)): Config specifying nodes, labels, and edges.
        state (np.array, list, or dict): The state of the graph.
        background_nodes (list): A list of nodes to freeze as background.

    Attributes:
        state (np.array): Current state of the graph.
        background_nodes (list): Nodes currently frozen as background.
        foreground_nodes (list): All nodes not currently frozen as background.
        tpm (np.array): State-by-node TPM of the full system in LOLI format.
            Not conditioned on background elements!
        connectivity_matrix (np.array): Connectivity matrix of full system.
        node_tokens (list(str)): Printable node IDs in case you didn't give them
            string objects
    """
    # Nodes will be in Graph.nodes() in the same order as they were added to the
    #   graph. Order will be preserved by all networkx methods. NO guarantees
    #   are made about edge order.
    node_dict_factory = OrderedDict

    def __init__(self, graph_config=[], state={}, background_nodes=[]):
        """ Construct a graph."""
        super().__init__()
        self._add_from_config(graph_config)
        self.state = state
        self.background_nodes = background_nodes

    def _add_from_config(self, config):
        """Enlarge this graph with nodes and edges specified in a Python
           configuration object.

           Args:
               config (list(tuple)): Specifies nodes, edges, and labels to add.
           """
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
        """All nodes not frozen as background."""
        return self.complement(self.background_nodes)

    @foreground_nodes.setter
    def foreground_nodes(self, foreground_nodes):
        self.background_nodes = self.complement(foreground_nodes)

    def complement(self, nodes):
        """Return all nodes not in the list provided."""
        return [node for node in self.nodes() if node not in nodes]

    def subgraph(self, subgraph_nodes):
        """Create a subgraph containing only the nodes provided and edges
           between them. Background elements and state are inherited."""
        subgraph = super().subgraph(nodes)
        subgraph_nodes_indices = self.get_indices(subgraph.nodes())
        subgraph.state = self.state[subgraph_node_indices]
        subgraph.background_nodes = [node for node in subgraph.nodes()
                                     if node in self.background_nodes]

        return subgraph

    def _get_node_ordering(self, unordered_nodes):
        """Sort the provided nodes according to their order in the graph."""
        return [node for node in self.nodes() if node in unordered_nodes]

    def markov_blanket(self, node):
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

    def neighborhood(self, node):
        """Yield a subgraph induced on the node, its parents, and children."""
        parents = set(self.pred[node])
        children = set(self.succ[node])

        neighborhood = set.union({node}, parents, children)
        neighborhood = self._get_node_ordering(neighborhood)
        return self.subgraph(neighborhood)

    def get_index(self, node):
        """Get the index of a single node, according to the graph's node order."""
        return self.nodes().index(node)

    def get_indicies(self, nodes):
        """Get a a list of node indices according to graph order. The ith entry
           in the returned list is the index of the ith node in the input list.
           PyPhi networks spawned using Graph methods maintain these node
           indices."""
        return [self.get_index(node) for node in nodes]

    def tic(self, timesteps=1):
        """Evolve the system's state according to its mechanisms. Background
           elements are ignored.

        Keyword Args:
            timesteps (int): The number of iterations to evolve. Default is 1.
        """
        for t in range(timesteps):
            self.state = utils.predict_next_state(self, self.state)

    @property
    def tpm(self):
        """Yield the State-by-node LOLI tpm for the full system. Not conditioned
           on background elements. Can be piped right into PyPhi."""
        return self.loli_tpm

    @property
    def loli_tpm(self):
        # TODO: Condition on background elements
        """Yield the State-by-node LOLI tpm for the full system. Not conditioned
           on background elements."""
        number_of_states = 2 ** len(self)
        number_of_nodes = len(self)
        tpm = np.zeros([number_of_states, number_of_nodes])
        for state_index in range(number_of_states):
            current_state = loli_index2state(state_index, number_of_nodes)
            tpm[state_index] = utils.predict_next_state(self, current_state)

        return tpm

    @property
    def connectivity_matrix(self):
        """Yields a np.array connectivity matrix for the graph.
           Can be piped right into PyPhi."""
        return nx.to_numpy_matrix(self)

    @property
    def node_tokens(self):
        return [str(node) for node in self.nodes()]

    def pyphi_network(self):
        # TODO: Make PyPhi maintain node labels
        """Yield a PyPhi network corresponding to the graph. PyPhi node indices
           will match graph node indices."""
        return pyphi.Network(self.tpm, self.connectivity_matrix)

    def pyphi_subsystem(self):
        """Yield a PyPhi subsystem corresponding to the graph in its current
           state. Background elements are frozen in PyPhi. PyPhi node indicies
           match graph node indices."""
        net = pyphi.Network(self.tpm, self.connectivity_matrix)
        foreground_node_indices = self.get_indices(self.foreground_nodes)
        return pyphi.Subsystem(net, self.state, foreground_node_indices)

    @property
    def state(self):
        """The current state of the system.

        Getting this property always yields a numpy array for easy calls to
        PyPhi, but setting is flexible.
        Example 1: graph.state = np.array([0, 0, 1])
        Example 2: graph.state = [0, 0, 1]
        Example 3: graph.state = {'on' : ['C']}
        """
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
