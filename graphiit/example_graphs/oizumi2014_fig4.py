import graphiit
from graphiit.micro_mechanisms import AND, OR, XOR

graph_conf = [('A', OR, 'B', 'C'),
            ('B', AND, 'A', 'C'),
            ('C', XOR, 'A', 'B')]

state1 = {'on': ['A']}

# TODO : move this to separate file
if __name__ == "__main__":
    graph = g.Graph(graph_conf, state1)
    concepts = graph.net_first_order_concepts(just_phi=False, use_background_nodes=False)
    print(concepts)
    big_phi = graph.net_first_order_mip()
    print(big_phi)
    import pdb; pdb.set_trace()
