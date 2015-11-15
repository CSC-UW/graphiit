from micro_elements import AND, OR, XOR

net_conf = [('A', OR, 'B', 'C'),
            ('B', AND, 'A', 'C'),
            ('C', XOR, 'A', 'B')]

state1 = {'on': ['A']}
