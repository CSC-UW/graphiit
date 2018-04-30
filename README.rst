Graphiit
~~~~~~~~

Utilities for building `PyPhi <https://github.com/wmayner/pyphi>`_ networks
that need to be large and/or malleable.


Installation
~~~~~~~~~~~~

You can install ``graphiit`` from `PyPi
<https://pypi.python.org/pypi/graphiit>`_::

    pip install graphiit

Or the latest development version from `Github
<https://github.com/grahamfindlay/graphiit>`_::

    pip install git+https://github.com/grahamfindlay/graphiit@develop


Basic Usage
~~~~~~~~~~~

At the core of ``graphiit`` is the ``Graph`` object.

    >>> from graphiit import Graph

``Graph`` takes a graph configuration as a parameter:

    >>> graph_config = [
        ('A', 'OR', 'B', 'C'),
        ('B', 'AND', 'A', 'C'),
        ('C', 'XOR', 'A', 'B')]
    >>> graph = Graph(graph_config)

Each line in the configuration specifies the name of a node, the mechanism that
the node implements, and the nodes in the network which input to the node. For
example, in the above configuration the line ``('A', 'OR', 'B', 'C')`` specifies
that node ``A`` is an OR-gate over the inputs ``B`` and ``C``.

Once we've initialized a ``Graph`` object, we can create a PyPhi ``Network``:

    >>> network = graph.pyphi_network()

That's it! You can now perform all IIT computations using this network.


Mechanisms
~~~~~~~~~~

While ``graphiit`` has a number of builtin mechanisms, you can easily specify
your own by defining a function which takes the states of the input nodes as a
parameter and returns ``True`` if the mechanism should be on and ``False`` if
it should be off.

    >>> def ALWAYS_ON(inputs):
    ...     return True

You can then use this function in the graph configuration:

    >>> graph_config = [('A', ALWAYS_ON, 'A')]
    >>> graph = Graph(graph_config)

See ``graphiit.micro_mechanisms`` for implementations of the basic mechanisms.


Other Functionality
~~~~~~~~~~~~~~~~~~~

TODO
