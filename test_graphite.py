import pytest
import fig4_conf
from graphite import *


@pytest.fixture
def fig4():
    return Network(fig4_conf.net_conf)


def test_Network():
    empty_net = Network(fig4_conf.net_conf)


def test_node_tokens(fig4):
    assert fig4.node_tokens == ['A', 'B', 'C']

def test_format_node_tokens_by_state(fig4):
    state = (1, 0, 0)
    fore = format_node_tokens_by_state(fig4.node_tokens, state, mode='fore')
    print("Tokens formatted by foreground color, should be cyan:red:red")
    print(':'.join(fore))
    back = format_node_tokens_by_state(fig4.node_tokens, state, mode='back')
    print("Tokens formatted by background color, should be white:black:black")
    print(':'.join(back))
    fore_and_back = format_node_tokens_by_state(fore, state, mode='back')
    print("Tokens formatter by both FG and BG.")
    print(':'.join(fore_and_back))

def test_pretty_print_tpm(fig4):
    print("Pretty printing figure 4 TPM")
    pretty_print_tpm(fig4.node_tokens, fig4.tpm)
