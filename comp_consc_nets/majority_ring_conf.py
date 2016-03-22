from micro_mechanisms import NOR
import graphite as g

net_conf = [('0', NOR),
            ('1', NOR),
            ('2', NOR),
            ('3', NOR),
            ('4', NOR),
            ('5', NOR),
            ('6', NOR, '0', '1'),
            ('7', NOR, '2', '3'),
            ('8', NOR, '4', '5'),
            ('9', NOR, '6', '7', '8'),
            ('10', NOR, '9')]

state_conf = {'off': []}

if __name__ == "__main__":
    net = g.Network(net_conf, state_conf)
    import pdb; pdb.set_trace()
    concepts = net.net_first_order_concepts(just_phi=True, use_roi=False)
    print(concepts)
