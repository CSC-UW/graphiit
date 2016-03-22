from itertools import chain, combinations
from pyphi.convert import loli_index2state, state2holi_index
import numpy as np


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


def convert_holi_tpm_to_loli(holi_tpm):
    # Assumes state by node format
    states, nodes = holi_tpm.shape
    loli_tpm = np.zeros([states, nodes])
    for i in range(states):
        loli_state = loli_index2state(i, nodes)
        holi_tpm_row = state2holi_index(loli_state)
        loli_tpm[i, :] = holi_tpm[holi_tpm_row, :]

    return loli_tpm


def powerset(iterable):
    # unused
    # https://docs.python.org/2/library/itertools.html
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


def bit(boolean):
    # unused
    return int(boolean)
