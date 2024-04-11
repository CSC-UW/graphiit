from collections import namedtuple

import numpy as np
import pyphi

from . import node_functions

NodeConfig = namedtuple("NodeConfig", ["label", "mechanism", "inputs"])


def parse_graph_config(graph_config: dict) -> "list[NodeConfig]":
    """Parse a graph configuration list.

    Returns:
        list[NodeConfig]
    """
    all_labels = []
    all_inputs = set()

    parsed_config = []
    for node_config in graph_config:

        label = node_config[0]
        inputs = node_config[2:]

        all_labels.append(label)
        all_inputs.update(inputs)

        if isinstance(node_config[1], str):
            mechanism = node_functions.MAP[node_config[1]]
        else:
            mechanism = node_config[1]

        parsed_config.append(NodeConfig(label, mechanism, inputs))

    if all_inputs - set(all_labels):
        raise ValueError(
            "Nodes {} are given as inputs but are not specified as nodes in "
            "the graph".format(all_inputs - set(all_labels))
        )

    if len(all_labels) != len(set(all_labels)):
        raise ValueError("Duplicate node labels provided")

    return parsed_config


def format_node_labels_by_state(
    node_labels: list, states: list, mode: str = "fore"
) -> "list[str]":
    assert len(node_labels) is len(states)
    assert mode in ["fore", "back"]

    CYAN_FORE = "\033[36m"
    RED_FORE = "\033[31m"
    WHITE_BACK = "\033[47m"
    BLACK_BACK = "\033[40m"
    END = "\033[0m"

    new_labels = list()
    for label, state in zip(node_labels, states):
        label = str(label)
        if state and mode == "fore":
            new_labels.append(CYAN_FORE + label + END)
        if state and mode == "back":
            new_labels.append(WHITE_BACK + label + END)
        if not state and mode == "fore":
            new_labels.append(RED_FORE + label + END)
        if not state and mode == "back":
            new_labels.append(BLACK_BACK + label + END)

    return new_labels


def pretty_print_tpm(node_labels: list, tpm: np.ndarray):
    number_of_states, number_of_nodes = tpm.shape
    for state_index in range(number_of_states):
        current_state = pyphi.convert.le_index2state(state_index, number_of_nodes)
        next_state = tpm[state_index, :]
        pretty_tokens = format_node_labels_by_state(
            node_labels, current_state, mode="back"
        )
        pretty_tokens = format_node_labels_by_state(
            pretty_tokens, next_state, mode="fore"
        )
        print(":".join(pretty_tokens))
