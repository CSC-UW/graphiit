from __future__ import annotations
from collections import OrderedDict

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
        tpm (np.array): State-by-node TPM of the full system. Not conditioned on background nodes!
        cm (np.array): Connectivity matrix of full system.
        node_labels (list): Node IDs
    """

    # Nodes will be in Graph.nodes() in the same order as they were added to the
    #   graph. Order will be preserved by all networkx methods. NO guarantees
    #   are made about edge order.
    node_dict_factory = OrderedDict

    def __init__(self, graph_config=None, state=None, background=None):
        """Construct a graph."""
        super().__init__()
        self._config = graph_config or []
        self._add_from_config(self._config)
        self.set_state(state)
        self.set_background(background)

    def _add_from_config(self, config: list[tuple]):
        """Enlarge this graph with nodes and edges specified in a Python
        configuration object.

        Args:
            config (list(tuple)): Specifies nodes, edges, and labels to add.
        """
        parsed_config = utils.parse_graph_config(config)

        # add nodes before adding any edges,
        # so that they are added to the graph in config file order
        for label, node_fn, inputs in parsed_config:
            self.add_node(label, function=node_fn)

        # now add edges
        for label, node_fn, inputs in parsed_config:
            for input in inputs:
                self.add_edge(input, label)

    def __repr__(self):
        return f"graphiit.Graph({self.nodes})"

    def __str__(self):
        return repr(self)

    def subgraph(self, subgraph_nodes) -> Graph:
        """Create a subgraph containing only the nodes provided and edges
        between them, preserving order. Background nodes and state are inherited."""
        subgraph_config = [
            node_conf for node_conf in self._config if node_conf[0] in subgraph_nodes
        ]  # Remove nodes not in subgraph
        subgraph_config = [
            (
                *node_conf[:2],
                *filter(lambda node: node in subgraph_nodes, node_conf[2:]),
            )
            for node_conf in subgraph_config
        ]  # Remove edges not in subgraph
        subgraph_config = [
            node_conf for node_conf in subgraph_config if len(node_conf) > 2
        ]  # Remove nodes with no edges left
        return Graph(
            graph_config=subgraph_config,
            state=self.get_state_dict(subgraph_nodes),
            background=self.get_background_dict(subgraph_nodes),
        )

    def markov_blanket(self, node) -> Graph:
        """Yield a subgraph induced on the node, its parents, children, and
        children's parents."""
        parents = set(self.pred[node])
        children = set(self.succ[node])
        childrens_parents = set()
        for child in children:
            childrens_parents.update(set(self.pred[child]))

        blanket = set.union({node}, parents, children, childrens_parents)
        return self.subgraph(blanket)

    def neighborhood(self, node) -> Graph:
        """Yield a subgraph induced on the node, its parents, and children."""
        parents = set(self.pred[node])
        children = set(self.succ[node])

        neighborhood = set.union({node}, parents, children)
        return self.subgraph(neighborhood)

    @property
    def tpm(self) -> np.ndarray:
        """Yield the State-by-Node TPM for the full system.

        Not conditioned on background nodes. Can piped directly into PyPhi
        """
        n = len(self)
        tpm = np.zeros([2**n, n])

        for i, state in enumerate(pyphi.utils.all_states(n)):
            tpm[i] = self.predict_next_state(current_state=state, asarray=True)

        return tpm

    @property
    def cm(self) -> np.ndarray:
        """Yields a connectivity matrix. Can be piped right into PyPhi."""
        return nx.adjacency_matrix(self).todense()

    def pyphi_network(self) -> pyphi.Network:
        """Yield a PyPhi network corresponding to the graph. PyPhi node indices
        will match graph node indices."""
        return pyphi.Network(self.tpm, self.cm, list(self.nodes))

    def set_state(self, state):
        """Flexible state setting.
        Example 1: graph.state = np.array([0, 0, 1])
        Example 2: graph.state = [0, 0, 1]
        Example 3: graph.state = {'on' : ['C']}
        Example 4: graph.state = {'A': 0, 'B': 0, 'C': 1}
        """
        if state:
            node_states = self.parse_state(state)
            nx.set_node_attributes(self, node_states, "state")

    def get_state_dict(self, nodes=None) -> OrderedDict:
        """The current state of the system, as a dictionary keyed by node.

        If the state has not been set, np.NaNs will be returned.
        Example 1: graph.get_state_dict() = {'A': 0, 'B': 0, 'C': 1}
        Example 2: graph.get_state_dict(['A', 'C']) = {'A': 0, 'C': 1}
        Example 3: graph.get_state_dict() = {'A': np.nan, 'B': np.nan, 'C': np.nan}
        """
        if nodes is None:
            nodes = self.nodes
        return OrderedDict(
            {
                node: state
                for node, state in nx.get_node_attributes(self, "state", np.nan).items()
                if node in nodes
            }
        )

    def get_state_array(self, nodes=None, dtype=int) -> np.ndarray:
        """The current state of the system, as a numpy array.

        If the state has not been set, np.NaNs will be returned.
        Example 1: graph.get_state_array() = np.array([0, 0, 1])
        Example 2: graph.get_state_array(['A', 'C']) = np.array([0, 1])
        Example 3: graph.get_state_array() = np.array([np.nan, np.nan, np.nan])
        """
        node_states = self.get_state_dict(nodes)
        return np.array(list(node_states.values()), dtype=dtype)

    def input_nodes(self, node) -> list:
        """Yield the inputs nodes to a node.

        Preserves input order from the underlying config,
        in case input order/identity matters to the node's function.
        """
        return list(self.pred[node])

    def predict_next_state(self, current_state=None, asarray=False):
        """Yield the next state of the graph, given a current state.

        Memory friendly: doesn't require a TPM.
        """
        if current_state:
            current_state = self.parse_state(current_state)
        else:
            current_state = self.get_state_dict()

        next_state = {}
        for node in self.nodes:
            input_nodes = self.input_nodes(node)
            if input_nodes:
                input_vector = np.array([current_state[x] for x in input_nodes])
                node_func = self.nodes[node]["function"]
                next_state[node] = node_func(input_vector)
            else:
                # Here we define the state of an inputless node as persistent.
                #   This may not be your intented behavior!
                next_state[node] = current_state[node]

        if asarray:
            next_state = np.array(list(next_state.values()))

        return next_state

    def tic(self, timesteps: int = 1) -> np.ndarray:
        """Evolve the system's state according to its node functions.

        Keyword Args:
            timesteps (int): The number of iterations to evolve. Default is 1.
        """
        for t in range(timesteps):
            self.set_state(self.predict_next_state())

    def parse_state(self, state) -> dict:
        """Parse a state in any supported format into a dictionary of node states.

        For example, any of the following:
            - np.array([0, 0, 1])
            - [0, 0, 1]
            - {'on' : ['C']}
            - {'A': 0, 'B': 0, 'C': 1}
        Yield:
            {'A': 0, 'B': 0, 'C': 1}
        """
        if isinstance(state, (tuple, list, np.ndarray)):
            if len(self) != len(state):
                raise ValueError(
                    "Mis-sized state config. States passed in tuple form must "
                    "specify the state of every node in the graph, no more."
                )
            else:
                return {node: x for node, x in zip(self.nodes, state)}

        if isinstance(state, dict) and set(state) == set(self.nodes):
            return state

        if isinstance(state, dict) and set(state).issubset({"on", "off"}):
            all_nodes = set(self.nodes)
            if ("on" in state) and not ("off" in state):
                on_nodes = set(state["on"])
                off_nodes = all_nodes - on_nodes
            elif ("off" in state) and not ("on" in state):
                off_nodes = set(state["off"])
                on_nodes = all_nodes - off_nodes
            else:
                raise ValueError("State config cannot specifiy both on and off nodes")
            return {node: 1 for node in on_nodes} | {node: 0 for node in off_nodes}

        raise ValueError("State config not recognized.")

    def set_background(self, background):
        if background:
            background = self.parse_background(background)
            nx.set_node_attributes(self, background, "background")

    def get_background_dict(self, nodes=None) -> OrderedDict:
        """A dictionary keyed by node, 1 if that unit is backgrounded, else 0."

        Example 1: graph.get_background_dict() = {'A': 0, 'B': 0, 'C': 1}
        Example 2: graph.get_background_dict(['A', 'C']) = {'A': 0, 'C': 1}
        """
        if nodes is None:
            nodes = self.nodes
        return OrderedDict(
            {
                node: background
                for node, background in nx.get_node_attributes(
                    self, "background", 0
                ).items()
                if node in nodes
            }
        )

    def parse_background(self, background) -> dict:
        """Parse a background config in any supported format into a dictionary of node statuses.

        1 = Background, 0 = Foreground.
        For example, any of the following:
            - np.array([0, 0, 1])
            - [0, 0, 1]
            - {'background' : ['C']}
            - {'A': 0, 'B': 0, 'C': 1}
        Yield:
            {'A': 0, 'B': 0, 'C': 1}

        """
        if isinstance(background, (tuple, list, np.ndarray)):
            if len(self) != len(background):
                raise ValueError(
                    "Mis-sized background config. Status passed in tuple form must "
                    "specify the status of every node in the graph, no more."
                )
            else:
                return {node: x for node, x in zip(self.nodes(), background)}

        if isinstance(background, dict) and set(background) == set(self.nodes):
            return background

        if isinstance(background, dict) and set(background).issubset(
            {"background", "foreground"}
        ):
            all_nodes = set(self.nodes)
            if ("background" in background) and not ("foreground" in background):
                in_nodes = set(background["background"])
                out_nodes = all_nodes - in_nodes
            elif ("foreground" in background) and not ("background" in background):
                out_nodes = set(background["foreground"])
                in_nodes = all_nodes - out_nodes
            else:
                raise ValueError(
                    "Background config cannot specifiy both background and foreground nodes"
                )
            return {node: 1 for node in in_nodes} | {node: 0 for node in out_nodes}

        raise ValueError("Background config not recognized.")
