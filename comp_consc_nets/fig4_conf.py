from micro_mechanisms import AND, OR, XOR
import graphite as g

net_conf = [('A', OR, 'B', 'C'),
            ('B', AND, 'A', 'C'),
            ('C', XOR, 'A', 'B')]

state1 = {'on': ['A']}

if __name__ == "__main__":
    net = g.Network(net_conf, state1)
    concepts = net.net_first_order_concepts(just_phi=False, use_roi=False)
    print(concepts)
    big_phi = net.net_first_order_mip()
    print(big_phi)
    import pdb; pdb.set_trace()

