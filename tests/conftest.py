from copy import deepcopy

import pytest

from graphiit import Graph
from graphiit.example_graphs import oizumi2014_fig4


@pytest.fixture
def fig4_graph():
    return Graph(oizumi2014_fig4.graph_config)


@pytest.fixture
def fig4_config():
    return deepcopy(oizumi2014_fig4.graph_config)
