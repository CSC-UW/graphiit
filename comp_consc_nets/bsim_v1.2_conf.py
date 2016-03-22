import graphite as g
from micro_mechanisms import OR, AND, XOR, COPY, NOT

net_conf = [('A', OR, 'M', 'O'),
            ('B', COPY, 'M'),
            ('C', XOR, 'O', 'P'),
            ('D', COPY, 'B'),
            ('E', COPY, 'C'),
            ('F', COPY, 'E'),
            ('G', AND, 'A', 'HH', 'II'),
            ('H', AND, 'D', 'HH', 'JJ'),
            ('I', AND, 'F', 'GG', 'JJ'),
            ('J', XOR, 'G', 'H', 'I'),
            ('K', AND, 'J', 'LL', 'MM'),
            ('L', AND, 'J', 'LL', 'NN'),
            ('M', AND, 'J', 'KK', 'NN'),
            ('N', COPY, 'K'),
            ('O', COPY, 'L'),
            ('P', COPY, 'N'),
            ('AA', COPY, 'FF'),
            ('BB', COPY, 'AA'),
            ('CC', COPY, 'BB'),
            ('DD', COPY, 'CC'),
            ('EE', COPY, 'DD'),
            ('FF', COPY, 'EE'),
            ('GG', NOT, 'BB'),
            ('HH', COPY, 'BB'),
            ('II', NOT, 'CC'),
            ('JJ', COPY, 'CC'),
            ('KK', NOT, 'PP'),
            ('LL', COPY, 'PP'),
            ('MM', NOT, 'RR'),
            ('NN', COPY, 'RR'),
            ('OO', COPY, 'BB'),
            ('PP', COPY, 'OO'),
            ('QQ', COPY, 'CC'),
            ('RR', COPY, 'QQ')]

state1 = {'on': ['P', 'AA', 'BB']}
state4 = {'on': ['F', 'DD', 'EE', 'GG', 'JJ', 'LL', 'MM', 'PP', 'QQ', 'RR']}

roi = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
       'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']

if __name__ == "__main__":
    net = g.Network(net_conf, state4, roi)
    concepts = net.net_first_order_concepts(just_phi=True, use_roi=True)
    print(concepts)
